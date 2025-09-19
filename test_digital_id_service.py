#!/usr/bin/env python3
"""
Test script for Digital ID & Blockchain Service
"""
import asyncio
import sys
from pathlib import Path
import os

# Set up environment
service_dir = Path(__file__).parent / "digital_id_service"
sys.path.insert(0, str(service_dir))

# Set required environment variables
os.environ["MONGO_URL"] = "mongodb://localhost:27017/"
os.environ["DATABASE_NAME"] = "tourism_security_test"
os.environ["SERVICE_API_KEY"] = "test_api_key_12345"

# Generate test encryption key
from cryptography.fernet import Fernet
import base64
key = Fernet.generate_key()
os.environ["ENCRYPTION_KEY_BASE64"] = base64.urlsafe_b64encode(key).decode()

async def test_digital_id_service():
    """Test the Digital ID service functionality"""
    print("Testing Digital ID & Blockchain Service...")
    
    try:
        # Import after setting environment
        from digital_id_service.database import connect_to_mongo, close_mongo_connection
        from digital_id_service.services.encryption_service import encryption_service
        from digital_id_service.services.blockchain_simulator import blockchain_simulator
        from digital_id_service.services.secure_data_service import secure_data_service
        from digital_id_service.models import TouristRegistrationRequest, DataAccessRequest, AccessReason, EmergencyContact
        from datetime import datetime
        
        # Connect to database
        print("Connecting to database...")
        await connect_to_mongo()
        print("✓ Database connected")
        
        # Test encryption service
        print("\nTesting encryption service...")
        test_data = {"name": "John Doe", "passport": "AB123456"}
        encrypted = encryption_service.encrypt_data(test_data)
        decrypted = encryption_service.decrypt_data(encrypted)
        assert decrypted == test_data
        print("✓ Encryption/decryption works")
        
        # Test hash generation
        test_hash = encryption_service.generate_hash("test data")
        assert len(test_hash) == 64  # SHA-256 produces 64 character hex string
        print("✓ Hash generation works")
        
        # Test blockchain simulator
        print("\nTesting blockchain simulator...")
        next_block = await blockchain_simulator.get_next_block_number()
        print(f"✓ Next block number: {next_block}")
        
        # Test tourist registration
        print("\nTesting tourist registration...")
        registration_request = TouristRegistrationRequest(
            tourist_id="TEST_001",
            full_name="John Doe",
            nationality="US",
            kyc_type="passport",
            kyc_document_number="AB123456",
            detailed_itinerary="Visit Delhi, Agra, Jaipur",
            emergency_contacts=[
                EmergencyContact(name="Jane Doe", phone="+1234567890", relationship="wife")
            ]
        )
        
        registration_response = await secure_data_service.register_tourist_data(registration_request)
        print(f"✓ Tourist registered: {registration_response.tourist_id}")
        print(f"  Registration ID: {registration_response.registration_id}")
        print(f"  KYC Hash: {registration_response.kyc_hash[:16]}...")
        
        # Test emergency access
        print("\nTesting emergency access...")
        access_request = DataAccessRequest(
            tourist_id="TEST_001",
            authority_id="POLICE_001",
            authority_name="Officer Smith",
            authority_department="Emergency Response",
            access_reason=AccessReason.PANIC_ALERT,
            alert_id="ALERT_123"
        )
        
        access_response = await secure_data_service.request_emergency_access(access_request)
        print(f"✓ Emergency access granted")
        print(f"  Full name: {access_response.full_name}")
        print(f"  Emergency contacts: {len(access_response.emergency_contacts)}")
        print(f"  Access log ID: {access_response.access_log_id}")
        
        # Test data integrity verification
        print("\nTesting data integrity verification...")
        integrity_result = await secure_data_service.verify_data_integrity("TEST_001")
        print(f"✓ Data integrity: {integrity_result['status']}")
        print(f"  KYC valid: {integrity_result['kyc_hash_valid']}")
        print(f"  Itinerary valid: {integrity_result['itinerary_hash_valid']}")
        
        # Test audit logs
        print("\nTesting audit logs...")
        logs = await secure_data_service.get_access_logs("TEST_001")
        print(f"✓ Retrieved {len(logs)} audit log entries")
        
        # Test blockchain integrity
        print("\nTesting blockchain integrity...")
        chain_result = await blockchain_simulator.verify_chain_integrity()
        print(f"✓ Blockchain status: {chain_result['status']}")
        print(f"  Verified entries: {chain_result['verified_count']}")
        
        # Cleanup
        await close_mongo_connection()
        print("\n✓ All tests passed successfully!")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_digital_id_service())
    sys.exit(0 if success else 1)