#!/usr/bin/env python3
"""
Test script to verify the enhanced adversarial service activation endpoint
"""

import requests
import json
import time

def test_activation_endpoint():
    """Test the activation endpoint"""
    base_url = "http://34.202.215.209:8000"
    
    print("🔧 Testing Enhanced Adversarial Service Activation Endpoint...")
    
    # Test 1: Check if service is already running
    try:
        print("1. Checking if service is already running...")
        response = requests.get(f"{base_url}/custody/activate-enhanced-adversarial", timeout=10)
        print(f"   Response: {response.status_code}")
        if response.status_code == 405:  # Method not allowed - need to use POST
            print("   ✅ Endpoint exists (requires POST)")
        else:
            print(f"   Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Activate the service
    try:
        print("2. Activating enhanced adversarial service...")
        activation_data = {"action": "start"}
        
        response = requests.post(
            f"{base_url}/custody/activate-enhanced-adversarial",
            headers={"Content-Type": "application/json"},
            data=json.dumps(activation_data),
            timeout=30
        )
        
        print(f"   Response status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Activation successful: {result.get('message', 'Unknown')}")
            print(f"   Service status: {result.get('service_status', 'Unknown')}")
        else:
            print(f"   ❌ Activation failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Activation error: {e}")
    
    # Test 3: Verify service is running
    try:
        print("3. Verifying service is running...")
        time.sleep(2)  # Wait a moment
        response = requests.get("http://34.202.215.209:8001/health", timeout=10)
        if response.status_code == 200:
            print("   ✅ Service is running on port 8001")
        else:
            print(f"   ❌ Service not running: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Verification error: {e}")
    
    print("🎉 Activation endpoint test completed!")

if __name__ == "__main__":
    test_activation_endpoint() 