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
class UserRole(str, Enum):
    POLICE = "police"
    TOURISM_ADMIN = "tourism_admin"

class TouristStatus(str, Enum):
    SAFE = "safe"
    ANOMALY = "anomaly" 
    PANIC = "panic"

class AlertType(str, Enum):
    PANIC_BUTTON = "panic_button"
    GEOFENCE_BREACH = "geofence_breach"
    ROUTE_DEVIATION = "route_deviation"
    PROLONGED_INACTIVITY = "prolonged_inactivity"

class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"

class GeofenceType(str, Enum):
    RESTRICTED = "restricted"
    HIGH_RISK = "high_risk"
    SAFE_ZONE = "safe_zone"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# Base Models
class EmergencyContact(BaseModel):
    name: str
    phone: str
    relationship: str = "family"

class Coordinates(BaseModel):
    longitude: float = Field(..., ge=-180, le=180)
    latitude: float = Field(..., ge=-90, le=90)

class LocationPoint(BaseModel):
    type: str = "Point"
    coordinates: List[float]  # [longitude, latitude]

class LocationData(BaseModel):
    coordinates: LocationPoint
    address: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    accuracy: Optional[float] = None
    speed: Optional[float] = None

# User Models
class User(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    email: str
    password_hash: str
    full_name: str
    role: UserRole
    department: str
    badge_number: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    role: UserRole
    department: str
    badge_number: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: UserRole
    department: str
    badge_number: Optional[str] = None
    last_login: Optional[datetime] = None

# Tourist Models
class Tourist(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    digital_id: str
    full_name: str
    nationality: str
    photo_url: Optional[str] = None
    kyc_type: Literal["passport", "aadhaar"] = "passport"
    kyc_id_hash: str
    visit_start_date: datetime
    visit_end_date: datetime
    itinerary: str
    emergency_contacts: List[EmergencyContact] = []
    status: TouristStatus = TouristStatus.SAFE
    safety_score: int = Field(default=95, ge=0, le=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_location_update: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class TouristCreate(BaseModel):
    full_name: str
    nationality: str
    photo_url: Optional[str] = None
    kyc_type: Literal["passport", "aadhaar"] = "passport"
    kyc_id: str
    visit_start_date: datetime
    visit_end_date: datetime
    itinerary: str
    emergency_contacts: List[EmergencyContact] = []

class TouristResponse(BaseModel):
    id: str
    digital_id: str
    full_name: str
    nationality: str
    photo_url: Optional[str] = None
    visit_start_date: datetime
    visit_end_date: datetime
    itinerary: str
    emergency_contacts: List[EmergencyContact]
    status: TouristStatus
    safety_score: int
    last_location_update: Optional[datetime] = None
    location: Optional[LocationData] = None

class TouristStatusUpdate(BaseModel):
    status: TouristStatus
    reason: Optional[str] = None

# Location Models
class LocationHistory(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    tourist_id: PyObjectId
    coordinates: LocationPoint
    address: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    accuracy: Optional[float] = None
    speed: Optional[float] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class LocationUpdate(BaseModel):
    tourist_id: str
    longitude: float = Field(..., ge=-180, le=180)
    latitude: float = Field(..., ge=-90, le=90)
    address: Optional[str] = None
    accuracy: Optional[float] = None
    speed: Optional[float] = None

# Geofence Models
class GeofencePolygon(BaseModel):
    type: str = "Polygon"
    coordinates: List[List[List[float]]]  # Array of linear rings

class Geofence(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    type: GeofenceType
    risk_level: RiskLevel
    coordinates: GeofencePolygon
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    active: bool = True

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class GeofenceCreate(BaseModel):
    name: str
    type: GeofenceType
    risk_level: RiskLevel
    coordinates: GeofencePolygon
    description: Optional[str] = None

class GeofenceResponse(BaseModel):
    id: str
    name: str
    type: GeofenceType
    risk_level: RiskLevel
    coordinates: GeofencePolygon
    description: Optional[str] = None
    active: bool

# Alert Models
class AlertLocation(BaseModel):
    coordinates: List[float]  # [longitude, latitude]
    address: Optional[str] = None

class Alert(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    alert_id: str  # PN-XXXX format
    tourist_id: PyObjectId
    alert_type: AlertType
    severity: AlertSeverity
    status: AlertStatus = AlertStatus.NEW
    location: AlertLocation
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[PyObjectId] = None
    response_actions: List[str] = []

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class AlertCreate(BaseModel):
    tourist_id: str
    alert_type: AlertType
    severity: AlertSeverity
    longitude: float
    latitude: float
    address: Optional[str] = None
    description: Optional[str] = None

class AlertResponse(BaseModel):
    id: str
    alert_id: str
    tourist_name: str
    tourist_id: str
    alert_type: AlertType
    severity: AlertSeverity
    status: AlertStatus
    location: AlertLocation
    description: Optional[str] = None
    timestamp: datetime
    resolved_at: Optional[datetime] = None
    response_actions: List[str] = []

class AlertStatusUpdate(BaseModel):
    status: AlertStatus
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None

class AlertActionLog(BaseModel):
    action: str
    performed_by: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Analytics Models
class DashboardKPIs(BaseModel):
    total_active_tourists: int
    active_alerts: int
    safe_status: int
    high_risk_tourists: int
    resolved_alerts_today: int
    avg_safety_score: float

class SafetyScoreResponse(BaseModel):
    tourist_id: str
    safety_score: int
    risk_factors: List[str]
    last_updated: datetime

# WebSocket Models
class LocationWebSocketData(BaseModel):
    tourist_id: str
    longitude: float
    latitude: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class WebSocketMessage(BaseModel):
    type: str  # location_update, alert, status_change
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Filter Models
class TouristFilters(BaseModel):
    status: Optional[TouristStatus] = None
    nationality: Optional[str] = None
    search: Optional[str] = None
    skip: int = 0
    limit: int = 100

class AlertFilters(BaseModel):
    alert_type: Optional[AlertType] = None
    status: Optional[AlertStatus] = None
    severity: Optional[AlertSeverity] = None
    search: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    skip: int = 0
    limit: int = 100