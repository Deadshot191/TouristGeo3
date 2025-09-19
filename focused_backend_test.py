#!/usr/bin/env python3
"""
Focused Backend API Testing for Tourism Safety System
Tests specific endpoints as requested:
1. GET /api/tourists/{tourist_id}/alerts - New tourist alerts endpoint
2. GET /api/tourists/{tourist_id} - Existing tourist detail endpoint  
3. GET /api/analytics/dashboard - Dashboard KPIs endpoint
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://demo-ready-check.preview.emergentagent.com')
API_BASE_URL = f"{BACKEND_URL}/api"

class FocusedAPITester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = {}
        self.tourist_ids = []
        
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
        """Authenticate and get access token"""
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
                f"Successfully logged in as {data.get('user', {}).get('full_name', 'Unknown')}"
            )
            return True
        else:
            self.log_test(
                "Authentication", 
                False,
                f"Status: {status}, Response: {data}"
            )
            return False
    
    async def get_tourist_ids(self):
        """Get existing tourist IDs from database for testing"""
        print("\n=== Getting Tourist IDs ===")
        
        success, data, status = await self.make_request("GET", "/tourists")
        
        if success and status == 200 and isinstance(data, list):
            self.tourist_ids = [tourist.get('id') for tourist in data if tourist.get('id')]
            self.log_test(
                "Get Tourist IDs", 
                len(self.tourist_ids) > 0,
                f"Found {len(self.tourist_ids)} tourists in database"
            )
            return len(self.tourist_ids) > 0
        else:
            self.log_test(
                "Get Tourist IDs", 
                False,
                f"Status: {status}, Response: {data}"
            )
            return False
    
    async def test_tourist_alerts_endpoint(self):
        """Test GET /api/tourists/{tourist_id}/alerts endpoint"""
        print("\n=== Testing Tourist Alerts Endpoint ===")
        
        if not self.tourist_ids:
            self.log_test("Tourist Alerts Endpoint", False, "No tourist IDs available for testing")
            return
        
        # Test with multiple tourist IDs
        for i, tourist_id in enumerate(self.tourist_ids[:3]):  # Test first 3 tourists
            success, data, status = await self.make_request("GET", f"/tourists/{tourist_id}/alerts")
            
            if success and status == 200:
                alerts = data if isinstance(data, list) else []
                
                # Validate alert format
                valid_format = True
                format_details = []
                
                for alert in alerts:
                    if not isinstance(alert, dict):
                        valid_format = False
                        format_details.append("Alert is not a dictionary")
                        continue
                    
                    required_fields = ['id', 'alert_id', 'tourist_id', 'alert_type', 'severity', 'status', 'location', 'created_at']
                    missing_fields = [field for field in required_fields if field not in alert]
                    
                    if missing_fields:
                        valid_format = False
                        format_details.append(f"Missing fields: {missing_fields}")
                    
                    # Check location format
                    if 'location' in alert and isinstance(alert['location'], dict):
                        if 'coordinates' not in alert['location']:
                            valid_format = False
                            format_details.append("Location missing coordinates")
                
                self.log_test(
                    f"Tourist Alerts - Tourist {i+1} (ID: {tourist_id[:8]}...)", 
                    success and valid_format,
                    f"Status: {status}, Alerts count: {len(alerts)}, Format valid: {valid_format}" + 
                    (f", Issues: {'; '.join(format_details)}" if format_details else "")
                )
            else:
                self.log_test(
                    f"Tourist Alerts - Tourist {i+1} (ID: {tourist_id[:8]}...)", 
                    False,
                    f"Status: {status}, Response: {data}"
                )
        
        # Test with invalid tourist ID
        invalid_id = "507f1f77bcf86cd799439011"  # Valid ObjectId format but non-existent
        success, data, status = await self.make_request("GET", f"/tourists/{invalid_id}/alerts")
        
        self.log_test(
            "Tourist Alerts - Invalid ID", 
            success and status == 200 and isinstance(data, list) and len(data) == 0,
            f"Status: {status}, Response: {data}, Expected empty list for invalid ID"
        )
        
        # Test with malformed tourist ID
        malformed_id = "invalid_id_format"
        success, data, status = await self.make_request("GET", f"/tourists/{malformed_id}/alerts")
        
        self.log_test(
            "Tourist Alerts - Malformed ID", 
            not success or status >= 400,
            f"Status: {status}, Expected error for malformed ID"
        )
    
    async def test_tourist_detail_endpoint(self):
        """Test GET /api/tourists/{tourist_id} endpoint"""
        print("\n=== Testing Tourist Detail Endpoint ===")
        
        if not self.tourist_ids:
            self.log_test("Tourist Detail Endpoint", False, "No tourist IDs available for testing")
            return
        
        # Test with multiple tourist IDs
        for i, tourist_id in enumerate(self.tourist_ids[:3]):  # Test first 3 tourists
            success, data, status = await self.make_request("GET", f"/tourists/{tourist_id}")
            
            if success and status == 200 and isinstance(data, dict):
                # Check required fields
                required_fields = [
                    'id', 'digital_id', 'full_name', 'nationality', 
                    'visit_start_date', 'visit_end_date', 'emergency_contacts', 
                    'status', 'safety_score'
                ]
                
                missing_fields = [field for field in required_fields if field not in data]
                present_fields = [field for field in required_fields if field in data]
                
                # Check data types and formats
                format_issues = []
                
                if 'digital_id' in data and not (isinstance(data['digital_id'], str) and data['digital_id'].startswith('DIG-')):
                    format_issues.append("digital_id format invalid")
                
                if 'emergency_contacts' in data and not isinstance(data['emergency_contacts'], list):
                    format_issues.append("emergency_contacts not a list")
                
                if 'safety_score' in data and not isinstance(data['safety_score'], (int, float)):
                    format_issues.append("safety_score not numeric")
                
                # Check if location data is included
                has_location = 'location' in data and data['location'] is not None
                
                self.log_test(
                    f"Tourist Detail - Tourist {i+1} (ID: {tourist_id[:8]}...)", 
                    success and len(missing_fields) == 0 and len(format_issues) == 0,
                    f"Status: {status}, Present fields: {len(present_fields)}/{len(required_fields)}, " +
                    f"Missing: {missing_fields}, Format issues: {format_issues}, Has location: {has_location}"
                )
            else:
                self.log_test(
                    f"Tourist Detail - Tourist {i+1} (ID: {tourist_id[:8]}...)", 
                    False,
                    f"Status: {status}, Response type: {type(data)}, Success: {success}"
                )
        
        # Test with invalid tourist ID
        invalid_id = "507f1f77bcf86cd799439011"  # Valid ObjectId format but non-existent
        success, data, status = await self.make_request("GET", f"/tourists/{invalid_id}")
        
        self.log_test(
            "Tourist Detail - Invalid ID", 
            not success and status == 404,
            f"Status: {status}, Expected 404 for non-existent tourist"
        )
    
    async def test_dashboard_kpis_endpoint(self):
        """Test GET /api/analytics/dashboard endpoint"""
        print("\n=== Testing Dashboard KPIs Endpoint ===")
        
        success, data, status = await self.make_request("GET", "/analytics/dashboard")
        
        if success and status == 200 and isinstance(data, dict):
            # Check required KPI fields (based on actual API response)
            expected_kpis = [
                'total_active_tourists', 'active_alerts', 'safe_status', 
                'high_risk_tourists', 'resolved_alerts_today', 'avg_safety_score'
            ]
            
            present_kpis = [kpi for kpi in expected_kpis if kpi in data]
            missing_kpis = [kpi for kpi in expected_kpis if kpi not in data]
            
            # Validate data types
            type_issues = []
            for kpi in present_kpis:
                if not isinstance(data[kpi], (int, float)):
                    type_issues.append(f"{kpi} is not numeric")
            
            # Check for reasonable values
            value_issues = []
            if 'total_active_tourists' in data and data['total_active_tourists'] < 0:
                value_issues.append("total_active_tourists is negative")
            
            if 'active_alerts' in data and data['active_alerts'] < 0:
                value_issues.append("active_alerts is negative")
            
            if 'avg_safety_score' in data and not (0 <= data['avg_safety_score'] <= 100):
                value_issues.append("avg_safety_score not in 0-100 range")
            
            # Check consistency
            consistency_issues = []
            if ('active_alerts' in data and 'resolved_alerts' in data and 
                'total_active_tourists' in data):
                total_alerts = data['active_alerts'] + data['resolved_alerts']
                if total_alerts > data['total_active_tourists'] * 10:  # Reasonable ratio
                    consistency_issues.append("Alert to tourist ratio seems high")
            
            all_issues = type_issues + value_issues + consistency_issues
            
            self.log_test(
                "Dashboard KPIs", 
                len(missing_kpis) == 0 and len(all_issues) == 0,
                f"Status: {status}, Present KPIs: {len(present_kpis)}/{len(expected_kpis)}, " +
                f"Missing: {missing_kpis}, Issues: {all_issues}"
            )
            
            # Log actual values for verification
            kpi_values = {kpi: data.get(kpi, 'missing') for kpi in expected_kpis}
            print(f"   📊 KPI Values: {kpi_values}")
            
        else:
            self.log_test(
                "Dashboard KPIs", 
                False,
                f"Status: {status}, Response type: {type(data)}, Success: {success}"
            )
        
        # Test consistency by comparing with other endpoints
        await self.test_dashboard_consistency()
    
    async def test_dashboard_consistency(self):
        """Test dashboard KPIs consistency with other endpoints"""
        print("\n=== Testing Dashboard Consistency ===")
        
        # Get dashboard KPIs
        success_dash, dash_data, status_dash = await self.make_request("GET", "/analytics/dashboard")
        
        # Get tourists count
        success_tourists, tourists_data, status_tourists = await self.make_request("GET", "/tourists")
        
        # Get alerts count
        success_alerts, alerts_data, status_alerts = await self.make_request("GET", "/alerts")
        
        if (success_dash and success_tourists and success_alerts and 
            isinstance(dash_data, dict) and isinstance(tourists_data, list) and isinstance(alerts_data, list)):
            
            # Compare counts
            dashboard_tourists = dash_data.get('total_active_tourists', 0)
            actual_tourists = len(tourists_data)
            
            dashboard_alerts = dash_data.get('active_alerts', 0) + dash_data.get('resolved_alerts', 0)
            actual_alerts = len(alerts_data)
            
            # Allow some tolerance for active vs total counts
            tourist_consistency = abs(dashboard_tourists - actual_tourists) <= actual_tourists * 0.2
            alert_consistency = abs(dashboard_alerts - actual_alerts) <= max(actual_alerts * 0.2, 5)
            
            self.log_test(
                "Dashboard Consistency", 
                tourist_consistency and alert_consistency,
                f"Dashboard tourists: {dashboard_tourists}, Actual: {actual_tourists}, " +
                f"Dashboard alerts: {dashboard_alerts}, Actual: {actual_alerts}"
            )
        else:
            self.log_test(
                "Dashboard Consistency", 
                False,
                f"Failed to get data for consistency check. Dashboard: {success_dash}, " +
                f"Tourists: {success_tourists}, Alerts: {success_alerts}"
            )
    
    async def test_data_format_consistency(self):
        """Test data format consistency across endpoints"""
        print("\n=== Testing Data Format Consistency ===")
        
        if not self.tourist_ids:
            self.log_test("Data Format Consistency", False, "No tourist IDs available")
            return
        
        tourist_id = self.tourist_ids[0]
        
        # Get tourist details
        success_detail, detail_data, status_detail = await self.make_request("GET", f"/tourists/{tourist_id}")
        
        # Get tourist alerts
        success_alerts, alerts_data, status_alerts = await self.make_request("GET", f"/tourists/{tourist_id}/alerts")
        
        if (success_detail and success_alerts and 
            isinstance(detail_data, dict) and isinstance(alerts_data, list)):
            
            # Check tourist_id consistency in alerts
            id_consistency = True
            for alert in alerts_data:
                if alert.get('tourist_id') != tourist_id:
                    id_consistency = False
                    break
            
            # Check if tourist name in alerts matches detail
            tourist_name = detail_data.get('full_name', '')
            name_consistency = True
            
            for alert in alerts_data:
                alert_tourist_name = alert.get('tourist_name', '')
                if tourist_name != '[ENCRYPTED]' and alert_tourist_name != tourist_name:
                    name_consistency = False
                    break
            
            self.log_test(
                "Data Format Consistency", 
                id_consistency and name_consistency,
                f"Tourist ID consistency: {id_consistency}, Name consistency: {name_consistency}, " +
                f"Tourist name: {tourist_name}, Alerts count: {len(alerts_data)}"
            )
        else:
            self.log_test(
                "Data Format Consistency", 
                False,
                f"Failed to get data. Detail: {success_detail}, Alerts: {success_alerts}"
            )
    
    async def run_focused_tests(self):
        """Run all focused tests"""
        print(f"🎯 Starting Focused Tourism Safety API Tests")
        print(f"📍 Backend URL: {API_BASE_URL}")
        print("=" * 60)
        
        # Authenticate first
        if not await self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return self.test_results
        
        # Get tourist IDs
        if not await self.get_tourist_ids():
            print("❌ Failed to get tourist IDs. Cannot proceed with tourist-specific tests.")
        
        # Run focused tests
        await self.test_tourist_alerts_endpoint()
        await self.test_tourist_detail_endpoint()
        await self.test_dashboard_kpis_endpoint()
        await self.test_data_format_consistency()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 FOCUSED TEST SUMMARY")
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
    async with FocusedAPITester() as tester:
        results = await tester.run_focused_tests()
        
        # Save results to file
        with open('/app/focused_test_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Focused test results saved to: /app/focused_test_results.json")
        
        return results

if __name__ == "__main__":
    asyncio.run(main())