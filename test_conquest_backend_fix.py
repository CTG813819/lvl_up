#!/usr/bin/env python3
"""
Test script to check Conquest AI backend endpoints
"""

import requests
import json
import time

# Backend URL
BACKEND_URL = "http://ec2-3-250-182-141.eu-west-1.compute.amazonaws.com:8000"

def test_conquest_endpoints():
    """Test all Conquest AI endpoints"""
    print("🧪 Testing Conquest AI Backend Endpoints")
    print("=" * 50)
    
    # Test 1: Conquest overview
    print("\n1. Testing Conquest Overview...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/conquest/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Progress logs
    print("\n2. Testing Progress Logs...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/conquest/progress-logs", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Logs count: {len(data.get('logs', []))}")
            if data.get('logs'):
                print(f"   First log: {json.dumps(data['logs'][0], indent=2)}")
            else:
                print("   No logs found")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Basic statistics
    print("\n3. Testing Basic Statistics...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/conquest/statistics", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Statistics: {json.dumps(data, indent=2)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Enhanced statistics
    print("\n4. Testing Enhanced Statistics...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/conquest/enhanced-statistics", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Enhanced stats: {json.dumps(data, indent=2)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 5: Create a test app
    print("\n5. Testing App Creation...")
    try:
        test_app_data = {
            "name": "test-app-backend-fix",
            "description": "A test app to verify backend integration is working properly",
            "keywords": ["test", "backend", "integration", "flutter"],
            "app_type": "general",
            "features": [],
            "operation_type": "create_new"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/conquest/create-app",
            json=test_app_data,
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   App creation result: {json.dumps(data, indent=2)}")
            
            # If successful, wait a bit and check progress logs again
            if data.get('status') == 'success':
                print("\n   Waiting 5 seconds for progress logs to update...")
                time.sleep(5)
                
                response2 = requests.get(f"{BACKEND_URL}/api/conquest/progress-logs", timeout=10)
                if response2.status_code == 200:
                    logs_data = response2.json()
                    print(f"   Updated logs count: {len(logs_data.get('logs', []))}")
                    if logs_data.get('logs'):
                        latest_log = logs_data['logs'][0]
                        print(f"   Latest log: {json.dumps(latest_log, indent=2)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 6: List deployments
    print("\n6. Testing List Deployments...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/conquest/deployments", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Deployments count: {len(data.get('deployments', []))}")
            if data.get('deployments'):
                print(f"   First deployment: {json.dumps(data['deployments'][0], indent=2)}")
            else:
                print("   No deployments found")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_conquest_endpoints() 