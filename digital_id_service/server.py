from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import os
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any

# Import our modules
from .database import connect_to_mongo, close_mongo_connection
from .models import *
from .services.secure_data_service import secure_data_service
from .services.blockchain_simulator import blockchain_simulator
from .services.encryption_service import encryption_service

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Lifespan manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Digital ID Service...")
    await connect_to_mongo()
    logger.info("Digital ID Service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Digital ID Service...")
    await close_mongo_connection()
    logger.info("Digital ID Service shut down")

# Create the main app
app = FastAPI(
    title="Digital ID & Blockchain Service",
    description="Secure encrypted tourist data management with blockchain audit trail",
    version="1.0.0",
    lifespan=lifespan
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Service Authentication
def verify_service_key(authorization: str = Header(None)):
    """Verify service-to-service authentication"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    # Extract bearer token
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid authorization scheme")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization format"
        )
    
    # Verify service API key
    expected_key = os.environ.get("SERVICE_API_KEY")
    if not expected_key or token != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid service API key"
        )
    
    return True

# Health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Digital ID & Blockchain Service",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# Tourist Data Registration
@api_router.post("/register", response_model=RegistrationResponse)
async def register_tourist_data(
    request: TouristRegistrationRequest,
    authorized: bool = Depends(verify_service_key)
):
    """
    Register sensitive tourist data with encryption and blockchain logging
    This endpoint should only be called from the main backend service
    """
    try:
        logger.info(f"Registering tourist data for ID: {request.tourist_id}")
        
        response = await secure_data_service.register_tourist_data(request)
        
        logger.info(f"Successfully registered tourist data for ID: {request.tourist_id}")
        return response
        
    except ValueError as e:
        logger.warning(f"Registration validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error during tourist registration: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during registration")

# Emergency Data Access
@api_router.post("/request-access/{tourist_id}", response_model=DataAccessResponse)
async def request_emergency_access(
    tourist_id: str,
    request: DataAccessRequest,
    authorized: bool = Depends(verify_service_key)
):
    """
    Request access to decrypted tourist data during emergency
    Creates immutable audit log entry (blockchain simulation)
    """
    try:
        logger.info(f"Emergency access request for tourist: {tourist_id} by {request.authority_name}")
        
        # Ensure tourist_id matches
        if request.tourist_id != tourist_id:
            raise HTTPException(status_code=400, detail="Tourist ID mismatch")
        
        response = await secure_data_service.request_emergency_access(request)
        
        logger.info(f"Emergency access granted for tourist: {tourist_id}")
        return response
        
    except ValueError as e:
        logger.warning(f"Emergency access validation error: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error during emergency access request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during access request")

# Data Integrity Verification
@api_router.get("/verify-integrity/{tourist_id}")
async def verify_data_integrity(
    tourist_id: str,
    authorized: bool = Depends(verify_service_key)
):
    """
    Verify data integrity using stored cryptographic hashes
    Simulates blockchain verification functionality
    """
    try:
        logger.info(f"Verifying data integrity for tourist: {tourist_id}")
        
        result = await secure_data_service.verify_data_integrity(tourist_id)
        
        return result
        
    except Exception as e:
        logger.error(f"Error during data integrity verification: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during verification")

# Audit Log Access
@api_router.get("/audit-logs")
async def get_audit_logs(
    tourist_id: Optional[str] = None,
    limit: int = 50,
    authorized: bool = Depends(verify_service_key)
):
    """
    Get access audit logs for compliance and monitoring
    Returns immutable blockchain simulation records
    """
    try:
        logger.info(f"Retrieving audit logs - Tourist ID: {tourist_id}, Limit: {limit}")
        
        logs = await secure_data_service.get_access_logs(tourist_id, limit)
        
        return {
            "status": "success",
            "count": len(logs),
            "logs": logs
        }
        
    except Exception as e:
        logger.error(f"Error retrieving audit logs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error retrieving logs")

# Blockchain Chain Verification
@api_router.get("/verify-blockchain")
async def verify_blockchain_integrity(
    limit: int = 100,
    authorized: bool = Depends(verify_service_key)
):
    """
    Verify the integrity of the blockchain simulation chain
    Ensures all cryptographic links are valid
    """
    try:
        logger.info(f"Verifying blockchain integrity - Limit: {limit}")
        
        result = await blockchain_simulator.verify_chain_integrity(limit)
        
        return result
        
    except Exception as e:
        logger.error(f"Error during blockchain verification: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during blockchain verification")

# System Status
@app.get("/status")
async def system_status():
    """
    Public system status endpoint (no authentication required)
    """
    try:
        from .database import db
        
        # Test database connection
        if db.database:
            await db.database.command('ping')
            db_status = "connected"
        else:
            db_status = "disconnected"
        
        return {
            "service": "Digital ID & Blockchain Service",
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "database": db_status,
            "version": "1.0.0"
        }
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return {
            "service": "Digital ID & Blockchain Service",
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "version": "1.0.0"
        }

# Include the API router
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("SERVICE_PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)