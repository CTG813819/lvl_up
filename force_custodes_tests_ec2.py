#!/usr/bin/env python3
"""
Force Custodes Tests Script for EC2 Instance
This script forces Custodes Protocol tests for all AIs to enable proposal creation.
"""

import requests
import json
import time
from datetime import datetime

# EC2 Backend Configuration
EC2_BACKEND_URL = "http://34.202.215.209:8000"

def force_custodes_tests():
    """Force Custodes tests for all AIs on EC2"""
    print("🛡️ Starting forced Custodes tests for all AIs on EC2...")
    
    # List of AI types to test
    ai_types = ['imperium', 'guardian', 'sandbox', 'conquest']
    
    for ai_type in ai_types:
        print(f"🧪 Administering Custodes test for {ai_type} AI...")
        
        try:
            # Force administer a test for each AI
            response = requests.post(
                f"{EC2_BACKEND_URL}/api/custody/test/{ai_type}/force",
                headers={'Content-Type': 'application/json'},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {ai_type} AI test completed: {result}")
            else:
                print(f"❌ {ai_type} AI test failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Error testing {ai_type} AI: {e}")
            
    print("🎉 All Custodes tests completed!")

def check_custody_status():
    """Check the current custody status of all AIs"""
    try:
        print("📊 Checking current custody status...")
        
        # Get custody status for all AIs
        response = requests.get(
            f"{EC2_BACKEND_URL}/api/custody/",
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            analytics = data.get('analytics', {})
            
            print("📈 Current Custody Status:")
            ai_metrics = analytics.get('ai_specific_metrics', {})
            for ai_type, metrics in ai_metrics.items():
                print(f"  {ai_type}:")
                print(f"    - Tests Given: {metrics.get('total_tests_given', 0)}")
                print(f"    - Tests Passed: {metrics.get('total_tests_passed', 0)}")
                print(f"    - Pass Rate: {metrics.get('pass_rate', 0)}%")
                print(f"    - Custody Level: {metrics.get('custody_level', 1)}")
                print(f"    - Custody XP: {metrics.get('custody_xp', 0)}")
        else:
            print(f"❌ Failed to get custody status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking custody status: {e}")

def batch_test_all_ais():
    """Run batch test for all AIs"""
    try:
        print("🚀 Running batch test for all AIs...")
        
        response = requests.post(
            f"{EC2_BACKEND_URL}/api/custody/batch-test",
            headers={'Content-Type': 'application/json'},
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Batch test completed: {result}")
        else:
            print(f"❌ Batch test failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error in batch test: {e}")

def main():
    """Main function"""
    print("🚀 Starting Custodes Protocol Management on EC2...")
    print(f"📍 Backend URL: {EC2_BACKEND_URL}")
    
    # First check current status
    check_custody_status()
    
    # Try batch test first
    print("\n🔄 Attempting batch test...")
    batch_test_all_ais()
    
    # Wait a moment for tests to complete
    print("⏳ Waiting for tests to complete...")
    time.sleep(10)
    
    # Check status again
    print("\n📊 Checking status after tests...")
    check_custody_status()
    
    print("✅ Custodes Protocol Management completed!")

if __name__ == "__main__":
    main() 