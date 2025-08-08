#!/usr/bin/env python3
"""
Test script for enhanced adversarial testing endpoint
"""

import requests
import json

def test_enhanced_endpoint():
    """Test the enhanced adversarial testing endpoint"""
    
    # Test data
    test_data = {
        "ai_types": ["imperium", "guardian"],
        "target_domain": "system_level",
        "complexity": "advanced",
        "reward_level": "standard",
        "adaptive": False,
        "target_weaknesses": []
    }
    
    print("🧪 Testing Enhanced Adversarial Testing Endpoint")
    print("=" * 50)
    
    try:
        # Test the endpoint
        response = requests.post(
            "http://localhost:8001/generate-and-execute",
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint working!")
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Endpoint failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")

if __name__ == "__main__":
    test_enhanced_endpoint() 