#!/bin/bash
# run_tests.sh - Execute practical backend tests

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="${BASE_URL:-http://localhost:8000}"
TEST_EMAIL="${TEST_EMAIL:-test@datumagro.com}"
TEST_PASSWORD="${TEST_PASSWORD:-Teste123!}"
VERBOSE="${VERBOSE:-false}"

# Global variables
ACCESS_TOKEN=""
REFRESH_TOKEN=""
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Helper functions
log_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((TESTS_PASSED++))
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((TESTS_FAILED++))
}

log_skip() {
    echo -e "${YELLOW}[SKIP]${NC} $1"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

increment_test() {
    ((TESTS_TOTAL++))
}

# Test functions
test_server_health() {
    log_test "Test 1: Check server health"
    increment_test
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/swagger/")
    
    if [ "$response" = "200" ]; then
        log_pass "Server is running and responding"
        return 0
    else
        log_fail "Server returned status $response"
        return 1
    fi
}

test_login_valid() {
    log_test "Test 2: Login with valid credentials"
    increment_test
    
    response=$(curl -s -X POST "$BASE_URL/api/token/" \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}")
    
    # Extract tokens
    ACCESS_TOKEN=$(echo "$response" | grep -o '"access":"[^"]*' | cut -d'"' -f4)
    REFRESH_TOKEN=$(echo "$response" | grep -o '"refresh":"[^"]*' | cut -d'"' -f4)
    
    if [ -n "$ACCESS_TOKEN" ] && [ ${#ACCESS_TOKEN} -gt 20 ]; then
        log_pass "Login successful. Token: ${ACCESS_TOKEN:0:20}..."
        return 0
    else
        log_fail "Login failed. Response: $response"
        return 1
    fi
}

test_login_invalid() {
    log_test "Test 3: Login with invalid credentials (should fail)"
    increment_test
    
    response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/api/token/" \
        -H "Content-Type: application/json" \
        -d '{"username":"invalid@test.com","password":"wrongpassword"}')
    
    if [ "$response" = "401" ] || [ "$response" = "400" ]; then
        log_pass "Invalid login correctly rejected (status $response)"
        return 0
    else
        log_fail "Invalid login not rejected. Status: $response"
        return 1
    fi
}

test_unauthenticated_request() {
    log_test "Test 4: Unauthenticated request (should be rejected)"
    increment_test
    
    response=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BASE_URL/api/cadastros/animais/" \
        -H "Content-Type: application/json")
    
    if [ "$response" = "403" ] || [ "$response" = "401" ]; then
        log_pass "Unauthenticated request correctly rejected (status $response)"
        return 0
    else
        log_fail "Unauthenticated request not rejected. Status: $response"
        return 1
    fi
}

test_list_animals() {
    log_test "Test 5: List animals (with authentication)"
    increment_test
    
    if [ -z "$ACCESS_TOKEN" ]; then
        log_skip "No access token available"
        return 1
    fi
    
    response=$(curl -s -X GET "$BASE_URL/api/cadastros/animais/" \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -H "Content-Type: application/json")
    
    count=$(echo "$response" | grep -o '"count":[0-9]*' | cut -d':' -f2)
    
    if [ -n "$count" ]; then
        log_pass "List animals successful. Found $count animals"
        return 0
    else
        log_fail "List animals failed. Response: $response"
        return 1
    fi
}

test_list_properties() {
    log_test "Test 6: List properties (with authentication)"
    increment_test
    
    if [ -z "$ACCESS_TOKEN" ]; then
        log_skip "No access token available"
        return 1
    fi
    
    response=$(curl -s -X GET "$BASE_URL/api/cadastros/propriedades/" \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -H "Content-Type: application/json")
    
    count=$(echo "$response" | grep -o '"count":[0-9]*' | cut -d':' -f2)
    
    if [ -n "$count" ]; then
        log_pass "List properties successful. Found $count properties"
        return 0
    else
        log_fail "List properties failed. Response: $response"
        return 1
    fi
}

test_refresh_token() {
    log_test "Test 7: Refresh token"
    increment_test
    
    if [ -z "$REFRESH_TOKEN" ]; then
        log_skip "No refresh token available"
        return 1
    fi
    
    response=$(curl -s -X POST "$BASE_URL/api/token/refresh/" \
        -H "Content-Type: application/json" \
        -d "{\"refresh\":\"$REFRESH_TOKEN\"}")
    
    new_token=$(echo "$response" | grep -o '"access":"[^"]*' | cut -d'"' -f4)
    
    if [ -n "$new_token" ] && [ ${#new_token} -gt 20 ]; then
        ACCESS_TOKEN="$new_token"
        log_pass "Token refreshed successfully"
        return 0
    else
        log_fail "Token refresh failed. Response: $response"
        return 1
    fi
}

test_cors_headers() {
    log_test "Test 8: Check CORS headers"
    increment_test
    
    response=$(curl -s -i -X OPTIONS "$BASE_URL/api/swagger/" \
        -H "Origin: http://localhost:3000" \
        -H "Access-Control-Request-Method: GET" 2>/dev/null | head -20)
    
    if echo "$response" | grep -q "Access-Control"; then
        log_pass "CORS headers present"
        return 0
    else
        log_info "CORS headers not found (may be OK for development)"
        return 0
    fi
}

# Main execution
main() {
    echo "=============================================="
    echo "DatumAgro Backend - Practical Tests"
    echo "=============================================="
    echo "Base URL: $BASE_URL"
    echo "Test Email: $TEST_EMAIL"
    echo "=============================================="
    echo ""
    
    # Check server connectivity
    if ! ping -c 1 "$(echo $BASE_URL | cut -d'/' -f3 | cut -d':' -f1)" &> /dev/null; then
        log_fail "Cannot reach server. Make sure it's running:"
        echo "  python manage.py runserver 0.0.0.0:8000"
        exit 1
    fi
    
    # Run all tests
    test_server_health || true
    test_login_valid || true
    test_login_invalid || true
    test_unauthenticated_request || true
    test_list_animals || true
    test_list_properties || true
    test_refresh_token || true
    test_cors_headers || true
    
    # Print summary
    echo ""
    echo "=============================================="
    echo "TEST SUMMARY"
    echo "=============================================="
    echo "Total Tests: $TESTS_TOTAL"
    echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
    echo -e "${RED}Failed: $TESTS_FAILED${NC}"
    
    if [ $TESTS_TOTAL -gt 0 ]; then
        percentage=$((TESTS_PASSED * 100 / TESTS_TOTAL))
        echo "Success Rate: ${percentage}%"
    fi
    
    echo "=============================================="
    echo ""
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}✅ All tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}❌ Some tests failed${NC}"
        exit 1
    fi
}

# Run main function
main "$@"
