#!/usr/bin/env python3

import requests
import json

def test_terra_extensions_api():
    url = "http://localhost:8000/api/terra/extensions"
    
    data = {
        "feature_name": "TestWidget",
        "menu_title": "Test Extension", 
        "icon_name": "Icons.star",
        "description": "A test widget",
        "dart_code": "class TestWidget extends StatelessWidget { @override Widget build(BuildContext context) { return Container(); } }"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ API call successful!")
        else:
            print("❌ API call failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_terra_extensions_api() 