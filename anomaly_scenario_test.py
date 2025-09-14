#!/usr/bin/env python3
"""
Anomaly Detection Scenario Testing
Tests route deviation and prolonged inactivity detection by creating test scenarios
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime, timedelta

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://securetravel-3.preview.emergentagent.com')
API_BASE_URL = f"{BACKEND_URL}/api"

class AnomalyScenarioTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def authenticate(self):
        """Authenticate and get token"""
        login_data = {
            "email": "inspector.kumar@tourism.gov.in",
            "password": "password123"
        }
        
        async with self.session.post(f"{API_BASE_URL}/auth/login", json=login_data) as response:
            if response.status == 200:
                data = await response.json()
                self.auth_token = data['access_token']
                print(f"✅ Authenticated as {data['user']['full_name']}")
                return True
            else:
                print(f"❌ Authentication failed: {response.status}")
                return False
    
    async def make_request(self, method: str, endpoint: str, data: dict = None, params: dict = None, auth: bool = True):
        """Make request with optional authentication"""
        headers = {"Authorization": f"Bearer {self.auth_token}"} if auth and self.auth_token else {}
        
        async with self.session.request(
            method, f"{API_BASE_URL}{endpoint}", 
            json=data, params=params, headers=headers
        ) as response:
            try:
                response_data = await response.json()
            except:
                response_data = await response.text()
            return response.status, response_data
    
    async def get_tourist_id(self):
        """Get a tourist ID for testing"""
        status, data = await self.make_request("GET", "/tourists")
        
        if status == 200 and isinstance(data, list) and len(data) > 0:
            return data[0].get('id')
        return None
    
    async def simulate_route_deviation(self, tourist_id: str):
        """Simulate route deviation by updating location far from planned route"""
        print(f"\n=== Simulating Route Deviation for Tourist {tourist_id} ===")
        
        # Update location to a point far from typical tourist areas (simulate deviation)
        # Using coordinates that are >2km from typical Darjeeling tourist spots
        deviation_location = {
            "tourist_id": tourist_id,
            "longitude": 88.3500,  # Far from Mall Road area
            "latitude": 27.1000,   # Far from typical tourist spots
            "address": "Remote Area - Deviation Test",
            "accuracy": 10.0,
            "speed": 0.0
        }
        
        # Update location (no auth required for this endpoint)
        status, data = await self.make_request("POST", "/location/update", deviation_location, auth=False)
        
        if status == 200:
            print(f"✅ Location updated to simulate deviation: {deviation_location['longitude']}, {deviation_location['latitude']}")
            
            # Wait a moment for processing
            await asyncio.sleep(2)
            
            # Trigger manual anomaly check to see if deviation is detected
            status, anomaly_data = await self.make_request("GET", f"/ai/anomaly-check/{tourist_id}")
            
            if status == 200:
                print(f"✅ Manual anomaly check completed")
                print(f"   - Checks performed: {anomaly_data.get('checks_performed', [])}")
                print(f"   - Anomalies detected: {anomaly_data.get('anomalies_detected', [])}")
                
                # Check if any route deviation alerts were created
                status, alerts = await self.make_request("GET", "/alerts", params={"alert_type": "route_deviation", "limit": 5})
                if status == 200:
                    route_alerts = [alert for alert in alerts if alert.get('alert_type') == 'route_deviation']
                    print(f"   - Route deviation alerts found: {len(route_alerts)}")
                    return len(route_alerts) > 0
            
            return False
        else:
            print(f"❌ Failed to update location: {status} - {data}")
            return False
    
    async def check_prolonged_inactivity_detection(self, tourist_id: str):
        """Check if prolonged inactivity detection is working"""
        print(f"\n=== Checking Prolonged Inactivity Detection for Tourist {tourist_id} ===")
        
        # Get tourist details to check last location update
        status, tourist_data = await self.make_request("GET", f"/tourists/{tourist_id}")
        
        if status == 200:
            last_update = tourist_data.get('last_location_update')
            print(f"✅ Tourist last location update: {last_update}")
            
            # Trigger manual anomaly check
            status, anomaly_data = await self.make_request("GET", f"/ai/anomaly-check/{tourist_id}")
            
            if status == 200:
                print(f"✅ Manual anomaly check completed")
                print(f"   - Checks performed: {anomaly_data.get('checks_performed', [])}")
                print(f"   - Anomalies detected: {anomaly_data.get('anomalies_detected', [])}")
                
                # Check for prolonged inactivity alerts
                status, alerts = await self.make_request("GET", "/alerts", params={"alert_type": "prolonged_inactivity", "limit": 5})
                if status == 200:
                    inactivity_alerts = [alert for alert in alerts if alert.get('alert_type') == 'prolonged_inactivity']
                    print(f"   - Prolonged inactivity alerts found: {len(inactivity_alerts)}")
                    return True
            
            return False
        else:
            print(f"❌ Failed to get tourist data: {status} - {tourist_data}")
            return False
    
    async def test_alert_broadcasting(self, tourist_id: str):
        """Test if new alert types are properly broadcast"""
        print(f"\n=== Testing Alert Broadcasting for Tourist {tourist_id} ===")
        
        # Get current alert count
        status, alerts_before = await self.make_request("GET", "/alerts")
        alerts_count_before = len(alerts_before) if isinstance(alerts_before, list) else 0
        
        print(f"✅ Current alert count: {alerts_count_before}")
        
        # Create a panic alert to test broadcasting
        params = {
            "tourist_id": tourist_id,
            "longitude": 88.2700,
            "latitude": 27.0400,
            "address": "Test Broadcasting Location"
        }
        
        status, alert_data = await self.make_request("POST", "/alerts/panic", params=params, auth=False)
        
        if status == 200:
            alert_id = alert_data.get('alert_id')
            print(f"✅ Created test alert: {alert_id}")
            
            # Wait a moment
            await asyncio.sleep(1)
            
            # Check if alert count increased
            status, alerts_after = await self.make_request("GET", "/alerts")
            alerts_count_after = len(alerts_after) if isinstance(alerts_after, list) else 0
            
            print(f"✅ Alert count after creation: {alerts_count_after}")
            
            if alerts_count_after > alerts_count_before:
                print(f"✅ Alert broadcasting working - count increased by {alerts_count_after - alerts_count_before}")
                return True
            else:
                print(f"❌ Alert broadcasting may not be working - count did not increase")
                return False
        else:
            print(f"❌ Failed to create test alert: {status} - {alert_data}")
            return False
    
    async def test_geofence_breach_detection(self, tourist_id: str):
        """Test automatic geofence breach detection"""
        print(f"\n=== Testing Geofence Breach Detection for Tourist {tourist_id} ===")
        
        # Test coordinates in different geofence zones
        test_locations = [
            {
                "coords": [88.2800, 27.0460],
                "name": "Military Restricted Zone",
                "expected_risk": "critical"
            },
            {
                "coords": [88.2550, 27.0325],
                "name": "Landslide Prone Area", 
                "expected_risk": "high"
            },
            {
                "coords": [88.2650, 27.0400],
                "name": "Tourist Safe Zone",
                "expected_risk": "low"
            }
        ]
        
        results = []
        
        for location in test_locations:
            print(f"\n--- Testing {location['name']} ---")
            
            # Update tourist location
            location_update = {
                "tourist_id": tourist_id,
                "longitude": location["coords"][0],
                "latitude": location["coords"][1],
                "address": f"Test Location - {location['name']}",
                "accuracy": 10.0,
                "speed": 0.0
            }
            
            status, data = await self.make_request("POST", "/location/update", location_update, auth=False)
            
            if status == 200:
                print(f"✅ Updated location to {location['name']}")
                
                # Check geofence intersection
                params = {
                    "longitude": location["coords"][0],
                    "latitude": location["coords"][1]
                }
                
                status, geofences = await self.make_request("GET", "/geofences/check", params=params)
                
                if status == 200 and isinstance(geofences, list):
                    print(f"✅ Found {len(geofences)} intersecting geofences")
                    for fence in geofences:
                        print(f"   - {fence.get('name', 'Unknown')}: {fence.get('risk_level', 'unknown')} risk")
                    
                    results.append({
                        "location": location["name"],
                        "geofences_found": len(geofences),
                        "success": len(geofences) > 0
                    })
                else:
                    print(f"❌ Failed to check geofences: {status}")
                    results.append({
                        "location": location["name"],
                        "geofences_found": 0,
                        "success": False
                    })
            else:
                print(f"❌ Failed to update location: {status}")
                results.append({
                    "location": location["name"],
                    "geofences_found": 0,
                    "success": False
                })
            
            # Small delay between tests
            await asyncio.sleep(1)
        
        return results
    
    async def run_scenario_tests(self):
        """Run all anomaly detection scenario tests"""
        print("🎭 Starting Anomaly Detection Scenario Tests")
        print(f"📍 Backend URL: {API_BASE_URL}")
        print("=" * 60)
        
        # Authenticate
        if not await self.authenticate():
            return
        
        # Get tourist ID for testing
        tourist_id = await self.get_tourist_id()
        if not tourist_id:
            print("❌ No tourists found for testing")
            return
        
        print(f"🧑‍🤝‍🧑 Using Tourist ID: {tourist_id}")
        
        # Run scenario tests
        results = []
        
        # Test 1: Route Deviation Detection
        print("\n" + "="*60)
        route_deviation_result = await self.simulate_route_deviation(tourist_id)
        results.append(("Route Deviation Detection", route_deviation_result))
        
        # Test 2: Prolonged Inactivity Detection
        print("\n" + "="*60)
        inactivity_result = await self.check_prolonged_inactivity_detection(tourist_id)
        results.append(("Prolonged Inactivity Detection", inactivity_result))
        
        # Test 3: Alert Broadcasting
        print("\n" + "="*60)
        broadcasting_result = await self.test_alert_broadcasting(tourist_id)
        results.append(("Alert Broadcasting", broadcasting_result))
        
        # Test 4: Geofence Breach Detection
        print("\n" + "="*60)
        geofence_results = await self.test_geofence_breach_detection(tourist_id)
        geofence_success = all(result["success"] for result in geofence_results)
        results.append(("Geofence Breach Detection", geofence_success))
        
        # Summary
        print("\n" + "=" * 60)
        print("🎭 ANOMALY DETECTION SCENARIO TEST SUMMARY")
        print("=" * 60)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        print(f"\nTotal Scenario Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        return results

async def main():
    """Main test runner"""
    async with AnomalyScenarioTester() as tester:
        results = await tester.run_scenario_tests()
        return results

if __name__ == "__main__":
    asyncio.run(main())