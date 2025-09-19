"""
Initialize demo data for Smart Tourist Safety System
Creates a compelling demonstration with hardcoded scenarios for non-technical audience
"""
import asyncio
import hashlib
from datetime import datetime, timedelta
from bson import ObjectId
import uuid

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import (
    connect_to_mongo, get_users_collection, get_tourists_collection, 
    get_alerts_collection, get_geofences_collection, get_location_history_collection
)
from models import (
    User, Tourist, UserRole, TouristStatus, EmergencyContact, Alert, AlertType, 
    AlertSeverity, AlertStatus, Geofence, GeofenceType, RiskLevel, GeofencePolygon,
    PlannedItinerary, LocationHistory, LocationPoint, AlertLocation
)
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


async def create_demo_geofences():
    """Create demo geo-fences including the Restricted Forest Area"""
    geofences_collection = await get_geofences_collection()
    
    # Clear existing geofences for demo
    await geofences_collection.delete_many({})
    
    demo_geofences = [
        # High-risk Restricted Forest Area for Emily Carter scenario
        Geofence(
            name="Restricted Forest Area",
            type=GeofenceType.RESTRICTED,
            risk_level=RiskLevel.CRITICAL,
            coordinates=GeofencePolygon(
                type="Polygon",
                coordinates=[[
                    [88.2900, 27.0200],  # Southwest corner
                    [88.3100, 27.0200],  # Southeast corner  
                    [88.3100, 27.0400],  # Northeast corner
                    [88.2900, 27.0400],  # Northwest corner
                    [88.2900, 27.0200]   # Close polygon
                ]]
            ),
            description="Protected forest area - entry strictly prohibited. High risk of wildlife encounters and getting lost."
        ),
        # Keep some existing ones for context
        Geofence(
            name="Military Restricted Zone",
            type=GeofenceType.RESTRICTED,
            risk_level=RiskLevel.CRITICAL,
            coordinates=GeofencePolygon(
                type="Polygon",
                coordinates=[[
                    [88.2750, 27.0450],
                    [88.2850, 27.0450],
                    [88.2850, 27.0480],
                    [88.2750, 27.0480],
                    [88.2750, 27.0450]
                ]]
            ),
            description="Military installation - strictly prohibited"
        ),
        Geofence(
            name="Tourist Safe Zone - Mall Road",
            type=GeofenceType.SAFE_ZONE,
            risk_level=RiskLevel.LOW,
            coordinates=GeofencePolygon(
                type="Polygon",
                coordinates=[[
                    [88.2600, 27.0380],
                    [88.2700, 27.0380],
                    [88.2700, 27.0420],
                    [88.2600, 27.0420],
                    [88.2600, 27.0380]
                ]]
            ),
            description="Main tourist area with police patrol"
        )
    ]
    
    for geofence in demo_geofences:
        result = await geofences_collection.insert_one(geofence.dict(by_alias=True))
        print(f"Created geo-fence: {geofence.name} with ID: {result.inserted_id}")

