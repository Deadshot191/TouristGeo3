from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from bson import ObjectId
from enum import Enum

# Custom ObjectId field for Pydantic v2
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_json_schema__(cls, _source_type, _handler):
        return {"type": "string"}
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, field=None):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

# Enums
class AccessType(str, Enum):
    EMERGENCY_ACCESS = "emergency_access"
    AUDIT_VERIFICATION = "audit_verification" 
    SYSTEM_MAINTENANCE = "system_maintenance"

class AccessReason(str, Enum):
    PANIC_ALERT = "panic_alert"
    GEOFENCE_BREACH = "geofence_breach"
    ROUTE_DEVIATION = "route_deviation"
    PROLONGED_INACTIVITY = "prolonged_inactivity"
    AUDIT_REQUEST = "audit_request"
    SYSTEM_UPDATE = "system_update"

# Core Data Models
class EmergencyContact(BaseModel):
    name: str
    phone: str
    relationship: str = "family"

class TouristKYCData(BaseModel):
    """Sensitive KYC data that will be encrypted"""
    kyc_type: Literal["passport", "aadhaar"]
    kyc_document_number: str
    kyc_expiry_date: Optional[datetime] = None
    issuing_authority: Optional[str] = None

class SecureTouristData(BaseModel):
    """Complete sensitive tourist data model - stored encrypted"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    tourist_id: str  # Links to main database tourist record
    
    # Sensitive Personal Information (encrypted in database)
    full_name: str
    nationality: str
    date_of_birth: Optional[datetime] = None
    passport_country: Optional[str] = None
    
    # KYC Information (encrypted in database)
    kyc_data: TouristKYCData
    
    # Emergency Contacts (encrypted in database)
    emergency_contacts: List[EmergencyContact] = []
    
    # Travel Information (encrypted in database)
    detailed_itinerary: str
    accommodation_details: Optional[str] = None
    local_guide_contact: Optional[str] = None
    travel_insurance_details: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    # Data integrity hashes (for blockchain simulation)
    kyc_hash: str  # SHA-256 hash of KYC data
    itinerary_hash: str  # SHA-256 hash of itinerary
    data_version: int = 1

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class DataAccessLog(BaseModel):
    """Immutable audit log entry - simulates blockchain record"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    
    # Access Details
    tourist_id: str
    authority_id: str  # ID of the user/service requesting access
    authority_name: str  # Name of the requesting authority
    authority_department: str  # Department of the requesting authority
    
    # Access Context
    access_type: AccessType
    access_reason: AccessReason
    alert_id: Optional[str] = None  # Link to the alert that triggered access
    
    # Timing
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Request Details
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    
    # Data Access Details
    data_fields_accessed: List[str] = []  # Which specific fields were accessed
    access_granted: bool = True
    access_denied_reason: Optional[str] = None
    
    # Blockchain Simulation Fields
    previous_log_hash: Optional[str] = None  # Hash of previous log entry (blockchain chain)
    current_log_hash: str  # Hash of this log entry
    block_number: int  # Simulated block number
    
    # Verification
    data_integrity_verified: bool = True
    verification_timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Request/Response Models
class TouristRegistrationRequest(BaseModel):
    """Request to register sensitive tourist data"""
    tourist_id: str
    full_name: str
    nationality: str
    date_of_birth: Optional[datetime] = None
    passport_country: Optional[str] = None
    
    # KYC Data
    kyc_type: Literal["passport", "aadhaar"]
    kyc_document_number: str
    kyc_expiry_date: Optional[datetime] = None
    issuing_authority: Optional[str] = None
    
    # Emergency Contacts
    emergency_contacts: List[EmergencyContact] = []
    
    # Travel Information
    detailed_itinerary: str
    accommodation_details: Optional[str] = None
    local_guide_contact: Optional[str] = None
    travel_insurance_details: Optional[str] = None

class DataAccessRequest(BaseModel):
    """Request to access decrypted tourist data during emergency"""
    tourist_id: str
    authority_id: str
    authority_name: str
    authority_department: str
    access_reason: AccessReason
    alert_id: Optional[str] = None
    requested_fields: Optional[List[str]] = None  # If None, return all fields

class DataAccessResponse(BaseModel):
    """Response containing decrypted tourist data"""
    tourist_id: str
    access_log_id: str
    
    # Decrypted sensitive data
    full_name: str
    nationality: str
    date_of_birth: Optional[datetime] = None
    passport_country: Optional[str] = None
    
    kyc_data: TouristKYCData
    emergency_contacts: List[EmergencyContact]
    
    detailed_itinerary: str
    accommodation_details: Optional[str] = None
    local_guide_contact: Optional[str] = None
    travel_insurance_details: Optional[str] = None
    
    # Access metadata
    accessed_at: datetime
    accessed_by: str
    access_reason: str

class RegistrationResponse(BaseModel):
    """Response after successful registration"""
    tourist_id: str
    registration_id: str
    kyc_hash: str
    itinerary_hash: str
    created_at: datetime
    status: str = "registered"