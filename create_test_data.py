#!/usr/bin/env python3
"""
Create test data for the Tourism Safety System
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import uuid

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

from database import connect_to_mongo, get_tourists_collection, close_mongo_connection
from models import Tourist, TouristStatus, EmergencyContact

async def create_test_tourists():
    """Create test tourists for testing"""
    try:
        # Connect to database
        await connect_to_mongo()
        tourists_collection = await get_tourists_collection()
        
        # Check if tourists already exist
        existing_count = await tourists_collection.count_documents({})
        if existing_count > 0:
            print(f"✅ {existing_count} tourists already exist in database")
            return
        
        # Create test tourists
        test_tourists = [
            Tourist(
                digital_id=f"DT{str(uuid.uuid4())[:8].upper()}",
                full_name="Rajesh Sharma",
                nationality="Indian",
                kyc_type="passport",
                kyc_id_hash="hash_passport_123",
                visit_start_date=datetime.utcnow() - timedelta(days=2),
                visit_end_date=datetime.utcnow() + timedelta(days=5),
                itinerary="Darjeeling Tea Gardens, Tiger Hill, Batasia Loop",
                emergency_contacts=[
                    EmergencyContact(name="Priya Sharma", phone="+91-9876543210", relationship="wife")
                ],
                status=TouristStatus.SAFE,
                safety_score=95,
                created_at=datetime.utcnow(),
                last_location_update=datetime.utcnow() - timedelta(minutes=30)
            ),
            Tourist(
                digital_id=f"DT{str(uuid.uuid4())[:8].upper()}",
                full_name="Sarah Johnson",
                nationality="American",
                kyc_type="passport",
                kyc_id_hash="hash_passport_456",
                visit_start_date=datetime.utcnow() - timedelta(days=1),
                visit_end_date=datetime.utcnow() + timedelta(days=7),
                itinerary="Darjeeling Himalayan Railway, Peace Pagoda, Mall Road",
                emergency_contacts=[
                    EmergencyContact(name="John Johnson", phone="+1-555-123-4567", relationship="husband")
                ],
                status=TouristStatus.SAFE,
                safety_score=88,
                created_at=datetime.utcnow(),
                last_location_update=datetime.utcnow() - timedelta(minutes=15)
            ),
            Tourist(
                digital_id=f"DT{str(uuid.uuid4())[:8].upper()}",
                full_name="Hiroshi Tanaka",
                nationality="Japanese",
                kyc_type="passport",
                kyc_id_hash="hash_passport_789",
                visit_start_date=datetime.utcnow(),
                visit_end_date=datetime.utcnow() + timedelta(days=4),
                itinerary="Ghoom Monastery, Observatory Hill, Happy Valley Tea Estate",
                emergency_contacts=[
                    EmergencyContact(name="Yuki Tanaka", phone="+81-90-1234-5678", relationship="wife")
                ],
                status=TouristStatus.SAFE,
                safety_score=92,
                created_at=datetime.utcnow(),
                last_location_update=datetime.utcnow() - timedelta(minutes=5)
            )
        ]
        
        # Insert tourists
        for tourist in test_tourists:
            result = await tourists_collection.insert_one(tourist.dict(by_alias=True))
            print(f"✅ Created tourist: {tourist.full_name} (ID: {result.inserted_id})")
        
        print(f"✅ Created {len(test_tourists)} test tourists")
        
    except Exception as e:
        print(f"❌ Error creating test tourists: {e}")
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(create_test_tourists())