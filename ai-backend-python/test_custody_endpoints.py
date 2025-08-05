#!/usr/bin/env python3
"""
Test script to verify custody protocol endpoints are working correctly
"""

import requests
import json
import time

BACKEND_URL = "http://localhost:8000"

def test_custody_endpoints():
    """Test all custody protocol endpoints"""
    print("🧪 Testing Custody Protocol Endpoints")
    print("=" * 50)
    
    # Test 1: Check if custody protocol is accessible
    print("\n1. Testing custody protocol overview...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/custody/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Custody protocol is accessible")
            print(f"   Status: {data.get('status')}")
            print(f"   Message: {data.get('message')}")
        else:
            print(f"❌ Custody protocol not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing custody protocol: {e}")
        return False
    
    # Test 2: Get custody analytics
    print("\n2. Testing custody analytics...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/custody/analytics", timeout=10)
        if response.status_code == 200:
            data = response.json()
            analytics = data.get('data', {})
            print(f"✅ Analytics retrieved successfully")
            print(f"   Total tests administered: {analytics.get('total_tests_administered', 0)}")
            print(f"   Total tests passed: {analytics.get('total_tests_passed', 0)}")
            print(f"   Total tests failed: {analytics.get('total_tests_failed', 0)}")
        else:
            print(f"❌ Failed to get analytics: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting analytics: {e}")
    
    # Test 3: Check eligibility for each AI
    print("\n3. Testing AI eligibility checks...")
    for ai_type in ["imperium", "guardian", "conquest", "sandbox"]:
        try:
            response = requests.get(f"{BACKEND_URL}/api/custody/eligibility/{ai_type}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                ai_data = data.get('data', {})
                current_status = ai_data.get('current_status', {})
                print(f"✅ {ai_type}: XP={current_status.get('custody_xp', 0)}, "
                      f"Tests passed={current_status.get('total_tests_passed', 0)}, "
                      f"Can create proposals={ai_data.get('can_create_proposals', False)}")
            else:
                print(f"❌ Failed to check {ai_type} eligibility: {response.status_code}")
        except Exception as e:
            print(f"❌ Error checking {ai_type} eligibility: {e}")
    
    # Test 4: Force tests for each AI
    print("\n4. Testing forced custody tests...")
    for ai_type in ["imperium", "guardian", "conquest", "sandbox"]:
        try:
            print(f"   Testing {ai_type}...")
            response = requests.post(f"{BACKEND_URL}/api/custody/test/{ai_type}/force", timeout=30)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {ai_type} test administered successfully")
                print(f"   Result: {data.get('data', {}).get('status', 'unknown')}")
            else:
                print(f"❌ Failed to test {ai_type}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error testing {ai_type}: {e}")
        
        # Wait a bit between tests
        time.sleep(2)
    
    # Test 5: Check analytics again after tests
    print("\n5. Checking analytics after tests...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/custody/analytics", timeout=10)
        if response.status_code == 200:
            data = response.json()
            analytics = data.get('data', {})
            print(f"✅ Updated analytics retrieved")
            print(f"   Total tests administered: {analytics.get('total_tests_administered', 0)}")
            print(f"   Total tests passed: {analytics.get('total_tests_passed', 0)}")
            print(f"   Total tests failed: {analytics.get('total_tests_failed', 0)}")
            
            # Show AI-specific metrics
            ai_metrics = analytics.get('ai_specific_metrics', {})
            for ai_type, metrics in ai_metrics.items():
                xp = metrics.get('custody_xp', 0)
                level = metrics.get('custody_level', 1)
                tests_passed = metrics.get('total_tests_passed', 0)
                print(f"   {ai_type}: Level {level}, XP {xp}, Tests passed {tests_passed}")
        else:
            print(f"❌ Failed to get updated analytics: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting updated analytics: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Custody protocol endpoint testing completed!")
    return True

if __name__ == "__main__":
    test_custody_endpoints() 