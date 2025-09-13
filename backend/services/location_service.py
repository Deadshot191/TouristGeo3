from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from bson import ObjectId
import logging

from ..models import LocationHistory, LocationUpdate, LocationPoint, TouristStatus
from ..database import get_location_history_collection, get_tourists_collection, get_geofences_collection

logger = logging.getLogger(__name__)

class LocationService:
    
    @staticmethod
    async def update_location(location_update: LocationUpdate) -> bool:
        """Update tourist location"""
        try:
            location_collection = await get_location_history_collection()
            tourists_collection = await get_tourists_collection()
            
            # Create location history record
            location_record = LocationHistory(
                tourist_id=ObjectId(location_update.tourist_id),
                coordinates=LocationPoint(
                    coordinates=[location_update.longitude, location_update.latitude]
                ),
                address=location_update.address,
                accuracy=location_update.accuracy,
                speed=location_update.speed
            )
            
            # Insert location record
            await location_collection.insert_one(location_record.dict(by_alias=True))
            
            # Update tourist's last location update time
            await tourists_collection.update_one(
                {"_id": ObjectId(location_update.tourist_id)},
                {"$set": {"last_location_update": datetime.utcnow()}}
            )
            
            # Check for geo-fence breaches
            breaches = await LocationService.check_geofence_breaches(
                location_update.longitude, 
                location_update.latitude,
                location_update.tourist_id
            )
            
            if breaches:
                logger.warning(f"Geo-fence breaches detected for tourist {location_update.tourist_id}: {breaches}")
                # Here we would trigger alert creation
                from .alert_service import AlertService
                for breach in breaches:
                    await AlertService.create_geofence_breach_alert(
                        location_update.tourist_id,
                        location_update.longitude,
                        location_update.latitude,
                        breach["fence_name"],
                        breach["risk_level"]
                    )
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating location: {e}")
            return False
    
    @staticmethod
    async def get_current_locations() -> List[Dict[str, Any]]:
        """Get current locations of all tourists"""
        try:
            location_collection = await get_location_history_collection()
            tourists_collection = await get_tourists_collection()
            
            # Get latest location for each tourist
            pipeline = [
                {
                    "$sort": {"timestamp": -1}
                },
                {
                    "$group": {
                        "_id": "$tourist_id",
                        "latest_location": {"$first": "$$ROOT"}
                    }
                }
            ]
            
            cursor = location_collection.aggregate(pipeline)
            location_data = await cursor.to_list(length=None)
            
            # Get tourist details
            current_locations = []
            for item in location_data:
                tourist_data = await tourists_collection.find_one({"_id": item["_id"]})
                if tourist_data:
                    location = item["latest_location"]
                    current_locations.append({
                        "tourist_id": str(item["_id"]),
                        "tourist_name": tourist_data["full_name"],
                        "digital_id": tourist_data["digital_id"],
                        "status": tourist_data["status"],
                        "safety_score": tourist_data["safety_score"],
                        "coordinates": location["coordinates"]["coordinates"],
                        "address": location.get("address"),
                        "timestamp": location["timestamp"]
                    })
            
            return current_locations
            
        except Exception as e:
            logger.error(f"Error getting current locations: {e}")
            return []
    
    @staticmethod
    async def check_geofence_breaches(longitude: float, latitude: float, tourist_id: str) -> List[Dict[str, Any]]:
        """Check if coordinates are within any restricted geo-fences"""
        try:
            geofences_collection = await get_geofences_collection()
            
            # Use MongoDB's geospatial query to find intersecting geofences
            query = {
                "active": True,
                "type": {"$in": ["restricted", "high_risk"]},
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
            breached_fences = await cursor.to_list(length=None)
            
            breaches = []
            for fence in breached_fences:
                breaches.append({
                    "fence_id": str(fence["_id"]),
                    "fence_name": fence["name"],
                    "fence_type": fence["type"],
                    "risk_level": fence["risk_level"]
                })
            
            return breaches
            
        except Exception as e:
            logger.error(f"Error checking geo-fence breaches: {e}")
            return []
    
    @staticmethod
    async def detect_prolonged_inactivity(threshold_minutes: int = 120) -> List[str]:
        """Detect tourists with prolonged inactivity"""
        try:
            location_collection = await get_location_history_collection()
            tourists_collection = await get_tourists_collection()
            
            threshold_time = datetime.utcnow() - timedelta(minutes=threshold_minutes)
            
            # Find tourists whose last location update is older than threshold
            inactive_tourists = []
            
            cursor = tourists_collection.find({
                "status": {"$ne": TouristStatus.PANIC.value},
                "$or": [
                    {"last_location_update": {"$lt": threshold_time}},
                    {"last_location_update": {"$exists": False}}
                ]
            })
            
            async for tourist in cursor:
                # Double-check with actual location data
                latest_location = await location_collection.find_one(
                    {"tourist_id": tourist["_id"]},
                    sort=[("timestamp", -1)]
                )
                
                if not latest_location or latest_location["timestamp"] < threshold_time:
                    inactive_tourists.append(str(tourist["_id"]))
            
            return inactive_tourists
            
        except Exception as e:
            logger.error(f"Error detecting prolonged inactivity: {e}")
            return []
    
    @staticmethod
    async def detect_route_deviation(tourist_id: str, threshold_km: float = 5.0) -> bool:
        """Detect if tourist has deviated significantly from their planned route"""
        try:
            # This is a simplified implementation
            # In a real system, you would compare against the stored itinerary
            location_collection = await get_location_history_collection()
            
            # Get recent locations (last 2 hours)
            recent_time = datetime.utcnow() - timedelta(hours=2)
            cursor = location_collection.find({
                "tourist_id": ObjectId(tourist_id),
                "timestamp": {"$gte": recent_time}
            }).sort("timestamp", 1)
            
            locations = await cursor.to_list(length=None)
            
            if len(locations) < 3:
                return False
            
            # Simple heuristic: check if tourist has moved more than threshold distance
            # from their starting point in the last 2 hours
            start_coords = locations[0]["coordinates"]["coordinates"]
            end_coords = locations[-1]["coordinates"]["coordinates"]
            
            distance = LocationService.calculate_distance(
                start_coords[1], start_coords[0],  # lat, lon
                end_coords[1], end_coords[0]
            )
            
            # If moved more than threshold and speed suggests unusual movement
            if distance > threshold_km:
                time_diff = (locations[-1]["timestamp"] - locations[0]["timestamp"]).total_seconds() / 3600
                speed_kmh = distance / time_diff if time_diff > 0 else 0
                
                # Flag if speed is unusually high (> 80 km/h in tourist areas)
                if speed_kmh > 80:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting route deviation: {e}")
            return False
    
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates using Haversine formula (returns km)"""
        import math
        
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        distance = R * c
        return distance
    
    @staticmethod
    async def get_location_trail(tourist_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get location trail for a tourist over specified hours"""
        try:
            location_collection = await get_location_history_collection()
            
            start_time = datetime.utcnow() - timedelta(hours=hours)
            
            cursor = location_collection.find({
                "tourist_id": ObjectId(tourist_id),
                "timestamp": {"$gte": start_time}
            }).sort("timestamp", 1)
            
            locations = await cursor.to_list(length=None)
            
            # Convert ObjectIds to strings
            for location in locations:
                location["_id"] = str(location["_id"])
                location["tourist_id"] = str(location["tourist_id"])
            
            return locations
            
        except Exception as e:
            logger.error(f"Error getting location trail: {e}")
            return []