async def create_demo_tourists():
    """Create demo tourist scenarios for compelling presentation"""
    tourists_collection = await get_tourists_collection()
    
    # Clear existing tourists for demo
    await tourists_collection.delete_many({})
    
    # Planned itinerary for Priya Sharma (route deviation scenario)
    priya_planned_route = PlannedItinerary(
        type="LineString",
        coordinates=[
            [88.2620, 27.0400],  # Starting point - Darjeeling Mall Road
            [88.2650, 27.0410],  # Checkpoint 1
            [88.2680, 27.0415],  # Checkpoint 2  
            [88.2720, 27.0425],  # Checkpoint 3
            [88.2750, 27.0435]   # End point - planned destination
        ],
        waypoint_names=["Mall Road", "Observatory Hill", "Chowrasta", "Happy Valley Tea Estate", "Himalayan Mountaineering Institute"],
        description="Planned tourist route through safe Darjeeling attractions"
    )
    
    demo_tourists = [
        # Scenario 1: Raj Verma - Panic Alert (Critical)
        Tourist(
            digital_id="DIG-PANIC01",
            full_name="Raj Verma",
            nationality="India",
            photo_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face",
            kyc_type="passport",
            kyc_id_hash=hashlib.sha256("IN123456789".encode()).hexdigest(),
            visit_start_date=datetime(2025, 1, 10),
            visit_end_date=datetime(2025, 1, 17),
            itinerary="Delhi -> Darjeeling -> Kalimpong",
            emergency_contacts=[
                EmergencyContact(name="Sunita Verma", phone="+91-9876543210", relationship="wife"),
                EmergencyContact(name="Dr. Amit Verma", phone="+91-9876543211", relationship="brother"),
                EmergencyContact(name="Delhi Police", phone="+91-11-23454321", relationship="emergency")
            ],
            status=TouristStatus.PANIC,
            safety_score=15,
            last_location_update=datetime.utcnow() - timedelta(minutes=5)
        ),
        
        # Scenario 2: Emily Carter - Geo-fence Breach (High Severity)  
        Tourist(
            digital_id="DIG-BREACH02",
            full_name="Emily Carter",
            nationality="USA",
            photo_url="https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face",
            kyc_type="passport",
            kyc_id_hash=hashlib.sha256("US987654321".encode()).hexdigest(),
            visit_start_date=datetime(2025, 1, 8),
            visit_end_date=datetime(2025, 1, 16),
            itinerary="Kolkata -> Darjeeling -> Sikkim -> Gangtok",
            emergency_contacts=[
                EmergencyContact(name="Michael Carter", phone="+1-555-0198", relationship="husband"),
                EmergencyContact(name="Embassy USA", phone="+91-33-2419-8000", relationship="embassy"),
                EmergencyContact(name="Sarah Johnson", phone="+1-555-0199", relationship="sister")
            ],
            status=TouristStatus.ANOMALY,
            safety_score=35,
            last_location_update=datetime.utcnow() - timedelta(minutes=12)
        ),
        
        # Scenario 3: Priya Sharma - Route Deviation (Medium Severity)
        Tourist(
            digital_id="DIG-DEVIATE03", 
            full_name="Priya Sharma",
            nationality="India",
            photo_url="https://images.unsplash.com/photo-1494790108755-2616b612b5e5?w=150&h=150&fit=crop&crop=face",
            kyc_type="aadhaar",
            kyc_id_hash=hashlib.sha256("AADHAAR123456789".encode()).hexdigest(),
            visit_start_date=datetime(2025, 1, 9),
            visit_end_date=datetime(2025, 1, 14),
            itinerary="Mumbai -> Darjeeling -> Kalimpong",
            planned_route=priya_planned_route,
            emergency_contacts=[
                EmergencyContact(name="Rakesh Sharma", phone="+91-9123456789", relationship="father"),
                EmergencyContact(name="Meera Sharma", phone="+91-9123456790", relationship="mother"),
                EmergencyContact(name="Mumbai Police", phone="+91-22-22621855", relationship="emergency")
            ],
            status=TouristStatus.ANOMALY,
            safety_score=55,
            last_location_update=datetime.utcnow() - timedelta(minutes=8)
        ),
        
        # Scenario 4: John Doe - Safe & Secure (Normal) - Data Locked
        Tourist(
            digital_id="DIG-SAFE04",
            full_name="John Doe",
            nationality="UK",
            photo_url="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face",
            kyc_type="passport",
            kyc_id_hash=hashlib.sha256("UK456789123".encode()).hexdigest(),
            visit_start_date=datetime(2025, 1, 7),
            visit_end_date=datetime(2025, 1, 19),
            itinerary="London -> Kolkata -> Darjeeling -> Gangtok",
            emergency_contacts=[
                EmergencyContact(name="Jane Doe", phone="+44-20-7946-0958", relationship="wife"),
                EmergencyContact(name="British High Commission", phone="+91-11-2419-2100", relationship="embassy")
            ],
            status=TouristStatus.SAFE,
            safety_score=95,
            last_location_update=datetime.utcnow() - timedelta(minutes=15)
        ),
        
        # Scenario 5: Aisha Khan - Resolved Incident  
        Tourist(
            digital_id="DIG-RESOLVED05",
            full_name="Aisha Khan",
            nationality="Bangladesh",
            photo_url="https://images.unsplash.com/photo-1489424731084-a5d8b219a5bb?w=150&h=150&fit=crop&crop=face",
            kyc_type="passport",
            kyc_id_hash=hashlib.sha256("BD789456123".encode()).hexdigest(),
            visit_start_date=datetime(2025, 1, 6),
            visit_end_date=datetime(2025, 1, 13),
            itinerary="Dhaka -> Kolkata -> Darjeeling -> Kalimpong",
            emergency_contacts=[
                EmergencyContact(name="Omar Khan", phone="+880-1712345678", relationship="brother"),
                EmergencyContact(name="Bangladesh High Commission", phone="+91-11-2419-6389", relationship="embassy")
            ],
            status=TouristStatus.SAFE,
            safety_score=88,
            last_location_update=datetime.utcnow() - timedelta(minutes=20)
        )
    ]
    
    tourist_ids = {}
    for tourist in demo_tourists:
        result = await tourists_collection.insert_one(tourist.dict(by_alias=True))
        tourist_ids[tourist.full_name] = result.inserted_id
        print(f"Created tourist: {tourist.full_name} ({tourist.digital_id}) with ID: {result.inserted_id}")
    
    return tourist_ids

