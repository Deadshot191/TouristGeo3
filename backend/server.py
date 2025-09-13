from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Query
from fastapi.security import HTTPBearer
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional

# Import our modules
try:
    from .database import connect_to_mongo, close_mongo_connection
    from .auth import create_access_token, authenticate_user, get_current_user, get_current_admin_or_police_user
    from .models import *
    from .services.tourist_service import TouristService
    from .services.location_service import LocationService
    from .services.alert_service import AlertService
    from .services.geofence_service import GeofenceService
    from .services.analytics_service import AnalyticsService
    from .websocket_manager import manager, handle_location_websocket, handle_dashboard_websocket
except ImportError:
    from database import connect_to_mongo, close_mongo_connection
    from auth import create_access_token, authenticate_user, get_current_user, get_current_admin_or_police_user
    from models import *
    from services.tourist_service import TouristService
    from services.location_service import LocationService
    from services.alert_service import AlertService
    from services.geofence_service import GeofenceService
    from services.analytics_service import AnalyticsService
    from websocket_manager import manager, handle_location_websocket, handle_dashboard_websocket

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create the main app
app = FastAPI(
    title="Tourism Safety API",
    description="Real-time tourist monitoring and safety system",
    version="1.0.0"
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@api_router.post("/auth/login")
async def login(user_credentials: UserLogin):
    """Authenticate user and return JWT token"""
    user = await authenticate_user(user_credentials.email, user_credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            department=user.department,
            badge_number=user.badge_number,
            last_login=user.last_login
        )
    }

