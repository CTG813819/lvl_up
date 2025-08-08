#!/usr/bin/env python3
"""
Test to check Android device connectivity to EC2 instance
"""

import requests
import json

def test_android_connectivity():
    """Test if Android devices can reach the EC2 instance"""
    print("🔧 Testing Android Device Connectivity to EC2...")
    
    # Test endpoints that Android device needs to reach
    endpoints = [
        "http://34.202.215.209:8000/custody/",
        "http://34.202.215.209:8001/health",
        "http://34.202.215.209:8000/custody/activate-enhanced-adversarial"
    ]
    
    for i, endpoint in enumerate(endpoints, 1):
        try:
            print(f"{i}. Testing {endpoint}")
            response = requests.get(endpoint, timeout=10)
            print(f"   ✅ Accessible: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Not accessible: {e}")
    
    print("\n💡 If all tests fail, the issue is:")
    print("   • EC2 security group not allowing mobile connections")
    print("   • Mobile network blocking the connection")
    print("   • Network configuration issues")
    
    print("\n🔧 Solutions:")
    print("   1. Check EC2 security group allows port 8000 and 8001")
    print("   2. Try using WiFi instead of mobile data")
    print("   3. Check if your mobile network allows the connection")

if __name__ == "__main__":
    test_android_connectivity() 