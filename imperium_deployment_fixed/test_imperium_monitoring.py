#!/usr/bin/env python3
# Test Imperium Monitoring System

import requests
import time
import json
import sys

def test_imperium_endpoints():
    """Test all Imperium monitoring endpoints"""
    base_url = "http://localhost:8000"
    
    endpoints = [
        "/api/imperium/monitoring",
        "/api/imperium/improvements", 
        "/api/imperium/issues",
        "/api/imperium/status"
    ]
    
    print("🧪 Testing Imperium Monitoring Endpoints...")
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {endpoint}: SUCCESS")
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)}")
            else:
                print(f"❌ {endpoint}: FAILED (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ {endpoint}: ERROR - {str(e)}")
    
    # Test trigger scan
    try:
        response = requests.post(f"{base_url}/api/imperium/trigger-scan", timeout=10)
        if response.status_code == 200:
            print("✅ /api/imperium/trigger-scan: SUCCESS")
        else:
            print(f"❌ /api/imperium/trigger-scan: FAILED (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ /api/imperium/trigger-scan: ERROR - {str(e)}")

if __name__ == "__main__":
    test_imperium_endpoints()
