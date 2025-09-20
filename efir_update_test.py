#!/usr/bin/env python3
"""
Quick test for E-FIR update functionality
"""

import asyncio
import aiohttp
import json
import os

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://efir-paperless.preview.emergentagent.com')
API_BASE_URL = f"{BACKEND_URL}/api"

async def test_efir_update():
    """Test E-FIR update functionality"""
    
    async with aiohttp.ClientSession() as session:
        # Login first
        login_data = {
            "email": "inspector.kumar@tourism.gov.in",
            "password": "password123"
        }
        
        async with session.post(f"{API_BASE_URL}/auth/login", json=login_data) as response:
            if response.status != 200:
                print(f"❌ Login failed: {response.status}")
                return
            
            data = await response.json()
            auth_token = data['access_token']
            print(f"✅ Login successful")
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create a test E-FIR document
        efir_create_data = {
            "title": "Test E-FIR for Update",
            "fir_type": "tourist_incident",
            "priority": "medium",
            "incident_date": "2025-01-15T14:30:00Z",
            "incident_location": {
                "coordinates": {
                    "type": "Point",
                    "coordinates": [88.2700, 27.0400]
                },
                "address": "Test Location, Darjeeling",
                "timestamp": "2025-01-15T14:30:00Z"
            },
            "incident_description": "Test incident for update functionality",
            "case_details": "Initial case details for testing update functionality"
        }
        
        async with session.post(f"{API_BASE_URL}/efir", json=efir_create_data, headers=headers) as response:
            if response.status != 200:
                print(f"❌ E-FIR creation failed: {response.status}")
                return
            
            data = await response.json()
            efir_id = data['id']
            fir_number = data['fir_number']
            print(f"✅ E-FIR created: {fir_number} (ID: {efir_id})")
        
        # Now test the update
        update_data = {
            "status": "under_investigation",
            "action_taken": "Investigation team assigned. Preliminary inquiry completed.",
            "changes_summary": "Updated status and added investigation progress"
        }
        
        async with session.put(f"{API_BASE_URL}/efir/{efir_id}", json=update_data, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ E-FIR update successful: Version {data.get('current_version', 'unknown')}")
                print(f"   Status: {data.get('status', 'unknown')}")
                print(f"   Action Taken: {data.get('action_taken', 'unknown')}")
            else:
                error_data = await response.text()
                print(f"❌ E-FIR update failed: {response.status}")
                print(f"   Error: {error_data}")
        
        # Test version history
        async with session.get(f"{API_BASE_URL}/efir/{efir_id}/history", headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                history = data.get('history', [])
                print(f"✅ Version history retrieved: {len(history)} versions")
                for version in history:
                    print(f"   Version {version['version']}: {version['changes_summary']}")
            else:
                print(f"❌ Version history failed: {response.status}")

if __name__ == "__main__":
    asyncio.run(test_efir_update())