#!/usr/bin/env python3
"""
Test to verify button functionality works correctly
"""

import requests
import json
import time

def test_button_functionality():
    """Test the complete button functionality flow"""
    print("🔧 Testing Button Functionality...")
    
    # Test 1: Check if backend is accessible
    try:
        print("1. Testing backend connectivity...")
        response = requests.get("http://34.202.215.209:8000/custody/", timeout=10)
        if response.status_code == 200:
            print("   ✅ Backend is accessible")
        else:
            print(f"   ❌ Backend returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Backend not accessible: {e}")
        print("   💡 This explains why the Flutter button doesn't work!")
        print("   🔧 Network connectivity issue detected")
        return False
    
    # Test 2: Test activation endpoint
    try:
        print("2. Testing activation endpoint...")
        activation_data = {"action": "start"}
        response = requests.post(
            "http://34.202.215.209:8000/custody/activate-enhanced-adversarial",
            headers={"Content-Type": "application/json"},
            data=json.dumps(activation_data),
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Activation successful: {result.get('message', 'Unknown')}")
        else:
            print(f"   ❌ Activation failed: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Activation error: {e}")
        return False
    
    # Test 3: Verify enhanced service
    try:
        print("3. Verifying enhanced service...")
        response = requests.get("http://34.202.215.209:8001/health", timeout=10)
        if response.status_code == 200:
            print("   ✅ Enhanced service is running")
        else:
            print(f"   ❌ Enhanced service not running: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Enhanced service error: {e}")
        return False
    
    print("🎉 Button functionality test completed successfully!")
    print("💡 If this test passes but Flutter button doesn't work,")
    print("   it's likely a network connectivity issue from your device.")
    return True

if __name__ == "__main__":
    success = test_button_functionality()
    if not success:
        print("\n🔧 Troubleshooting Steps:")
        print("1. Check if you can access http://34.202.215.209:8000 from your browser")
        print("2. Verify your network connection")
        print("3. Check if there are any firewall rules blocking the connection")
        print("4. Try using a VPN or different network") 