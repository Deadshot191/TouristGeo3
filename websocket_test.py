#!/usr/bin/env python3
"""
WebSocket Testing for Tourism Safety System Real-time Features
Tests WebSocket location tracking, panic alerts, and dashboard updates
"""

import asyncio
import websockets
import json
import aiohttp
import os
from datetime import datetime
from typing import Dict, Any

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://tourist-shield-1.preview.emergentagent.com')
API_BASE_URL = f"{BACKEND_URL}/api"
WS_BASE_URL = BACKEND_URL.replace('https://', 'wss://').replace('http://', 'ws://')

class WebSocketTester:
    def __init__(self):
        self.auth_token = None
        self.test_results = {}
        self.tourist_id = None
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        self.test_results[test_name] = {
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
    
    async def authenticate(self):
        """Authenticate and get token"""
        try:
            async with aiohttp.ClientSession() as session:
                login_data = {
                    "email": "inspector.kumar@tourism.gov.in",
                    "password": "password123"
                }
                
                async with session.post(f"{API_BASE_URL}/auth/login", json=login_data) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.auth_token = data['access_token']
                        self.log_test("Authentication", True, "Successfully authenticated")
                        return True
                    else:
                        self.log_test("Authentication", False, f"Status: {response.status}")
                        return False
        except Exception as e:
            self.log_test("Authentication", False, f"Error: {e}")
            return False
    
    async def get_tourist_id(self):
        """Get a tourist ID for testing"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                async with session.get(f"{API_BASE_URL}/tourists", headers=headers) as response:
                    if response.status == 200:
                        tourists = await response.json()
                        if tourists:
                            self.tourist_id = tourists[0]['id']
                            self.log_test("Get Tourist ID", True, f"Using tourist: {tourists[0]['full_name']}")
                            return True
                    
                    self.log_test("Get Tourist ID", False, f"Status: {response.status}")
                    return False
        except Exception as e:
            self.log_test("Get Tourist ID", False, f"Error: {e}")
            return False
    
    async def test_location_websocket(self):
        """Test WebSocket location tracking endpoint"""
        print("\n=== Testing WebSocket Location Tracking ===")
        
        if not self.tourist_id:
            self.log_test("Location WebSocket", False, "No tourist ID available")
            return
        
        try:
            ws_url = f"{WS_BASE_URL}/api/ws/location/{self.tourist_id}"
            print(f"Connecting to: {ws_url}")
            
            async with websockets.connect(ws_url) as websocket:
                self.log_test("Location WebSocket Connection", True, "Connected successfully")
                
                # Send location update
                location_data = {
                    "tourist_id": self.tourist_id,
                    "longitude": 88.2700,
                    "latitude": 27.0400,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                await websocket.send(json.dumps(location_data))
                self.log_test("Send Location Update", True, "Location data sent")
                
                # Wait for any response or confirmation
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    response_data = json.loads(response)
                    if "error" in response_data:
                        self.log_test("Location Update Response", False, f"Error: {response_data['error']}")
                    else:
                        self.log_test("Location Update Response", True, "Received response")
                except asyncio.TimeoutError:
                    self.log_test("Location Update Response", True, "No response (expected for successful update)")
                
        except Exception as e:
            self.log_test("Location WebSocket", False, f"Error: {e}")
    
    async def test_dashboard_websocket(self):
        """Test dashboard WebSocket endpoint"""
        print("\n=== Testing Dashboard WebSocket ===")
        
        try:
            ws_url = f"{WS_BASE_URL}/api/ws/dashboard"
            print(f"Connecting to: {ws_url}")
            
            async with websockets.connect(ws_url) as websocket:
                self.log_test("Dashboard WebSocket Connection", True, "Connected successfully")
                
                # Send ping command
                ping_command = {"type": "ping"}
                await websocket.send(json.dumps(ping_command))
                
                # Wait for pong response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    response_data = json.loads(response)
                    if response_data.get("type") == "pong":
                        self.log_test("Dashboard Ping-Pong", True, "Received pong response")
                    else:
                        self.log_test("Dashboard Ping-Pong", False, f"Unexpected response: {response_data}")
                except asyncio.TimeoutError:
                    self.log_test("Dashboard Ping-Pong", False, "No pong response received")
                
                # Request system status
                status_command = {"type": "request_status"}
                await websocket.send(json.dumps(status_command))
                
                # Wait for status response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    response_data = json.loads(response)
                    if response_data.get("type") == "system_status":
                        self.log_test("Dashboard Status Request", True, "Received system status")
                    else:
                        self.log_test("Dashboard Status Request", False, f"Unexpected response: {response_data}")
                except asyncio.TimeoutError:
                    self.log_test("Dashboard Status Request", False, "No status response received")
                
        except Exception as e:
            self.log_test("Dashboard WebSocket", False, f"Error: {e}")
    
    async def test_panic_alert_system(self):
        """Test panic button alert system"""
        print("\n=== Testing Panic Alert System ===")
        
        if not self.tourist_id:
            self.log_test("Panic Alert System", False, "No tourist ID available")
            return
        
        try:
            async with aiohttp.ClientSession() as session:
                # Create panic alert
                params = {
                    "tourist_id": self.tourist_id,
                    "longitude": 88.2700,
                    "latitude": 27.0400,
                    "address": "Emergency Location, Darjeeling"
                }
                
                async with session.post(f"{API_BASE_URL}/alerts/panic", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        alert_id = data.get('alert_id')
                        self.log_test("Create Panic Alert", True, f"Alert created: {alert_id}")
                        
                        # Verify alert was saved to database
                        headers = {"Authorization": f"Bearer {self.auth_token}"}
                        async with session.get(f"{API_BASE_URL}/alerts", headers=headers) as alerts_response:
                            if alerts_response.status == 200:
                                alerts = await alerts_response.json()
                                panic_alerts = [a for a in alerts if a.get('alert_id') == alert_id]
                                if panic_alerts:
                                    alert = panic_alerts[0]
                                    self.log_test("Verify Alert in Database", True, 
                                                f"Alert {alert_id} found with severity: {alert.get('severity')}")
                                else:
                                    self.log_test("Verify Alert in Database", False, f"Alert {alert_id} not found")
                            else:
                                self.log_test("Verify Alert in Database", False, f"Status: {alerts_response.status}")
                    else:
                        error_text = await response.text()
                        self.log_test("Create Panic Alert", False, f"Status: {response.status}, Error: {error_text}")
                        
        except Exception as e:
            self.log_test("Panic Alert System", False, f"Error: {e}")
    
    async def test_websocket_stats(self):
        """Test WebSocket connection statistics"""
        print("\n=== Testing WebSocket Statistics ===")
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                async with session.get(f"{API_BASE_URL}/ws/stats", headers=headers) as response:
                    if response.status == 200:
                        stats = await response.json()
                        self.log_test("WebSocket Statistics", True, 
                                    f"Total connections: {stats.get('total_connections', 0)}")
                    else:
                        self.log_test("WebSocket Statistics", False, f"Status: {response.status}")
        except Exception as e:
            self.log_test("WebSocket Statistics", False, f"Error: {e}")
    
    async def verify_location_history(self):
        """Verify location data was saved to location_history collection"""
        print("\n=== Verifying Location History ===")
        
        if not self.tourist_id:
            self.log_test("Location History Verification", False, "No tourist ID available")
            return
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                async with session.get(f"{API_BASE_URL}/tourists/{self.tourist_id}/location-history", 
                                     headers=headers) as response:
                    if response.status == 200:
                        history = await response.json()
                        if history:
                            self.log_test("Location History Verification", True, 
                                        f"Found {len(history)} location entries")
                        else:
                            self.log_test("Location History Verification", False, "No location history found")
                    else:
                        self.log_test("Location History Verification", False, f"Status: {response.status}")
        except Exception as e:
            self.log_test("Location History Verification", False, f"Error: {e}")
    
    async def run_all_tests(self):
        """Run all WebSocket tests"""
        print("🚀 Starting WebSocket Real-time Features Tests")
        print(f"📍 Backend URL: {BACKEND_URL}")
        print(f"🔌 WebSocket URL: {WS_BASE_URL}")
        print("=" * 60)
        
        # Authenticate first
        if not await self.authenticate():
            print("❌ Authentication failed, cannot proceed with tests")
            return
        
        # Get tourist ID
        if not await self.get_tourist_id():
            print("❌ Could not get tourist ID, some tests will be skipped")
        
        # Run WebSocket tests
        await self.test_location_websocket()
        await self.test_dashboard_websocket()
        await self.test_panic_alert_system()
        await self.test_websocket_stats()
        await self.verify_location_history()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 WEBSOCKET TEST SUMMARY")
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
    tester = WebSocketTester()
    results = await tester.run_all_tests()
    
    # Save results to file
    with open('/app/websocket_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 WebSocket test results saved to: /app/websocket_test_results.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())