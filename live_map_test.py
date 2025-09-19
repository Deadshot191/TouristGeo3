#!/usr/bin/env python3
"""
Live Map Data Integration Test for Tourism Safety System
Tests the specific endpoints and data structures required for Live Map functionality
after demo data population.

Focus Areas:
1. Authentication with demo user credentials (inspector.kumar@tourism.gov.in / password123)
2. Core Live Map endpoints data verification
3. Data structure validation for frontend integration
4. Individual tourist data testing
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://realtime-tourist.preview.emergentagent.com')
API_BASE_URL = f"{BACKEND_URL}/api"

class LiveMapDataTester:
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
        """Authenticate to get access token"""
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
    
    async def test_database_data_existence(self):
        """Test what data exists in the database"""
        print("\n=== Database Data Existence Check ===")
        
        if not self.auth_token:
            self.log_test("Database Check", False, "No auth token available")
            return
        
        # 1. Check if we have any tourists in the database
        success, data, status = await self.make_request("GET", "/tourists")
        tourists_list = data if isinstance(data, list) else []
        
        self.log_test(
            "Tourists in Database", 
            success and status == 200 and len(tourists_list) > 0,
            f"Status: {status}, Found {len(tourists_list)} tourists",
            tourists_list[:2] if tourists_list else None  # Show first 2 tourists
        )
        
        if not tourists_list:
            print("❌ CRITICAL: No tourists found in database - this explains why Live Map is empty!")
            return
        
        # 2. Check tourist data structure
        sample_tourist = tourists_list[0]
        required_fields = ['id', 'digital_id', 'full_name', 'status']
        missing_fields = [field for field in required_fields if field not in sample_tourist]
        
        self.log_test(
            "Tourist Data Structure", 
            len(missing_fields) == 0,
            f"Required fields present: {len(required_fields) - len(missing_fields)}/{len(required_fields)}, Missing: {missing_fields}",
            sample_tourist
        )
        
        # 3. Check if tourists have location data
        tourists_with_location = 0
        for tourist in tourists_list:
            if 'location' in tourist and tourist['location'] is not None:
                tourists_with_location += 1
        
        self.log_test(
            "Tourists with Location Data", 
            tourists_with_location > 0,
            f"Tourists with location: {tourists_with_location}/{len(tourists_list)}",
            [t for t in tourists_list if t.get('location')][:2]  # Show first 2 with location
        )
        
        # 4. Check location history for tourists
        if tourists_list:
            tourist_id = tourists_list[0]['id']
            success, location_history, status = await self.make_request("GET", f"/tourists/{tourist_id}/location-history")
            
            self.log_test(
                "Location History Data", 
                success and status == 200 and isinstance(location_history, list),
                f"Status: {status}, Location history entries: {len(location_history) if isinstance(location_history, list) else 0}",
                location_history[:2] if isinstance(location_history, list) else None
            )
    
    async def test_live_locations_endpoint(self):
        """Test GET /api/location/live endpoint - should return 5 tourists with locations"""
        print("\n=== Live Locations Endpoint Test ===")
        
        if not self.auth_token:
            self.log_test("Live Locations Endpoint", False, "No auth token available")
            return []
        
        success, data, status = await self.make_request("GET", "/location/live")
        live_locations = data if isinstance(data, list) else []
        
        expected_count = 5  # As mentioned in review request
        
        self.log_test(
            "GET /api/location/live", 
            success and status == 200,
            f"Status: {status}, Live locations returned: {len(live_locations)} (expected: {expected_count})",
            live_locations[:2] if live_locations else None
        )
        
        if not live_locations:
            print("❌ CRITICAL: No live locations returned - this is why Live Map shows no markers!")
            return []
        
        # Check data structure matches frontend requirements
        # Frontend expects: tourist_id, tourist_name, digital_id, status, coordinates (array), address, timestamp
        required_fields = ['tourist_id', 'tourist_name', 'digital_id', 'status', 'coordinates', 'address', 'timestamp']
        
        valid_tourists = []
        structure_issues = []
        
        for i, location in enumerate(live_locations):
            missing_fields = [field for field in required_fields if field not in location]
            if missing_fields:
                structure_issues.append(f"Tourist {i+1} missing: {missing_fields}")
                continue
            
            # Validate coordinates format (must be array)
            coords = location.get('coordinates')
            if not isinstance(coords, list) or len(coords) != 2:
                structure_issues.append(f"Tourist {i+1} invalid coordinates format: {coords}")
                continue
            
            # Validate coordinates are numeric and in valid range
            try:
                lon, lat = float(coords[0]), float(coords[1])
                if not (-180 <= lon <= 180) or not (-90 <= lat <= 90):
                    structure_issues.append(f"Tourist {i+1} coordinates out of range: [{lon}, {lat}]")
                    continue
            except (ValueError, TypeError):
                structure_issues.append(f"Tourist {i+1} non-numeric coordinates: {coords}")
                continue
            
            valid_tourists.append(location)
        
        self.log_test(
            "Live Location Data Structure", 
            len(structure_issues) == 0,
            f"Valid tourists: {len(valid_tourists)}/{len(live_locations)}, Issues: {structure_issues[:3]}{'...' if len(structure_issues) > 3 else ''}",
            live_locations[0] if live_locations else None
        )
        
        # Log sample data for verification
        if live_locations:
            sample = live_locations[0]
            print(f"   📍 Sample Tourist: {sample.get('tourist_name', 'Unknown')} " +
                  f"({sample.get('digital_id', 'No ID')}) at {sample.get('coordinates', 'No coords')} - {sample.get('status', 'No status')}")
        
        return valid_tourists
    
    async def test_dashboard_kpis_endpoint(self):
        """Test GET /api/analytics/dashboard endpoint - should return KPIs with proper counts"""
        print("\n=== Dashboard KPIs Endpoint Test ===")
        
        if not self.auth_token:
            self.log_test("Dashboard KPIs Endpoint", False, "No auth token available")
            return {}
        
        success, data, status = await self.make_request("GET", "/analytics/dashboard")
        
        self.log_test(
            "GET /api/analytics/dashboard", 
            success and status == 200,
            f"Status: {status}, KPIs data available: {isinstance(data, dict)}",
            data
        )
        
        if success and isinstance(data, dict):
            # Check required KPI fields as mentioned in review request
            required_kpis = ['total_active_tourists', 'active_alerts', 'safe_status', 'high_risk_tourists']
            present_kpis = [kpi for kpi in required_kpis if kpi in data]
            missing_kpis = [kpi for kpi in required_kpis if kpi not in data]
            
            # Validate data types and reasonable values
            validation_issues = []
            for kpi in present_kpis:
                value = data[kpi]
                if not isinstance(value, (int, float)):
                    validation_issues.append(f"{kpi} is not numeric: {type(value)}")
                elif value < 0:
                    validation_issues.append(f"{kpi} is negative: {value}")
            
            # Check if all values are zero (indicates empty database)
            all_zero = all(data.get(kpi, 0) == 0 for kpi in required_kpis)
            if all_zero:
                validation_issues.append("All KPI values are zero - may indicate empty database")
            
            self.log_test(
                "Dashboard KPIs Structure", 
                len(missing_kpis) == 0 and len(validation_issues) == 0,
                f"Present KPIs: {len(present_kpis)}/{len(required_kpis)}, Missing: {missing_kpis}, Issues: {validation_issues}",
                {k: v for k, v in data.items() if k in required_kpis}
            )
            
            # Log actual KPI values for verification
            kpi_values = {kpi: data.get(kpi, 'missing') for kpi in required_kpis}
            print(f"   📊 KPI Values: {kpi_values}")
            
            return data
        
        return {}
    
    async def test_geofences_endpoint(self):
        """Test GET /api/geofences endpoint - should return 3 geofences"""
        print("\n=== Geofences Endpoint Test ===")
        
        if not self.auth_token:
            self.log_test("Geofences Endpoint", False, "No auth token available")
            return []
        
        success, data, status = await self.make_request("GET", "/geofences")
        geofences_list = data if isinstance(data, list) else []
        
        expected_count = 3  # As mentioned in review request
        
        self.log_test(
            "GET /api/geofences", 
            success and status == 200,
            f"Status: {status}, Geofences returned: {len(geofences_list)} (expected: {expected_count})",
            geofences_list[:2] if geofences_list else None
        )
        
        if geofences_list:
            # Check geofence data structure
            valid_geofences = []
            structure_issues = []
            
            required_fields = ['id', 'name', 'type', 'risk_level', 'coordinates', 'active']
            
            for i, geofence in enumerate(geofences_list):
                missing_fields = [field for field in required_fields if field not in geofence]
                if missing_fields:
                    structure_issues.append(f"Geofence {i+1} missing: {missing_fields}")
                    continue
                
                # Validate coordinates format (GeoJSON format expected)
                coordinates = geofence.get('coordinates')
                if not isinstance(coordinates, dict):
                    structure_issues.append(f"Geofence {i+1} coordinates not in GeoJSON format")
                    continue
                
                # Check GeoJSON structure
                try:
                    if coordinates.get('type') != 'Polygon':
                        raise ValueError("GeoJSON type is not Polygon")
                    
                    coord_array = coordinates.get('coordinates')
                    if not isinstance(coord_array, list) or len(coord_array) == 0:
                        raise ValueError("GeoJSON coordinates array is invalid")
                    
                    # Check first ring of polygon
                    first_ring = coord_array[0]
                    if not isinstance(first_ring, list) or len(first_ring) < 4:
                        raise ValueError("Polygon ring has insufficient points")
                    
                    # Validate coordinate pairs in the ring
                    for coord_pair in first_ring:
                        if not isinstance(coord_pair, list) or len(coord_pair) != 2:
                            raise ValueError("Invalid coordinate pair format")
                        lon, lat = float(coord_pair[0]), float(coord_pair[1])
                        if not (-180 <= lon <= 180) or not (-90 <= lat <= 90):
                            raise ValueError("Coordinate values out of range")
                            
                except (ValueError, TypeError) as e:
                    structure_issues.append(f"Geofence {i+1} GeoJSON validation failed: {str(e)}")
                    continue
                
                valid_geofences.append(geofence)
            
            self.log_test(
                "Geofence Data Structure", 
                len(structure_issues) == 0,
                f"Valid geofences: {len(valid_geofences)}/{len(geofences_list)}, Issues: {structure_issues[:2]}{'...' if len(structure_issues) > 2 else ''}",
                geofences_list[0] if geofences_list else None
            )
            
            # Log geofence names for verification
            geofence_names = [gf.get('name', 'Unnamed') for gf in geofences_list]
            print(f"   🗺️  Geofences: {', '.join(geofence_names)}")
            
            return valid_geofences
        
        return []
    
    async def test_data_structure_compatibility(self):
        """Test if data structure matches frontend expectations"""
        print("\n=== Data Structure Compatibility Test ===")
        
        if not self.auth_token:
            self.log_test("Data Structure Compatibility", False, "No auth token available")
            return
        
        # Get live locations and check against expected frontend structure
        success, live_data, status = await self.make_request("GET", "/location/live")
        
        if success and isinstance(live_data, list) and live_data:
            sample_location = live_data[0]
            
            # Frontend expects: tourist_id, tourist_name, digital_id, status, coordinates, address, timestamp
            frontend_expected = ['tourist_id', 'tourist_name', 'digital_id', 'status', 'coordinates', 'timestamp']
            present_fields = [field for field in frontend_expected if field in sample_location]
            missing_fields = [field for field in frontend_expected if field not in sample_location]
            
            compatibility_score = len(present_fields) / len(frontend_expected)
            
            self.log_test(
                "Frontend Data Compatibility", 
                compatibility_score >= 0.8,  # At least 80% compatibility
                f"Compatibility: {compatibility_score:.1%} ({len(present_fields)}/{len(frontend_expected)} fields), Missing: {missing_fields}",
                {k: v for k, v in sample_location.items() if k in frontend_expected}
            )
            
            # Check if coordinates are in the right format [longitude, latitude]
            coords = sample_location.get('coordinates')
            if isinstance(coords, list) and len(coords) == 2:
                lon, lat = coords
                valid_coords = (-180 <= lon <= 180) and (-90 <= lat <= 90)
                
                self.log_test(
                    "Coordinates Range Validation", 
                    valid_coords,
                    f"Coordinates: [{lon}, {lat}], Valid range: {valid_coords}"
                )
            else:
                self.log_test(
                    "Coordinates Range Validation", 
                    False,
                    f"Invalid coordinates format: {coords}"
                )
        else:
            self.log_test(
                "Frontend Data Compatibility", 
                False,
                "No live location data available for compatibility testing"
            )
    
    async def test_individual_tourist_data(self, tourist_ids: List[str]):
        """Test individual tourist data endpoints as requested in review"""
        print("\n=== Individual Tourist Data Testing ===")
        
        if not self.auth_token:
            self.log_test("Individual Tourist Data", False, "No auth token available")
            return
        
        if not tourist_ids:
            self.log_test("Individual Tourist Data", False, "No tourist IDs available for testing")
            return
        
        # Test first tourist from the list
        tourist_id = tourist_ids[0]
        
        # Test GET /api/tourists/{tourist_id}
        success, data, status = await self.make_request("GET", f"/tourists/{tourist_id}")
        
        if success and status == 200 and isinstance(data, dict):
            required_fields = ['id', 'digital_id', 'full_name', 'nationality', 'status', 'safety_score', 'emergency_contacts']
            missing_fields = [field for field in required_fields if field not in data]
            
            self.log_test(
                "GET /api/tourists/{tourist_id}", 
                len(missing_fields) == 0,
                f"Status: {status}, Tourist: {data.get('full_name', 'Unknown')} ({data.get('digital_id', 'No ID')}), Missing fields: {missing_fields}",
                {k: v for k, v in data.items() if k in required_fields}
            )
            
            # Log key tourist details for verification
            print(f"   👤 Tourist Details: {data.get('full_name', 'Unknown')} - {data.get('digital_id', 'No ID')} - Status: {data.get('status', 'Unknown')}")
        else:
            self.log_test(
                "GET /api/tourists/{tourist_id}", 
                False,
                f"Status: {status}, Response type: {type(data)}",
                {"status": status, "response": data}
            )
        
        # Test GET /api/tourists/{tourist_id}/alerts
        success, data, status = await self.make_request("GET", f"/tourists/{tourist_id}/alerts")
        
        if success and status == 200 and isinstance(data, list):
            alerts_count = len(data)
            
            # Validate alert structure if alerts exist
            structure_valid = True
            if alerts_count > 0:
                required_alert_fields = ['id', 'alert_id', 'tourist_id', 'alert_type', 'severity', 'status', 'location', 'timestamp']
                sample_alert = data[0]
                missing_fields = [field for field in required_alert_fields if field not in sample_alert]
                structure_valid = len(missing_fields) == 0
                
                if not structure_valid:
                    print(f"   ⚠️  Alert structure issues: Missing {missing_fields}")
            
            self.log_test(
                "GET /api/tourists/{tourist_id}/alerts", 
                structure_valid,
                f"Status: {status}, Alerts count: {alerts_count}, Structure valid: {structure_valid}",
                data[0] if data else None
            )
            
            # Log alert details for verification
            if data:
                alert_types = [alert.get('alert_type', 'Unknown') for alert in data]
                print(f"   🚨 Tourist Alerts: {alerts_count} alerts - Types: {', '.join(set(alert_types))}")
        else:
            self.log_test(
                "GET /api/tourists/{tourist_id}/alerts", 
                False,
                f"Status: {status}, Response type: {type(data)}",
                {"status": status, "response": data}
            )
        
        # Test GET /api/tourists/{tourist_id}/location-history
        success, data, status = await self.make_request("GET", f"/tourists/{tourist_id}/location-history")
        
        if success and status == 200 and isinstance(data, list):
            history_count = len(data)
            
            # Validate location history structure if entries exist
            structure_valid = True
            coordinates_valid = True
            
            if history_count > 0:
                sample_location = data[0]
                
                # Check for required fields in location history
                if 'coordinates' not in sample_location:
                    structure_valid = False
                else:
                    # Validate coordinates format
                    coords = sample_location['coordinates']
                    if isinstance(coords, dict) and 'coordinates' in coords:
                        # GeoJSON format
                        coord_array = coords['coordinates']
                        if not isinstance(coord_array, list) or len(coord_array) != 2:
                            coordinates_valid = False
                    elif isinstance(coords, list) and len(coords) == 2:
                        # Direct array format
                        try:
                            lon, lat = float(coords[0]), float(coords[1])
                            if not (-180 <= lon <= 180) or not (-90 <= lat <= 90):
                                coordinates_valid = False
                        except (ValueError, TypeError):
                            coordinates_valid = False
                    else:
                        coordinates_valid = False
            
            self.log_test(
                "GET /api/tourists/{tourist_id}/location-history", 
                structure_valid and coordinates_valid,
                f"Status: {status}, History entries: {history_count}, Structure valid: {structure_valid}, Coordinates valid: {coordinates_valid}",
                data[0] if data else None
            )
            
            # Log location history details for verification
            if data:
                latest_location = data[0]
                coords = latest_location.get('coordinates', 'No coordinates')
                timestamp = latest_location.get('timestamp', 'No timestamp')
                print(f"   📍 Latest Location: {coords} at {timestamp}")
        else:
            self.log_test(
                "GET /api/tourists/{tourist_id}/location-history", 
                False,
                f"Status: {status}, Response type: {type(data)}",
                {"status": status, "response": data}
            )
    
    async def run_live_map_tests(self):
        """Run all Live Map integration tests as requested in review"""
        print(f"🗺️  Starting Live Map Data Integration Tests After Demo Data Population")
        print(f"📍 Backend URL: {API_BASE_URL}")
        print("=" * 70)
        
        # Step 1: Authentication Test with demo user credentials
        print("\n🔐 STEP 1: Authentication Test")
        if not await self.authenticate():
            print("❌ Authentication failed - cannot proceed with Live Map tests")
            return self.test_results
        
        # Step 2: Core Live Map Endpoints Testing
        print("\n🗺️  STEP 2: Core Live Map Endpoints")
        
        # Test the three main endpoints that Live Map uses
        valid_tourists = await self.test_live_locations_endpoint()
        dashboard_data = await self.test_dashboard_kpis_endpoint()
        valid_geofences = await self.test_geofences_endpoint()
        
        # Step 3: Data Structure Verification
        print("\n📋 STEP 3: Data Structure Verification")
        await self.test_data_structure_compatibility()
        
        # Step 4: Individual Tourist Data Testing
        print("\n👤 STEP 4: Individual Tourist Data")
        tourist_ids = [t.get('tourist_id') for t in valid_tourists if t.get('tourist_id')]
        if tourist_ids:
            await self.test_individual_tourist_data(tourist_ids)
        else:
            self.log_test("Individual Tourist Data", False, "No tourist IDs available from live locations")
        
        # Print comprehensive summary
        print("\n" + "=" * 70)
        print("📊 LIVE MAP INTEGRATION TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Live Map Integration Status
        print(f"\n🗺️  LIVE MAP INTEGRATION STATUS:")
        print(f"   📍 Live Locations: {'✅' if len(valid_tourists) > 0 else '❌'} ({len(valid_tourists)} tourists with valid data)")
        print(f"   📊 Dashboard KPIs: {'✅' if dashboard_data else '❌'}")
        print(f"   🗺️  Geofences: {'✅' if len(valid_geofences) > 0 else '❌'} ({len(valid_geofences)} valid geofences)")
        print(f"   👤 Individual Data: {'✅' if tourist_ids else '❌'} ({len(tourist_ids)} tourists available)")
        
        # Detailed response data for verification
        print(f"\n📋 RESPONSE DATA VERIFICATION:")
        if valid_tourists:
            sample_tourist = valid_tourists[0]
            print(f"   Sample Tourist Data: {json.dumps(sample_tourist, indent=2, default=str)}")
        
        if dashboard_data:
            kpi_summary = {k: v for k, v in dashboard_data.items() if k in ['total_active_tourists', 'active_alerts', 'safe_status', 'high_risk_tourists']}
            print(f"   Dashboard KPIs: {json.dumps(kpi_summary, indent=2, default=str)}")
        
        if failed_tests > 0:
            print(f"\n🔍 FAILED TESTS DETAILS:")
            for test_name, result in self.test_results.items():
                if not result['success']:
                    print(f"  ❌ {test_name}: {result['details']}")
        
        # Final diagnosis for Live Map integration
        live_map_ready = (
            len(valid_tourists) > 0 and 
            dashboard_data and 
            len(valid_geofences) > 0 and 
            len(tourist_ids) > 0
        )
        
        print(f"\n🎯 LIVE MAP INTEGRATION READY: {'✅ YES' if live_map_ready else '❌ NO'}")
        
        if live_map_ready:
            print("   ✅ All required data is available for Live Map frontend integration")
            print("   ✅ Coordinates and status fields are properly populated")
            print("   ✅ Frontend should be able to display tourist markers correctly")
        else:
            print("   ❌ Live Map integration issues detected - frontend will not display correctly")
        
        return self.test_results

async def main():
    """Main test runner for Live Map"""
    async with LiveMapDataTester() as tester:
        results = await tester.run_live_map_tests()
        
        # Save results to file
        with open('/app/live_map_test_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Live Map test results saved to: /app/live_map_test_results.json")
        
        return results

if __name__ == "__main__":
    asyncio.run(main())