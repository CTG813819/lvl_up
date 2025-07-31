#!/usr/bin/env python3
"""
Simple script to force Custodes tests by calling API endpoints directly
"""

import requests
import json
import time

BACKEND_URL = "http://localhost:8000"

def force_custodes_tests():
    """Force Custodes tests for all AIs by calling API endpoints"""
    print("🛡️ Forcing Custodes Protocol Tests...")
    
    # Check current status first
    print("📊 Checking current custody status...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/custody/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2))
        else:
            print(f"❌ Failed to get custody status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting custody status: {e}")
    
    # Use batch test to test all AIs at once
    print("\n🧪 Running batch test for all AIs...")
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/custody/batch-test",
            timeout=60
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Batch test completed: {result.get('status', 'unknown')}")
            if 'results' in result:
                for ai_result in result['results']:
                    ai_name = ai_result.get('ai_type', 'unknown')
                    status = ai_result.get('status', 'unknown')
                    print(f"   {ai_name}: {status}")
        else:
            print(f"❌ Batch test failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error running batch test: {e}")
    
    # Also try individual force tests for each AI
    ai_types = ["imperium", "guardian", "conquest"]
    
    for ai_type in ai_types:
        print(f"\n🧪 Force testing {ai_type} AI...")
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/custody/test/{ai_type}/force",
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {ai_type} force test completed: {result.get('status', 'unknown')}")
                if 'result' in result:
                    print(f"   Test result: {result['result']}")
            else:
                print(f"❌ {ai_type} force test failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Error testing {ai_type}: {e}")
    
    # Wait a moment for tests to complete
    print("\n⏳ Waiting for tests to complete...")
    time.sleep(5)
    
    # Check final status
    print("\n📊 Checking final custody status...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/custody/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2))
            
            # Check if any AIs can now create proposals
            for ai_name, ai_data in data.items():
                if ai_data.get('can_create_proposals', False):
                    print(f"✅ {ai_name} can now create proposals!")
                else:
                    print(f"❌ {ai_name} still cannot create proposals")
        else:
            print(f"❌ Failed to get final custody status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting final custody status: {e}")
    
    print("\n🎉 Custodes tests completed!")

if __name__ == "__main__":
    force_custodes_tests() 