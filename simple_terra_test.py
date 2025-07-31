#!/usr/bin/env python3
"""
Simple test for Terra extensions endpoint
"""

import requests
import json

# Configuration
BASE_URL = "http://34.202.215.209:4000"
API_BASE = f"{BASE_URL}/api/terra"

def test_simple_extension():
    """Test submitting a simple extension"""
    print("🧪 Testing simple extension submission...")
    
    test_extension = {
        "feature_name": "SimpleWidget",
        "menu_title": "Simple Extension",
        "icon_name": "Icons.star",
        "description": "A simple test widget",
        "dart_code": "class SimpleWidget extends StatelessWidget { @override Widget build(BuildContext context) { return Container(); } }"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/extensions",
            headers={"Content-Type": "application/json"},
            json=test_extension,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Extension submitted successfully!")
            return True
        else:
            print(f"❌ Failed to submit extension: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error submitting extension: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting simple Terra extensions test...")
    success = test_simple_extension()
    if success:
        print("✅ Test passed!")
    else:
        print("❌ Test failed!") 