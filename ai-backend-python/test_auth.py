#!/usr/bin/env python3
"""
Test rolling password authentication
"""

import requests
import json

BASE_URL = "https://compassionate-truth-production-2fcd.up.railway.app"

def test_authentication():
    """Test authentication with current password"""
    print("🧪 Testing Rolling Password Authentication")
    print("=" * 50)
    
    # Test authentication with current password
    test_data = {
        "user_id": "app_user",
        "password": "pb?7XAS+WsNS"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
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

if __name__ == "__main__":
    test_authentication()
