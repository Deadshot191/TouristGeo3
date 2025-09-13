from datetime import datetime
from typing import List, Optional, Dict, Any
from bson import ObjectId
import logging

from ..models import Geofence, GeofenceCreate, GeofenceResponse, GeofenceType, RiskLevel
from ..database import get_geofences_collection

logger = logging.getLogger(__name__)

class GeofenceService:
    
    @staticmethod
    async def create_geofence(geofence_data: GeofenceCreate) -> Geofence:
        """Create a new geo-fence"""
        try:
            geofences_collection = await get_geofences_collection()
            
            geofence = Geofence(
                name=geofence_data.name,
                type=geofence_data.type,
                risk_level=geofence_data.risk_level,
                coordinates=geofence_data.coordinates,
                description=geofence_data.description
            )
            
            result = await geofences_collection.insert_one(geofence.dict(by_alias=True))
            geofence.id = result.inserted_id
            
            logger.info(f"Created geo-fence: {geofence.name}")
            return geofence
            
        except Exception as e:
            logger.error(f"Error creating geo-fence: {e}")
            raise
    
    @staticmethod
    async def get_all_geofences(active_only: bool = True) -> List[GeofenceResponse]:
        """Get all geo-fences"""
        try:
            geofences_collection = await get_geofences_collection()
            
            query = {}
            if active_only:
                query["active"] = True
            
            cursor = geofences_collection.find(query)
            geofences_data = await cursor.to_list(length=None)
            
            geofences = []
            for geofence_data in geofences_data:
                geofence = GeofenceResponse(
                    id=str(geofence_data["_id"]),
                    name=geofence_data["name"],
                    type=geofence_data["type"],
                    risk_level=geofence_data["risk_level"],
                    coordinates=geofence_data["coordinates"],
                    description=geofence_data.get("description"),
                    active=geofence_data["active"]
                )
                geofences.append(geofence)
            
            return geofences
            
        except Exception as e:
            logger.error(f"Error fetching geo-fences: {e}")
            return []
    
    @staticmethod
    async def get_geofence_by_id(geofence_id: str) -> Optional[Geofence]:
        """Get geo-fence by ID"""
        try:
            geofences_collection = await get_geofences_collection()
            geofence_data = await geofences_collection.find_one({"_id": ObjectId(geofence_id)})
            
            if geofence_data:
                return Geofence(**geofence_data)
            return None
            
        except Exception as e:
            logger.error(f"Error fetching geo-fence {geofence_id}: {e}")
            return None
    
    @staticmethod
    async def update_geofence(geofence_id: str, update_data: Dict[str, Any]) -> bool:
        """Update geo-fence"""
        try:
            geofences_collection = await get_geofences_collection()
            
            update_data["updated_at"] = datetime.utcnow()
            
            result = await geofences_collection.update_one(
                {"_id": ObjectId(geofence_id)},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating geo-fence: {e}")
            return False
    
    @staticmethod
    async def delete_geofence(geofence_id: str) -> bool:
        """Deactivate geo-fence (soft delete)"""
        try:
            geofences_collection = await get_geofences_collection()
            
            result = await geofences_collection.update_one(
                {"_id": ObjectId(geofence_id)},
                {"$set": {"active": False, "deactivated_at": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error deactivating geo-fence: {e}")
            return False
    
    @staticmethod
    async def check_point_in_geofences(longitude: float, latitude: float) -> List[Dict[str, Any]]:
        """Check if a point is within any geo-fences"""
        try:
            geofences_collection = await get_geofences_collection()
            
            query = {
                "active": True,
                "coordinates": {
                    "$geoIntersects": {
                        "$geometry": {
                            "type": "Point",
                            "coordinates": [longitude, latitude]
                        }
                    }
                }
            }
            
            cursor = geofences_collection.find(query)
            intersecting_fences = await cursor.to_list(length=None)
            
            results = []
            for fence in intersecting_fences:
                results.append({
                    "id": str(fence["_id"]),
                    "name": fence["name"],
                    "type": fence["type"],
                    "risk_level": fence["risk_level"],
                    "description": fence.get("description")
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error checking point in geo-fences: {e}")
            return []
    
    @staticmethod
    async def create_default_geofences():
        """Create default geo-fences for Darjeeling area"""
        try:
            # Check if default fences already exist
            geofences_collection = await get_geofences_collection()
            existing_count = await geofences_collection.count_documents({})
            
            if existing_count > 0:
                logger.info("Default geo-fences already exist")
                return
            
            default_fences = [
                {
                    "name": "Military Restricted Zone",
                    "type": GeofenceType.RESTRICTED,
                    "risk_level": RiskLevel.CRITICAL,
                    "coordinates": {
                        "type": "Polygon",
                        "coordinates": [[
                            [88.2750, 27.0450],
                            [88.2850, 27.0450],
                            [88.2850, 27.0480],
                            [88.2750, 27.0480],
                            [88.2750, 27.0450]
                        ]]
                    },
                    "description": "Military installation - strictly prohibited"
                },
                {
                    "name": "Landslide Prone Area",
                    "type": GeofenceType.HIGH_RISK,
                    "risk_level": RiskLevel.HIGH,
                    "coordinates": {
                        "type": "Polygon",
                        "coordinates": [[
                            [88.2500, 27.0300],
                            [88.2600, 27.0300],
                            [88.2600, 27.0350],
                            [88.2500, 27.0350],
                            [88.2500, 27.0300]
                        ]]
                    },
                    "description": "High risk of landslides during monsoon"
                },
                {
                    "name": "Tourist Safe Zone - Mall Road",
                    "type": GeofenceType.SAFE_ZONE,
                    "risk_level": RiskLevel.LOW,
                    "coordinates": {
                        "type": "Polygon",
                        "coordinates": [[
                            [88.2600, 27.0380],
                            [88.2700, 27.0380],
                            [88.2700, 27.0420],
                            [88.2600, 27.0420],
                            [88.2600, 27.0380]
                        ]]
                    },
                    "description": "Main tourist area with police patrol"
                }
            ]
            
            for fence_data in default_fences:
                geofence = Geofence(**fence_data)
                await geofences_collection.insert_one(geofence.dict(by_alias=True))
            
            logger.info(f"Created {len(default_fences)} default geo-fences")
            
        except Exception as e:
            logger.error(f"Error creating default geo-fences: {e}")