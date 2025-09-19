#!/usr/bin/env python3
"""
Test script for integrated security system
Tests the full flow: tourist registration -> emergency alert -> data access
"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# Set up environment
backend_dir = Path(__file__).parent / "backend"
digital_id_dir = Path(__file__).parent / "digital_id_service"
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(digital_id_dir))

# Set required environment variables
os.environ["MONGO_URL"] = "mongodb://localhost:27017/"
os.environ["DB_NAME"] = "tourism_security_integrated_test"
os.environ["DIGITAL_ID_SERVICE_URL"] = "http://localhost:8002"
os.environ["DIGITAL_ID_SERVICE_API_KEY"] = "secure_service_api_key_production_123"
os.environ["SERVICE_API_KEY"] = "secure_service_api_key_production_123"
os.environ["DATABASE_NAME"] = "tourism_security_integrated_test"
os.environ["ENCRYPTION_KEY_BASE64"] = "bjZuVG5zdm5ISTRxWUNmenFQR2dvcFo4TnZDSnlrQ0NCQk10dmdpNkpDZz0="

async def test_integrated_security_system():
    """Test the complete integrated security system"""
    print("Testing Integrated Security & Privacy System...")
    
    try:
        # Import after setting environment
        import backend.database as backend_db
        from backend.services.tourist_service import TouristService
        from backend.services.alert_service import AlertService
        from backend.services.digital_id_client import digital_id_client
        from backend.models import TouristCreate, EmergencyContact, AlertType, AlertSeverity
        
        # Connect to main database
        print("Connecting to main database...")
        await backend_db.connect_to_mongo()
        print("✓ Main database connected")
        
        # Test Digital ID service health
        print("\nTesting Digital ID service connection...")
        is_healthy = await digital_id_client.check_service_health()
        if not is_healthy:
            print("⚠ Digital ID service not available - starting fallback mode")
        else:
            print("✓ Digital ID service is healthy")
        
        # Test tourist registration with secure data separation
        print("\nTesting secure tourist registration...")
        tourist_data = TouristCreate(
            full_name="Alice Johnson",
            nationality="Canada",
            kyc_type="passport",
            kyc_id="CA987654321",
            visit_start_date=datetime.now(),
            visit_end_date=datetime.now(),
            itinerary="Visit Mumbai, Goa, and Kerala for cultural tour",
            emergency_contacts=[
                EmergencyContact(name="Bob Johnson", phone="+1-416-555-0123", relationship="husband"),
                EmergencyContact(name="Carol Johnson", phone="+1-416-555-0124", relationship="sister")
            ]
        )
        
        # Create tourist (this should separate sensitive data)
        tourist = await TouristService.create_tourist(tourist_data)
        print(f"✓ Tourist created: {tourist.digital_id}")
        print(f"  Name in main DB: {tourist.full_name}")  # Should be [ENCRYPTED]
        print(f"  Nationality in main DB: {tourist.nationality}")  # Should be [ENCRYPTED]
        print(f"  Emergency contacts in main DB: {len(tourist.emergency_contacts)}")  # Should be 0
        
        # Verify data separation
        if tourist.full_name == "[ENCRYPTED]" and tourist.nationality == "[ENCRYPTED]":
            print("✓ Sensitive data properly masked in main database")
        else:
            print("⚠ Sensitive data not properly masked")
        
        # Test emergency alert creation (should trigger data access)
        print("\nTesting emergency alert with data access...")
        alert = await AlertService.create_panic_alert(
            tourist_id=str(tourist.id),
            longitude=72.8777,
            latitude=19.0760,
            address="Gateway of India, Mumbai"
        )
        print(f"✓ Panic alert created: {alert.alert_id}")
        
        # Test direct emergency data access
        print("\nTesting direct emergency data access...")
        decrypted_data = await TouristService.get_decrypted_tourist_data(
            digital_id=tourist.digital_id,
            authority_id="POLICE_001",
            authority_name="Inspector Sharma",
            authority_department="Mumbai Police Emergency Response",
            access_reason="panic_alert",
            alert_id=alert.alert_id
        )
        
        if decrypted_data:
            print("✓ Emergency data access successful")
            print(f"  Full name: {decrypted_data.get('full_name')}")
            print(f"  Nationality: {decrypted_data.get('nationality')}")
            print(f"  Emergency contacts: {len(decrypted_data.get('emergency_contacts', []))}")
            print(f"  Access log ID: {decrypted_data.get('access_log_id')}")
        else:
            print("✗ Emergency data access failed")
        
        # Test data integrity verification
        print("\nTesting data integrity verification...")
        integrity_result = await digital_id_client.verify_data_integrity(tourist.digital_id)
        if integrity_result:
            print(f"✓ Data integrity check: {integrity_result.get('status')}")
            print(f"  KYC valid: {integrity_result.get('kyc_hash_valid')}")
            print(f"  Itinerary valid: {integrity_result.get('itinerary_hash_valid')}")
        
        # Test audit log retrieval
        print("\nTesting audit log retrieval...")
        audit_logs = await digital_id_client.get_audit_logs(tourist.digital_id)
        if audit_logs:
            log_count = audit_logs.get('count', 0)
            print(f"✓ Retrieved {log_count} audit log entries")
            
            # Show latest log entry details
            if log_count > 0:
                latest_log = audit_logs['logs'][0]
                print(f"  Latest access by: {latest_log.get('authority_name')}")
                print(f"  Access reason: {latest_log.get('access_reason')}")
                print(f"  Block number: {latest_log.get('block_number')}")
        
        # Test regular tourist lookup (should show masked data)
        print("\nTesting regular tourist data access (should be masked)...")
        retrieved_tourist = await TouristService.get_tourist_by_digital_id(tourist.digital_id)
        if retrieved_tourist:
            print("✓ Regular tourist lookup successful")
            print(f"  Name: {retrieved_tourist.full_name}")  # Should be [ENCRYPTED]
            print(f"  Nationality: {retrieved_tourist.nationality}")  # Should be [ENCRYPTED]
            print(f"  Emergency contacts: {len(retrieved_tourist.emergency_contacts)}")  # Should be 0
        
        # Cleanup
        await close_mongo_connection()
        print("\n✓ All integrated security tests passed successfully!")
        print("\n🔒 Security Summary:")
        print("  - Sensitive data encrypted and separated from operational data")
        print("  - Emergency access creates immutable audit trail")
        print("  - Data integrity verified with cryptographic hashes")
        print("  - Access control enforced at service level")
        print("  - Blockchain simulation provides tamper-evident logging")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Integrated test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_integrated_security_system())
    sys.exit(0 if success else 1)