import json
import logging
from pathlib import Path
from typing import List, Dict, Any

try:
    from ..database import get_geofences_collection
    from ..models import GeofenceType, RiskLevel
except ImportError:
    from database import get_geofences_collection  
    from models import GeofenceType, RiskLevel

logger = logging.getLogger(__name__)

class StaticGeofenceLoader:
    """Service to load static geofences from JSON configuration into MongoDB"""
    
    @staticmethod
    async def load_static_geofences() -> bool:
        """Load static geofences from geofences.json file"""
        try:
            # Get the path to geofences.json
            current_dir = Path(__file__).parent.parent
            geofences_file = current_dir / "geofences.json"
            
            if not geofences_file.exists():
                logger.error(f"Geofences configuration file not found: {geofences_file}")
                return False
            
            # Read the geofences configuration
            with open(geofences_file, 'r') as file:
                geofences_config = json.load(file)
            
            if not geofences_config:
                logger.warning("No geofences found in configuration file")
                return True
            
            # Get database collection
            geofences_collection = await get_geofences_collection()
            
            # Ensure 2dsphere index exists on geometry field for high-performance geospatial queries
            await StaticGeofenceLoader._ensure_geospatial_index(geofences_collection)
            
            # Check if static geofences already exist to avoid duplicates
            existing_count = await geofences_collection.count_documents({"source": "static_config"})
            
            if existing_count > 0:
                logger.info(f"Static geofences already loaded ({existing_count} found). Skipping reload.")
                return True
            
            # Process and insert each geofence
            loaded_count = 0
            for geofence_config in geofences_config:
                try:
                    geofence_doc = await StaticGeofenceLoader._create_geofence_document(geofence_config)
                    await geofences_collection.insert_one(geofence_doc)
                    loaded_count += 1
                    logger.debug(f"Loaded geofence: {geofence_config['name']}")
                    
                except Exception as e:
                    logger.error(f"Error loading geofence '{geofence_config.get('name', 'Unknown')}': {e}")
                    continue
            
            logger.info(f"Successfully loaded {loaded_count} static geofences into MongoDB")
            return True
            
        except Exception as e:
            logger.error(f"Error loading static geofences: {e}")
            return False
    
    @staticmethod
    async def _ensure_geospatial_index(collection):
        """Ensure 2dsphere index exists on coordinates field for optimal geospatial queries"""
        try:
            # Create 2dsphere index on coordinates field (maps to geometry in our case)
            await collection.create_index([("coordinates", "2dsphere")])
            logger.debug("2dsphere index ensured on coordinates field")
            
        except Exception as e:
            logger.error(f"Error creating geospatial index: {e}")
    
    @staticmethod
    async def _create_geofence_document(config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a geofence document from configuration"""
        from datetime import datetime
        
        # Map string values to enum values
        type_mapping = {
            "restricted": GeofenceType.RESTRICTED,
            "high_risk": GeofenceType.HIGH_RISK,
            "safe_zone": GeofenceType.SAFE_ZONE
        }
        
        risk_mapping = {
            "low": RiskLevel.LOW,
            "medium": RiskLevel.MEDIUM, 
            "high": RiskLevel.HIGH,
            "critical": RiskLevel.CRITICAL
        }
        
        # Create the document following our MongoDB schema
        geofence_doc = {
            "name": config["name"],
            "type": type_mapping.get(config["type"], GeofenceType.HIGH_RISK).value,
            "risk_level": risk_mapping.get(config["risk_level"], RiskLevel.MEDIUM).value,
            "coordinates": config["geometry"],  # GeoJSON geometry
            "description": config.get("description", ""),
            "active": True,
            "source": "static_config",  # Mark as static configuration
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        return geofence_doc
    
    @staticmethod
    async def reload_static_geofences() -> bool:
        """Reload static geofences (useful for updates)"""
        try:
            geofences_collection = await get_geofences_collection()
            
            # Remove existing static geofences
            result = await geofences_collection.delete_many({"source": "static_config"})
            logger.info(f"Removed {result.deleted_count} existing static geofences")
            
            # Reload from configuration
            return await StaticGeofenceLoader.load_static_geofences()
            
        except Exception as e:
            logger.error(f"Error reloading static geofences: {e}")
            return False
    
    @staticmethod
    async def get_static_geofences_stats() -> Dict[str, Any]:
        """Get statistics about loaded static geofences"""
        try:
            geofences_collection = await get_geofences_collection()
            
            # Count by type
            pipeline = [
                {"$match": {"source": "static_config", "active": True}},
                {"$group": {
                    "_id": "$type",
                    "count": {"$sum": 1}
                }}
            ]
            
            type_counts = {}
            async for result in geofences_collection.aggregate(pipeline):
                type_counts[result["_id"]] = result["count"]
            
            # Count by risk level
            risk_pipeline = [
                {"$match": {"source": "static_config", "active": True}},
                {"$group": {
                    "_id": "$risk_level", 
                    "count": {"$sum": 1}
                }}
            ]
            
            risk_counts = {}
            async for result in geofences_collection.aggregate(risk_pipeline):
                risk_counts[result["_id"]] = result["count"]
            
            total_static = await geofences_collection.count_documents({
                "source": "static_config", 
                "active": True
            })
            
            return {
                "total_static_geofences": total_static,
                "by_type": type_counts,
                "by_risk_level": risk_counts
            }
            
        except Exception as e:
            logger.error(f"Error getting static geofences stats: {e}")
            return {"error": str(e)}