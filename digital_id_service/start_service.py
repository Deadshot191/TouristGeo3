#!/usr/bin/env python3
"""
Startup script for Digital ID & Blockchain Service
"""
import os
import sys
from pathlib import Path

# Add the digital_id_service directory to Python path
service_dir = Path(__file__).parent
sys.path.insert(0, str(service_dir))

# Set environment variables if not already set
if not os.environ.get("MONGO_URL"):
    os.environ["MONGO_URL"] = "mongodb://localhost:27017/"

if not os.environ.get("DATABASE_NAME"):
    os.environ["DATABASE_NAME"] = "tourism_security"

if not os.environ.get("SERVICE_PORT"):
    os.environ["SERVICE_PORT"] = "8002"

# Generate encryption key if not provided
if not os.environ.get("ENCRYPTION_KEY_BASE64"):
    from cryptography.fernet import Fernet
    import base64
    key = Fernet.generate_key()
    os.environ["ENCRYPTION_KEY_BASE64"] = base64.urlsafe_b64encode(key).decode()
    print(f"Generated encryption key: {os.environ['ENCRYPTION_KEY_BASE64']}")
    print("IMPORTANT: Save this key securely and add it to your .env file!")

# Generate service API key if not provided
if not os.environ.get("SERVICE_API_KEY"):
    import secrets
    api_key = secrets.token_urlsafe(32)
    os.environ["SERVICE_API_KEY"] = api_key
    print(f"Generated service API key: {api_key}")
    print("IMPORTANT: Save this key securely and add it to your .env file!")

if __name__ == "__main__":
    import uvicorn
    
    print("Starting Digital ID & Blockchain Service...")
    print(f"Service will run on port: {os.environ.get('SERVICE_PORT', 8002)}")
    print(f"Database: {os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')}")
    
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=int(os.environ.get("SERVICE_PORT", 8002)),
        reload=True,
        log_level="info"
    )