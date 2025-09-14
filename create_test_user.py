#!/usr/bin/env python3
"""
Create test user for the Tourism Safety System
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

from database import connect_to_mongo, get_users_collection, close_mongo_connection
from auth import hash_password
from models import User, UserRole
from datetime import datetime

async def create_test_user():
    """Create a test user for authentication testing"""
    try:
        # Connect to database
        await connect_to_mongo()
        users_collection = await get_users_collection()
        
        # Check if user already exists
        existing_user = await users_collection.find_one({"email": "inspector.kumar@tourism.gov.in"})
        if existing_user:
            print("✅ Test user already exists")
            return
        
        # Create test user
        test_user = User(
            email="inspector.kumar@tourism.gov.in",
            password_hash=hash_password("password123"),
            full_name="Inspector Kumar",
            role=UserRole.POLICE,
            department="Tourism Police",
            badge_number="TP001",
            created_at=datetime.utcnow()
        )
        
        # Insert user
        result = await users_collection.insert_one(test_user.dict(by_alias=True))
        print(f"✅ Created test user with ID: {result.inserted_id}")
        
        # Create admin user too
        admin_user = User(
            email="admin@tourism.gov.in",
            password_hash=hash_password("admin123"),
            full_name="Tourism Admin",
            role=UserRole.TOURISM_ADMIN,
            department="Tourism Department",
            badge_number="TA001",
            created_at=datetime.utcnow()
        )
        
        result = await users_collection.insert_one(admin_user.dict(by_alias=True))
        print(f"✅ Created admin user with ID: {result.inserted_id}")
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(create_test_user())