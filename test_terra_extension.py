import requests
import json

# Test data
test_extension = {
    "feature_name": "Test Feature",
    "menu_title": "Test Menu", 
    "icon_name": "test_icon",
    "description": "Test description",
    "dart_code": "class TestWidget extends StatelessWidget { @override Widget build(BuildContext context) { return Container(); }}"
}

# Test the endpoint on EC2 instance
url = "http://34.202.215.209:4000/api/terra/extensions"
headers = {"Content-Type": "application/json"}

try:
    print("Testing Terra extensions endpoint on EC2...")
    response = requests.post(url, headers=headers, json=test_extension)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        print("✅ SUCCESS: Extension submitted successfully!")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print("❌ ERROR: Failed to submit extension")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ EXCEPTION: {e}") 