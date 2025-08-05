#!/usr/bin/env python3
"""
Quick test to check Railway deployment status
"""

import requests
import time

def test_railway_endpoints():
    """Test Railway endpoints"""
    print("🔍 Quick Railway Deployment Test")
    print("=" * 40)
    
    railway_url = "https://lvlup-production.up.railway.app"
    endpoints = ["/health", "/api/health", "/api/status"]
    
    for endpoint in endpoints:
        try:
            print(f"Testing: {railway_url}{endpoint}")
            response = requests.get(f"{railway_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {endpoint}: {response.status_code}")
                print(f"📄 Response: {response.text[:100]}...")
            else:
                print(f"⚠️ {endpoint}: {response.status_code}")
            
            print()
            
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")
            print()
    
    print("🎯 If all endpoints still return 404:")
    print("1. Check Railway dashboard for deployment status")
    print("2. Verify DATABASE_URL environment variable is set")
    print("3. Force a redeploy in Railway dashboard")
    print("4. Check deployment logs for errors")

if __name__ == "__main__":
    test_railway_endpoints() 