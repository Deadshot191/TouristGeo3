import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..database import get_database
from ..models import (
    SecureTouristData, TouristRegistrationRequest, 
    DataAccessRequest, DataAccessResponse, RegistrationResponse,
    TouristKYCData, AccessType, AccessReason
)
from .encryption_service import encryption_service
from .blockchain_simulator import blockchain_simulator
import logging

logger = logging.getLogger(__name__)

class SecureDataService:
    """
    Core service for managing encrypted tourist data and access control
    Handles registration, secure storage, and emergency data access
    """
    
    async def register_tourist_data(self, request: TouristRegistrationRequest) -> RegistrationResponse:
        """
        Register sensitive tourist data with encryption and blockchain logging
        """
        try:
            db = get_database()
            
            # Check if tourist already exists
            existing = await db.secure_tourist_data.find_one({"tourist_id": request.tourist_id})
            if existing:
                raise ValueError(f"Tourist data already registered for ID: {request.tourist_id}")
            
            # Prepare KYC data
            kyc_data = TouristKYCData(
                kyc_type=request.kyc_type,
                kyc_document_number=request.kyc_document_number,
                kyc_expiry_date=request.kyc_expiry_date,
                issuing_authority=request.issuing_authority
            )
            
            # Create the secure data model
            secure_data = SecureTouristData(
                tourist_id=request.tourist_id,
                full_name=request.full_name,
                nationality=request.nationality,
                date_of_birth=request.date_of_birth,
                passport_country=request.passport_country,
                kyc_data=kyc_data,
                emergency_contacts=request.emergency_contacts,
                detailed_itinerary=request.detailed_itinerary,
                accommodation_details=request.accommodation_details,
                local_guide_contact=request.local_guide_contact,
                travel_insurance_details=request.travel_insurance_details
            )
            
            # Generate integrity hashes (for blockchain simulation)
            kyc_hash = encryption_service.generate_hash(
                f"{request.kyc_type}:{request.kyc_document_number}"
            )
            itinerary_hash = encryption_service.generate_hash(request.detailed_itinerary)
            
            secure_data.kyc_hash = kyc_hash
            secure_data.itinerary_hash = itinerary_hash
            
            # Prepare data for encryption
            sensitive_data = {
                "full_name": secure_data.full_name,
                "nationality": secure_data.nationality,
                "date_of_birth": secure_data.date_of_birth.isoformat() if secure_data.date_of_birth else None,
                "passport_country": secure_data.passport_country,
                "kyc_data": secure_data.kyc_data.dict(),
                "emergency_contacts": [contact.dict() for contact in secure_data.emergency_contacts],
                "detailed_itinerary": secure_data.detailed_itinerary,
                "accommodation_details": secure_data.accommodation_details,
                "local_guide_contact": secure_data.local_guide_contact,
                "travel_insurance_details": secure_data.travel_insurance_details
            }
            
            # Encrypt the sensitive data
            encrypted_data = encryption_service.encrypt_data(sensitive_data)
            
            # Store encrypted data in database
            document = {
                "tourist_id": secure_data.tourist_id,
                "encrypted_data": encrypted_data,
                "kyc_hash": secure_data.kyc_hash,
                "itinerary_hash": secure_data.itinerary_hash,
                "data_version": secure_data.data_version,
                "created_at": secure_data.created_at,
                "last_updated": secure_data.last_updated
            }
            
            result = await db.secure_tourist_data.insert_one(document)
            registration_id = str(result.inserted_id)
            
            # Create blockchain simulation log for registration
            log_data = {
                "tourist_id": request.tourist_id,
                "authority_id": "SYSTEM",
                "authority_name": "Digital ID Service",
                "authority_department": "System Registration",
                "access_type": AccessType.SYSTEM_MAINTENANCE,
                "access_reason": AccessReason.SYSTEM_UPDATE,
                "data_fields_accessed": ["registration"],
                "data_integrity_verified": True
            }
            
            log_entry = await blockchain_simulator.create_immutable_log_entry(log_data)
            await db.data_access_log.insert_one(log_entry.dict(by_alias=True))
            
            logger.info(f"Successfully registered encrypted data for tourist: {request.tourist_id}")
            
            return RegistrationResponse(
                tourist_id=request.tourist_id,
                registration_id=registration_id,
                kyc_hash=kyc_hash,
                itinerary_hash=itinerary_hash,
                created_at=secure_data.created_at,
                status="registered"
            )
            
        except Exception as e:
            logger.error(f"Error registering tourist data: {e}")
            raise
    
    async def request_emergency_access(self, request: DataAccessRequest) -> DataAccessResponse:
        """
        Request access to decrypted tourist data during emergency
        Creates immutable audit log entry
        """
        try:
            db = get_database()
            
            # Find encrypted data
            document = await db.secure_tourist_data.find_one({"tourist_id": request.tourist_id})
            if not document:
                raise ValueError(f"No secure data found for tourist: {request.tourist_id}")
            
            # Decrypt the sensitive data
            encrypted_data = document["encrypted_data"]
            decrypted_data = encryption_service.decrypt_data(encrypted_data)
            
            # Determine which fields to return
            requested_fields = request.requested_fields or [
                "full_name", "nationality", "date_of_birth", "passport_country",
                "kyc_data", "emergency_contacts", "detailed_itinerary",
                "accommodation_details", "local_guide_contact", "travel_insurance_details"
            ]
            
            # Create immutable access log entry
            log_data = {
                "tourist_id": request.tourist_id,
                "authority_id": request.authority_id,
                "authority_name": request.authority_name,
                "authority_department": request.authority_department,
                "access_type": AccessType.EMERGENCY_ACCESS,
                "access_reason": request.access_reason,
                "alert_id": request.alert_id,
                "data_fields_accessed": requested_fields,
                "data_integrity_verified": True
            }
            
            log_entry = await blockchain_simulator.create_immutable_log_entry(log_data)
            result = await db.data_access_log.insert_one(log_entry.dict(by_alias=True))
            access_log_id = str(result.inserted_id)
            
            # Parse date_of_birth if present
            date_of_birth = None
            if decrypted_data.get("date_of_birth"):
                date_of_birth = datetime.fromisoformat(decrypted_data["date_of_birth"])
            
            # Reconstruct KYC data
            kyc_data_dict = decrypted_data.get("kyc_data", {})
            kyc_data = TouristKYCData(**kyc_data_dict)
            
            # Prepare response
            response = DataAccessResponse(
                tourist_id=request.tourist_id,
                access_log_id=access_log_id,
                full_name=decrypted_data.get("full_name", ""),
                nationality=decrypted_data.get("nationality", ""),
                date_of_birth=date_of_birth,
                passport_country=decrypted_data.get("passport_country"),
                kyc_data=kyc_data,
                emergency_contacts=[
                    request.emergency_contacts[i] for i in range(len(decrypted_data.get("emergency_contacts", [])))
                ] if decrypted_data.get("emergency_contacts") else [],
                detailed_itinerary=decrypted_data.get("detailed_itinerary", ""),
                accommodation_details=decrypted_data.get("accommodation_details"),
                local_guide_contact=decrypted_data.get("local_guide_contact"),
                travel_insurance_details=decrypted_data.get("travel_insurance_details"),
                accessed_at=datetime.utcnow(),
                accessed_by=request.authority_name,
                access_reason=request.access_reason.value
            )
            
            logger.info(f"Emergency access granted for tourist: {request.tourist_id} by {request.authority_name}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error during emergency access request: {e}")
            
            # Log failed access attempt
            try:
                db = get_database()
                log_data = {
                    "tourist_id": request.tourist_id,
                    "authority_id": request.authority_id,
                    "authority_name": request.authority_name,
                    "authority_department": request.authority_department,
                    "access_type": AccessType.EMERGENCY_ACCESS,
                    "access_reason": request.access_reason,
                    "alert_id": request.alert_id,
                    "data_fields_accessed": [],
                    "access_granted": False,
                    "access_denied_reason": str(e),
                    "data_integrity_verified": False
                }
                
                log_entry = await blockchain_simulator.create_immutable_log_entry(log_data)
                await db.data_access_log.insert_one(log_entry.dict(by_alias=True))
                
            except Exception as log_error:
                logger.error(f"Error logging failed access attempt: {log_error}")
            
            raise
    
    async def verify_data_integrity(self, tourist_id: str) -> Dict[str, Any]:
        """
        Verify data integrity using stored hashes
        """
        try:
            db = get_database()
            
            document = await db.secure_tourist_data.find_one({"tourist_id": tourist_id})
            if not document:
                return {
                    "status": "error",
                    "message": "Tourist data not found"
                }
            
            # Decrypt data for verification
            encrypted_data = document["encrypted_data"]
            decrypted_data = encryption_service.decrypt_data(encrypted_data)
            
            # Verify KYC hash
            kyc_data = decrypted_data.get("kyc_data", {})
            kyc_string = f"{kyc_data.get('kyc_type')}:{kyc_data.get('kyc_document_number')}"
            calculated_kyc_hash = encryption_service.generate_hash(kyc_string)
            kyc_valid = calculated_kyc_hash == document["kyc_hash"]
            
            # Verify itinerary hash
            itinerary = decrypted_data.get("detailed_itinerary", "")
            calculated_itinerary_hash = encryption_service.generate_hash(itinerary)
            itinerary_valid = calculated_itinerary_hash == document["itinerary_hash"]
            
            return {
                "status": "verified" if kyc_valid and itinerary_valid else "invalid",
                "tourist_id": tourist_id,
                "kyc_hash_valid": kyc_valid,
                "itinerary_hash_valid": itinerary_valid,
                "verification_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error verifying data integrity: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def get_access_logs(self, tourist_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get access logs for audit purposes
        """
        try:
            db = get_database()
            
            query = {}
            if tourist_id:
                query["tourist_id"] = tourist_id
            
            logs = await db.data_access_log.find(query).sort("timestamp", -1).limit(limit).to_list(length=limit)
            
            # Convert ObjectId to string for response
            for log in logs:
                log["_id"] = str(log["_id"])
            
            return logs
            
        except Exception as e:
            logger.error(f"Error getting access logs: {e}")
            return []

# Global secure data service instance
secure_data_service = SecureDataService()