#!/usr/bin/env python3
"""
Field Mapping Integration Test for Tourism Safety System
Tests specific field mappings between backend API responses and frontend components
Focus on Tourist Detail Modal and Tourist Database Page data consistency
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://fence-alert.preview.emergentagent.com')
API_BASE_URL = f"{BACKEND_URL}/api"

class FieldMappingTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = {}
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        self.test_results[test_name] = {
            "success": success,
            "details": details,
            "response_data": response_data,
            "timestamp": datetime.now().isoformat()
        }
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
    async def make_request(self, method: str, endpoint: str, data: Dict = None, 
                          headers: Dict = None, params: Dict = None) -> tuple:
        """Make HTTP request and return (success, response_data, status_code)"""
        try:
            url = f"{API_BASE_URL}{endpoint}"
            request_headers = headers or {}
            
            if self.auth_token and 'Authorization' not in request_headers:
                request_headers['Authorization'] = f"Bearer {self.auth_token}"
                
            async with self.session.request(
                method, url, json=data, headers=request_headers, params=params
            ) as response:
                try:
                    response_data = await response.json()
                except:
                    response_data = await response.text()
                    
                return response.status < 400, response_data, response.status
                
        except Exception as e:
            return False, str(e), 0
    
    async def authenticate(self):
        """Authenticate with the API"""
        print("\n=== Authentication ===")
        
        login_data = {
            "email": "inspector.kumar@tourism.gov.in",
            "password": "password123"
        }
        
        success, data, status = await self.make_request("POST", "/auth/login", login_data)
        
        if success and status == 200 and isinstance(data, dict) and 'access_token' in data:
            self.auth_token = data['access_token']
            self.log_test(
                "Authentication", 
                True,
                f"Successfully authenticated as {data.get('user', {}).get('full_name', 'Unknown')}"
            )
            return True
        else:
            self.log_test(
                "Authentication", 
                False,
                f"Failed to authenticate. Status: {status}, Response: {data}"
            )
            return False
    
    async def test_tourists_endpoint_field_structure(self):
        """Test GET /api/tourists endpoint field structure"""
        print("\n=== Testing GET /api/tourists Field Structure ===")
        
        if not self.auth_token:
            self.log_test("GET /api/tourists Field Structure", False, "No auth token available")
            return None
        
        success, data, status = await self.make_request("GET", "/tourists")
        
        if not success or status != 200 or not isinstance(data, list):
            self.log_test(
                "GET /api/tourists Field Structure", 
                False,
                f"Failed to get tourists. Status: {status}, Response: {data}"
            )
            return None
        
        if len(data) == 0:
            self.log_test(
                "GET /api/tourists Field Structure", 
                False,
                "No tourists found in database"
            )
            return None
        
        # Analyze field structure of first tourist
        tourist = data[0]
        expected_fields = [
            'id', 'digital_id', 'full_name', 'status', 'nationality', 
            'emergency_contacts', 'location', 'safety_score', 'visit_start_date', 
            'visit_end_date', 'itinerary', 'photo_url', 'last_location_update'
        ]
        
        present_fields = list(tourist.keys())
        missing_fields = [field for field in expected_fields if field not in present_fields]
        extra_fields = [field for field in present_fields if field not in expected_fields]
        
        # Check specific field formats
        field_analysis = {
            "total_tourists": len(data),
            "present_fields": present_fields,
            "missing_fields": missing_fields,
            "extra_fields": extra_fields,
            "sample_tourist": {
                "id": tourist.get('id'),
                "digital_id": tourist.get('digital_id'),
                "full_name": tourist.get('full_name'),
                "status": tourist.get('status'),
                "location_structure": type(tourist.get('location')).__name__ if tourist.get('location') else None,
                "emergency_contacts_structure": type(tourist.get('emergency_contacts')).__name__ if tourist.get('emergency_contacts') else None,
                "visit_start_date": tourist.get('visit_start_date'),
                "visit_end_date": tourist.get('visit_end_date')
            }
        }
        
        self.log_test(
            "GET /api/tourists Field Structure", 
            len(missing_fields) == 0,
            f"Found {len(data)} tourists. Missing fields: {missing_fields}. Extra fields: {extra_fields}",
            field_analysis
        )
        
        return data
    
    async def test_individual_tourist_endpoint(self, tourist_id: str):
        """Test GET /api/tourists/{tourist_id} endpoint field structure"""
        print(f"\n=== Testing GET /api/tourists/{tourist_id} Field Structure ===")
        
        if not self.auth_token:
            self.log_test("GET /api/tourists/{id} Field Structure", False, "No auth token available")
            return None
        
        success, data, status = await self.make_request("GET", f"/tourists/{tourist_id}")
        
        if not success or status != 200 or not isinstance(data, dict):
            self.log_test(
                "GET /api/tourists/{id} Field Structure", 
                False,
                f"Failed to get tourist {tourist_id}. Status: {status}, Response: {data}"
            )
            return None
        
        # Check all fields used by TouristDetailModal
        modal_required_fields = [
            'full_name', 'digital_id', 'status', 'emergency_contacts', 
            'location', 'safety_score', 'itinerary', 'visit_start_date', 
            'visit_end_date', 'nationality', 'photo_url'
        ]
        
        present_fields = list(data.keys())
        missing_modal_fields = [field for field in modal_required_fields if field not in present_fields]
        
        # Analyze specific field structures that frontend expects
        field_analysis = {
            "tourist_id": tourist_id,
            "present_fields": present_fields,
            "missing_modal_fields": missing_modal_fields,
            "field_details": {
                "full_name": data.get('full_name'),
                "digital_id": data.get('digital_id'),
                "status": data.get('status'),
                "location_structure": self._analyze_location_structure(data.get('location')),
                "emergency_contacts_structure": self._analyze_emergency_contacts_structure(data.get('emergency_contacts')),
                "visit_start_date": data.get('visit_start_date'),
                "visit_end_date": data.get('visit_end_date'),
                "safety_score": data.get('safety_score'),
                "itinerary": data.get('itinerary')
            }
        }
        
        self.log_test(
            "GET /api/tourists/{id} Field Structure", 
            len(missing_modal_fields) == 0,
            f"Tourist {tourist_id} analysis. Missing modal fields: {missing_modal_fields}",
            field_analysis
        )
        
        return data
    
    async def test_tourist_alerts_endpoint(self, tourist_id: str):
        """Test GET /api/tourists/{tourist_id}/alerts endpoint"""
        print(f"\n=== Testing GET /api/tourists/{tourist_id}/alerts Field Structure ===")
        
        if not self.auth_token:
            self.log_test("GET /api/tourists/{id}/alerts Field Structure", False, "No auth token available")
            return None
        
        success, data, status = await self.make_request("GET", f"/tourists/{tourist_id}/alerts")
        
        if not success or status != 200:
            self.log_test(
                "GET /api/tourists/{id}/alerts Field Structure", 
                False,
                f"Failed to get alerts for tourist {tourist_id}. Status: {status}, Response: {data}"
            )
            return None
        
        if not isinstance(data, list):
            self.log_test(
                "GET /api/tourists/{id}/alerts Field Structure", 
                False,
                f"Expected list response, got {type(data).__name__}"
            )
            return None
        
        alert_analysis = {
            "tourist_id": tourist_id,
            "total_alerts": len(data),
            "alerts_structure": []
        }
        
        if len(data) > 0:
            # Analyze first alert structure
            alert = data[0]
            alert_fields = list(alert.keys())
            expected_alert_fields = [
                'id', 'alert_id', 'tourist_id', 'tourist_name', 'alert_type', 
                'severity', 'status', 'location', 'description', 'timestamp', 'resolved_at'
            ]
            
            missing_alert_fields = [field for field in expected_alert_fields if field not in alert_fields]
            
            alert_analysis["sample_alert"] = {
                "present_fields": alert_fields,
                "missing_fields": missing_alert_fields,
                "alert_id": alert.get('alert_id'),
                "alert_type": alert.get('alert_type'),
                "severity": alert.get('severity'),
                "status": alert.get('status'),
                "location_structure": self._analyze_location_structure(alert.get('location')),
                "timestamp": alert.get('timestamp')
            }
        
        self.log_test(
            "GET /api/tourists/{id}/alerts Field Structure", 
            True,
            f"Found {len(data)} alerts for tourist {tourist_id}",
            alert_analysis
        )
        
        return data
    
    async def test_specific_tourist_raj_verma(self):
        """Test specific tourist Raj Verma (DIG-PANIC01) with PANIC status"""
        print("\n=== Testing Specific Tourist: Raj Verma (DIG-PANIC01) ===")
        
        if not self.auth_token:
            self.log_test("Raj Verma Test", False, "No auth token available")
            return
        
        # First get all tourists to find Raj Verma
        success, tourists_data, status = await self.make_request("GET", "/tourists")
        
        if not success or not isinstance(tourists_data, list):
            self.log_test("Raj Verma Test", False, "Could not retrieve tourists list")
            return
        
        # Find Raj Verma by digital_id
        raj_verma = None
        raj_verma_id = None
        
        for tourist in tourists_data:
            if tourist.get('digital_id') == 'DIG-PANIC01':
                raj_verma = tourist
                raj_verma_id = tourist.get('id')
                break
        
        if not raj_verma:
            self.log_test("Raj Verma Test", False, "Raj Verma (DIG-PANIC01) not found in tourists list")
            return
        
        # Test individual tourist endpoint for Raj Verma
        detailed_raj = await self.test_individual_tourist_endpoint(raj_verma_id)
        
        # Test alerts for Raj Verma
        raj_alerts = await self.test_tourist_alerts_endpoint(raj_verma_id)
        
        # Analyze Raj Verma's data completeness
        raj_analysis = {
            "digital_id": raj_verma.get('digital_id'),
            "full_name": raj_verma.get('full_name'),
            "status": raj_verma.get('status'),
            "has_panic_status": raj_verma.get('status') == 'panic',
            "has_location": raj_verma.get('location') is not None,
            "has_emergency_contacts": len(raj_verma.get('emergency_contacts', [])) > 0,
            "safety_score": raj_verma.get('safety_score'),
            "visit_dates": {
                "start": raj_verma.get('visit_start_date'),
                "end": raj_verma.get('visit_end_date')
            },
            "alerts_count": len(raj_alerts) if raj_alerts else 0
        }
        
        # Check if all required fields are populated
        required_populated = all([
            raj_verma.get('digital_id'),
            raj_verma.get('full_name'),
            raj_verma.get('status'),
            raj_verma.get('safety_score') is not None
        ])
        
        self.log_test(
            "Raj Verma Complete Data Test", 
            required_populated,
            f"Status: {raj_verma.get('status')}, Required fields populated: {required_populated}",
            raj_analysis
        )
    
    async def test_field_mapping_mismatches(self):
        """Test for specific field mapping mismatches between backend and frontend"""
        print("\n=== Testing Field Mapping Mismatches ===")
        
        if not self.auth_token:
            self.log_test("Field Mapping Mismatches", False, "No auth token available")
            return
        
        # Get a sample tourist
        success, tourists_data, status = await self.make_request("GET", "/tourists")
        
        if not success or not isinstance(tourists_data, list) or len(tourists_data) == 0:
            self.log_test("Field Mapping Mismatches", False, "No tourists available for testing")
            return
        
        tourist_id = tourists_data[0].get('id')
        success, tourist_detail, status = await self.make_request("GET", f"/tourists/{tourist_id}")
        
        if not success or not isinstance(tourist_detail, dict):
            self.log_test("Field Mapping Mismatches", False, "Could not get tourist detail")
            return
        
        # Check for specific field mapping issues mentioned in the review
        mapping_issues = []
        
        # 1. Check visit date field names
        if 'visitEndDate' in tourist_detail and 'visit_end_date' not in tourist_detail:
            mapping_issues.append("Backend uses 'visitEndDate' but frontend expects 'visit_end_date'")
        elif 'visit_end_date' in tourist_detail and 'visitEndDate' not in tourist_detail:
            mapping_issues.append("Backend uses 'visit_end_date' but frontend might expect 'visitEndDate'")
        
        if 'visitStartDate' in tourist_detail and 'visit_start_date' not in tourist_detail:
            mapping_issues.append("Backend uses 'visitStartDate' but frontend expects 'visit_start_date'")
        elif 'visit_start_date' in tourist_detail and 'visitStartDate' not in tourist_detail:
            mapping_issues.append("Backend uses 'visit_start_date' but frontend might expect 'visitStartDate'")
        
        # 2. Check location structure
        location = tourist_detail.get('location')
        if location:
            if not isinstance(location, dict):
                mapping_issues.append(f"Location is {type(location).__name__}, expected dict")
            elif 'address' not in location:
                mapping_issues.append("Location missing 'address' field that frontend expects")
        else:
            mapping_issues.append("Location field is missing or null")
        
        # 3. Check emergency contacts structure
        emergency_contacts = tourist_detail.get('emergency_contacts')
        if emergency_contacts:
            if not isinstance(emergency_contacts, list):
                mapping_issues.append(f"Emergency contacts is {type(emergency_contacts).__name__}, expected list")
            elif len(emergency_contacts) > 0:
                first_contact = emergency_contacts[0]
                if not isinstance(first_contact, dict):
                    mapping_issues.append("Emergency contact items should be dict objects")
                elif 'phone' not in first_contact:
                    mapping_issues.append("Emergency contact missing 'phone' field that frontend expects")
        
        # Create detailed analysis
        field_mapping_analysis = {
            "tourist_id": tourist_id,
            "mapping_issues_found": mapping_issues,
            "field_analysis": {
                "visit_start_date": tourist_detail.get('visit_start_date'),
                "visit_end_date": tourist_detail.get('visit_end_date'),
                "visitStartDate": tourist_detail.get('visitStartDate'),
                "visitEndDate": tourist_detail.get('visitEndDate'),
                "location_type": type(tourist_detail.get('location')).__name__,
                "location_has_address": isinstance(tourist_detail.get('location'), dict) and 'address' in tourist_detail.get('location', {}),
                "emergency_contacts_type": type(tourist_detail.get('emergency_contacts')).__name__,
                "emergency_contacts_count": len(tourist_detail.get('emergency_contacts', [])) if isinstance(tourist_detail.get('emergency_contacts'), list) else 0,
                "first_contact_has_phone": (
                    isinstance(tourist_detail.get('emergency_contacts'), list) and 
                    len(tourist_detail.get('emergency_contacts', [])) > 0 and
                    isinstance(tourist_detail.get('emergency_contacts')[0], dict) and
                    'phone' in tourist_detail.get('emergency_contacts')[0]
                ) if tourist_detail.get('emergency_contacts') else False
            }
        }
        
        self.log_test(
            "Field Mapping Mismatches", 
            len(mapping_issues) == 0,
            f"Found {len(mapping_issues)} mapping issues: {mapping_issues}",
            field_mapping_analysis
        )
    
    def _analyze_location_structure(self, location):
        """Analyze location field structure"""
        if location is None:
            return {"type": "null", "has_address": False, "has_coordinates": False}
        
        if not isinstance(location, dict):
            return {"type": type(location).__name__, "has_address": False, "has_coordinates": False}
        
        return {
            "type": "dict",
            "has_address": 'address' in location,
            "has_coordinates": 'coordinates' in location,
            "fields": list(location.keys()),
            "coordinates_type": type(location.get('coordinates')).__name__ if 'coordinates' in location else None
        }
    
    def _analyze_emergency_contacts_structure(self, emergency_contacts):
        """Analyze emergency contacts field structure"""
        if emergency_contacts is None:
            return {"type": "null", "count": 0, "first_contact_has_phone": False}
        
        if not isinstance(emergency_contacts, list):
            return {"type": type(emergency_contacts).__name__, "count": 0, "first_contact_has_phone": False}
        
        first_contact_has_phone = False
        if len(emergency_contacts) > 0 and isinstance(emergency_contacts[0], dict):
            first_contact_has_phone = 'phone' in emergency_contacts[0]
        
        return {
            "type": "list",
            "count": len(emergency_contacts),
            "first_contact_has_phone": first_contact_has_phone,
            "first_contact_fields": list(emergency_contacts[0].keys()) if len(emergency_contacts) > 0 and isinstance(emergency_contacts[0], dict) else []
        }
    
    async def run_field_mapping_tests(self):
        """Run all field mapping tests"""
        print(f"🔍 Starting Field Mapping Integration Tests")
        print(f"📍 Backend URL: {API_BASE_URL}")
        print("=" * 60)
        
        # Authenticate first
        if not await self.authenticate():
            print("❌ Authentication failed, cannot proceed with tests")
            return self.test_results
        
        # Test tourists endpoint field structure
        tourists_data = await self.test_tourists_endpoint_field_structure()
        
        if tourists_data and len(tourists_data) > 0:
            # Test individual tourist endpoint
            first_tourist_id = tourists_data[0].get('id')
            if first_tourist_id:
                await self.test_individual_tourist_endpoint(first_tourist_id)
                await self.test_tourist_alerts_endpoint(first_tourist_id)
        
        # Test specific tourist (Raj Verma)
        await self.test_specific_tourist_raj_verma()
        
        # Test field mapping mismatches
        await self.test_field_mapping_mismatches()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 FIELD MAPPING TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "No tests run")
        
        if failed_tests > 0:
            print(f"\n🔍 FAILED TESTS:")
            for test_name, result in self.test_results.items():
                if not result['success']:
                    print(f"  ❌ {test_name}: {result['details']}")
        
        print(f"\n📋 DETAILED FIELD ANALYSIS:")
        for test_name, result in self.test_results.items():
            if result.get('response_data'):
                print(f"\n🔸 {test_name}:")
                print(f"   {json.dumps(result['response_data'], indent=4, default=str)}")
        
        return self.test_results

async def main():
    """Main test runner"""
    async with FieldMappingTester() as tester:
        results = await tester.run_field_mapping_tests()
        
        # Save results to file
        with open('/app/field_mapping_test_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Field mapping test results saved to: /app/field_mapping_test_results.json")
        
        return results

if __name__ == "__main__":
    asyncio.run(main())