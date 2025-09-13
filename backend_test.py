#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Tourism Safety System
Tests all major API endpoints including authentication, tourist management, 
alerts, geofencing, location services, and analytics.
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://safemonitor-1.preview.emergentagent.com')
API_BASE_URL = f"{BACKEND_URL}/api"

class TourismSafetyAPITester:
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
    
    async def test_health_endpoints(self):
        """Test system health endpoints"""
        print("\n=== Testing Health Endpoints ===")
        
        # Test root endpoint
        success, data, status = await self.make_request("GET", "/")
        self.log_test(
            "Health Check Root", 
            success and status == 200,
            f"Status: {status}, Response: {data}"
        )
        
        # Test detailed health check
        success, data, status = await self.make_request("GET", "/health")
        self.log_test(
            "Detailed Health Check", 
            success and status == 200,
            f"Status: {status}, Database: {data.get('database', 'unknown') if isinstance(data, dict) else 'error'}"
        )
    
    async def test_authentication(self):
        """Test authentication system"""
        print("\n=== Testing Authentication System ===")
        
        # Test login with valid credentials
        login_data = {
            "email": "inspector.kumar@tourism.gov.in",
            "password": "password123"
        }
        
        success, data, status = await self.make_request("POST", "/auth/login", login_data)
        
        if success and status == 200 and isinstance(data, dict) and 'access_token' in data:
            self.auth_token = data['access_token']
            self.log_test(
                "Login Valid Credentials", 
                True,
                f"Successfully logged in as {data.get('user', {}).get('full_name', 'Unknown')}"
            )
        else:
            self.log_test(
                "Login Valid Credentials", 
                False,
                f"Status: {status}, Response: {data}"
            )
            return
        
        # Test login with invalid credentials
        invalid_login = {
            "email": "invalid@test.com",
            "password": "wrongpassword"
        }
        
        success, data, status = await self.make_request("POST", "/auth/login", invalid_login)
        self.log_test(
            "Login Invalid Credentials", 
            not success and status == 401,
            f"Status: {status}, Expected 401 for invalid credentials"
        )
        
        # Test protected endpoint with valid token
        success, data, status = await self.make_request("GET", "/auth/me")
        self.log_test(
            "Protected Endpoint Valid Token", 
            success and status == 200,
            f"Status: {status}, User: {data.get('full_name', 'Unknown') if isinstance(data, dict) else 'error'}"
        )
        
        # Test protected endpoint without token
        temp_token = self.auth_token
        self.auth_token = None
        success, data, status = await self.make_request("GET", "/auth/me")
        self.auth_token = temp_token
        
        self.log_test(
            "Protected Endpoint No Token", 
            not success and status == 403,
            f"Status: {status}, Expected 403 for missing token"
        )
        
        # Test protected endpoint with invalid token
        headers = {"Authorization": "Bearer invalid_token_here"}
        success, data, status = await self.make_request("GET", "/auth/me", headers=headers)
        self.log_test(
            "Protected Endpoint Invalid Token", 
            not success and status == 401,
            f"Status: {status}, Expected 401 for invalid token"
        )
    
    async def test_tourist_management(self):
        """Test tourist management endpoints"""
        print("\n=== Testing Tourist Management ===")
        
        if not self.auth_token:
            self.log_test("Tourist Management", False, "No auth token available")
            return
        
        # Test get all tourists
        success, data, status = await self.make_request("GET", "/tourists")
        tourists_list = data if isinstance(data, list) else []
        
        self.log_test(
            "Get All Tourists", 
            success and status == 200 and isinstance(data, list),
            f"Status: {status}, Found {len(tourists_list)} tourists"
        )
        
        if not tourists_list:
            self.log_test("Tourist Management", False, "No tourists found for further testing")
            return
            
        # Get first tourist for detailed testing
        tourist_id = tourists_list[0].get('id')
        if not tourist_id:
            self.log_test("Tourist Management", False, "No tourist ID found")
            return
        
        # Test get specific tourist
        success, data, status = await self.make_request("GET", f"/tourists/{tourist_id}")
        self.log_test(
            "Get Specific Tourist", 
            success and status == 200,
            f"Status: {status}, Tourist: {data.get('full_name', 'Unknown') if isinstance(data, dict) else 'error'}"
        )
        
        # Test update tourist status
        status_update = {
            "status": "safe",
            "reason": "Test status update"
        }
        
        success, data, status = await self.make_request("PUT", f"/tourists/{tourist_id}/status", status_update)
        self.log_test(
            "Update Tourist Status", 
            success and status == 200,
            f"Status: {status}, Response: {data}"
        )
        
        # Test get tourist location history
        success, data, status = await self.make_request("GET", f"/tourists/{tourist_id}/location-history")
        self.log_test(
            "Get Location History", 
            success and status == 200,
            f"Status: {status}, History entries: {len(data) if isinstance(data, list) else 'error'}"
        )
        
        # Test get tourists with filters
        params = {"status": "safe", "limit": 10}
        success, data, status = await self.make_request("GET", "/tourists", params=params)
        self.log_test(
            "Get Tourists With Filters", 
            success and status == 200,
            f"Status: {status}, Filtered results: {len(data) if isinstance(data, list) else 'error'}"
        )
    
    async def test_location_services(self):
        """Test location tracking endpoints"""
        print("\n=== Testing Location Services ===")
        
        if not self.auth_token:
            self.log_test("Location Services", False, "No auth token available")
            return
        
        # Test get live locations
        success, data, status = await self.make_request("GET", "/location/live")
        self.log_test(
            "Get Live Locations", 
            success and status == 200,
            f"Status: {status}, Live locations: {len(data) if isinstance(data, list) else 'error'}"
        )
        
        # Get a real tourist ID for location update test
        success, tourists_data, status = await self.make_request("GET", "/tourists")
        if not success or not isinstance(tourists_data, list) or len(tourists_data) == 0:
            self.log_test("Update Location", False, "No tourists available for location update test")
            return
            
        tourist_id = tourists_data[0].get('id')
        if not tourist_id:
            self.log_test("Update Location", False, "No valid tourist ID found")
            return
        
        # Test location update (this endpoint doesn't require auth based on the code)
        location_update = {
            "tourist_id": tourist_id,  # Using actual tourist ObjectId
            "longitude": 88.2700,
            "latitude": 27.0400,
            "address": "Test Location, Darjeeling",
            "accuracy": 10.0,
            "speed": 0.0
        }
        
        # Remove auth token for this request as it's not required
        temp_token = self.auth_token
        self.auth_token = None
        success, data, status = await self.make_request("POST", "/location/update", location_update)
        self.auth_token = temp_token
        
        self.log_test(
            "Update Location", 
            success and status == 200,
            f"Status: {status}, Response: {data}"
        )
    
    async def test_alerts_system(self):
        """Test alerts management endpoints"""
        print("\n=== Testing Alerts System ===")
        
        if not self.auth_token:
            self.log_test("Alerts System", False, "No auth token available")
            return
        
        # Test get all alerts
        success, data, status = await self.make_request("GET", "/alerts")
        alerts_list = data if isinstance(data, list) else []
        
        self.log_test(
            "Get All Alerts", 
            success and status == 200,
            f"Status: {status}, Found {len(alerts_list)} alerts"
        )
        
        # Get a real tourist ID for panic alert test
        success, tourists_data, status = await self.make_request("GET", "/tourists")
        if not success or not isinstance(tourists_data, list) or len(tourists_data) == 0:
            self.log_test("Create Panic Alert", False, "No tourists available for panic alert test")
        else:
            tourist_id = tourists_data[0].get('id')
            if not tourist_id:
                self.log_test("Create Panic Alert", False, "No valid tourist ID found")
            else:
                # Test create panic alert (no auth required based on code)
                temp_token = self.auth_token
                self.auth_token = None
                
                # Create panic alert via query params as per the endpoint definition
                params = {
                    "tourist_id": tourist_id,  # Using actual tourist ObjectId
                    "longitude": 88.2700,
                    "latitude": 27.0400,
                    "address": "Emergency Location, Darjeeling"
                }
                
                success, data, status = await self.make_request("POST", "/alerts/panic", params=params)
                self.auth_token = temp_token
                
                alert_id = None
                if success and isinstance(data, dict) and 'alert_id' in data:
                    alert_id = data['alert_id']
                    
                self.log_test(
                    "Create Panic Alert", 
                    success and status == 200,
                    f"Status: {status}, Alert ID: {alert_id}"
                )
                
                # Test update alert status if we have an alert
                if alert_id:
                    status_update = {
                        "status": "in_progress",
                        "resolved_by": "Test Officer",
                        "resolution_notes": "Test resolution"
                    }
                    
                    success, data, status = await self.make_request("PUT", f"/alerts/{alert_id}/status", status_update)
                    self.log_test(
                        "Update Alert Status", 
                        success and status == 200,
                        f"Status: {status}, Response: {data}"
                    )
        
        # Test get alerts with filters
        params = {"severity": "high", "limit": 10}
        success, data, status = await self.make_request("GET", "/alerts", params=params)
        self.log_test(
            "Get Alerts With Filters", 
            success and status == 200,
            f"Status: {status}, Filtered alerts: {len(data) if isinstance(data, list) else 'error'}"
        )
    
    async def test_geofencing(self):
        """Test geofencing endpoints"""
        print("\n=== Testing Geofencing System ===")
        
        if not self.auth_token:
            self.log_test("Geofencing", False, "No auth token available")
            return
        
        # Test get all geofences
        success, data, status = await self.make_request("GET", "/geofences")
        geofences_list = data if isinstance(data, list) else []
        
        self.log_test(
            "Get All Geofences", 
            success and status == 200,
            f"Status: {status}, Found {len(geofences_list)} geofences"
        )
        
        # Test check point in geofences
        params = {
            "longitude": 88.2700,
            "latitude": 27.0400
        }
        
        success, data, status = await self.make_request("GET", "/geofences/check", params=params)
        self.log_test(
            "Check Point in Geofences", 
            success and status == 200,
            f"Status: {status}, Intersecting geofences: {len(data) if isinstance(data, list) else 'error'}"
        )
    
    async def test_analytics_dashboard(self):
        """Test analytics and dashboard endpoints"""
        print("\n=== Testing Analytics Dashboard ===")
        
        if not self.auth_token:
            self.log_test("Analytics Dashboard", False, "No auth token available")
            return
        
        # Test dashboard KPIs
        success, data, status = await self.make_request("GET", "/analytics/dashboard")
        self.log_test(
            "Get Dashboard KPIs", 
            success and status == 200,
            f"Status: {status}, Active tourists: {data.get('total_active_tourists', 'unknown') if isinstance(data, dict) else 'error'}"
        )
        
        # Test safety score for a tourist
        tourist_id = "DIG-12AB34CD"  # Using sample tourist ID
        success, data, status = await self.make_request("GET", f"/analytics/safety-score/{tourist_id}")
        self.log_test(
            "Get Safety Score", 
            success and status == 200,
            f"Status: {status}, Safety score: {data.get('safety_score', 'unknown') if isinstance(data, dict) else 'error'}"
        )
        
        # Test location analytics
        params = {"hours": 24}
        success, data, status = await self.make_request("GET", "/analytics/location", params=params)
        self.log_test(
            "Get Location Analytics", 
            success and status == 200,
            f"Status: {status}, Analytics data available: {isinstance(data, dict)}"
        )
        
        # Test alert analytics
        params = {"days": 7}
        success, data, status = await self.make_request("GET", "/analytics/alerts", params=params)
        self.log_test(
            "Get Alert Analytics", 
            success and status == 200,
            f"Status: {status}, Analytics data available: {isinstance(data, dict)}"
        )
    
    async def run_all_tests(self):
        """Run all test suites"""
        print(f"🚀 Starting Tourism Safety API Tests")
        print(f"📍 Backend URL: {API_BASE_URL}")
        print("=" * 60)
        
        # Run test suites in order
        await self.test_health_endpoints()
        await self.test_authentication()
        await self.test_tourist_management()
        await self.test_location_services()
        await self.test_alerts_system()
        await self.test_geofencing()
        await self.test_analytics_dashboard()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n🔍 FAILED TESTS:")
            for test_name, result in self.test_results.items():
                if not result['success']:
                    print(f"  ❌ {test_name}: {result['details']}")
        
        return self.test_results

async def main():
    """Main test runner"""
    async with TourismSafetyAPITester() as tester:
        results = await tester.run_all_tests()
        
        # Save results to file
        with open('/app/test_results_backend.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Test results saved to: /app/test_results_backend.json")
        
        return results

if __name__ == "__main__":
    asyncio.run(main())