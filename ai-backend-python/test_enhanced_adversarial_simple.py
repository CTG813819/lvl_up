#!/usr/bin/env python3
"""
Simple test script for enhanced adversarial testing endpoint
"""

import asyncio
import json
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Import the router directly
from app.routers.enhanced_adversarial_testing import router

# Create a test app
app = FastAPI()
app.include_router(router, prefix="/api")

# Create test client
client = TestClient(app)

def test_enhanced_adversarial_testing():
    """Test the enhanced adversarial testing endpoints"""
    
    print("🧪 Testing Enhanced Adversarial Testing Endpoints...")
    
    # Test 1: Get overview
    print("\n1. Testing overview endpoint...")
    response = client.get("/api/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Overview endpoint works: {data.get('message', 'No message')}")
    else:
        print(f"❌ Overview endpoint failed: {response.text}")
    
    # Test 2: Get domains
    print("\n2. Testing domains endpoint...")
    response = client.get("/api/domains")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Domains endpoint works: {len(data.get('domains', []))} domains available")
    else:
        print(f"❌ Domains endpoint failed: {response.text}")
    
    # Test 3: Get complexities
    print("\n3. Testing complexities endpoint...")
    response = client.get("/api/complexities")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Complexities endpoint works: {len(data.get('complexities', []))} complexity levels available")
    else:
        print(f"❌ Complexities endpoint failed: {response.text}")
    
    # Test 4: Generate and execute scenario
    print("\n4. Testing generate-and-execute endpoint...")
    test_data = {
        "ai_types": ["imperium", "guardian"],
        "target_domain": "system_level",
        "complexity": "intermediate",
        "reward_level": "standard",
        "adaptive": False,
        "target_weaknesses": []
    }
    
    response = client.post("/api/generate-and-execute", json=test_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Generate-and-execute endpoint works!")
        print(f"   Scenario: {data.get('scenario', {}).get('description', 'No description')}")
        print(f"   Winners: {data.get('result', {}).get('winners', [])}")
    else:
        print(f"❌ Generate-and-execute endpoint failed: {response.text}")
    
    # Test 5: Get recent scenarios
    print("\n5. Testing recent-scenarios endpoint...")
    response = client.get("/api/recent-scenarios")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Recent scenarios endpoint works: {len(data.get('recent_scenarios', []))} scenarios")
    else:
        print(f"❌ Recent scenarios endpoint failed: {response.text}")
    
    print("\n🎉 Enhanced Adversarial Testing test completed!")

if __name__ == "__main__":
    test_enhanced_adversarial_testing() 