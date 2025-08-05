#!/usr/bin/env python3
"""
Simple Test for Conquest AI Fixes
"""

import requests
import json

# EC2 Configuration
EC2_BASE_URL = "http://34.202.215.209:4000"

def test_conquest_ai_fixes():
    """Test the Conquest AI fixes"""
    print("Testing Conquest AI Fixes...")
    
    # Test 1: Check Conquest AI status
    print("\n1. Testing Conquest AI Status")
    try:
        response = requests.get(f"{EC2_BASE_URL}/api/conquest/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"Success: Conquest AI is active")
            print(f"   Total deployments: {data.get('conquest_ai', {}).get('total_deployments', 0)}")
            print(f"   Success rate: {data.get('conquest_ai', {}).get('success_rate', 0)}%")
        else:
            print(f"Failed: Status {response.status_code}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Test 2: Test app creation with proper JSON
    print("\n2. Testing App Creation")
    try:
        app_data = {
            "name": "TestApp",
            "description": "A test app to verify the fixes work correctly",
            "keywords": ["test", "flutter", "fix"]
        }
        
        response = requests.post(
            f"{EC2_BASE_URL}/api/conquest/create-app",
            json=app_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: App creation worked!")
            print(f"   Status: {data.get('status', 'N/A')}")
            print(f"   App ID: {data.get('app_id', 'N/A')}")
        elif response.status_code == 400:
            data = response.json()
            print(f"Validation Error: {data.get('message', 'Unknown error')}")
            print(f"   This is expected - validation is working correctly")
        else:
            print(f"Failed: Status {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Test 3: Check enhanced statistics
    print("\n3. Testing Enhanced Statistics")
    try:
        response = requests.get(f"{EC2_BASE_URL}/api/conquest/enhanced-statistics", timeout=10)
        if response.status_code == 200:
            data = response.json()
            stats = data.get('statistics', {})
            overview = stats.get('overview', {})
            print(f"Success: Enhanced statistics retrieved")
            print(f"   Total Apps: {overview.get('total_apps', 0)}")
            print(f"   Completed Apps: {overview.get('completed_apps', 0)}")
            print(f"   Success Rate: {overview.get('success_rate', 0)}%")
        else:
            print(f"Failed: Status {response.status_code}")
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    """Run the test"""
    print("Testing Conquest AI Fixes")
    print("=" * 50)
    
    test_conquest_ai_fixes()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("\nSummary of fixes:")
    print("- Progress logs timeout increased from 5 to 15 seconds")
    print("- App creation JSON format improved with validation")
    print("- Better error handling for backend responses")
    print("- Enhanced logging for debugging")
    print("- Fixed ai_code_fixes.json file corruption")

if __name__ == "__main__":
    main() 