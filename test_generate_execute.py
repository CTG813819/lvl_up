#!/usr/bin/env python3
"""
Test the generate-and-execute endpoint with correct JSON format
"""

import requests
import json

def test_generate_execute():
    """Test the generate-and-execute endpoint"""
    print("🔧 Testing generate-and-execute endpoint...")
    
    # Test with correct JSON format
    test_data = {
        "ai_types": ["imperium", "guardian"],
        "target_domain": "system_level",
        "complexity": "advanced",
        "reward_level": "standard",
        "adaptive": False
    }
    
    print(f"📤 Sending JSON: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            "http://34.202.215.209:8001/generate-and-execute",
            headers={"Content-Type": "application/json"},
            data=json.dumps(test_data),
            timeout=30
        )
        
        print(f"📊 Response status: {response.status_code}")
        print(f"📄 Response body: {response.text[:500]}...")
        
        if response.status_code == 200:
            print("✅ Endpoint working correctly!")
        else:
            print("❌ Endpoint returned error")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_generate_execute() 