async def create_demo_alerts(tourist_ids):
    """Create demo alerts for specific tourist scenarios"""
    alerts_collection = await get_alerts_collection()
    
    # Clear existing alerts for demo
    await alerts_collection.delete_many({})
    
    demo_alerts = [
        # Scenario 1: Raj Verma - Active Panic Alert (Critical)
        Alert(
            alert_id=f"PN-{str(uuid.uuid4())[:4].upper()}",
            tourist_id=tourist_ids["Raj Verma"],
            alert_type=AlertType.PANIC_BUTTON,
            severity=AlertSeverity.CRITICAL,
            status=AlertStatus.NEW,
            location=AlertLocation(
                coordinates=[88.2640, 27.0390],  # Near Mall Road
                address="Mall Road, Darjeeling, West Bengal"
            ),
            description="Tourist activated panic button - immediate assistance required",
            created_at=datetime.utcnow() - timedelta(minutes=5),
            response_actions=["Emergency services notified", "Nearest police patrol dispatched"]
        ),
        
        # Scenario 2: Emily Carter - Active Geo-fence Breach (High Severity)
        Alert(
            alert_id=f"GB-{str(uuid.uuid4())[:4].upper()}",
            tourist_id=tourist_ids["Emily Carter"],
            alert_type=AlertType.GEOFENCE_BREACH,
            severity=AlertSeverity.HIGH,
            status=AlertStatus.IN_PROGRESS,
            location=AlertLocation(
                coordinates=[88.3000, 27.0300],  # Inside Restricted Forest Area
                address="Restricted Forest Area, Darjeeling Hills"
            ),
            description="Tourist entered restricted forest area - unauthorized access detected",
            created_at=datetime.utcnow() - timedelta(minutes=12),
            response_actions=["Forest rangers contacted", "Search team on standby"]
        ),
        
        # Scenario 3: Priya Sharma - Active Route Deviation (Medium Severity)
        Alert(
            alert_id=f"RD-{str(uuid.uuid4())[:4].upper()}",
            tourist_id=tourist_ids["Priya Sharma"],
            alert_type=AlertType.ROUTE_DEVIATION,
            severity=AlertSeverity.MEDIUM,
            status=AlertStatus.NEW,
            location=AlertLocation(
                coordinates=[88.2950, 27.0500],  # Far from planned route
                address="Tiger Hill Road, Darjeeling"
            ),
            description="Tourist deviated significantly from planned route - 3.2km off course",
            created_at=datetime.utcnow() - timedelta(minutes=8),
            response_actions=["GPS tracking enhanced", "Local guide contacted"]
        ),
        
        # Scenario 5: Aisha Khan - Resolved Alert (For history demonstration)  
        Alert(
            alert_id=f"PI-{str(uuid.uuid4())[:4].upper()}",
            tourist_id=tourist_ids["Aisha Khan"],
            alert_type=AlertType.PROLONGED_INACTIVITY,
            severity=AlertSeverity.MEDIUM,
            status=AlertStatus.RESOLVED,
            location=AlertLocation(
                coordinates=[88.2670, 27.0405],
                address="Chowrasta, Darjeeling"
            ),
            description="Tourist showed no movement for 2 hours - communication lost",
            created_at=datetime.utcnow() - timedelta(hours=6),
            resolved_at=datetime.utcnow() - timedelta(hours=4),
            response_actions=[
                "Local police contacted tourist", 
                "Tourist confirmed safe - phone battery dead",
                "Incident resolved - tourist at hotel"
            ]
        )
    ]
    
    for alert in demo_alerts:
        result = await alerts_collection.insert_one(alert.dict(by_alias=True))
        print(f"Created alert: {alert.alert_id} for {alert.alert_type.value} with ID: {result.inserted_id}")

