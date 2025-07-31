#!/usr/bin/env python3
"""
Comprehensive test script for Terra extensions system.
Tests the full workflow from submission to approval and live integration.
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"  # Update with your backend URL
API_BASE = f"{BASE_URL}/api/terra"

def test_extension_submission():
    """Test submitting a new extension"""
    print("🧪 Testing extension submission...")
    
    test_extension = {
        "feature_name": "TestWidget",
        "menu_title": "Test Extension",
        "icon_name": "Icons.star",
        "description": "A simple test widget that displays a greeting message",
        "dart_code": '''
import 'package:flutter/material.dart';

class TestWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.all(16),
      child: Column(
        children: [
          Icon(Icons.star, color: Colors.amber, size: 48),
          SizedBox(height: 16),
          Text(
            'Hello from Test Extension!',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          SizedBox(height: 8),
          Text('This is a test extension created by the Terra system.'),
        ],
      ),
    );
  }
}'''
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/extensions",
            headers={"Content-Type": "application/json"},
            json=test_extension
        )
        
        if response.status_code == 200:
            extension_data = response.json()
            print(f"✅ Extension submitted successfully!")
            print(f"   ID: {extension_data['id']}")
            print(f"   Status: {extension_data['status']}")
            return extension_data['id']
        else:
            print(f"❌ Failed to submit extension: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error submitting extension: {e}")
        return None

def test_extension_retrieval(extension_id):
    """Test retrieving extension details"""
    print(f"🧪 Testing extension retrieval for ID: {extension_id}")
    
    try:
        response = requests.get(f"{API_BASE}/extensions/{extension_id}")
        
        if response.status_code == 200:
            extension_data = response.json()
            print(f"✅ Extension retrieved successfully!")
            print(f"   Feature Name: {extension_data['feature_name']}")
            print(f"   Menu Title: {extension_data['menu_title']}")
            print(f"   Status: {extension_data['status']}")
            return extension_data
        else:
            print(f"❌ Failed to retrieve extension: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error retrieving extension: {e}")
        return None

def test_extension_listing():
    """Test listing extensions"""
    print("🧪 Testing extension listing...")
    
    try:
        response = requests.get(f"{API_BASE}/extensions")
        
        if response.status_code == 200:
            extensions = response.json()
            print(f"✅ Retrieved {len(extensions)} extensions")
            for ext in extensions:
                print(f"   - {ext['feature_name']} ({ext['status']})")
            return extensions
        else:
            print(f"❌ Failed to list extensions: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error listing extensions: {e}")
        return []

def test_extension_approval(extension_id):
    """Test approving an extension"""
    print(f"🧪 Testing extension approval for ID: {extension_id}")
    
    try:
        response = requests.patch(
            f"{API_BASE}/extensions/{extension_id}",
            headers={"Content-Type": "application/json"},
            json={"status": "approved"}
        )
        
        if response.status_code == 200:
            print(f"✅ Extension approved successfully!")
            return True
        else:
            print(f"❌ Failed to approve extension: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error approving extension: {e}")
        return False

def test_approved_extensions():
    """Test fetching approved extensions"""
    print("🧪 Testing approved extensions retrieval...")
    
    try:
        response = requests.get(f"{API_BASE}/extensions?status=approved")
        
        if response.status_code == 200:
            extensions = response.json()
            print(f"✅ Retrieved {len(extensions)} approved extensions")
            for ext in extensions:
                print(f"   - {ext['menu_title']} (approved at {ext.get('approved_at', 'N/A')})")
            return extensions
        else:
            print(f"❌ Failed to retrieve approved extensions: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error retrieving approved extensions: {e}")
        return []

def test_invalid_extension():
    """Test submitting an invalid extension"""
    print("🧪 Testing invalid extension submission...")
    
    invalid_extension = {
        "feature_name": "InvalidWidget",
        "menu_title": "Invalid Extension",
        "icon_name": "Icons.star",
        "description": "This extension has invalid Dart code",
        "dart_code": '''
// Invalid Dart code - missing imports and proper structure
class InvalidWidget {
  // Missing build method and proper widget structure
}
'''
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/extensions",
            headers={"Content-Type": "application/json"},
            json=invalid_extension
        )
        
        if response.status_code == 200:
            extension_data = response.json()
            print(f"✅ Invalid extension submitted (should fail tests)")
            print(f"   ID: {extension_data['id']}")
            return extension_data['id']
        else:
            print(f"❌ Failed to submit invalid extension: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error submitting invalid extension: {e}")
        return None

def wait_for_testing_completion(extension_id, max_wait=60):
    """Wait for extension testing to complete"""
    print(f"⏳ Waiting for testing to complete for extension {extension_id}...")
    
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"{API_BASE}/extensions/{extension_id}")
            if response.status_code == 200:
                extension_data = response.json()
                status = extension_data['status']
                
                if status in ['ready_for_approval', 'failed']:
                    print(f"✅ Testing completed! Status: {status}")
                    if extension_data.get('test_results'):
                        test_results = extension_data['test_results']
                        print(f"   Integration Test: {'✅' if test_results.get('integration_test') else '❌'}")
                        print(f"   Functional Test: {'✅' if test_results.get('functional_test') else '❌'}")
                        print(f"   Combined Test: {'✅' if test_results.get('combined_test') else '❌'}")
                    return extension_data
                elif status == 'testing':
                    print(f"   Still testing... ({int(time.time() - start_time)}s)")
                else:
                    print(f"   Status: {status}")
                    
            time.sleep(2)
        except Exception as e:
            print(f"   Error checking status: {e}")
            time.sleep(2)
    
    print(f"❌ Testing timeout after {max_wait} seconds")
    return None

def run_comprehensive_test():
    """Run comprehensive test of the Terra extensions system"""
    print("🚀 Starting comprehensive Terra extensions test...")
    print("=" * 60)
    
    # Test 1: Submit valid extension
    print("\n📝 Test 1: Submit valid extension")
    valid_extension_id = test_extension_submission()
    if not valid_extension_id:
        print("❌ Test 1 failed - cannot continue")
        return False
    
    # Test 2: Submit invalid extension
    print("\n📝 Test 2: Submit invalid extension")
    invalid_extension_id = test_invalid_extension()
    
    # Test 3: List all extensions
    print("\n📝 Test 3: List all extensions")
    all_extensions = test_extension_listing()
    
    # Test 4: Wait for testing completion
    print("\n📝 Test 4: Wait for testing completion")
    valid_extension_data = wait_for_testing_completion(valid_extension_id)
    if invalid_extension_id:
        invalid_extension_data = wait_for_testing_completion(invalid_extension_id)
    
    # Test 5: Retrieve extension details
    print("\n📝 Test 5: Retrieve extension details")
    retrieved_extension = test_extension_retrieval(valid_extension_id)
    
    # Test 6: Approve valid extension
    print("\n📝 Test 6: Approve valid extension")
    if valid_extension_data and valid_extension_data['status'] == 'ready_for_approval':
        approval_success = test_extension_approval(valid_extension_id)
    else:
        print("⚠️  Extension not ready for approval")
        approval_success = False
    
    # Test 7: Check approved extensions
    print("\n📝 Test 7: Check approved extensions")
    approved_extensions = test_approved_extensions()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"   Valid extension submitted: {'✅' if valid_extension_id else '❌'}")
    print(f"   Invalid extension submitted: {'✅' if invalid_extension_id else '❌'}")
    print(f"   Extensions listed: {'✅' if all_extensions else '❌'}")
    print(f"   Testing completed: {'✅' if valid_extension_data else '❌'}")
    print(f"   Extension approved: {'✅' if approval_success else '❌'}")
    print(f"   Approved extensions found: {'✅' if approved_extensions else '❌'}")
    
    success = all([
        valid_extension_id,
        all_extensions,
        valid_extension_data,
        approval_success,
        approved_extensions
    ])
    
    if success:
        print("\n🎉 All tests passed! Terra extensions system is working correctly.")
        print("You can now:")
        print("- Submit extensions via the Flutter app")
        print("- Test extensions automatically")
        print("- Approve extensions for live use")
        print("- See extensions in the side menu")
    else:
        print("\n❌ Some tests failed. Check the backend logs for details.")
    
    return success

if __name__ == "__main__":
    print("Terra Extensions System Test")
    print("=" * 60)
    
    try:
        success = run_comprehensive_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1) 