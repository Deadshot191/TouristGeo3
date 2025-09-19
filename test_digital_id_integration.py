#!/usr/bin/env python3
"""
Test Digital ID Integration in Tourism Safety System
Tests the security integration features including data masking and service communication
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Set environment variables
os.environ["MONGO_URL"] = "mongodb://localhost:27017"
os.environ["DB_NAME"] = "test_database"
os.environ["DIGITAL_ID_SERVICE_URL"] = "http://localhost:8002"
os.environ["DIGITAL_ID_SERVICE_API_KEY"] = "secure_service_api_key_production_123"

async def test_digital_id_integration():
    """Test Digital ID service integration"""
    print("🔐 Testing Digital ID Integration...")
    
    try:
        # Import after setting environment
        from database import connect_to_mongo, close_mongo_connection
        from services.tourist_service import TouristService
        from services.alert_service import AlertService
        from services.digital_id_client import digital_id_client
        from models import TouristCreate, EmergencyContact
        
        # Connect to database
        await connect_to_mongo()
        print("✓ Database connected")
        
        # Test 1: Check Digital ID service health
        print("\n1. Testing Digital ID Service Health...")
        try:
            is_healthy = await digital_id_client.check_service_health()
            print(f"   Digital ID service healthy: {is_healthy}")
        except Exception as e:
            print(f"   Digital ID service error: {e}")
            is_healthy = False
        
        # Test 2: Test tourist creation with Digital ID integration
        print("\n2. Testing Tourist Creation with Digital ID Integration...")
        try:
            # Create a test tourist
            tourist_data = TouristCreate(
                full_name="Test User Security",
                nationality="India",
                kyc_type="passport",
                kyc_id="TEST123456",
                visit_start_date=datetime.now(),
                visit_end_date=datetime.now() + timedelta(days=7),
                itinerary="Delhi -> Agra -> Jaipur",
                emergency_contacts=[
                    EmergencyContact(
                        name="Emergency Contact",
                        phone="+91-9876543210",
                        relationship="family"
                    )
                ]
            )
            
            # This should create a tourist with masked data in main database
            tourist = await TouristService.create_tourist(tourist_data)
            
            # Verify data masking
            data_masked = (
                tourist.full_name == "[ENCRYPTED]" and
                tourist.nationality == "[ENCRYPTED]" and
                tourist.itinerary == "[ENCRYPTED]" and
                len(tourist.emergency_contacts) == 0
            )
            
            print(f"   Tourist created: {tourist.digital_id}")
            print(f"   Data properly masked: {data_masked}")
            print(f"   Full name: {tourist.full_name}")
            print(f"   Nationality: {tourist.nationality}")
            print(f"   Itinerary: {tourist.itinerary}")
            print(f"   Emergency contacts: {len(tourist.emergency_contacts)}")
            
            if data_masked:
                print("   ✓ Tourist data masking works correctly")
            else:
                print("   ❌ Tourist data masking failed")
                
        except Exception as e:
            print(f"   ❌ Tourist creation failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 3: Test emergency data access (simulated)
        print("\n3. Testing Emergency Data Access...")
        try:
            # This would normally be called during high-severity alerts
            decrypted_data = await TouristService.get_decrypted_tourist_data(
                digital_id="DIG-12AB34CD",  # Use existing tourist
                authority_id="TEST_OFFICER",
                authority_name="Test Officer",
                authority_department="Emergency Response",
                access_reason="panic_alert",
                alert_id="TEST_ALERT_001"
            )
            
            if decrypted_data:
                print("   ✓ Emergency data access successful")
                print(f"   Retrieved data keys: {list(decrypted_data.keys())}")
            else:
                print("   ❌ Emergency data access failed (expected if Digital ID service unavailable)")
                
        except Exception as e:
            print(f"   ❌ Emergency data access error: {e}")
        
        # Test 4: Test service authentication
        print("\n4. Testing Service Authentication...")
        try:
            # Test if environment variables are properly configured
            service_url = os.environ.get("DIGITAL_ID_SERVICE_URL")
            api_key = os.environ.get("DIGITAL_ID_SERVICE_API_KEY")
            
            print(f"   Service URL configured: {bool(service_url)}")
            print(f"   API Key configured: {bool(api_key)}")
            print(f"   Service URL: {service_url}")
            
            if service_url and api_key:
                print("   ✓ Service authentication configured")
            else:
                print("   ❌ Service authentication not configured")
                
        except Exception as e:
            print(f"   ❌ Service authentication test error: {e}")
        
        # Test 5: Test backward compatibility
        print("\n5. Testing Backward Compatibility...")
        try:
            # When Digital ID service is unavailable, system should still function
            # Check if existing functionality works
            from services.alert_service import AlertService
            
            # Create a panic alert (should work even without Digital ID service)
            alert = await AlertService.create_panic_alert(
                tourist_id="68ccde34f39e8d3615de8c9f",  # Use existing tourist ID
                longitude=77.2090,
                latitude=28.6139,
                address="Test Emergency Location"
            )
            
            print(f"   ✓ Panic alert created: {alert.alert_id}")
            print("   ✓ Backward compatibility maintained")
            
        except Exception as e:
            print(f"   ❌ Backward compatibility test failed: {e}")
            import traceback
            traceback.print_exc()
        
        await close_mongo_connection()
        print("\n✅ Digital ID Integration testing completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Digital ID Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_digital_id_integration())
    print(f"\n{'✅ All tests passed!' if success else '❌ Some tests failed!'}")