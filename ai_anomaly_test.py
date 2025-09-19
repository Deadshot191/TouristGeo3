#!/usr/bin/env python3
"""
Focused AI Anomaly Detection Testing
Tests the new AI anomaly detection features specifically
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://realtime-tourist.preview.emergentagent.com')
API_BASE_URL = f"{BACKEND_URL}/api"

class AIAnomalyTester:
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
    
    async def make_request(self, method: str, endpoint: str, data: dict = None, params: dict = None):
        """Make authenticated request"""
        headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
        
        async with self.session.request(
            method, f"{API_BASE_URL}{endpoint}", 
            json=data, params=params, headers=headers
        ) as response:
            try:
                response_data = await response.json()
            except:
                response_data = await response.text()
            return response.status, response_data
    
    async def test_background_task_status(self):
        """Test background task status endpoint"""
        print("\n=== Testing Background Task Status ===")
        
        status, data = await self.make_request("GET", "/ai/background-tasks/status")
        
        if status == 200 and isinstance(data, dict):
            print(f"✅ Background Task Status: {status}")
            print(f"   - Is Running: {data.get('is_running', 'unknown')}")
            print(f"   - Anomaly Detection Running: {data.get('anomaly_detection', {}).get('running', 'unknown')}")
            print(f"   - Task Done: {data.get('anomaly_detection', {}).get('done', 'unknown')}")
            print(f"   - Task Cancelled: {data.get('anomaly_detection', {}).get('cancelled', 'unknown')}")
            return True
        else:
            print(f"❌ Background Task Status Failed: {status} - {data}")
            return False
    
    async def test_ai_safety_score(self, tourist_id: str):
        """Test AI safety score calculation"""
        print(f"\n=== Testing AI Safety Score for Tourist {tourist_id} ===")
        
        status, data = await self.make_request("GET", f"/ai/safety-score/{tourist_id}")
        
        if status == 200 and isinstance(data, dict):
            print(f"✅ AI Safety Score: {status}")
            print(f"   - Safety Score: {data.get('safety_score', 'unknown')}")
            print(f"   - Risk Factors: {data.get('risk_factors', [])}")
            print(f"   - Last Updated: {data.get('last_updated', 'unknown')}")
            return True
        else:
            print(f"❌ AI Safety Score Failed: {status} - {data}")
            return False
    
    async def test_manual_anomaly_check(self, tourist_id: str):
        """Test manual anomaly detection"""
        print(f"\n=== Testing Manual Anomaly Check for Tourist {tourist_id} ===")
        
        status, data = await self.make_request("GET", f"/ai/anomaly-check/{tourist_id}")
        
        if status == 200 and isinstance(data, dict):
            print(f"✅ Manual Anomaly Check: {status}")
            print(f"   - Tourist ID: {data.get('tourist_id', 'unknown')}")
            print(f"   - Timestamp: {data.get('timestamp', 'unknown')}")
            print(f"   - Checks Performed: {data.get('checks_performed', [])}")
            print(f"   - Anomalies Detected: {data.get('anomalies_detected', [])}")
            if 'safety_score' in data:
                safety_data = data['safety_score']
                print(f"   - Safety Score: {safety_data.get('safety_score', 'unknown')}")
                print(f"   - Risk Factors: {safety_data.get('risk_factors', [])}")
            return True
        else:
            print(f"❌ Manual Anomaly Check Failed: {status} - {data}")
            return False
    
    async def test_background_task_restart(self):
        """Test background task restart"""
        print("\n=== Testing Background Task Restart ===")
        
        status, data = await self.make_request("POST", "/ai/background-tasks/restart")
        
        if status == 200 and isinstance(data, dict):
            print(f"✅ Background Task Restart: {status}")
            print(f"   - Message: {data.get('message', 'unknown')}")
            if 'status' in data:
                task_status = data['status']
                print(f"   - Is Running: {task_status.get('is_running', 'unknown')}")
                print(f"   - Anomaly Detection Running: {task_status.get('anomaly_detection', {}).get('running', 'unknown')}")
            return True
        else:
            print(f"❌ Background Task Restart Failed: {status} - {data}")
            return False
    
    async def test_geospatial_queries(self):
        """Test enhanced geofencing with geospatial queries"""
        print("\n=== Testing Enhanced Geospatial Queries ===")
        
        # Test different coordinate points
        test_points = [
            {"lon": 88.2700, "lat": 27.0400, "name": "Central Darjeeling"},
            {"lon": 88.2800, "lat": 27.0460, "name": "Military Zone Area"},
            {"lon": 88.2550, "lat": 27.0325, "name": "Landslide Prone Area"},
            {"lon": 88.2650, "lat": 27.0400, "name": "Mall Road Safe Zone"}
        ]
        
        results = []
        for point in test_points:
            params = {"longitude": point["lon"], "latitude": point["lat"]}
            status, data = await self.make_request("GET", "/geofences/check", params=params)
            
            if status == 200 and isinstance(data, list):
                print(f"✅ {point['name']}: Found {len(data)} intersecting geofences")
                for fence in data:
                    print(f"   - {fence.get('name', 'Unknown')}: {fence.get('type', 'unknown')} ({fence.get('risk_level', 'unknown')} risk)")
                results.append({"point": point, "geofences": data})
            else:
                print(f"❌ {point['name']}: Failed - {status}")
                results.append({"point": point, "geofences": []})
        
        return results
    
    async def get_tourist_id(self):
        """Get a tourist ID for testing"""
        status, data = await self.make_request("GET", "/tourists")
        
        if status == 200 and isinstance(data, list) and len(data) > 0:
            return data[0].get('id')
        return None
    
    async def run_all_ai_tests(self):
        """Run all AI anomaly detection tests"""
        print("🤖 Starting AI Anomaly Detection Tests")
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
        
        # Run AI-specific tests
        results = []
        
        # Test 1: Background Task Status
        results.append(await self.test_background_task_status())
        
        # Test 2: AI Safety Score
        results.append(await self.test_ai_safety_score(tourist_id))
        
        # Test 3: Manual Anomaly Check
        results.append(await self.test_manual_anomaly_check(tourist_id))
        
        # Test 4: Background Task Restart
        results.append(await self.test_background_task_restart())
        
        # Test 5: Enhanced Geospatial Queries
        geospatial_results = await self.test_geospatial_queries()
        results.append(len(geospatial_results) > 0)
        
        # Summary
        print("\n" + "=" * 60)
        print("🤖 AI ANOMALY DETECTION TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(results)
        total = len(results)
        
        print(f"Total AI Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        return results

async def main():
    """Main test runner"""
    async with AIAnomalyTester() as tester:
        results = await tester.run_all_ai_tests()
        return results

if __name__ == "__main__":
    asyncio.run(main())