@api_router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information"""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        department=current_user.department,
        badge_number=current_user.badge_number,
        last_login=current_user.last_login
    )

# ============================================================================
# TOURIST MANAGEMENT ROUTES
# ============================================================================

@api_router.get("/tourists", response_model=List[TouristResponse])
async def get_tourists(
    status: Optional[TouristStatus] = None,
    nationality: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user)
):
    """Get tourists with optional filters"""
    filters = TouristFilters(
        status=status,
        nationality=nationality,
        search=search,
        skip=skip,
        limit=limit
    )
    
    return await TouristService.get_tourists(filters)

@api_router.get("/tourists/{tourist_id}", response_model=TouristResponse)
async def get_tourist(tourist_id: str, current_user: User = Depends(get_current_user)):
    """Get specific tourist details"""
    tourist = await TouristService.get_tourist_by_id(tourist_id)
    
    if not tourist:
        raise HTTPException(status_code=404, detail="Tourist not found")
    
    # Get latest location
    location_history = await TouristService.get_tourist_location_history(tourist_id, limit=1)
    location_data = None
    if location_history:
        latest = location_history[0]
        location_data = LocationData(
            coordinates=latest["coordinates"],
            address=latest.get("address"),
            timestamp=latest["timestamp"]
        )
    
    return TouristResponse(
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

@api_router.put("/tourists/{tourist_id}/status")
async def update_tourist_status(
    tourist_id: str, 
    status_update: TouristStatusUpdate,
    current_user: User = Depends(get_current_admin_or_police_user)
):
    """Update tourist status"""
    success = await TouristService.update_tourist_status(
        tourist_id, 
        status_update.status, 
        status_update.reason
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Tourist not found or update failed")
    
    # Broadcast status change
    tourist = await TouristService.get_tourist_by_id(tourist_id)
    if tourist:
        await manager.broadcast_status_change(
            tourist_id, 
            tourist.full_name, 
            "unknown",  # We don't track old status here
            status_update.status.value,
            status_update.reason
        )
    
    return {"message": "Status updated successfully"}

@api_router.get("/tourists/{tourist_id}/location-history")
async def get_tourist_location_history(
    tourist_id: str,
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user)
):
    """Get tourist location history"""
    history = await TouristService.get_tourist_location_history(tourist_id, limit)
    return history

# ============================================================================
# LOCATION TRACKING ROUTES
# ============================================================================

@api_router.post("/location/update")
async def update_location(location_update: LocationUpdate):
    """Update tourist location"""
    success = await LocationService.update_location(location_update)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update location")
    
    return {"message": "Location updated successfully"}

@api_router.get("/location/live")
async def get_live_locations(current_user: User = Depends(get_current_user)):
    """Get current locations of all tourists"""
    locations = await LocationService.get_current_locations()
    return locations

# ============================================================================
# ALERTS MANAGEMENT ROUTES
# ============================================================================

@api_router.get("/alerts", response_model=List[AlertResponse])
async def get_alerts(
    alert_type: Optional[AlertType] = None,
    status: Optional[AlertStatus] = None,
    severity: Optional[AlertSeverity] = None,
    search: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user)
):
    """Get alerts with optional filters"""
    filters = AlertFilters(
        alert_type=alert_type,
        status=status,
        severity=severity,
        search=search,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )
    
    return await AlertService.get_alerts(filters)

@api_router.post("/alerts/panic")
async def create_panic_alert(
    tourist_id: str,
    longitude: float,
    latitude: float,
    address: Optional[str] = None
):
    """Create panic button alert (highest priority)"""
    alert = await AlertService.create_panic_alert(tourist_id, longitude, latitude, address)
    
    # Broadcast alert immediately
    tourist = await TouristService.get_tourist_by_id(tourist_id)
    alert_data = {
        "alert_id": alert.alert_id,
        "tourist_id": tourist_id,
        "tourist_name": tourist.full_name if tourist else "Unknown",
        "alert_type": alert.alert_type.value,
        "severity": alert.severity.value,
        "location": {
            "longitude": longitude,
            "latitude": latitude,
            "address": address
        },
        "timestamp": alert.created_at.isoformat()
    }
    
    await manager.broadcast_alert(alert_data)
    
    return {"message": "Panic alert created", "alert_id": alert.alert_id}

@api_router.put("/alerts/{alert_id}/status")
async def update_alert_status(
    alert_id: str,
    status_update: AlertStatusUpdate,
    current_user: User = Depends(get_current_admin_or_police_user)
):
    """Update alert status"""
    success = await AlertService.update_alert_status(
        alert_id,
        status_update.status,
        status_update.resolved_by,
        status_update.resolution_notes
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found or update failed")
    
    # Broadcast alert resolution if resolved
    if status_update.status == AlertStatus.RESOLVED:
        alert = await AlertService.get_alert_by_id(alert_id)
        if alert:
            await manager.broadcast_alert_resolution({
                "alert_id": alert.alert_id,
                "resolved_by": current_user.full_name,
                "resolved_at": datetime.utcnow().isoformat()
            })
    
    return {"message": "Alert status updated successfully"}

@api_router.post("/alerts/{alert_id}/actions")
async def add_response_action(
    alert_id: str,
    action: str,
    current_user: User = Depends(get_current_admin_or_police_user)
):
    """Add response action to alert"""
    success = await AlertService.add_response_action(alert_id, action, current_user.full_name)
    
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"message": "Response action added successfully"}

# ============================================================================
# GEO-FENCING ROUTES
# ============================================================================

@api_router.get("/geofences", response_model=List[GeofenceResponse])
async def get_geofences(
    active_only: bool = True,
    current_user: User = Depends(get_current_user)
):
    """Get all geo-fences"""
    return await GeofenceService.get_all_geofences(active_only)

@api_router.post("/geofences", response_model=GeofenceResponse)
async def create_geofence(
    geofence_data: GeofenceCreate,
    current_user: User = Depends(get_current_admin_or_police_user)
):
    """Create new geo-fence"""
    geofence = await GeofenceService.create_geofence(geofence_data)
    
    return GeofenceResponse(
        id=str(geofence.id),
        name=geofence.name,
        type=geofence.type,
        risk_level=geofence.risk_level,
        coordinates=geofence.coordinates,
        description=geofence.description,
        active=geofence.active
    )

@api_router.get("/geofences/check")
async def check_geofences(
    longitude: float,
    latitude: float,
    current_user: User = Depends(get_current_user)
):
    """Check if coordinates are in any geo-fences"""
    intersecting_fences = await GeofenceService.check_point_in_geofences(longitude, latitude)
    return intersecting_fences

# ============================================================================
# ANALYTICS & DASHBOARD ROUTES
# ============================================================================

@api_router.get("/analytics/dashboard", response_model=DashboardKPIs)
async def get_dashboard_kpis(current_user: User = Depends(get_current_user)):
    """Get dashboard KPIs"""
    return await AnalyticsService.get_dashboard_kpis()

@api_router.get("/analytics/safety-score/{tourist_id}", response_model=SafetyScoreResponse)
async def get_safety_score(tourist_id: str, current_user: User = Depends(get_current_user)):
    """Get calculated safety score for tourist"""
    return await AnalyticsService.calculate_safety_score(tourist_id)

@api_router.get("/analytics/location")
async def get_location_analytics(
    hours: int = Query(24, ge=1, le=168),
    current_user: User = Depends(get_current_user)
):
    """Get location-based analytics"""
    return await AnalyticsService.get_location_analytics(hours)

@api_router.get("/analytics/alerts")
async def get_alert_analytics(
    days: int = Query(7, ge=1, le=30),
    current_user: User = Depends(get_current_user)
):
    """Get alert-based analytics"""
    return await AnalyticsService.get_alert_analytics(days)

# ============================================================================
# WEBSOCKET ROUTES
# ============================================================================

@app.websocket("/api/ws/location/{tourist_id}")
async def websocket_location_endpoint(websocket: WebSocket, tourist_id: str):
    """WebSocket endpoint for location tracking"""
    await handle_location_websocket(websocket, tourist_id)

@app.websocket("/api/ws/dashboard")
async def websocket_dashboard_endpoint(websocket: WebSocket):
    """WebSocket endpoint for dashboard real-time updates"""
    await handle_dashboard_websocket(websocket)

@api_router.get("/ws/stats")
async def get_websocket_stats(current_user: User = Depends(get_current_admin_or_police_user)):
    """Get WebSocket connection statistics"""
    return manager.get_connection_stats()

# ============================================================================
# HEALTH CHECK ROUTES
# ============================================================================

@api_router.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Tourism Safety API",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat()
    }

@api_router.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "websockets": manager.get_connection_stats(),
        "timestamp": datetime.utcnow().isoformat()
    }

# Include the router in the main app
app.include_router(api_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# APP LIFECYCLE EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    logger.info("Starting Tourism Safety API...")
    
    # Connect to MongoDB
    await connect_to_mongo()
    
    # Create default geo-fences
    await GeofenceService.create_default_geofences()
    
    logger.info("Tourism Safety API started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Tourism Safety API...")
    await close_mongo_connection()
    logger.info("Tourism Safety API shut down successfully")
