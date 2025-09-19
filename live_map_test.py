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
                
                # Validate coordinates format (should be array of coordinate pairs for polygon)
                coordinates = geofence.get('coordinates')
                if not isinstance(coordinates, list) or len(coordinates) == 0:
                    structure_issues.append(f"Geofence {i+1} invalid coordinates format")
                    continue
                
                # Check coordinate pairs format
                try:
                    for coord_pair in coordinates:
                        if not isinstance(coord_pair, list) or len(coord_pair) != 2:
                            raise ValueError("Invalid coordinate pair format")
                        lon, lat = float(coord_pair[0]), float(coord_pair[1])
                        if not (-180 <= lon <= 180) or not (-90 <= lat <= 90):
                            raise ValueError("Coordinate values out of range")
                except (ValueError, TypeError) as e:
                    structure_issues.append(f"Geofence {i+1} coordinate validation failed: {str(e)}")
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
    
    async def test_specific_tourist_data(self):
        """Test specific tourist data to understand the issue"""
        print("\n=== Specific Tourist Data Analysis ===")
        
        if not self.auth_token:
            self.log_test("Tourist Data Analysis", False, "No auth token available")
            return
        
        # Get tourists list
        success, tourists_data, status = await self.make_request("GET", "/tourists")
        
        if not success or not isinstance(tourists_data, list) or not tourists_data:
            self.log_test("Tourist Data Analysis", False, "No tourists data available")
            return
        
        # Analyze each tourist's data
        for i, tourist in enumerate(tourists_data[:3]):  # Check first 3 tourists
            tourist_id = tourist.get('id')
            tourist_name = tourist.get('full_name', 'Unknown')
            
            print(f"\n--- Analyzing Tourist {i+1}: {tourist_name} ---")
            
            # Check if tourist has last_known_location
            has_location = 'location' in tourist and tourist['location'] is not None
            
            self.log_test(
                f"Tourist {i+1} - Has Location", 
                has_location,
                f"Tourist: {tourist_name}, Has location: {has_location}",
                tourist.get('location')
            )
            
            # Get detailed tourist info
            if tourist_id:
                success, detailed_tourist, status = await self.make_request("GET", f"/tourists/{tourist_id}")
                
                if success and isinstance(detailed_tourist, dict):
                    location_data = detailed_tourist.get('location')
                    
                    self.log_test(
                        f"Tourist {i+1} - Detailed Location", 
                        location_data is not None,
                        f"Detailed location available: {location_data is not None}",
                        location_data
                    )
                    
                    # Check location history
                    success, location_history, status = await self.make_request("GET", f"/tourists/{tourist_id}/location-history")
                    
                    if success and isinstance(location_history, list):
                        self.log_test(
                            f"Tourist {i+1} - Location History", 
                            len(location_history) > 0,
                            f"Location history entries: {len(location_history)}",
                            location_history[0] if location_history else None
                        )
    
    async def run_live_map_tests(self):
        """Run all Live Map specific tests"""
        print(f"🗺️  Starting Live Map Data Integration Tests")
        print(f"📍 Backend URL: {API_BASE_URL}")
        print("=" * 60)
        
        # Authenticate first
        if not await self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return self.test_results
        
        # Run Live Map specific tests
        await self.test_database_data_existence()
        await self.test_live_locations_endpoint()
        await self.test_dashboard_kpis_endpoint()
        await self.test_geofences_endpoint()
        await self.test_data_structure_compatibility()
        await self.test_specific_tourist_data()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 LIVE MAP TEST SUMMARY")
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
        
        # Provide diagnosis
        print(f"\n🔍 LIVE MAP DIAGNOSIS:")
        
        # Check key indicators
        has_tourists = any("Tourists in Database" in name and result['success'] for name, result in self.test_results.items())
        has_live_locations = any("GET /api/location/live" in name and result['success'] for name, result in self.test_results.items())
        has_location_data = any("Live locations returned: 0" not in result['details'] for name, result in self.test_results.items() if "GET /api/location/live" in name)
        
        if not has_tourists:
            print("  🚨 ROOT CAUSE: No tourists in database")
        elif not has_live_locations:
            print("  🚨 ROOT CAUSE: Live locations endpoint failing")
        elif not has_location_data:
            print("  🚨 ROOT CAUSE: No location data available for tourists")
        else:
            print("  ✅ Data appears to be available - issue may be in frontend integration")
        
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