import hashlib
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from bson import ObjectId
import logging

try:
    from ..models import (
        Tourist, TouristCreate, TouristResponse, TouristFilters, 
        TouristStatus, LocationData, LocationPoint
    )
    from ..database import get_tourists_collection, get_location_history_collection
    from .digital_id_client import digital_id_client
except ImportError:
    from models import (
        Tourist, TouristCreate, TouristResponse, TouristFilters, 
        TouristStatus, LocationData, LocationPoint
    )
    from database import get_tourists_collection, get_location_history_collection
    from services.digital_id_client import digital_id_client

logger = logging.getLogger(__name__)

class TouristService:
    
    @staticmethod
    def generate_digital_id(kyc_id: str) -> str:
        """Generate unique digital ID from KYC data"""
        # Create a hash of the KYC ID with timestamp for uniqueness
        timestamp = str(int(datetime.utcnow().timestamp()))
        combined = f"{kyc_id}_{timestamp}"
        hash_object = hashlib.sha256(combined.encode())
        hex_dig = hash_object.hexdigest()[:8].upper()
        return f"DIG-{hex_dig}"
    
    @staticmethod
    def hash_kyc_id(kyc_id: str) -> str:
        """Hash KYC ID for security"""
        return hashlib.sha256(kyc_id.encode()).hexdigest()
    
    @staticmethod
    async def create_tourist(tourist_data: TouristCreate) -> Tourist:
        """Create a new tourist"""
        try:
            tourists_collection = await get_tourists_collection()
            
            # Generate digital ID and hash KYC
            digital_id = TouristService.generate_digital_id(tourist_data.kyc_id)
            kyc_hash = TouristService.hash_kyc_id(tourist_data.kyc_id)
            
            # Create tourist object
            tourist = Tourist(
                digital_id=digital_id,
                full_name=tourist_data.full_name,
                nationality=tourist_data.nationality,
                photo_url=tourist_data.photo_url,
                kyc_type=tourist_data.kyc_type,
                kyc_id_hash=kyc_hash,
                visit_start_date=tourist_data.visit_start_date,
                visit_end_date=tourist_data.visit_end_date,
                itinerary=tourist_data.itinerary,
                emergency_contacts=tourist_data.emergency_contacts
            )
            
            # Insert into database
            result = await tourists_collection.insert_one(tourist.dict(by_alias=True))
            tourist.id = result.inserted_id
            
            logger.info(f"Created tourist: {digital_id}")
            return tourist
            
        except Exception as e:
            logger.error(f"Error creating tourist: {e}")
            raise
    
    @staticmethod
    async def get_tourist_by_id(tourist_id: str) -> Optional[Tourist]:
        """Get tourist by ID"""
        try:
            tourists_collection = await get_tourists_collection()
            tourist_data = await tourists_collection.find_one({"_id": ObjectId(tourist_id)})
            
            if tourist_data:
                return Tourist(**tourist_data)
            return None
            
        except Exception as e:
            logger.error(f"Error fetching tourist {tourist_id}: {e}")
            return None
    
    @staticmethod
    async def get_tourist_by_digital_id(digital_id: str) -> Optional[Tourist]:
        """Get tourist by digital ID"""
        try:
            tourists_collection = await get_tourists_collection()
            tourist_data = await tourists_collection.find_one({"digital_id": digital_id})
            
            if tourist_data:
                return Tourist(**tourist_data)
            return None
            
        except Exception as e:
            logger.error(f"Error fetching tourist by digital ID {digital_id}: {e}")
            return None
    
    @staticmethod
    async def get_tourists(filters: TouristFilters) -> List[TouristResponse]:
        """Get tourists with filters"""
        try:
            tourists_collection = await get_tourists_collection()
            location_collection = await get_location_history_collection()
            
            # Build query
            query = {}
            
            if filters.status:
                query["status"] = filters.status.value
            
            if filters.nationality:
                query["nationality"] = filters.nationality
            
            if filters.search:
                query["$or"] = [
                    {"full_name": {"$regex": filters.search, "$options": "i"}},
                    {"digital_id": {"$regex": filters.search, "$options": "i"}},
                    {"nationality": {"$regex": filters.search, "$options": "i"}}
                ]
            
            # Execute query with pagination
            cursor = tourists_collection.find(query).skip(filters.skip).limit(filters.limit)
            tourists_data = await cursor.to_list(length=filters.limit)
            
            # Convert to response format with latest location
            tourists_response = []
            for tourist_data in tourists_data:
                tourist = Tourist(**tourist_data)
                
                # Get latest location
                latest_location = await location_collection.find_one(
                    {"tourist_id": tourist.id},
                    sort=[("timestamp", -1)]
                )
                
                location_data = None
                if latest_location:
                    location_data = LocationData(
                        coordinates=latest_location["coordinates"],
                        address=latest_location.get("address"),
                        timestamp=latest_location["timestamp"]
                    )
                
                tourist_response = TouristResponse(
                    id=str(tourist.id),
                    digital_id=tourist.digital_id,
                    full_name=tourist.full_name,
                    nationality=tourist.nationality,
                    photo_url=tourist.photo_url,
                    visit_start_date=tourist.visit_start_date,
                    visit_end_date=tourist.visit_end_date,
                    itinerary=tourist.itinerary,
                    emergency_contacts=tourist.emergency_contacts,
                    status=tourist.status,
                    safety_score=tourist.safety_score,
                    last_location_update=tourist.last_location_update,
                    location=location_data
                )
                
                tourists_response.append(tourist_response)
            
            return tourists_response
            
        except Exception as e:
            logger.error(f"Error fetching tourists: {e}")
            raise
    
    @staticmethod
    async def update_tourist_status(tourist_id: str, status: TouristStatus, reason: str = None) -> bool:
        """Update tourist status"""
        try:
            tourists_collection = await get_tourists_collection()
            
            update_data = {
                "status": status.value,
                "last_status_update": datetime.utcnow()
            }
            
            if reason:
                update_data["status_reason"] = reason
            
            result = await tourists_collection.update_one(
                {"_id": ObjectId(tourist_id)},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                logger.info(f"Updated tourist {tourist_id} status to {status.value}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating tourist status: {e}")
            return False
    
    @staticmethod
    async def update_safety_score(tourist_id: str, safety_score: int) -> bool:
        """Update tourist safety score"""
        try:
            tourists_collection = await get_tourists_collection()
            
            result = await tourists_collection.update_one(
                {"_id": ObjectId(tourist_id)},
                {"$set": {"safety_score": safety_score, "score_updated_at": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating safety score: {e}")
            return False
    
    @staticmethod
    async def get_tourist_location_history(tourist_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get tourist location history"""
        try:
            location_collection = await get_location_history_collection()
            
            cursor = location_collection.find(
                {"tourist_id": ObjectId(tourist_id)}
            ).sort("timestamp", -1).limit(limit)
            
            locations = await cursor.to_list(length=limit)
            
            # Convert ObjectId to strings
            for location in locations:
                location["_id"] = str(location["_id"])
                location["tourist_id"] = str(location["tourist_id"])
            
            return locations
            
        except Exception as e:
            logger.error(f"Error fetching location history: {e}")
            return []
    
    @staticmethod
    async def get_active_tourists_count() -> int:
        """Get count of active tourists"""
        try:
            tourists_collection = await get_tourists_collection()
            
            current_date = datetime.utcnow().date()
            count = await tourists_collection.count_documents({
                "visit_start_date": {"$lte": datetime.combine(current_date, datetime.min.time())},
                "visit_end_date": {"$gte": datetime.combine(current_date, datetime.min.time())}
            })
            
            return count
            
        except Exception as e:
            logger.error(f"Error getting active tourists count: {e}")
            return 0
    
    @staticmethod
    async def get_tourists_by_status(status: TouristStatus) -> int:
        """Get count of tourists by status"""
        try:
            tourists_collection = await get_tourists_collection()
            count = await tourists_collection.count_documents({"status": status.value})
            return count
            
        except Exception as e:
            logger.error(f"Error getting tourists by status: {e}")
            return 0