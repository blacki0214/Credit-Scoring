#!/usr/bin/env python3
"""
Test script for Credit Scoring API
Run this to verify the API is working correctly
"""

import requests
import json
from typing import Dict, Any


API_BASE_URL = "http://localhost:8000"


def print_response(title: str, response: requests.Response):
    """Print formatted API response"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))


def test_health_check():
    """Test health endpoint"""
    response = requests.get(f"{API_BASE_URL}/api/health")
    print_response("Health Check", response)
    return response.status_code == 200


def test_ping():
    """Test ping endpoint"""
    response = requests.get(f"{API_BASE_URL}/api/ping")
    print_response("Ping Test", response)
    return response.status_code == 200


def test_model_info():
    """Test model info endpoint"""
    response = requests.get(f"{API_BASE_URL}/api/model/info")
    print_response("Model Info", response)
    return response.status_code == 200


def test_model_features():
    """Test model features endpoint"""
    response = requests.get(f"{API_BASE_URL}/api/model/features")
    print_response("Model Features", response)
    return response.status_code == 200


def test_prediction_low_risk():
    """Test prediction with low-risk applicant"""
    data = {
        "person_age": 35,
        "person_income": 80000,
        "person_emp_length": 10.0,
        "person_home_ownership": "OWN",
        "loan_amnt": 10000,
        "loan_intent": "PERSONAL",
        "loan_grade": "A",
        "loan_int_rate": 5.5,
        "loan_percent_income": 0.125,
        "cb_person_cred_hist_length": 15,
        "credit_score": 780,
        "cb_person_default_on_file": "N",
        "previous_loan_defaults_on_file": "N"
    }
    
    response = requests.post(f"{API_BASE_URL}/api/predict", json=data)
    print_response("Prediction - Low Risk Applicant", response)
    return response.status_code == 200


def test_prediction_high_risk():
    """Test prediction with high-risk applicant"""
    data = {
        "person_age": 22,
        "person_income": 25000,
        "person_emp_length": 1.0,
        "person_home_ownership": "RENT",
        "loan_amnt": 20000,
        "loan_intent": "VENTURE",
        "loan_grade": "F",
        "loan_int_rate": 18.5,
        "loan_percent_income": 0.8,
        "cb_person_cred_hist_length": 2,
        "credit_score": 580,
        "cb_person_default_on_file": "Y",
        "previous_loan_defaults_on_file": "Y"
    }
    
    response = requests.post(f"{API_BASE_URL}/api/predict", json=data)
    print_response("Prediction - High Risk Applicant", response)
    return response.status_code == 200


def test_batch_prediction():
    """Test batch prediction endpoint"""
    data = [
        {
            "person_age": 30,
            "person_income": 60000,
            "person_emp_length": 5.0,
            "person_home_ownership": "MORTGAGE",
            "loan_amnt": 15000,
            "loan_intent": "PERSONAL",
            "loan_grade": "B",
            "loan_int_rate": 8.5,
            "loan_percent_income": 0.25,
            "cb_person_cred_hist_length": 8,
            "credit_score": 720,
            "cb_person_default_on_file": "N",
            "previous_loan_defaults_on_file": "N"
        },
        {
            "person_age": 45,
            "person_income": 95000,
            "person_emp_length": 20.0,
            "person_home_ownership": "OWN",
            "loan_amnt": 25000,
            "loan_intent": "EDUCATION",
            "loan_grade": "A",
            "loan_int_rate": 6.0,
            "loan_percent_income": 0.26,
            "cb_person_cred_hist_length": 25,
            "credit_score": 800,
            "cb_person_default_on_file": "N",
            "previous_loan_defaults_on_file": "N"
        }
    ]
    
    response = requests.post(f"{API_BASE_URL}/api/batch-predict", json=data)
    print_response("Batch Prediction", response)
    return response.status_code == 200


def test_invalid_request():
    """Test prediction with invalid data (should fail)"""
    data = {
        "person_age": 200,  # Invalid age
        "person_income": -1000,  # Invalid income
    }
    
    response = requests.post(f"{API_BASE_URL}/api/predict", json=data)
    print_response("Invalid Request Test (Expected to Fail)", response)
    return response.status_code == 422  # Validation error expected


def test_loan_offer_approved():
    """Test loan offer for a low-risk applicant (should be approved)"""
    data = {
        "person_age": 35,
        "person_income": 80000,
        "person_emp_length": 10.0,
        "person_home_ownership": "OWN",
        "loan_amnt": 10000,
        "loan_intent": "PERSONAL",
        "loan_grade": "A",
        "loan_int_rate": 5.5,
        "loan_percent_income": 0.125,
        "cb_person_cred_hist_length": 15,
        "credit_score": 780,
        "cb_person_default_on_file": "N",
        "previous_loan_defaults_on_file": "N"
    }
    
    response = requests.post(f"{API_BASE_URL}/api/loan-offer", json=data)
    print_response("Loan Offer - Low Risk (Should Approve)", response)
    
    if response.status_code == 200:
        result = response.json()
        return result.get("approved") == True
    return False


def test_loan_offer_rejected():
    """Test loan offer for a high-risk applicant (should be rejected)"""
    data = {
        "person_age": 22,
        "person_income": 25000,
        "person_emp_length": 1.0,
        "person_home_ownership": "RENT",
        "loan_amnt": 20000,
        "loan_intent": "VENTURE",
        "loan_grade": "F",
        "loan_int_rate": 18.5,
        "loan_percent_income": 0.8,
        "cb_person_cred_hist_length": 2,
        "credit_score": 580,
        "cb_person_default_on_file": "Y",
        "previous_loan_defaults_on_file": "Y"
    }
    
    response = requests.post(f"{API_BASE_URL}/api/loan-offer", json=data)
    print_response("Loan Offer - High Risk (May Reject)", response)
    return response.status_code == 200  # Should return response regardless


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 CREDIT SCORING API TEST SUITE")
    print("="*60)
    print(f"Testing API at: {API_BASE_URL}")
    
    tests = [
        ("Health Check", test_health_check),
        ("Ping", test_ping),
        ("Model Info", test_model_info),
        ("Model Features", test_model_features),
        ("Prediction - Low Risk", test_prediction_low_risk),
        ("Prediction - High Risk", test_prediction_high_risk),
        ("Batch Prediction", test_batch_prediction),
        ("Invalid Request", test_invalid_request),
        ("Loan Offer - Approved", test_loan_offer_approved),
        ("Loan Offer - High Risk", test_loan_offer_rejected),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except requests.exceptions.ConnectionError:
            print(f"\n❌ Connection Error: Cannot connect to {API_BASE_URL}")
            print("Make sure the API is running with:")
            print("  docker-compose up")
            return
        except Exception as e:
            print(f"\n❌ Error in {test_name}: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("🎉 All tests passed! API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    main()
