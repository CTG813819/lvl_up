#!/usr/bin/env python3

import requests
import json
import time

def test_extension_flow():
    base_url = "http://localhost:8000/api/terra/extensions"
    
    # Step 1: Create an extension
    print("🔄 Creating extension...")
    extension_data = {
        "feature_name": "TestWidget",
        "menu_title": "Test Extension", 
        "icon_name": "Icons.star",
        "description": "A test widget for testing the approval flow",
        "dart_code": "class TestWidget extends StatelessWidget { @override Widget build(BuildContext context) { return Container(); } }"
    }
    
    try:
        response = requests.post(base_url, json=extension_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            extension = response.json()
            extension_id = extension['id']
            print(f"✅ Extension created with ID: {extension_id}")
            
            # Step 2: Wait a moment for testing to complete
            print("⏳ Waiting for testing to complete...")
            time.sleep(5)
            
            # Step 3: Check extension status
            print("🔍 Checking extension status...")
            response = requests.get(f"{base_url}/{extension_id}")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.statusCode == 200:
                extension = response.json()
                status = extension.get('status')
                print(f"📊 Extension status: {status}")
                
                # Step 4: Approve the extension if ready
                if status == 'ready_for_approval':
                    print("✅ Approving extension...")
                    response = requests.patch(
                        f"{base_url}/{extension_id}",
                        json={'status': 'approved'}
                    )
                    print(f"Approval Status Code: {response.status_code}")
                    print(f"Approval Response: {response.text}")
                    
                    if response.status_code == 200:
                        print("✅ Extension approved successfully!")
                    else:
                        print("❌ Failed to approve extension")
                else:
                    print(f"⚠️ Extension not ready for approval (status: {status})")
            else:
                print("❌ Failed to get extension details")
                
        else:
            print("❌ Failed to create extension")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_extension_flow() 