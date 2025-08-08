#!/usr/bin/env python3
"""
Test script to verify the build failure endpoint fix
"""

import requests
import json
import sys

def test_build_failure_endpoint():
    """Test the build-failure endpoint with various scenarios"""
    
    base_url = "http://34.202.215.209:4000"
    endpoint = "/api/conquest/build-failure"
    
    test_cases = [
        {
            "name": "Valid UUID app_id",
            "data": {
                "app_id": "12345678-1234-1234-1234-123456789abc",
                "error_message": "Test error with valid UUID",
                "build_logs": "Test build logs",
                "failure_type": "build_error"
            },
            "expected_status": 200
        },
        {
            "name": "Missing app_id (should return success without DB update)",
            "data": {
                "error_message": "Test error with missing app_id",
                "build_logs": "Test build logs",
                "failure_type": "build_error"
            },
            "expected_status": 200
        },
        {
            "name": "Invalid app_id format",
            "data": {
                "app_id": "invalid-uuid-format",
                "error_message": "Test error with invalid UUID",
                "build_logs": "Test build logs",
                "failure_type": "build_error"
            },
            "expected_status": 200
        },
        {
            "name": "Empty app_id",
            "data": {
                "app_id": "",
                "error_message": "Test error with empty app_id",
                "build_logs": "Test build logs",
                "failure_type": "build_error"
            },
            "expected_status": 200
        },
        {
            "name": "GitHub Actions format (appId)",
            "data": {
                "appId": "87654321-4321-4321-4321-cba987654321",
                "error": "Test error with GitHub Actions format",
                "build_logs": "Test build logs",
                "failure_type": "build_error"
            },
            "expected_status": 200
        }
    ]
    
    print("🧪 Testing build-failure endpoint fixes...")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print("-" * 40)
        
        try:
            response = requests.post(
                f"{base_url}{endpoint}",
                json=test_case["data"],
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Expected: {test_case['expected_status']}")
            
            if response.status_code == test_case["expected_status"]:
                print("✅ Status code matches expected")
            else:
                print("❌ Status code mismatch")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"Response: {json.dumps(result, indent=2)}")
                    
                    # Check if response contains expected fields
                    if "status" in result and result["status"] == "success":
                        print("✅ Response indicates success")
                    else:
                        print("❌ Response does not indicate success")
                        
                except json.JSONDecodeError:
                    print("❌ Response is not valid JSON")
                    print(f"Raw response: {response.text}")
            else:
                print(f"❌ Request failed: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Test completed!")

if __name__ == "__main__":
    test_build_failure_endpoint() 