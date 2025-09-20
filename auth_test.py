#!/usr/bin/env python3
"""
Authentication-Focused Backend Testing for Tourism Safety System
Tests authentication functionality specifically as requested:
1. Test login endpoint POST /api/auth/login with demo credentials
2. Verify authentication is working with demo accounts
3. Test a few key protected endpoints after login

Focus: User reported they cannot login through demo accounts after UI changes.
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://efir-ui-consistency.preview.emergentagent.com')
API_BASE_URL = f"{BACKEND_URL}/api"

class AuthenticationTester:
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
    
    async def test_demo_account_login(self):
        """Test login with demo account credentials"""
        print("\n=== Testing Demo Account Login ===")
        
        # Demo credentials based on test_result.md
        demo_accounts = [
            {
                "email": "inspector.kumar@tourism.gov.in",
                "password": "password123",
                "name": "Inspector Kumar"
            },
            {
                "email": "admin@tourism.gov.in", 
                "password": "admin123",
                "name": "Admin User"
            },
            {
                "email": "police.officer@tourism.gov.in",
                "password": "police123", 
                "name": "Police Officer"
            }
        ]
        
        successful_logins = 0
        
        for account in demo_accounts:
            login_data = {
                "email": account["email"],
                "password": account["password"]
            }
            
            success, data, status = await self.make_request("POST", "/auth/login", login_data)
            
            if success and status == 200 and isinstance(data, dict) and 'access_token' in data:
                # Store token from first successful login
                if not self.auth_token:
                    self.auth_token = data['access_token']
                
                user_info = data.get('user', {})
                successful_logins += 1
                
                self.log_test(
                    f"Demo Login - {account['name']}", 
                    True,
                    f"Status: {status}, User: {user_info.get('full_name', 'Unknown')}, " +
                    f"Role: {user_info.get('role', 'Unknown')}, Token received: {bool(data.get('access_token'))}"
                )
                
                # Validate token format
                token = data.get('access_token', '')
                token_valid_format = len(token) > 50 and '.' in token  # Basic JWT format check
                
                self.log_test(
                    f"Token Format - {account['name']}", 
                    token_valid_format,
                    f"Token length: {len(token)}, Has JWT structure: {'.' in token}"
                )
                
                # Validate user response structure
                required_user_fields = ['id', 'email', 'full_name', 'role']
                missing_fields = [field for field in required_user_fields if field not in user_info]
                
                self.log_test(
                    f"User Response Structure - {account['name']}", 
                    len(missing_fields) == 0,
                    f"Missing fields: {missing_fields}, Present fields: {list(user_info.keys())}"
                )
                
            else:
                self.log_test(
                    f"Demo Login - {account['name']}", 
                    False,
                    f"Status: {status}, Response: {data}"
                )
        
        # Overall demo login success
        self.log_test(
            "Demo Accounts Overall", 
            successful_logins > 0,
            f"Successful logins: {successful_logins}/{len(demo_accounts)}"
        )
        
        return successful_logins > 0
    
    async def test_invalid_login_attempts(self):
        """Test login with invalid credentials"""
        print("\n=== Testing Invalid Login Attempts ===")
        
        invalid_attempts = [
            {
                "email": "inspector.kumar@tourism.gov.in",
                "password": "wrongpassword",
                "name": "Valid Email, Wrong Password"
            },
            {
                "email": "nonexistent@tourism.gov.in",
                "password": "password123",
                "name": "Invalid Email, Valid Password"
            },
            {
                "email": "invalid-email-format",
                "password": "password123",
                "name": "Malformed Email"
            },
            {
                "email": "",
                "password": "password123",
                "name": "Empty Email"
            },
            {
                "email": "inspector.kumar@tourism.gov.in",
                "password": "",
                "name": "Empty Password"
            }
        ]
        
        for attempt in invalid_attempts:
            login_data = {
                "email": attempt["email"],
                "password": attempt["password"]
            }
            
            success, data, status = await self.make_request("POST", "/auth/login", login_data)
            
            # Should fail with 401 or 422 status
            expected_failure = not success and status in [401, 422]
            
            self.log_test(
                f"Invalid Login - {attempt['name']}", 
                expected_failure,
                f"Status: {status}, Expected failure: {expected_failure}, Response: {data}"
            )
    
    async def test_protected_endpoints_with_auth(self):
        """Test key protected endpoints with valid authentication"""
        print("\n=== Testing Protected Endpoints with Authentication ===")
        
        if not self.auth_token:
            self.log_test("Protected Endpoints", False, "No auth token available")
            return
        
        # Test key protected endpoints
        protected_endpoints = [
            {
                "method": "GET",
                "endpoint": "/auth/me",
                "name": "Get Current User Info",
                "expected_fields": ["id", "email", "full_name", "role"]
            },
            {
                "method": "GET", 
                "endpoint": "/tourists",
                "name": "Get All Tourists",
                "expected_type": list
            },
            {
                "method": "GET",
                "endpoint": "/alerts", 
                "name": "Get All Alerts",
                "expected_type": list
            },
            {
                "method": "GET",
                "endpoint": "/analytics/dashboard",
                "name": "Get Dashboard KPIs",
                "expected_fields": ["total_active_tourists", "active_alerts"]
            },
            {
                "method": "GET",
                "endpoint": "/geofences",
                "name": "Get Geofences",
                "expected_type": list
            }
        ]
        
        for endpoint_test in protected_endpoints:
            success, data, status = await self.make_request(
                endpoint_test["method"], 
                endpoint_test["endpoint"]
            )
            
            # Check if request succeeded
            request_success = success and status == 200
            
            # Check response format
            format_valid = True
            format_details = []
            
            if "expected_type" in endpoint_test:
                if not isinstance(data, endpoint_test["expected_type"]):
                    format_valid = False
                    format_details.append(f"Expected {endpoint_test['expected_type'].__name__}, got {type(data).__name__}")
            
            if "expected_fields" in endpoint_test and isinstance(data, dict):
                missing_fields = [field for field in endpoint_test["expected_fields"] if field not in data]
                if missing_fields:
                    format_valid = False
                    format_details.append(f"Missing fields: {missing_fields}")
            
            self.log_test(
                f"Protected Endpoint - {endpoint_test['name']}", 
                request_success and format_valid,
                f"Status: {status}, Format valid: {format_valid}" + 
                (f", Issues: {'; '.join(format_details)}" if format_details else "")
            )
    
    async def test_protected_endpoints_without_auth(self):
        """Test protected endpoints without authentication"""
        print("\n=== Testing Protected Endpoints without Authentication ===")
        
        # Temporarily remove auth token
        temp_token = self.auth_token
        self.auth_token = None
        
        protected_endpoints = [
            "/auth/me",
            "/tourists", 
            "/alerts",
            "/analytics/dashboard"
        ]
        
        for endpoint in protected_endpoints:
            success, data, status = await self.make_request("GET", endpoint)
            
            # Should fail with 401 or 403
            expected_failure = not success and status in [401, 403]
            
            self.log_test(
                f"No Auth - {endpoint}", 
                expected_failure,
                f"Status: {status}, Expected failure: {expected_failure}"
            )
        
        # Restore auth token
        self.auth_token = temp_token
    
    async def test_token_validation(self):
        """Test token validation with invalid tokens"""
        print("\n=== Testing Token Validation ===")
        
        invalid_tokens = [
            "invalid_token_format",
            "Bearer invalid_token",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature",  # Invalid JWT
            "",  # Empty token
            "expired_token_here"  # Simulated expired token
        ]
        
        for token in invalid_tokens:
            headers = {"Authorization": f"Bearer {token}"}
            success, data, status = await self.make_request("GET", "/auth/me", headers=headers)
            
            # Should fail with 401
            expected_failure = not success and status == 401
            
            self.log_test(
                f"Invalid Token - {token[:20]}...", 
                expected_failure,
                f"Status: {status}, Expected 401 for invalid token"
            )
    
    async def test_authentication_flow_end_to_end(self):
        """Test complete authentication flow"""
        print("\n=== Testing End-to-End Authentication Flow ===")
        
        # Step 1: Login with demo account
        login_data = {
            "email": "inspector.kumar@tourism.gov.in",
            "password": "password123"
        }
        
        success, data, status = await self.make_request("POST", "/auth/login", login_data)
        
        if not (success and status == 200 and isinstance(data, dict) and 'access_token' in data):
            self.log_test("E2E Authentication Flow", False, "Failed at login step")
            return
        
        # Step 2: Use token to access protected resource
        token = data['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        
        success, user_data, status = await self.make_request("GET", "/auth/me", headers=headers)
        
        if not (success and status == 200 and isinstance(user_data, dict)):
            self.log_test("E2E Authentication Flow", False, "Failed at token validation step")
            return
        
        # Step 3: Verify user data consistency
        login_user = data.get('user', {})
        me_user = user_data
        
        consistency_check = (
            login_user.get('id') == me_user.get('id') and
            login_user.get('email') == me_user.get('email') and
            login_user.get('full_name') == me_user.get('full_name')
        )
        
        # Step 4: Test accessing multiple protected endpoints
        endpoints_tested = 0
        endpoints_successful = 0
        
        test_endpoints = ["/tourists", "/alerts", "/analytics/dashboard"]
        
        for endpoint in test_endpoints:
            endpoints_tested += 1
            success, _, status = await self.make_request("GET", endpoint, headers=headers)
            if success and status == 200:
                endpoints_successful += 1
        
        # Overall E2E success
        e2e_success = (
            consistency_check and 
            endpoints_successful == endpoints_tested
        )
        
        self.log_test(
            "E2E Authentication Flow", 
            e2e_success,
            f"Login: ✓, Token validation: ✓, User consistency: {consistency_check}, " +
            f"Protected endpoints: {endpoints_successful}/{endpoints_tested}"
        )
    
    async def run_authentication_tests(self):
        """Run all authentication tests"""
        print(f"🔐 Starting Authentication-Focused Tests")
        print(f"📍 Backend URL: {API_BASE_URL}")
        print(f"🎯 Focus: Demo account login issues after UI changes")
        print("=" * 60)
        
        # Run authentication tests
        login_success = await self.test_demo_account_login()
        await self.test_invalid_login_attempts()
        
        if login_success:
            await self.test_protected_endpoints_with_auth()
            await self.test_authentication_flow_end_to_end()
        else:
            print("⚠️  Skipping protected endpoint tests due to login failures")
        
        await self.test_protected_endpoints_without_auth()
        await self.test_token_validation()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 AUTHENTICATION TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Critical authentication analysis
        critical_tests = [
            "Demo Login - Inspector Kumar",
            "E2E Authentication Flow",
            "Protected Endpoint - Get Current User Info"
        ]
        
        critical_failures = []
        for test_name in critical_tests:
            if test_name in self.test_results and not self.test_results[test_name]['success']:
                critical_failures.append(test_name)
        
        if critical_failures:
            print(f"\n🚨 CRITICAL AUTHENTICATION FAILURES:")
            for failure in critical_failures:
                print(f"  ❌ {failure}: {self.test_results[failure]['details']}")
        
        if failed_tests > 0:
            print(f"\n🔍 ALL FAILED TESTS:")
            for test_name, result in self.test_results.items():
                if not result['success']:
                    print(f"  ❌ {test_name}: {result['details']}")
        
        return self.test_results

async def main():
    """Main test runner"""
    async with AuthenticationTester() as tester:
        results = await tester.run_authentication_tests()
        
        # Save results to file
        with open('/app/auth_test_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Authentication test results saved to: /app/auth_test_results.json")
        
        return results

if __name__ == "__main__":
    asyncio.run(main())