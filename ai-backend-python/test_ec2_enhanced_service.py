#!/usr/bin/env python3
"""
Test script to verify Enhanced Adversarial Testing Service on EC2
"""

import requests
import json
import sys

def test_enhanced_adversarial_service():
    """Test the enhanced adversarial testing service on EC2"""
    base_url = "http://34.202.215.209:8001"
    
    print("🔧 Testing Enhanced Adversarial Testing Service on EC2...")
    
    # Test 1: Health check
    try:
        print("1. Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Get available domains
    try:
        print("2. Testing domains endpoint...")
        response = requests.get(f"{base_url}/domains", timeout=10)
        if response.status_code == 200:
            domains = response.json()
            print(f"✅ Domains endpoint working: {len(domains.get('domains', []))} domains available")
        else:
            print(f"❌ Domains endpoint failed: {response.statusCode}")
            return False
    except Exception as e:
        print(f"❌ Domains endpoint error: {e}")
        return False
    
    # Test 3: Generate and execute scenario
    try:
        print("3. Testing generate-and-execute endpoint...")
        request_data = {
            "ai_types": ["imperium", "guardian"],
            "target_domain": "system_level",
            "complexity": "advanced",
            "reward_level": "standard",
            "adaptive": False,
            "target_weaknesses": []
        }
        
        response = requests.post(
            f"{base_url}/generate-and-execute",
            headers={"Content-Type": "application/json"},
            data=json.dumps(request_data),
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Generate-and-execute endpoint working")
            print(f"   Scenario: {result.get('scenario', {}).get('name', 'Unknown')}")
            print(f"   Status: {result.get('status', 'Unknown')}")
        else:
            print(f"❌ Generate-and-execute failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Generate-and-execute error: {e}")
        return False
    
    # Test 4: Get recent scenarios
    try:
        print("4. Testing recent-scenarios endpoint...")
        response = requests.get(f"{base_url}/recent-scenarios", timeout=10)
        if response.status_code == 200:
            scenarios = response.json()
            print(f"✅ Recent scenarios endpoint working: {len(scenarios.get('recent_scenarios', []))} scenarios")
        else:
            print(f"❌ Recent scenarios failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Recent scenarios error: {e}")
    
    print("🎉 Enhanced adversarial testing service is working correctly!")
    return True

if __name__ == "__main__":
    success = test_enhanced_adversarial_service()
    sys.exit(0 if success else 1) 