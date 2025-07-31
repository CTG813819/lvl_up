#!/usr/bin/env python3
"""
Test to verify Flutter app can make HTTP requests to backend
"""

import requests
import json

def test_flutter_network_access():
    """Test if Flutter app can access the backend endpoints"""
    base_url = "http://34.202.215.209:8000"
    
    print("🔧 Testing Flutter Network Access...")
    
    # Test 1: Basic health check
    try:
        print("1. Testing basic connectivity...")
        response = requests.get(f"{base_url}/custody/", timeout=10)
        print(f"   ✅ Backend is accessible: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Backend not accessible: {e}")
        return False
    
    # Test 2: Activation endpoint
    try:
        print("2. Testing activation endpoint...")
        response = requests.post(
            f"{base_url}/custody/activate-enhanced-adversarial",
            headers={"Content-Type": "application/json"},
            data=json.dumps({"action": "start"}),
            timeout=10
        )
        print(f"   ✅ Activation endpoint accessible: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   📄 Response: {result.get('message', 'Unknown')}")
    except Exception as e:
        print(f"   ❌ Activation endpoint error: {e}")
    
    # Test 3: Enhanced service health
    try:
        print("3. Testing enhanced service health...")
        response = requests.get("http://34.202.215.209:8001/health", timeout=10)
        print(f"   ✅ Enhanced service accessible: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Enhanced service error: {e}")
    
    print("🎉 Network access test completed!")
    return True

if __name__ == "__main__":
    test_flutter_network_access() 