async def create_demo_location_history(tourist_ids):
    """Create location history for demo tourists"""
    location_collection = await get_location_history_collection()
    
    # Clear existing location history for demo
    await location_collection.delete_many({})
    
    # Create recent location entries for each tourist
    location_entries = [
        # Raj Verma - Last known location (Panic scenario)
        LocationHistory(
            tourist_id=tourist_ids["Raj Verma"],
            coordinates=LocationPoint(type="Point", coordinates=[88.2640, 27.0390]),
            address="Mall Road, Darjeeling, West Bengal",
            timestamp=datetime.utcnow() - timedelta(minutes=5),
            accuracy=5.0,
            speed=0.0
        ),
        
        # Emily Carter - Inside restricted forest area
        LocationHistory(
            tourist_id=tourist_ids["Emily Carter"],
            coordinates=LocationPoint(type="Point", coordinates=[88.3000, 27.0300]),
            address="Restricted Forest Area, Darjeeling Hills",
            timestamp=datetime.utcnow() - timedelta(minutes=12),
            accuracy=8.0,
            speed=2.5
        ),
        
        # Priya Sharma - Far from planned route
        LocationHistory(
            tourist_id=tourist_ids["Priya Sharma"],
            coordinates=LocationPoint(type="Point", coordinates=[88.2950, 27.0500]),
            address="Tiger Hill Road, Darjeeling",
            timestamp=datetime.utcnow() - timedelta(minutes=8),
            accuracy=4.0,
            speed=1.2
        ),
        
        # John Doe - Safe location
        LocationHistory(
            tourist_id=tourist_ids["John Doe"],
            coordinates=LocationPoint(type="Point", coordinates=[88.2650, 27.0395]),
            address="The Mall, Darjeeling, West Bengal",
            timestamp=datetime.utcnow() - timedelta(minutes=15),
            accuracy=3.0,
            speed=0.8
        ),
        
        # Aisha Khan - Hotel location  
        LocationHistory(
            tourist_id=tourist_ids["Aisha Khan"],
            coordinates=LocationPoint(type="Point", coordinates=[88.2655, 27.0400]),
            address="Hotel Mayfair, Darjeeling",
            timestamp=datetime.utcnow() - timedelta(minutes=20),
            accuracy=2.0,
            speed=0.0
        )
    ]
    
    for location in location_entries:
        result = await location_collection.insert_one(location.dict(by_alias=True))
        print(f"Created location entry for tourist ID: {location.tourist_id}")

async def main():
    """Main function to initialize demo data"""
    print("=" * 80)
    print("🚀 INITIALIZING SMART TOURIST SAFETY SYSTEM DEMO DATA")
    print("=" * 80)
    
    # Connect to database
    await connect_to_mongo()
    
    # Create demo data in sequence
    print("\n📋 Creating sample users (officers)...")
    await create_sample_users()
    
    print("\n🗺️  Creating demo geo-fences...")
    await create_demo_geofences()
    
    print("\n👥 Creating demo tourist scenarios...")
    tourist_ids = await create_demo_tourists()
    
    print("\n🚨 Creating demo alerts...")
    await create_demo_alerts(tourist_ids)
    
    print("\n📍 Creating location history...")
    await create_demo_location_history(tourist_ids)
    
    print("\n" + "=" * 80)
    print("✅ DEMO DATA INITIALIZATION COMPLETED!")
    print("=" * 80)
    
    print("\n🔐 Officer Login Credentials:")
    print("Inspector: inspector.kumar@tourism.gov.in / password123")
    print("Admin: admin.singh@tourism.gov.in / admin123") 
    print("Officer: officer.sharma@tourism.gov.in / officer123")
    
    print("\n👥 Demo Tourist Scenarios:")
    print("1. 🆘 Raj Verma - PANIC ALERT (Critical)")
    print("2. 🚫 Emily Carter - GEO-FENCE BREACH (High Risk)")
    print("3. 🗺️  Priya Sharma - ROUTE DEVIATION (Medium Risk)")
    print("4. ✅ John Doe - SAFE & SECURE (Data Locked)")
    print("5. 📋 Aisha Khan - RESOLVED INCIDENT (History)")
    
    print("\n🎯 System ready for compelling demo presentation!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())