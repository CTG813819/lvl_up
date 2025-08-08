#!/usr/bin/env python3
"""
Test script to check what endpoints are available on the Railway backend.
"""

import requests
import json

RAILWAY_URL = "https://compassionate-truth-production-2fcd.up.railway.app"

def test_endpoint(url, endpoint):
    """Test if an endpoint is available."""
    full_url = f"{url}{endpoint}"
    try:
        response = requests.get(full_url, timeout=10)
        print(f"✅ {endpoint} -> {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                if data:
                    print(f"   📊 Data: {json.dumps(data, indent=2)[:200]}...")
            except:
                print(f"   📄 Text: {response.text[:100]}...")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ {endpoint} -> ERROR: {e}")
        return False

def main():
    print(f"🧪 Testing endpoints on: {RAILWAY_URL}")
    print("=" * 60)
    
    # Test basic health endpoints
    print("\n🔍 BASIC HEALTH:")
    test_endpoint(RAILWAY_URL, "/health")
    test_endpoint(RAILWAY_URL, "/api/health")
    
    # Test Project Horus endpoints
    print("\n🔍 PROJECT HORUS ENDPOINTS:")
    test_endpoint(RAILWAY_URL, "/api/project-horus/status")
    test_endpoint(RAILWAY_URL, "/api/project-horus-v2/status")
    test_endpoint(RAILWAY_URL, "/api/project-horus-enhanced/status")
    
    # Test Project Berserk endpoints
    print("\n🔍 PROJECT BERSERK ENDPOINTS:")
    test_endpoint(RAILWAY_URL, "/api/project-berserk/status")
    test_endpoint(RAILWAY_URL, "/api/project-warmaster/status")
    
    # Test Quantum Chaos endpoints
    print("\n🔍 QUANTUM CHAOS ENDPOINTS:")
    test_endpoint(RAILWAY_URL, "/api/quantum-chaos/status")
    test_endpoint(RAILWAY_URL, "/api/quantum-chaos/generate")
    
    # Test Stealth Hub endpoints
    print("\n🔍 STEALTH HUB ENDPOINTS:")
    test_endpoint(RAILWAY_URL, "/api/stealth-hub/status")
    test_endpoint(RAILWAY_URL, "/api/stealth-assimilation/status")
    
    # Test Rolling Password endpoints
    print("\n🔍 ROLLING PASSWORD ENDPOINTS:")
    test_endpoint(RAILWAY_URL, "/api/rolling-password/status")
    
    print("\n" + "=" * 60)
    print("🏁 Endpoint testing complete!")

if __name__ == "__main__":
    main()