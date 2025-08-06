#!/usr/bin/env python3
"""
Simple test to check Railway deployment
"""

import requests
import time

RAILWAY_URL = "https://compassionate-truth-production-2fcd.up.railway.app"

def test_railway_deployment():
    """Test Railway deployment"""
    print("🧪 Testing Railway deployment...")
    print(f"📍 URL: {RAILWAY_URL}")
    print("=" * 50)
    
    # Test basic health endpoint
    try:
        print("🔍 Testing health endpoint...")
        response = requests.get(f"{RAILWAY_URL}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ SUCCESS - Railway deployment is working!")
            data = response.json()
            print(f"   Response: {data}")
        else:
            print(f"   ❌ ERROR: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ CONNECTION ERROR: {e}")
    
    # Test quantum chaos endpoint
    try:
        print("\n🔍 Testing quantum chaos endpoint...")
        response = requests.get(f"{RAILWAY_URL}/api/quantum-chaos/generate", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ SUCCESS - Quantum chaos endpoint is working!")
            data = response.json()
            print(f"   Chaos ID: {data.get('chaos_id', 'N/A')}")
            print(f"   Language: {data.get('chaos_language', {}).get('name', 'N/A')}")
        elif response.status_code == 404:
            print("   ⚠️  NOT FOUND - Endpoint not implemented yet")
        else:
            print(f"   ❌ ERROR: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ CONNECTION ERROR: {e}")

if __name__ == "__main__":
    test_railway_deployment() 