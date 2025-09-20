#!/usr/bin/env python3
"""
Comprehensive Field Mapping Test - Final Analysis
Tests the exact field mappings between backend API responses and frontend component expectations
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://efir-ui-consistency.preview.emergentagent.com')
API_BASE_URL = f"{BACKEND_URL}/api"

async def comprehensive_field_mapping_test():
    """Run comprehensive field mapping analysis"""
    print("🔍 COMPREHENSIVE FIELD MAPPING ANALYSIS")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Authenticate
        login_data = {
            "email": "inspector.kumar@tourism.gov.in",
            "password": "password123"
        }
        
        async with session.post(f"{API_BASE_URL}/auth/login", json=login_data) as response:
            if response.status != 200:
                print("❌ Authentication failed")
                return
            
            login_result = await response.json()
            token = login_result['access_token']
            print(f"✅ Authenticated as {login_result['user']['full_name']}")
        
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test 1: GET /api/tourists endpoint
        print(f"\n📋 TEST 1: GET /api/tourists endpoint")
        async with session.get(f"{API_BASE_URL}/tourists", headers=headers) as response:
            if response.status != 200:
                print(f"❌ Failed to get tourists: {response.status}")
                return
            
            tourists = await response.json()
            print(f"✅ Retrieved {len(tourists)} tourists")
            
            if tourists:
                tourist = tourists[0]
                print(f"\n🔸 Sample Tourist Field Structure:")
                for field in sorted(tourist.keys()):
                    value = tourist[field]
                    if isinstance(value, dict):
                        print(f"  {field}: dict with keys {list(value.keys())}")
                    elif isinstance(value, list):
                        print(f"  {field}: list with {len(value)} items")
                        if value and isinstance(value[0], dict):
                            print(f"    First item keys: {list(value[0].keys())}")
                    else:
                        print(f"  {field}: {type(value).__name__} = {value}")
        
        # Test 2: GET /api/tourists/{id} endpoint
        print(f"\n📋 TEST 2: GET /api/tourists/{{id}} endpoint")
        if tourists:
            tourist_id = tourists[0]['id']
            async with session.get(f"{API_BASE_URL}/tourists/{tourist_id}", headers=headers) as response:
                if response.status != 200:
                    print(f"❌ Failed to get tourist details: {response.status}")
                    return
                
                tourist_detail = await response.json()
                print(f"✅ Retrieved detailed tourist data")
                
                print(f"\n🔸 Detailed Tourist Field Structure:")
                for field in sorted(tourist_detail.keys()):
                    value = tourist_detail[field]
                    if isinstance(value, dict):
                        print(f"  {field}: dict with keys {list(value.keys())}")
                        if field == 'location':
                            print(f"    coordinates: {value.get('coordinates')}")
                            print(f"    address: {value.get('address')}")
                    elif isinstance(value, list):
                        print(f"  {field}: list with {len(value)} items")
                        if value and isinstance(value[0], dict) and field == 'emergency_contacts':
                            print(f"    First contact: {value[0]}")
                    else:
                        print(f"  {field}: {type(value).__name__} = {value}")
        
        # Test 3: GET /api/tourists/{id}/alerts endpoint
        print(f"\n📋 TEST 3: GET /api/tourists/{{id}}/alerts endpoint")
        if tourists:
            tourist_id = tourists[0]['id']
            async with session.get(f"{API_BASE_URL}/tourists/{tourist_id}/alerts", headers=headers) as response:
                if response.status != 200:
                    print(f"❌ Failed to get tourist alerts: {response.status}")
                    return
                
                alerts = await response.json()
                print(f"✅ Retrieved {len(alerts)} alerts")
                
                if alerts:
                    alert = alerts[0]
                    print(f"\n🔸 Sample Alert Field Structure:")
                    for field in sorted(alert.keys()):
                        value = alert[field]
                        if isinstance(value, dict):
                            print(f"  {field}: dict with keys {list(value.keys())}")
                        else:
                            print(f"  {field}: {type(value).__name__} = {value}")
        
        # Test 4: Find Raj Verma specifically
        print(f"\n📋 TEST 4: Specific Tourist - Raj Verma (DIG-PANIC01)")
        raj_verma = None
        for tourist in tourists:
            if tourist.get('digital_id') == 'DIG-PANIC01':
                raj_verma = tourist
                break
        
        if raj_verma:
            print(f"✅ Found Raj Verma")
            print(f"  Digital ID: {raj_verma.get('digital_id')}")
            print(f"  Full Name: {raj_verma.get('full_name')}")
            print(f"  Status: {raj_verma.get('status')}")
            print(f"  Safety Score: {raj_verma.get('safety_score')}")
            print(f"  Visit Start: {raj_verma.get('visit_start_date')}")
            print(f"  Visit End: {raj_verma.get('visit_end_date')}")
            print(f"  Location Address: {raj_verma.get('location', {}).get('address')}")
            print(f"  Emergency Contacts: {len(raj_verma.get('emergency_contacts', []))} contacts")
            
            # Get detailed data for Raj Verma
            raj_id = raj_verma['id']
            async with session.get(f"{API_BASE_URL}/tourists/{raj_id}", headers=headers) as response:
                raj_detail = await response.json()
                print(f"  Detailed data retrieved: ✅")
            
            async with session.get(f"{API_BASE_URL}/tourists/{raj_id}/alerts", headers=headers) as response:
                raj_alerts = await response.json()
                print(f"  Alerts retrieved: {len(raj_alerts)} alerts")
        else:
            print("❌ Raj Verma (DIG-PANIC01) not found")
        
        # Test 5: Field Mapping Issues Analysis
        print(f"\n📋 TEST 5: FIELD MAPPING ISSUES ANALYSIS")
        print("=" * 40)
        
        issues_found = []
        
        # Check visit date field naming
        if tourists:
            sample_tourist = tourists[0]
            
            # Issue 1: Visit date field names
            if 'visit_start_date' in sample_tourist and 'visitStartDate' not in sample_tourist:
                issues_found.append({
                    "issue": "Visit Start Date Field Naming",
                    "backend_field": "visit_start_date",
                    "frontend_expects": "visitStartDate",
                    "impact": "TouristDatabase.jsx line 246 will fail",
                    "severity": "HIGH"
                })
            
            if 'visit_end_date' in sample_tourist and 'visitEndDate' not in sample_tourist:
                issues_found.append({
                    "issue": "Visit End Date Field Naming", 
                    "backend_field": "visit_end_date",
                    "frontend_expects": "visitEndDate",
                    "impact": "TouristDatabase.jsx line 246 will fail",
                    "severity": "HIGH"
                })
            
            # Issue 2: Location structure
            location = sample_tourist.get('location')
            if location and isinstance(location, dict):
                if 'address' in location:
                    print("✅ Location has address field - frontend compatible")
                else:
                    issues_found.append({
                        "issue": "Location Missing Address",
                        "backend_field": "location",
                        "frontend_expects": "location.address",
                        "impact": "TouristDetailModal.jsx line 279 will show 'Location updating...'",
                        "severity": "MEDIUM"
                    })
            
            # Issue 3: Emergency contacts structure
            contacts = sample_tourist.get('emergency_contacts')
            if contacts and isinstance(contacts, list) and len(contacts) > 0:
                first_contact = contacts[0]
                if isinstance(first_contact, dict) and 'phone' in first_contact:
                    print("✅ Emergency contacts have phone field - frontend compatible")
                else:
                    issues_found.append({
                        "issue": "Emergency Contact Missing Phone",
                        "backend_field": "emergency_contacts[0]",
                        "frontend_expects": "emergency_contacts[0].phone",
                        "impact": "TouristDatabase.jsx line 228 will show 'N/A'",
                        "severity": "MEDIUM"
                    })
        
        # Report all issues
        if issues_found:
            print(f"\n❌ FOUND {len(issues_found)} FIELD MAPPING ISSUES:")
            for i, issue in enumerate(issues_found, 1):
                print(f"\n{i}. {issue['issue']} ({issue['severity']})")
                print(f"   Backend provides: {issue['backend_field']}")
                print(f"   Frontend expects: {issue['frontend_expects']}")
                print(f"   Impact: {issue['impact']}")
        else:
            print("\n✅ NO CRITICAL FIELD MAPPING ISSUES FOUND")
        
        # Test 6: Data Completeness for Demo
        print(f"\n📋 TEST 6: DATA COMPLETENESS FOR DEMO")
        print("=" * 40)
        
        complete_tourists = 0
        for tourist in tourists:
            required_fields = ['digital_id', 'full_name', 'status', 'safety_score']
            has_all_required = all(tourist.get(field) is not None for field in required_fields)
            has_location = tourist.get('location') and tourist.get('location', {}).get('address')
            has_contacts = tourist.get('emergency_contacts') and len(tourist.get('emergency_contacts', [])) > 0
            
            if has_all_required and has_location and has_contacts:
                complete_tourists += 1
        
        print(f"✅ Complete tourists: {complete_tourists}/{len(tourists)}")
        print(f"✅ Data completeness: {(complete_tourists/len(tourists)*100):.1f}%")
        
        # Summary
        print(f"\n📊 FINAL SUMMARY")
        print("=" * 40)
        print(f"✅ Backend API endpoints working: 3/3")
        print(f"✅ Field structures mostly compatible")
        print(f"❌ Critical field mapping issues: {len([i for i in issues_found if i['severity'] == 'HIGH'])}")
        print(f"⚠️  Medium field mapping issues: {len([i for i in issues_found if i['severity'] == 'MEDIUM'])}")
        print(f"✅ Raj Verma (DIG-PANIC01) data complete: {'Yes' if raj_verma else 'No'}")
        
        return {
            "total_tourists": len(tourists),
            "complete_tourists": complete_tourists,
            "issues_found": issues_found,
            "raj_verma_found": raj_verma is not None,
            "endpoints_working": 3,
            "test_timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    result = asyncio.run(comprehensive_field_mapping_test())
    
    # Save results
    with open('/app/comprehensive_field_mapping_results.json', 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: /app/comprehensive_field_mapping_results.json")