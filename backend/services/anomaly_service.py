import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from bson import ObjectId

try:
    from ..models import AlertType, AlertSeverity, TouristStatus
    from ..database import get_tourists_collection, get_location_history_collection, get_geofences_collection
    from .alert_service import AlertService
    from .location_service import LocationService
    from .tourist_service import TouristService
except ImportError:
    from models import AlertType, AlertSeverity, TouristStatus
    from database import get_tourists_collection, get_location_history_collection, get_geofences_collection
    from services.alert_service import AlertService
    from services.location_service import LocationService
    from services.tourist_service import TouristService

logger = logging.getLogger(__name__)

class AnomalyDetectionService:
    """AI-powered anomaly detection service for tourist safety monitoring"""
    
    # Configuration constants based on user requirements
    ROUTE_DEVIATION_THRESHOLD_KM = 2.0  # Alert if deviation > 2km from planned itinerary
    PROLONGED_INACTIVITY_THRESHOLD_MINUTES = 90  # Alert if no movement for > 90 minutes
    BACKGROUND_TASK_INTERVAL_MINUTES = 5  # Run anomaly detection every 5 minutes
    
    @staticmethod
    async def run_background_anomaly_detection():
        """Main background task that runs all anomaly detection algorithms"""
        logger.info("Starting background anomaly detection service")
        
        while True:
            try:
                logger.info("Running anomaly detection cycle...")
                
                # Get all active tourists
                active_tourists = await AnomalyDetectionService.get_active_tourists()
                logger.info(f"Monitoring {len(active_tourists)} active tourists")
                
                for tourist in active_tourists:
                    tourist_id = str(tourist["_id"])
                    
                    # Skip if tourist is already in panic state
                    if tourist["status"] == TouristStatus.PANIC.value:
                        continue
                    
                    # Run route deviation detection
                    await AnomalyDetectionService.check_route_deviation(tourist_id, tourist)
                    
                    # Run prolonged inactivity detection  
                    await AnomalyDetectionService.check_prolonged_inactivity(tourist_id, tourist)
                
                # Wait for next cycle
                await asyncio.sleep(AnomalyDetectionService.BACKGROUND_TASK_INTERVAL_MINUTES * 60)
                
            except Exception as e:
                logger.error(f"Error in background anomaly detection: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    @staticmethod
    async def get_active_tourists() -> List[Dict[str, Any]]:
        """Get all active tourists for monitoring"""
        try:
            tourists_collection = await get_tourists_collection()
            
            # Get tourists who are currently visiting
            current_time = datetime.utcnow()
            
            cursor = tourists_collection.find({
                "visit_start_date": {"$lte": current_time},
                "visit_end_date": {"$gte": current_time},
                "status": {"$ne": TouristStatus.PANIC.value}
            })
            
            return await cursor.to_list(length=None)
            
        except Exception as e:
            logger.error(f"Error getting active tourists: {e}")
            return []
    
    @staticmethod
    async def check_route_deviation(tourist_id: str, tourist_data: Dict[str, Any]):
        """Check if tourist has deviated from their planned itinerary"""
        try:
            # Get tourist's current location
            current_location = await AnomalyDetectionService.get_latest_location(tourist_id)
            if not current_location:
                return
            
            # Parse itinerary to get planned route points
            planned_route = await AnomalyDetectionService.parse_itinerary_route(tourist_data.get("itinerary", ""))
            if not planned_route:
                logger.debug(f"No planned route found for tourist {tourist_id}")
                return
            
            # Calculate minimum distance to any planned route point
            current_coords = current_location["coordinates"]["coordinates"]
            min_distance = float('inf')
            
            for route_point in planned_route:
                distance = LocationService.calculate_distance(
                    current_coords[1], current_coords[0],  # current lat, lon
                    route_point["lat"], route_point["lon"]  # planned lat, lon
                )
                min_distance = min(min_distance, distance)
            
            # Check if deviation exceeds threshold
            if min_distance > AnomalyDetectionService.ROUTE_DEVIATION_THRESHOLD_KM:
                logger.warning(f"Route deviation detected for tourist {tourist_id}: {min_distance:.2f}km from planned route")
                
                # Create route deviation alert
                await AlertService.create_route_deviation_alert(
                    tourist_id=tourist_id,
                    longitude=current_coords[0],
                    latitude=current_coords[1],
                    deviation_distance=min_distance,
                    address=current_location.get("address")
                )
                
                # Update tourist status to anomaly
                await TouristService.update_tourist_status(
                    tourist_id, 
                    TouristStatus.ANOMALY, 
                    f"Route deviation: {min_distance:.2f}km from planned itinerary"
                )
        
        except Exception as e:
            logger.error(f"Error checking route deviation for tourist {tourist_id}: {e}")
    
    @staticmethod
    async def check_prolonged_inactivity(tourist_id: str, tourist_data: Dict[str, Any]):
        """Check if tourist has been inactive for too long"""
        try:
            # Get latest location update time
            last_update = tourist_data.get("last_location_update")
            if not last_update:
                # Check location history directly
                latest_location = await AnomalyDetectionService.get_latest_location(tourist_id)
                if not latest_location:
                    return
                last_update = latest_location["timestamp"]
            
            # Calculate inactivity duration
            current_time = datetime.utcnow()
            inactivity_duration = current_time - last_update
            inactivity_minutes = inactivity_duration.total_seconds() / 60
            
            if inactivity_minutes > AnomalyDetectionService.PROLONGED_INACTIVITY_THRESHOLD_MINUTES:
                # Check if tourist is in a safe zone (hotel, tourist center, etc.)
                is_in_safe_zone = await AnomalyDetectionService.is_in_safe_zone(tourist_id)
                
                if not is_in_safe_zone:
                    logger.warning(f"Prolonged inactivity detected for tourist {tourist_id}: {inactivity_minutes:.1f} minutes")
                    
                    # Get last known location for alert
                    latest_location = await AnomalyDetectionService.get_latest_location(tourist_id)
                    if latest_location:
                        coords = latest_location["coordinates"]["coordinates"]
                        
                        # Create prolonged inactivity alert
                        await AlertService.create_prolonged_inactivity_alert(
                            tourist_id=tourist_id,
                            longitude=coords[0],
                            latitude=coords[1],
                            inactivity_duration_minutes=int(inactivity_minutes),
                            address=latest_location.get("address")
                        )
                        
                        # Update tourist status to anomaly
                        await TouristService.update_tourist_status(
                            tourist_id,
                            TouristStatus.ANOMALY,
                            f"Prolonged inactivity: {inactivity_minutes:.1f} minutes without location update"
                        )
        
        except Exception as e:
            logger.error(f"Error checking prolonged inactivity for tourist {tourist_id}: {e}")
    
    @staticmethod
    async def get_latest_location(tourist_id: str) -> Optional[Dict[str, Any]]:
        """Get the latest location for a tourist"""
        try:
            location_collection = await get_location_history_collection()
            
            latest_location = await location_collection.find_one(
                {"tourist_id": ObjectId(tourist_id)},
                sort=[("timestamp", -1)]
            )
            
            return latest_location
            
        except Exception as e:
            logger.error(f"Error getting latest location for tourist {tourist_id}: {e}")
            return None
    
    @staticmethod
    async def is_in_safe_zone(tourist_id: str) -> bool:
        """Check if tourist is currently in a designated safe zone"""
        try:
            # Get tourist's current location
            latest_location = await AnomalyDetectionService.get_latest_location(tourist_id)
            if not latest_location:
                return False
            
            coords = latest_location["coordinates"]["coordinates"]
            
            # Check if current location intersects with any safe zone geofences
            geofences_collection = await get_geofences_collection()
            
            query = {
                "active": True,
                "type": "safe_zone",
                "coordinates": {
                    "$geoIntersects": {
                        "$geometry": {
                            "type": "Point",
                            "coordinates": coords
                        }
                    }
                }
            }
            
            safe_zone = await geofences_collection.find_one(query)
            return safe_zone is not None
            
        except Exception as e:
            logger.error(f"Error checking safe zone for tourist {tourist_id}: {e}")
            return False
    
    @staticmethod
    async def parse_itinerary_route(itinerary_text: str) -> List[Dict[str, float]]:
        """Parse itinerary text to extract planned route coordinates"""
        try:
            # This is a simplified implementation
            # In a real system, you might use NLP to extract locations and geocode them
            # For now, we'll look for coordinate patterns or known location names
            
            route_points = []
            
            # Define some common tourist locations in Darjeeling with coordinates
            known_locations = {
                "mall road": {"lat": 27.0410, "lon": 88.2663},
                "darjeeling railway station": {"lat": 27.0410, "lon": 88.2663},
                "tiger hill": {"lat": 27.0340, "lon": 88.2780},
                "batasia loop": {"lat": 27.0330, "lon": 88.2570},
                "japanese peace pagoda": {"lat": 27.0510, "lon": 88.2420},
                "himalayan mountaineering institute": {"lat": 27.0520, "lon": 88.2580},
                "padmaja naidu himalayan zoological park": {"lat": 27.0520, "lon": 88.2580},
                "tea garden": {"lat": 27.0300, "lon": 88.2600},
                "observatory hill": {"lat": 27.0430, "lon": 88.2650}
            }
            
            # Convert itinerary to lowercase for matching
            itinerary_lower = itinerary_text.lower()
            
            # Find known locations mentioned in itinerary
            for location_name, coords in known_locations.items():
                if location_name in itinerary_lower:
                    route_points.append(coords)
            
            # If no known locations found, add some default tourist route
            if not route_points:
                route_points = [
                    {"lat": 27.0410, "lon": 88.2663},  # Mall Road (central area)
                    {"lat": 27.0340, "lon": 88.2780},  # Tiger Hill
                    {"lat": 27.0330, "lon": 88.2570}   # Batasia Loop
                ]
            
            logger.debug(f"Parsed {len(route_points)} route points from itinerary")
            return route_points
            
        except Exception as e:
            logger.error(f"Error parsing itinerary route: {e}")
            return []
    
    @staticmethod
    async def calculate_safety_score(tourist_id: str) -> Dict[str, Any]:
        """Calculate comprehensive safety score for a tourist"""
        try:
            tourist_data = await TouristService.get_tourist_by_id(tourist_id)
            if not tourist_data:
                return {"safety_score": 50, "risk_factors": ["Tourist not found"]}
            
            base_score = 100
            risk_factors = []
            
            # Factor 1: Current location risk level
            current_location = await AnomalyDetectionService.get_latest_location(tourist_id)
            if current_location:
                coords = current_location["coordinates"]["coordinates"]
                geofences = await LocationService.check_geofence_breaches(coords[0], coords[1], tourist_id)
                
                for fence in geofences:
                    if fence["risk_level"] == "critical":
                        base_score -= 40
                        risk_factors.append(f"In critical risk zone: {fence['fence_name']}")
                    elif fence["risk_level"] == "high":
                        base_score -= 25
                        risk_factors.append(f"In high risk zone: {fence['fence_name']}")
                    elif fence["risk_level"] == "medium":
                        base_score -= 10
                        risk_factors.append(f"In medium risk zone: {fence['fence_name']}")
            
            # Factor 2: Time since last location update
            if tourist_data.last_location_update:
                time_diff = datetime.utcnow() - tourist_data.last_location_update
                hours_inactive = time_diff.total_seconds() / 3600
                
                if hours_inactive > 3:
                    base_score -= 20
                    risk_factors.append(f"No location update for {hours_inactive:.1f} hours")
                elif hours_inactive > 1:
                    base_score -= 10
                    risk_factors.append(f"Location update delayed by {hours_inactive:.1f} hours")
            
            # Factor 3: Current status
            if tourist_data.status == TouristStatus.PANIC:
                base_score = 0
                risk_factors.append("Tourist in panic state")
            elif tourist_data.status == TouristStatus.ANOMALY:
                base_score -= 30
                risk_factors.append("Anomalous behavior detected")
            
            # Factor 4: Time of day (higher risk at night)
            current_hour = datetime.utcnow().hour
            if current_hour >= 22 or current_hour <= 5:  # 10 PM to 5 AM
                base_score -= 15
                risk_factors.append("Traveling during high-risk hours (night)")
            
            # Ensure score stays within bounds
            safety_score = max(0, min(100, base_score))
            
            return {
                "safety_score": safety_score,
                "risk_factors": risk_factors,
                "last_updated": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error calculating safety score for tourist {tourist_id}: {e}")
            return {"safety_score": 50, "risk_factors": ["Error calculating score"]}
    
    @staticmethod
    async def manual_anomaly_check(tourist_id: str) -> Dict[str, Any]:
        """Manually trigger anomaly detection for specific tourist"""
        try:
            tourist_data = await TouristService.get_tourist_by_id(tourist_id)
            if not tourist_data:
                return {"error": "Tourist not found"}
            
            results = {
                "tourist_id": tourist_id,
                "timestamp": datetime.utcnow(),
                "checks_performed": [],
                "anomalies_detected": []
            }
            
            # Check route deviation
            try:
                await AnomalyDetectionService.check_route_deviation(tourist_id, tourist_data.dict())
                results["checks_performed"].append("route_deviation")
            except Exception as e:
                results["anomalies_detected"].append(f"Route deviation check failed: {e}")
            
            # Check prolonged inactivity
            try:
                await AnomalyDetectionService.check_prolonged_inactivity(tourist_id, tourist_data.dict())
                results["checks_performed"].append("prolonged_inactivity")
            except Exception as e:
                results["anomalies_detected"].append(f"Inactivity check failed: {e}")
            
            # Calculate safety score
            safety_data = await AnomalyDetectionService.calculate_safety_score(tourist_id)
            results["safety_score"] = safety_data
            
            return results
            
        except Exception as e:
            logger.error(f"Error in manual anomaly check for tourist {tourist_id}: {e}")
            return {"error": str(e)}