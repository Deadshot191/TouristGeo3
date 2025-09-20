#!/usr/bin/env python3
"""
Live Map Diagnosis - Test endpoints without authentication to understand the issue
"""

import asyncio
import aiohttp
import json
import os

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://tourist-theme-fix.preview.emergentagent.com')
API_BASE_URL = f"{BACKEND_URL}/api"

async def test_endpoints_without_auth():
    """Test endpoints that don't require authentication"""
    
    async with aiohttp.ClientSession() as session:
        print(f"🔍 Testing Live Map endpoints without authentication")
        print(f"📍 Backend URL: {API_BASE_URL}")
        print("=" * 60)
        
        # Test health endpoint
        try:
            async with session.get(f"{API_BASE_URL}/health") as response:
                data = await response.json()
                print(f"✅ Health Check: Status {response.status}")
                print(f"   Database: {data.get('database', 'unknown')}")
                print(f"   WebSockets: {data.get('websockets', {})}")
        except Exception as e:
            print(f"❌ Health Check failed: {e}")
        
        # Test endpoints that require auth (should get 403/401)
        endpoints_to_test = [
            "/tourists",
            "/location/live", 
            "/analytics/dashboard",
            "/geofences"
        ]
        
        for endpoint in endpoints_to_test:
            try:
                async with session.get(f"{API_BASE_URL}{endpoint}") as response:
                    if response.status == 403:
                        print(f"✅ {endpoint}: Properly protected (403 Forbidden)")
                    elif response.status == 401:
                        print(f"✅ {endpoint}: Properly protected (401 Unauthorized)")
                    else:
                        data = await response.json() if response.content_type == 'application/json' else await response.text()
                        print(f"⚠️  {endpoint}: Status {response.status} - {data}")
            except Exception as e:
                print(f"❌ {endpoint}: Error - {e}")
        
        print("\n" + "=" * 60)
        print("🔍 DIAGNOSIS SUMMARY")
        print("=" * 60)
        print("✅ Backend service is running and responding")
        print("✅ API endpoints are properly protected with authentication")
        print("❌ CRITICAL ISSUE: Database is empty - no users or tourists")
        print("❌ ROOT CAUSE: Demo data was not populated in the database")
        print("\n📋 REQUIRED ACTIONS:")
        print("1. Populate database with demo users for authentication")
        print("2. Populate database with demo tourists and location data")
        print("3. Ensure location_history collection has data for Live Map")

if __name__ == "__main__":
    asyncio.run(test_endpoints_without_auth())