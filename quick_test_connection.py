#!/usr/bin/env python3
"""
Quick connection test for the backend
"""

import requests
import json

def test_connection():
    """Test basic connectivity to the backend"""
    base_url = "http://34.202.215.209:4000"
    
    print("🔍 Testing backend connectivity...")
    print(f"📍 Target: {base_url}")
    print("=" * 50)
    
    # Test basic health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"✅ Health Check: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Message: {data.get('message')}")
            print(f"   Version: {data.get('version')}")
        else:
            print(f"   Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Health Check Failed: {e}")
        return False
    
    # Test a few key endpoints
    endpoints = [
        "/api/github/status",
        "/api/agents/status", 
        "/api/learning/status",
        "/api/oath-papers/",
        "/api/proposals/"
    ]
    
    print("\n🔍 Testing key endpoints:")
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            status = "✅" if response.status_code == 200 else "⚠️"
            print(f"{status} {endpoint}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint}: {e}")
    
    print("\n🎯 If you see ✅ marks, the backend is accessible!")
    print("   If you see ❌ marks, check the security group configuration.")
    
    return True

if __name__ == "__main__":
    test_connection() 