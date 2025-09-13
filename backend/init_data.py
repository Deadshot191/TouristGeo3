"""
Initialize sample data for Tourism Safety System
Run this script to populate the database with sample users and tourists
"""
import asyncio
import hashlib
from datetime import datetime, timedelta
from bson import ObjectId

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import connect_to_mongo, get_users_collection, get_tourists_collection
from models import User, Tourist, UserRole, TouristStatus, EmergencyContact
from auth import hash_password

async def create_sample_users():
    """Create sample users (officers)"""
    users_collection = await get_users_collection()
    
    # Check if users already exist
    existing_count = await users_collection.count_documents({})
    if existing_count > 0:
        print("Users already exist, skipping user creation")
        return
    
    sample_users = [
        User(
            email="inspector.kumar@tourism.gov.in",
            password_hash=hash_password("password123"),
            full_name="Inspector Raj Kumar",
            role=UserRole.POLICE,
            department="Tourism Police",
            badge_number="TP-001"
        ),
        User(
            email="admin.singh@tourism.gov.in", 
            password_hash=hash_password("admin123"),
            full_name="Admin Priya Singh",
            role=UserRole.TOURISM_ADMIN,
            department="Tourism Department",
            badge_number="TD-001"
        ),
        User(
            email="officer.sharma@tourism.gov.in",
            password_hash=hash_password("officer123"),
            full_name="Officer Amit Sharma", 
            role=UserRole.POLICE,
            department="Tourism Police",
            badge_number="TP-002"
        )
    ]
    
    for user in sample_users:
        result = await users_collection.insert_one(user.dict(by_alias=True))
        print(f"Created user: {user.email} with ID: {result.inserted_id}")

async def create_sample_tourists():
    """Create sample tourists"""
    tourists_collection = await get_tourists_collection()
    
    # Check if tourists already exist
    existing_count = await tourists_collection.count_documents({})
    if existing_count > 0:
        print("Tourists already exist, skipping tourist creation")
        return
    
    sample_tourists = [
        Tourist(
            digital_id="DIG-12AB34CD",
            full_name="John Smith",
            nationality="USA",
            photo_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face",
            kyc_type="passport",
            kyc_id_hash=hashlib.sha256("P123456789".encode()).hexdigest(),
            visit_start_date=datetime(2025, 1, 8),
            visit_end_date=datetime(2025, 1, 15),
            itinerary="Kolkata -> Darjeeling -> Gangtok",
            emergency_contacts=[
                EmergencyContact(name="Sarah Smith", phone="+1-555-0123", relationship="spouse"),
                EmergencyContact(name="Embassy USA", phone="+91-33-2419-8000", relationship="embassy")
            ],
            status=TouristStatus.SAFE,
            safety_score=95
        ),
        Tourist(
            digital_id="DIG-56EF78GH",
            full_name="Maria Garcia",
            nationality="Spain", 
            photo_url="https://images.unsplash.com/photo-1494790108755-2616b612b5e5?w=150&h=150&fit=crop&crop=face",
            kyc_type="passport",
            kyc_id_hash=hashlib.sha256("ES987654321".encode()).hexdigest(),
            visit_start_date=datetime(2025, 1, 7),
            visit_end_date=datetime(2025, 1, 20),
            itinerary="Delhi -> Darjeeling -> Sikkim",
            emergency_contacts=[
                EmergencyContact(name="Pedro Garcia", phone="+34-600-123456", relationship="brother"),
                EmergencyContact(name="Embassy Spain", phone="+91-11-4127-9000", relationship="embassy")
            ],
            status=TouristStatus.ANOMALY,
            safety_score=72
        ),
        Tourist(
            digital_id="DIG-90IJ12KL",
            full_name="Hiroshi Tanaka",
            nationality="Japan",
            photo_url="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face",
            kyc_type="passport", 
            kyc_id_hash=hashlib.sha256("JP456789123".encode()).hexdigest(),
            visit_start_date=datetime(2025, 1, 9),
            visit_end_date=datetime(2025, 1, 18),
            itinerary="Mumbai -> Darjeeling -> Kalimpong",
            emergency_contacts=[
                EmergencyContact(name="Yuki Tanaka", phone="+81-90-1234-5678", relationship="sister"),
                EmergencyContact(name="Embassy Japan", phone="+91-11-2687-6581", relationship="embassy")
            ],
            status=TouristStatus.PANIC,
            safety_score=25
        ),
        Tourist(
            digital_id="DIG-34MN56OP",
            full_name="Emma Wilson", 
            nationality="UK",
            photo_url="https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face",
            kyc_type="passport",
            kyc_id_hash=hashlib.sha256("UK789123456".encode()).hexdigest(),
            visit_start_date=datetime(2025, 1, 6),
            visit_end_date=datetime(2025, 1, 16),
            itinerary="Kolkata -> Darjeeling -> Kalimpong -> Gangtok",
            emergency_contacts=[
                EmergencyContact(name="James Wilson", phone="+44-20-7946-0958", relationship="father"),
                EmergencyContact(name="British High Commission", phone="+91-11-2419-2100", relationship="embassy")
            ],
            status=TouristStatus.SAFE,
            safety_score=88
        ),
        Tourist(
            digital_id="DIG-78QR90ST",
            full_name="David Brown",
            nationality="Canada",
            photo_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=face",
            kyc_type="passport",
            kyc_id_hash=hashlib.sha256("CA123789456".encode()).hexdigest(), 
            visit_start_date=datetime(2025, 1, 5),
            visit_end_date=datetime(2025, 1, 19),
            itinerary="Delhi -> Darjeeling -> Kalimpong",
            emergency_contacts=[
                EmergencyContact(name="Linda Brown", phone="+1-416-555-0199", relationship="wife"),
                EmergencyContact(name="Canadian High Commission", phone="+91-11-4178-2000", relationship="embassy")
            ],
            status=TouristStatus.SAFE,
            safety_score=92
        )
    ]
    
    for tourist in sample_tourists:
        result = await tourists_collection.insert_one(tourist.dict(by_alias=True))
        print(f"Created tourist: {tourist.full_name} ({tourist.digital_id}) with ID: {result.inserted_id}")

async def main():
    """Main function to initialize sample data"""
    print("Initializing Tourism Safety System with sample data...")
    
    # Connect to database
    await connect_to_mongo()
    
    # Create sample data
    await create_sample_users()
    await create_sample_tourists()
    
    print("Sample data initialization completed!")
    print("\nLogin credentials:")
    print("Inspector: inspector.kumar@tourism.gov.in / password123")
    print("Admin: admin.singh@tourism.gov.in / admin123") 
    print("Officer: officer.sharma@tourism.gov.in / officer123")

if __name__ == "__main__":
    asyncio.run(main())