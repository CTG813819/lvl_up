#!/usr/bin/env python3
"""
Test script for rolling password system
"""

import requests
import json
import time

BASE_URL = "https://compassionate-truth-production-2fcd.up.railway.app"

def test_rolling_password_system():
    """Test the rolling password system"""
    print("🧪 Testing Rolling Password System")
    print("=" * 50)
    
    # Test 1: Check current password status
    print("\n1. Checking current password status...")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/current-password-status")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Password Active: {data.get('password_active')}")
            print(f"Expires At: {data.get('expires_at')}")
            print(f"Time Until Expiry: {data.get('time_until_expiry')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Try to initialize the system
    print("\n2. Initializing rolling password system...")
    try:
        response = requests.post(f"{BASE_URL}/api/auth/initialize")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('status')}")
            print(f"Message: {data.get('message')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Get current password
    print("\n3. Getting current password...")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/current-password")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data.get('status')}")
            print(f"Message: {data.get('message')}")
            if data.get('current_password'):
                print(f"Current Password: {data.get('current_password')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Try to authenticate with a test password
    print("\n4. Testing authentication...")
    try:
        test_data = {
            "user_id": "app_user",
            "password": "123456"
        }
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            headers={"Content-Type": "application/json"},
            json=test_data
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Message: {data.get('message')}")
            if data.get('next_password'):
                print(f"Next Password: {data.get('next_password')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Testing completed")

if __name__ == "__main__":
    test_rolling_password_system()
