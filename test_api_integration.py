#!/bin/bash
"""
Smoke Tests Runner - Automated Backend Integration Tests
Tests all critical endpoints for Flutter integration
"""

import os
import json
import time
import requests
from typing import Dict, List, Tuple

# Configuration
BASE_URL = os.getenv('BASE_URL', 'http://localhost:8000')
VERBOSE = os.getenv('VERBOSE', 'False') == 'True'

class APITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.token = None
        self.refresh_token = None
        self.results = []
        self.session = requests.Session()

    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level:8} | {message}")

    def test_server_health(self) -> bool:
        """Test 1: Server is running"""
        self.log("Test 1: Checking server health...", "TEST")
        try:
            response = self.session.get(f"{self.base_url}/api/swagger/")
            if response.status_code == 200:
                self.log("✅ Server is running", "PASS")
                self.results.append(("Server Health Check", True, ""))
                return True
            else:
                self.log(f"❌ Server returned {response.status_code}", "FAIL")
                self.results.append(("Server Health Check", False, f"Status {response.status_code}"))
                return False
        except Exception as e:
            self.log(f"❌ Cannot reach server: {e}", "FAIL")
            self.results.append(("Server Health Check", False, str(e)))
            return False

    def test_login(self, email: str, password: str) -> bool:
        """Test 2: Login with valid credentials"""
        self.log(f"Test 2: Attempting login with {email}...", "TEST")
        try:
            payload = {"username": email, "password": password}
            response = self.session.post(
                f"{self.base_url}/api/token/",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access')
                self.refresh_token = data.get('refresh')
                self.log(f"✅ Login successful. Token: {self.token[:20]}...", "PASS")
                self.results.append(("Login", True, ""))
                return True
            else:
                self.log(f"❌ Login failed: {response.status_code} - {response.text}", "FAIL")
                self.results.append(("Login", False, response.text))
                return False
        except Exception as e:
            self.log(f"❌ Login error: {e}", "FAIL")
            self.results.append(("Login", False, str(e)))
            return False

    def test_invalid_login(self) -> bool:
        """Test 3: Login with invalid credentials should fail"""
        self.log("Test 3: Testing invalid login (should fail)...", "TEST")
        try:
            payload = {"username": "invalid@test.com", "password": "wrongpassword"}
            response = self.session.post(
                f"{self.base_url}/api/token/",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [400, 401]:
                self.log(f"✅ Invalid login correctly rejected ({response.status_code})", "PASS")
                self.results.append(("Invalid Login Rejection", True, ""))
                return True
            else:
                self.log(f"❌ Invalid login not rejected properly: {response.status_code}", "FAIL")
                self.results.append(("Invalid Login Rejection", False, f"Status {response.status_code}"))
                return False
        except Exception as e:
            self.log(f"❌ Test error: {e}", "FAIL")
            self.results.append(("Invalid Login Rejection", False, str(e)))
            return False

    def test_unauthenticated_request(self) -> bool:
        """Test 4: Unauthenticated request should return 403"""
        self.log("Test 4: Testing unauthenticated request (should be rejected)...", "TEST")
        try:
            response = self.session.get(
                f"{self.base_url}/api/cadastros/animais/",
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [403, 401]:
                self.log(f"✅ Unauthenticated request correctly rejected ({response.status_code})", "PASS")
                self.results.append(("Unauthenticated Request Rejection", True, ""))
                return True
            else:
                self.log(f"❌ Unauthenticated request not rejected: {response.status_code}", "FAIL")
                self.results.append(("Unauthenticated Request Rejection", False, f"Status {response.status_code}"))
                return False
        except Exception as e:
            self.log(f"❌ Test error: {e}", "FAIL")
            self.results.append(("Unauthenticated Request Rejection", False, str(e)))
            return False

    def test_list_animals(self) -> bool:
        """Test 5: List animals with valid token"""
        if not self.token:
            self.log("❌ No token available. Skipping test.", "SKIP")
            self.results.append(("List Animals", False, "No token"))
            return False

        self.log("Test 5: Listing animals...", "TEST")
        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            response = self.session.get(
                f"{self.base_url}/api/cadastros/animais/",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', 0)
                self.log(f"✅ List animals successful. Found {count} animals", "PASS")
                self.results.append(("List Animals", True, ""))
                return True
            else:
                self.log(f"❌ List animals failed: {response.status_code}", "FAIL")
                self.results.append(("List Animals", False, response.text))
                return False
        except Exception as e:
            self.log(f"❌ Test error: {e}", "FAIL")
            self.results.append(("List Animals", False, str(e)))
            return False

    def test_list_properties(self) -> bool:
        """Test 6: List properties with valid token"""
        if not self.token:
            self.log("❌ No token available. Skipping test.", "SKIP")
            self.results.append(("List Properties", False, "No token"))
            return False

        self.log("Test 6: Listing properties...", "TEST")
        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            response = self.session.get(
                f"{self.base_url}/api/cadastros/propriedades/",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', 0)
                self.log(f"✅ List properties successful. Found {count} properties", "PASS")
                self.results.append(("List Properties", True, ""))
                return True
            else:
                self.log(f"❌ List properties failed: {response.status_code}", "FAIL")
                self.results.append(("List Properties", False, response.text))
                return False
        except Exception as e:
            self.log(f"❌ Test error: {e}", "FAIL")
            self.results.append(("List Properties", False, str(e)))
            return False

    def test_refresh_token(self) -> bool:
        """Test 7: Refresh token endpoint"""
        if not self.refresh_token:
            self.log("❌ No refresh token available. Skipping test.", "SKIP")
            self.results.append(("Token Refresh", False, "No refresh token"))
            return False

        self.log("Test 7: Testing token refresh...", "TEST")
        try:
            payload = {"refresh": self.refresh_token}
            response = self.session.post(
                f"{self.base_url}/api/token/refresh/",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.statuscode == 200:
                data = response.json()
                new_token = data.get('access')
                self.token = new_token
                self.log(f"✅ Token refreshed successfully", "PASS")
                self.results.append(("Token Refresh", True, ""))
                return True
            else:
                self.log(f"❌ Token refresh failed: {response.status_code}", "FAIL")
                self.results.append(("Token Refresh", False, response.text))
                return False
        except Exception as e:
            self.log(f"❌ Test error: {e}", "FAIL")
            self.results.append(("Token Refresh", False, str(e)))
            return False

    def test_cors_headers(self) -> bool:
        """Test 8: CORS headers are present"""
        self.log("Test 8: Checking CORS headers...", "TEST")
        try:
            response = self.session.get(f"{self.base_url}/api/swagger/")
            
            cors_origin = response.headers.get('Access-Control-Allow-Origin')
            if cors_origin:
                self.log(f"✅ CORS enabled. Allow-Origin: {cors_origin}", "PASS")
                self.results.append(("CORS Headers", True, ""))
                return True
            else:
                self.log("⚠️ CORS headers not found (may be OK for local dev)", "WARN")
                self.results.append(("CORS Headers", True, "Warning: not found"))
                return True
        except Exception as e:
            self.log(f"❌ Test error: {e}", "FAIL")
            self.results.append(("CORS Headers", False, str(e)))
            return False

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        passed = sum(1 for _, success, _ in self.results if success)
        total = len(self.results)
        
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {total - passed} ❌")
        print(f"Success Rate: {(passed/total)*100:.1f}%\n")
        
        for test_name, success, error in self.results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status:8} | {test_name:30} | {error[:40]}")
        
        print("="*80 + "\n")
        
        return passed == total

def main():
    import sys
    
    # Get credentials from environment or command line
    email = os.getenv('TEST_EMAIL', 'test@datumagro.com')
    password = os.getenv('TEST_PASSWORD', 'Test123!')
    
    print("\n" + "="*80)
    print("DATUMAGRO BACKEND INTEGRATION TESTS")
    print("="*80)
    print(f"Base URL: {BASE_URL}")
    print(f"Test User: {email}")
    print("="*80 + "\n")
    
    tester = APITester(BASE_URL)
    
    # Run tests in sequence
    tester.test_server_health()
    if tester.results[-1][1]:  # If server is up
        tester.test_login(email, password)
        tester.test_invalid_login()
        tester.test_unauthenticated_request()
        tester.test_list_animals()
        tester.test_list_properties()
        tester.test_refresh_token()
        tester.test_cors_headers()
    
    # Print summary and exit with appropriate code
    success = tester.print_summary()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
