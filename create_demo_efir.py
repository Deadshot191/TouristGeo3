#!/usr/bin/env python3
"""
Create Demo E-FIR Documents
Populates the database with sample E-FIR documents for demonstration
"""

import asyncio
import os
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# Set environment variables
os.environ['MONGO_URL'] = 'mongodb://localhost:27017'
os.environ['DB_NAME'] = 'tourist_safety_db'

async def create_demo_efir_documents():
    """Create demo E-FIR documents"""
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    efir_collection = db.efir_documents
    
    print("🗂️ Creating demo E-FIR documents...")
    
    # Clear existing E-FIR documents
    await efir_collection.delete_many({})
    print("🧹 Cleared existing E-FIR documents")
    
    # Demo E-FIR documents
    demo_efirs = [
        {
            "_id": ObjectId(),
            "fir_number": "FIR-2025-TI001",
            "title": "Tourist Safety Incident - Unauthorized Guide Activity",
            "fir_type": "tourist_incident",
            "priority": "high",
            "status": "under_investigation",
            "incident_date": datetime.utcnow() - timedelta(days=2, hours=5),
            "incident_location": {
                "coordinates": {
                    "type": "Point",
                    "coordinates": [88.2700, 27.0400]  # Darjeeling coordinates
                },
                "address": "Mall Road, Darjeeling, West Bengal",
                "timestamp": datetime.utcnow() - timedelta(days=2, hours=5)
            },
            "incident_description": "Tourist reported being approached by unauthorized guide demanding excessive fees and threatening behavior when refused. Tourist felt unsafe and requested immediate assistance.",
            "related_tourist_id": "DIG-PANIC01",
            "related_alert_id": "PN-PANIC-001",
            "complainant_name": "Sarah Johnson",
            "complainant_contact": "+1-555-0123",
            "accused_details": "Male, approximately 35 years old, wearing blue jacket, claimed to be official guide but no valid ID shown",
            "witness_details": "Local shopkeeper Mr. Ram Sharma witnessed the incident, contact: +91-9876543210",
            "case_details": "Unauthorized guide activity violating tourism safety regulations. Tourist safety compromised due to aggressive behavior and false representation as official guide. Investigation revealed pattern of similar incidents in the area.",
            "evidence_details": "Tourist provided photos of the accused, witness statement recorded, location coordinates captured, CCTV footage requested from nearby shops",
            "action_taken": "Immediate patrol dispatched to area, tourist escorted to safety, investigation initiated. Suspect identified through CCTV analysis. Warning issued to unauthorized operators.",
            "created_by": "inspector.kumar@tourism.gov.in",
            "created_at": datetime.utcnow() - timedelta(days=2, hours=4),
            "versions": [],
            "current_version": 1,
            "signatures": [
                {
                    "officer_id": "inspector.kumar@tourism.gov.in",
                    "officer_name": "Inspector Kumar",
                    "officer_badge": "TPI-001",
                    "department": "Tourism Police",
                    "signature_hash": "A1B2C3D4E5F6789012345ABCD...",
                    "signed_at": datetime.utcnow() - timedelta(days=1, hours=2),
                    "verification_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A...\n-----END PUBLIC KEY-----"
                }
            ],
            "qr_code_data": "FIR:FIR-2025-TI001|Hash:abc123def456|Version:1",
            "document_hash": "sha256:abc123def456789012345678901234567890abcdef",
            "pdf_file_path": None
        },
        {
            "_id": ObjectId(),
            "fir_number": "FIR-2025-SV002",
            "title": "Safety Violation - Overcrowded Tourist Vehicle",
            "fir_type": "safety_violation",
            "priority": "medium",
            "status": "submitted",
            "incident_date": datetime.utcnow() - timedelta(days=1, hours=8),
            "incident_location": {
                "coordinates": {
                    "type": "Point",
                    "coordinates": [78.0421, 27.1704]  # Agra coordinates
                },
                "address": "Taj Mahal West Gate, Agra, Uttar Pradesh",
                "timestamp": datetime.utcnow() - timedelta(days=1, hours=8)
            },
            "incident_description": "Tourist vehicle found operating with 15 passengers in a 10-seater capacity van. Safety violation reported by tourist safety patrol during routine inspection.",
            "related_tourist_id": None,
            "related_alert_id": None,
            "complainant_name": "Tourism Safety Patrol Unit",
            "complainant_contact": "+91-98765-43210",
            "accused_details": "Vehicle driver: Mohammad Khan, License No: UP-14-2019-123456, Vehicle Registration: UP14-AB-1234",
            "witness_details": "Patrol officers witnessed the violation, 5 tourists confirmed overcrowding",
            "case_details": "Vehicle capacity violation under tourism safety regulations. Driver was operating beyond permitted passenger capacity, compromising tourist safety and comfort.",
            "evidence_details": "Vehicle inspection report, photographs of overcrowded vehicle, driver license verification, tourist statements",
            "action_taken": "Vehicle stopped immediately, excess passengers transferred to alternative transport, penalty imposed, driver counseled on safety regulations",
            "created_by": "officer.sharma@tourism.gov.in",
            "created_at": datetime.utcnow() - timedelta(days=1, hours=7),
            "versions": [],
            "current_version": 1,
            "signatures": [],
            "qr_code_data": None,
            "document_hash": "sha256:def456789012345678901234567890abcdef123",
            "pdf_file_path": None
        },
        {
            "_id": ObjectId(),
            "fir_number": "FIR-2025-ER003",
            "title": "Emergency Response - Medical Assistance Required",
            "fir_type": "medical_emergency",
            "priority": "urgent",
            "status": "closed",
            "incident_date": datetime.utcnow() - timedelta(days=5, hours=12),
            "incident_location": {
                "coordinates": {
                    "type": "Point",
                    "coordinates": [73.0479, 22.3039]  # Udaipur coordinates
                },
                "address": "City Palace, Udaipur, Rajasthan",
                "timestamp": datetime.utcnow() - timedelta(days=5, hours=12)
            },
            "incident_description": "Elderly tourist collapsed due to dehydration and heat exhaustion while visiting City Palace. Immediate medical assistance required.",
            "related_tourist_id": "DIG-SAFE04",
            "related_alert_id": None,
            "complainant_name": "Tour Guide Association",
            "complainant_contact": "+91-87654-32109",
            "accused_details": "No accused party - medical emergency",
            "witness_details": "Tour guide Mr. Rajesh Sharma, fellow tourists Mr. and Mrs. Patel provided assistance",
            "case_details": "Medical emergency involving elderly tourist. Quick response by local guides and tourist police ensured timely medical care. Tourist recovered fully after treatment.",
            "evidence_details": "Medical report from City Hospital, witness statements, tourist insurance documentation",
            "action_taken": "Emergency medical team dispatched, tourist transported to City Hospital, family notified, insurance claim processed, full recovery achieved",
            "created_by": "admin.singh@tourism.gov.in",
            "created_at": datetime.utcnow() - timedelta(days=5, hours=11),
            "versions": [],
            "current_version": 1,
            "signatures": [
                {
                    "officer_id": "admin.singh@tourism.gov.in",
                    "officer_name": "Admin Singh",
                    "officer_badge": "TA-001",
                    "department": "Tourism Administration",
                    "signature_hash": "DEF456GHI789012345BCDEF...",
                    "signed_at": datetime.utcnow() - timedelta(days=4),
                    "verification_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8B...\n-----END PUBLIC KEY-----"
                }
            ],
            "qr_code_data": "FIR:FIR-2025-ER003|Hash:def456ghi789|Version:1",
            "document_hash": "sha256:def456ghi789012345678901234567890abcdef123",
            "pdf_file_path": None
        },
        {
            "_id": ObjectId(),
            "fir_number": "FIR-2025-PD004",
            "title": "Property Damage - Vandalism at Heritage Site",
            "fir_type": "property_damage",
            "priority": "high",
            "status": "under_investigation",
            "incident_date": datetime.utcnow() - timedelta(hours=18),
            "incident_location": {
                "coordinates": {
                    "type": "Point",
                    "coordinates": [77.2500, 28.6139]  # Red Fort, Delhi coordinates
                },
                "address": "Red Fort, Chandni Chowk, Delhi",
                "timestamp": datetime.utcnow() - timedelta(hours=18)
            },
            "incident_description": "Graffiti found on heritage wall section. Suspected vandalism by tourists ignoring preservation guidelines.",
            "related_tourist_id": None,
            "related_alert_id": None,
            "complainant_name": "Heritage Site Security",
            "complainant_contact": "+91-76543-21098",
            "accused_details": "Unknown individuals, investigation ongoing based on CCTV footage",
            "witness_details": "Security guard on duty, nearby tourists who reported the incident",
            "case_details": "Vandalism incident at protected heritage site. Property damage assessment ongoing, restoration costs being calculated.",
            "evidence_details": "Photographs of damage, CCTV footage being analyzed, security logs reviewed",
            "action_taken": "Site secured, damage documented, CCTV analysis initiated, increased security patrol deployed",
            "created_by": "inspector.kumar@tourism.gov.in",
            "created_at": datetime.utcnow() - timedelta(hours=17),
            "versions": [],
            "current_version": 1,
            "signatures": [],
            "qr_code_data": None,
            "document_hash": "sha256:ghi789012345678901234567890abcdef123456",
            "pdf_file_path": None
        },
        {
            "_id": ObjectId(),
            "fir_number": "FIR-2025-MP005",
            "title": "Missing Person - Tourist Lost in Wilderness Area",
            "fir_type": "missing_person",
            "priority": "urgent",
            "status": "closed",
            "incident_date": datetime.utcnow() - timedelta(days=7, hours=6),
            "incident_location": {
                "coordinates": {
                    "type": "Point",
                    "coordinates": [77.1025, 11.0168]  # Ooty coordinates
                },
                "address": "Nilgiri Hills, Ooty, Tamil Nadu",
                "timestamp": datetime.utcnow() - timedelta(days=7, hours=6)
            },
            "incident_description": "Tourist reported missing during trekking expedition. Last seen at viewpoint, failed to return to base camp by evening.",
            "related_tourist_id": "DIG-DEVIATE03",
            "related_alert_id": "PN-ROUTE-003",
            "complainant_name": "Adventure Tour Company",
            "complainant_contact": "+91-65432-10987",
            "accused_details": "No accused party - missing person case",
            "witness_details": "Fellow trekkers last saw the person at Tiger Hills viewpoint around 3 PM",
            "case_details": "Search and rescue operation for missing tourist. Coordinated effort between local police, forest department, and rescue teams.",
            "evidence_details": "Last known location GPS coordinates, witness statements, search area maps, rescue operation logs",
            "action_taken": "Immediate search operation launched, rescue teams deployed, tourist found safe after 8 hours, reunited with group",
            "created_by": "officer.sharma@tourism.gov.in",
            "created_at": datetime.utcnow() - timedelta(days=7, hours=5),
            "versions": [
                {
                    "version_number": 1,
                    "modified_by": "officer.sharma@tourism.gov.in",
                    "modified_at": datetime.utcnow() - timedelta(days=6),
                    "changes_summary": "Updated with search operation results and successful rescue",
                    "document_hash": "sha256:jkl012345678901234567890abcdef123456789"
                }
            ],
            "current_version": 2,
            "signatures": [
                {
                    "officer_id": "officer.sharma@tourism.gov.in",
                    "officer_name": "Officer Sharma",
                    "officer_badge": "TFO-003",
                    "department": "Tourism Field Operations",
                    "signature_hash": "JKL012MNO345678901CDEFGH...",
                    "signed_at": datetime.utcnow() - timedelta(days=6, hours=2),
                    "verification_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8C...\n-----END PUBLIC KEY-----"
                }
            ],
            "qr_code_data": "FIR:FIR-2025-MP005|Hash:jkl012mno345|Version:2",
            "document_hash": "sha256:jkl012mno345678901234567890abcdef123456789",
            "pdf_file_path": None
        }
    ]
    
    # Insert demo E-FIR documents
    result = await efir_collection.insert_many(demo_efirs)
    print(f"✅ Created {len(result.inserted_ids)} demo E-FIR documents:")
    
    for efir in demo_efirs:
        print(f"   📄 {efir['fir_number']}: {efir['title']} ({efir['status']})")
    
    # Close connection
    client.close()
    print("\n🎯 Demo E-FIR documents created successfully!")
    print("Users can now see E-FIR functionality with realistic data.")

if __name__ == "__main__":
    asyncio.run(create_demo_efir_documents())