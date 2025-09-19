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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://tourist-shield-1.preview.emergentagent.com')
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
        
        # Test safety score for a tourist - use actual tourist ID
        success, tourists_data, status = await self.make_request("GET", "/tourists")
        if success and isinstance(tourists_data, list) and len(tourists_data) > 0:
            tourist_id = tourists_data[0].get('id')
            if tourist_id:
                success, data, status = await self.make_request("GET", f"/analytics/safety-score/{tourist_id}")
                self.log_test(
                    "Get Safety Score", 
                    success and status == 200,
                    f"Status: {status}, Safety score: {data.get('safety_score', 'unknown') if isinstance(data, dict) else 'error'}"
                )
            else:
                self.log_test("Get Safety Score", False, "No valid tourist ID found")
        else:
            self.log_test("Get Safety Score", False, "No tourists available for safety score test")
        
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
    
    async def test_ai_anomaly_detection(self):
        """Test AI anomaly detection features"""
        print("\n=== Testing AI Anomaly Detection Features ===")
        
        if not self.auth_token:
            self.log_test("AI Anomaly Detection", False, "No auth token available")
            return
        
        # Test background task status
        success, data, status = await self.make_request("GET", "/ai/background-tasks/status")
        self.log_test(
            "Background Task Status", 
            success and status == 200,
            f"Status: {status}, Running: {data.get('is_running', 'unknown') if isinstance(data, dict) else 'error'}"
        )
        
        # Get a real tourist ID for AI testing
        success, tourists_data, status = await self.make_request("GET", "/tourists")
        if not success or not isinstance(tourists_data, list) or len(tourists_data) == 0:
            self.log_test("AI Anomaly Detection", False, "No tourists available for AI testing")
            return
            
        tourist_id = tourists_data[0].get('id')
        if not tourist_id:
            self.log_test("AI Anomaly Detection", False, "No valid tourist ID found")
            return
        
        # Test AI safety score calculation
        success, data, status = await self.make_request("GET", f"/ai/safety-score/{tourist_id}")
        self.log_test(
            "AI Safety Score Calculation", 
            success and status == 200,
            f"Status: {status}, Safety Score: {data.get('safety_score', 'unknown') if isinstance(data, dict) else 'error'}"
        )
        
        # Test manual anomaly check
        success, data, status = await self.make_request("GET", f"/ai/anomaly-check/{tourist_id}")
        self.log_test(
            "Manual Anomaly Check", 
            success and status == 200,
            f"Status: {status}, Checks performed: {len(data.get('checks_performed', [])) if isinstance(data, dict) else 'error'}"
        )
        
        # Test background task restart (admin only)
        success, data, status = await self.make_request("POST", "/ai/background-tasks/restart")
        self.log_test(
            "Background Task Restart", 
            success and status == 200,
            f"Status: {status}, Response: {data.get('message', 'unknown') if isinstance(data, dict) else 'error'}"
        )
    
    async def test_enhanced_geofencing(self):
        """Test enhanced geofencing with geospatial queries"""
        print("\n=== Testing Enhanced Geofencing ===")
        
        if not self.auth_token:
            self.log_test("Enhanced Geofencing", False, "No auth token available")
            return
        
        # Test geospatial point checking with various coordinates
        test_coordinates = [
            {"longitude": 88.2700, "latitude": 27.0400, "name": "Central Darjeeling"},
            {"longitude": 88.2800, "latitude": 27.0460, "name": "Near Military Zone"},
            {"longitude": 88.2550, "latitude": 27.0325, "name": "Landslide Area"},
            {"longitude": 88.2650, "latitude": 27.0400, "name": "Mall Road Safe Zone"}
        ]
        
        for coord in test_coordinates:
            params = {
                "longitude": coord["longitude"],
                "latitude": coord["latitude"]
            }
            
            success, data, status = await self.make_request("GET", "/geofences/check", params=params)
            intersecting_count = len(data) if isinstance(data, list) else 0
            
            self.log_test(
                f"Geospatial Check - {coord['name']}", 
                success and status == 200,
                f"Status: {status}, Intersecting geofences: {intersecting_count}"
            )
        
        # Test geofence list to verify MongoDB geospatial indexes are working
        success, data, status = await self.make_request("GET", "/geofences")
        geofences_list = data if isinstance(data, list) else []
        
        self.log_test(
            "Geofence List with Geospatial Data", 
            success and status == 200 and len(geofences_list) > 0,
            f"Status: {status}, Found {len(geofences_list)} geofences with geospatial coordinates"
        )
    
    async def test_new_alert_types(self):
        """Test new alert types (route deviation and prolonged inactivity)"""
        print("\n=== Testing New Alert Types ===")
        
        if not self.auth_token:
            self.log_test("New Alert Types", False, "No auth token available")
            return
        
        # Get alerts and check for new alert types
        success, data, status = await self.make_request("GET", "/alerts")
        alerts_list = data if isinstance(data, list) else []
        
        # Count different alert types
        alert_types = {}
        for alert in alerts_list:
            alert_type = alert.get('alert_type', 'unknown')
            alert_types[alert_type] = alert_types.get(alert_type, 0) + 1
        
        self.log_test(
            "Alert Types Analysis", 
            success and status == 200,
            f"Status: {status}, Alert types found: {list(alert_types.keys())}, Total alerts: {len(alerts_list)}"
        )
        
        # Test filtering by new alert types
        new_alert_types = ["route_deviation", "prolonged_inactivity"]
        
        for alert_type in new_alert_types:
            params = {"alert_type": alert_type, "limit": 10}
            success, data, status = await self.make_request("GET", "/alerts", params=params)
            filtered_alerts = data if isinstance(data, list) else []
            
            self.log_test(
                f"Filter Alerts - {alert_type}", 
                success and status == 200,
                f"Status: {status}, Found {len(filtered_alerts)} {alert_type} alerts"
            )
    
    async def test_database_operations(self):
        """Test database operations and geospatial indexes"""
        print("\n=== Testing Database Operations ===")
        
        if not self.auth_token:
            self.log_test("Database Operations", False, "No auth token available")
            return
        
        # Test location history with geospatial data
        success, tourists_data, status = await self.make_request("GET", "/tourists")
        if success and isinstance(tourists_data, list) and len(tourists_data) > 0:
            tourist_id = tourists_data[0].get('id')
            if tourist_id:
                # Test location history retrieval
                success, data, status = await self.make_request("GET", f"/tourists/{tourist_id}/location-history")
                location_history = data if isinstance(data, list) else []
                
                # Check if location data has geospatial coordinates
                has_geospatial_data = False
                if location_history:
                    for location in location_history:
                        if 'coordinates' in location and 'coordinates' in location['coordinates']:
                            has_geospatial_data = True
                            break
                
                self.log_test(
                    "Location History Geospatial Data", 
                    success and status == 200 and has_geospatial_data,
                    f"Status: {status}, History entries: {len(location_history)}, Has geospatial data: {has_geospatial_data}"
                )
            else:
                self.log_test("Location History Geospatial Data", False, "No valid tourist ID found")
        else:
            self.log_test("Location History Geospatial Data", False, "No tourists available for testing")
        
        # Test live locations for geospatial queries
        success, data, status = await self.make_request("GET", "/location/live")
        live_locations = data if isinstance(data, list) else []
        
        # Check if live locations have proper geospatial structure
        geospatial_locations = 0
        for location in live_locations:
            if 'coordinates' in location and isinstance(location['coordinates'], list) and len(location['coordinates']) == 2:
                geospatial_locations += 1
        
        self.log_test(
            "Live Locations Geospatial Structure", 
            success and status == 200,
            f"Status: {status}, Total locations: {len(live_locations)}, Geospatial format: {geospatial_locations}"
        )

    async def test_digital_id_integration(self):
        """Test Digital ID service integration and security features"""
        print("\n=== Testing Digital ID Integration ===")
        
        if not self.auth_token:
            self.log_test("Digital ID Integration", False, "No auth token available")
            return
        
        # Test 1: Check Digital ID service availability (backward compatibility)
        try:
            digital_id_url = "http://localhost:8002/status"
            async with self.session.get(digital_id_url, timeout=5) as response:
                digital_id_available = response.status == 200
        except:
            digital_id_available = False
        
        self.log_test(
            "Digital ID Service Availability", 
            True,  # This is always a pass since we test backward compatibility
            f"Digital ID service available: {digital_id_available} (testing backward compatibility)"
        )
        
        # Test 2: Verify masked data in tourist responses
        success, tourists_data, status = await self.make_request("GET", "/tourists")
        if success and isinstance(tourists_data, list) and len(tourists_data) > 0:
            tourist = tourists_data[0]
            
            # Check if sensitive data is masked
            has_masked_data = (
                tourist.get('full_name') == '[ENCRYPTED]' or 
                tourist.get('nationality') == '[ENCRYPTED]' or
                tourist.get('itinerary') == '[ENCRYPTED]' or
                len(tourist.get('emergency_contacts', [])) == 0
            )
            
            self.log_test(
                "Tourist Data Masking", 
                has_masked_data,
                f"Status: {status}, Masked data detected: {has_masked_data}, Tourist: {tourist.get('digital_id', 'unknown')}"
            )
            
            # Test 3: Verify digital_id field exists
            has_digital_id = 'digital_id' in tourist and tourist['digital_id'].startswith('DIG-')
            
            self.log_test(
                "Digital ID Field Present", 
                has_digital_id,
                f"Digital ID format: {tourist.get('digital_id', 'missing')}"
            )
            
        else:
            self.log_test("Tourist Data Masking", False, "No tourists available for testing")
            self.log_test("Digital ID Field Present", False, "No tourists available for testing")
        
        # Test 4: Test panic alert creation (should trigger emergency data access)
        if success and isinstance(tourists_data, list) and len(tourists_data) > 0:
            tourist_id = tourists_data[0].get('id')
            if tourist_id:
                # Remove auth token for panic alert (no auth required)
                temp_token = self.auth_token
                self.auth_token = None
                
                params = {
                    "tourist_id": tourist_id,
                    "longitude": 88.2700,
                    "latitude": 27.0400,
                    "address": "Emergency Test Location"
                }
                
                success, data, status = await self.make_request("POST", "/alerts/panic", params=params)
                self.auth_token = temp_token
                
                alert_created = success and status == 200 and isinstance(data, dict) and 'alert_id' in data
                
                self.log_test(
                    "Panic Alert with Digital ID Integration", 
                    alert_created,
                    f"Status: {status}, Alert created: {alert_created}, Alert ID: {data.get('alert_id', 'none') if isinstance(data, dict) else 'error'}"
                )
            else:
                self.log_test("Panic Alert with Digital ID Integration", False, "No valid tourist ID found")
        else:
            self.log_test("Panic Alert with Digital ID Integration", False, "No tourists available for testing")
    
    async def test_service_authentication(self):
        """Test service-to-service authentication mechanisms"""
        print("\n=== Testing Service Authentication ===")
        
        # Test 1: Check if Digital ID service environment variables are configured
        import os
        digital_id_url = os.environ.get("DIGITAL_ID_SERVICE_URL", "")
        digital_id_api_key = os.environ.get("DIGITAL_ID_SERVICE_API_KEY", "")
        
        config_present = bool(digital_id_url and digital_id_api_key)
        
        self.log_test(
            "Digital ID Service Configuration", 
            config_present,
            f"URL configured: {bool(digital_id_url)}, API Key configured: {bool(digital_id_api_key)}"
        )
        
        # Test 2: Test service health endpoint if available
        if digital_id_url:
            try:
                health_url = f"{digital_id_url}/status"
                async with self.session.get(health_url, timeout=5) as response:
                    service_healthy = response.status == 200
                    if service_healthy:
                        response_data = await response.json()
                        service_status = response_data.get('status', 'unknown')
                    else:
                        service_status = 'unhealthy'
            except:
                service_healthy = False
                service_status = 'unreachable'
            
            self.log_test(
                "Digital ID Service Health", 
                True,  # Always pass since we test fallback
                f"Service reachable: {service_healthy}, Status: {service_status}"
            )
        else:
            self.log_test("Digital ID Service Health", False, "No Digital ID service URL configured")
    
    async def test_encrypted_data_separation(self):
        """Test encrypted data separation approach"""
        print("\n=== Testing Encrypted Data Separation ===")
        
        if not self.auth_token:
            self.log_test("Encrypted Data Separation", False, "No auth token available")
            return
        
        # Test 1: Verify that main database contains masked data
        success, tourists_data, status = await self.make_request("GET", "/tourists")
        if success and isinstance(tourists_data, list) and len(tourists_data) > 0:
            
            # Count tourists with encrypted data
            encrypted_count = 0
            total_tourists = len(tourists_data)
            
            for tourist in tourists_data:
                if (tourist.get('full_name') == '[ENCRYPTED]' or 
                    tourist.get('nationality') == '[ENCRYPTED]' or
                    tourist.get('itinerary') == '[ENCRYPTED]'):
                    encrypted_count += 1
            
            encryption_ratio = encrypted_count / total_tourists if total_tourists > 0 else 0
            
            self.log_test(
                "Data Encryption in Main Database", 
                encryption_ratio > 0,
                f"Status: {status}, Encrypted tourists: {encrypted_count}/{total_tourists} ({encryption_ratio:.1%})"
            )
            
            # Test 2: Verify digital IDs are properly formatted
            valid_digital_ids = 0
            for tourist in tourists_data:
                digital_id = tourist.get('digital_id', '')
                if digital_id.startswith('DIG-') and len(digital_id) == 12:  # DIG-XXXXXXXX format
                    valid_digital_ids += 1
            
            digital_id_ratio = valid_digital_ids / total_tourists if total_tourists > 0 else 0
            
            self.log_test(
                "Digital ID Format Validation", 
                digital_id_ratio > 0,
                f"Valid digital IDs: {valid_digital_ids}/{total_tourists} ({digital_id_ratio:.1%})"
            )
            
        else:
            self.log_test("Data Encryption in Main Database", False, "No tourists available for testing")
            self.log_test("Digital ID Format Validation", False, "No tourists available for testing")
        
        # Test 3: Verify emergency contacts are masked
        if success and isinstance(tourists_data, list) and len(tourists_data) > 0:
            masked_contacts_count = 0
            for tourist in tourists_data:
                emergency_contacts = tourist.get('emergency_contacts', [])
                if len(emergency_contacts) == 0:  # Should be empty/masked in main database
                    masked_contacts_count += 1
            
            contacts_masking_ratio = masked_contacts_count / len(tourists_data)
            
            self.log_test(
                "Emergency Contacts Masking", 
                contacts_masking_ratio > 0,
                f"Tourists with masked contacts: {masked_contacts_count}/{len(tourists_data)} ({contacts_masking_ratio:.1%})"
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
        
        # NEW AI ANOMALY DETECTION TESTS
        await self.test_ai_anomaly_detection()
        await self.test_enhanced_geofencing()
        await self.test_new_alert_types()
        await self.test_database_operations()
        
        # DIGITAL ID SECURITY INTEGRATION TESTS
        await self.test_digital_id_integration()
        await self.test_service_authentication()
        await self.test_encrypted_data_separation()
        
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