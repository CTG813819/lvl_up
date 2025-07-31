#!/usr/bin/env python3
"""
Test script to verify backend fixes
"""

import requests
import time
import sys

def test_backend_health():
    """Test if the backend is responding properly"""
    try:
        # Test basic health endpoint
        response = requests.get('http://localhost:8000/health', timeout=10)
        if response.status_code == 200:
            print("✅ Backend health check passed")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend health check failed: {e}")
        return False

def test_imperium_endpoint():
    """Test if the imperium endpoint is working"""
    try:
        response = requests.get('http://localhost:8000/api/imperium/status', timeout=10)
        if response.status_code == 200:
            print("✅ Imperium endpoint working")
            return True
        else:
            print(f"❌ Imperium endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Imperium endpoint failed: {e}")
        return False

def test_database_connection():
    """Test if database queries are working"""
    try:
        response = requests.get('http://localhost:8000/api/learning/stats/Imperium', timeout=10)
        if response.status_code == 200:
            print("✅ Database queries working")
            return True
        else:
            print(f"❌ Database queries failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Database queries failed: {e}")
        return False

def main():
    print("🔍 Testing backend fixes...")
    print("=" * 40)
    
    # Wait a moment for service to start
    time.sleep(5)
    
    tests = [
        ("Health Check", test_backend_health),
        ("Imperium Endpoint", test_imperium_endpoint),
        ("Database Queries", test_database_connection)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend is working properly.")
        return 0
    else:
        print("⚠️ Some tests failed. Check the logs for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())