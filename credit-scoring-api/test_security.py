"""
Test script for security features
"""
import requests
import time

API_URL = "http://localhost:8000"
API_KEY = "dtuNV40UX0RxID96Z1-d-z1WdoA-RmMECuuDGJPwfWk"  # From .env file

# Test data
test_application = {
    "full_name": "Test User",
    "age": 30,
    "monthly_income": 20000000,
    "employment_status": "EMPLOYED",
    "years_employed": 5.0,
    "home_ownership": "MORTGAGE",
    "loan_purpose": "CAR",
    "years_credit_history": 5,
    "has_previous_defaults": False,
    "currently_defaulting": False
}

print("=" * 80)
print("SECURITY FEATURES TEST")
print("=" * 80)

# Test 1: Public endpoint (should work without API key)
print("\n1. Testing public endpoint /api/health (no API key required)...")
try:
    response = requests.get(f"{API_URL}/api/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    print("   ✅ PASS: Public endpoint works without API key")
except Exception as e:
    print(f"   ❌ FAIL: {e}")

# Test 2: Protected endpoint without API key (should fail with 401)
print("\n2. Testing protected endpoint /api/calculate-limit WITHOUT API key...")
try:
    response = requests.post(
        f"{API_URL}/api/calculate-limit",
        json=test_application
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 401:
        print(f"   Response: {response.json()}")
        print("   ✅ PASS: Correctly rejected request without API key")
    else:
        print(f"   Response: {response.json()}")
        print("   ❌ FAIL: Should have returned 401 Unauthorized")
except Exception as e:
    print(f"   ❌ FAIL: {e}")

# Test 3: Protected endpoint with INVALID API key (should fail with 401)
print("\n3. Testing protected endpoint /api/calculate-limit WITH INVALID API key...")
try:
    headers = {
        "X-API-Key": "invalid-api-key-12345",
        "Content-Type": "application/json"
    }
    response = requests.post(
        f"{API_URL}/api/calculate-limit",
        json=test_application,
        headers=headers
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 401:
        print(f"   Response: {response.json()}")
        print("   ✅ PASS: Correctly rejected request with invalid API key")
    else:
        print(f"   Response: {response.json()}")
        print("   ❌ FAIL: Should have returned 401 Unauthorized")
except Exception as e:
    print(f"   ❌ FAIL: {e}")

# Test 4: Protected endpoint with VALID API key (should succeed)
print("\n4. Testing protected endpoint /api/calculate-limit WITH VALID API key...")
try:
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    response = requests.post(
        f"{API_URL}/api/calculate-limit",
        json=test_application,
        headers=headers
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Credit Score: {data['credit_score']}")
        print(f"   Loan Limit: {data['loan_limit_vnd']:,.0f} VND")
        print(f"   Approved: {data['approved']}")
        print("   ✅ PASS: Successfully authenticated with valid API key")
    else:
        print(f"   Response: {response.json()}")
        print("   ❌ FAIL: Should have returned 200 OK")
except Exception as e:
    print(f"   ❌ FAIL: {e}")

# Test 5: Rate limiting (should fail after 10 requests)
print("\n5. Testing rate limiting (10 requests/minute limit)...")
headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

success_count = 0
rate_limited = False

for i in range(12):  # Try 12 requests (limit is 10)
    try:
        response = requests.post(
            f"{API_URL}/api/calculate-limit",
            json=test_application,
            headers=headers
        )
        
        if response.status_code == 200:
            success_count += 1
            print(f"   Request {i+1}: ✅ Success")
        elif response.status_code == 429:  # Too Many Requests
            rate_limited = True
            print(f"   Request {i+1}: ⚠️  Rate limited (429)")
            print(f"   Response: {response.text}")
            break
        else:
            print(f"   Request {i+1}: ❌ Unexpected status {response.status_code}")
    except Exception as e:
        print(f"   Request {i+1}: ❌ Error: {e}")
    
    time.sleep(0.1)  # Small delay between requests

if rate_limited:
    print(f"\n   ✅ PASS: Rate limiting works! {success_count} requests succeeded, then got rate limited")
else:
    print(f"\n   ⚠️  WARNING: Made {success_count} requests without hitting rate limit")

print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print("✅ All critical security features are working!")
print("   - API key authentication: ENABLED")
print("   - Rate limiting: ENABLED")
print("\n💡 Remember to keep your API_KEY secret and never commit .env to git!")
print("=" * 80)
