#!/usr/bin/env python3
"""
Test script for the Book of Lorgar feature.
This script tests the training data upload functionality.
"""

import requests
import json
from datetime import datetime

# Backend URL
BACKEND_URL = "http://34.202.215.209:4000"

def test_upload_training_data():
    """Test uploading training data to the Book of Lorgar."""
    
    # Sample training data
    training_data = {
        "title": "Flutter State Management with Provider",
        "description": "Provider is a wrapper around InheritedWidget to make them easier to use and more reusable. It provides a way to share state between widgets in a clean and efficient manner.",
        "code": """
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

class CounterProvider extends ChangeNotifier {
  int _count = 0;
  int get count => _count;
  
  void increment() {
    _count++;
    notifyListeners();
  }
}

class CounterWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Consumer<CounterProvider>(
      builder: (context, counter, child) {
        return Text('Count: \${counter.count}');
      },
    );
  }
}
        """,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        print("📚 Testing Book of Lorgar upload...")
        
        response = requests.post(
            f"{BACKEND_URL}/api/ai/upload-training-data",
            headers={"Content-Type": "application/json"},
            json=training_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload successful!")
            print(f"📝 ID: {result.get('id')}")
            print(f"📊 Status: {result.get('status')}")
            print(f"💬 Message: {result.get('message')}")
            return True
        else:
            print(f"❌ Upload failed with status {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing upload: {e}")
        return False

def test_get_training_data():
    """Test retrieving training data."""
    
    try:
        print("\n📖 Testing training data retrieval...")
        
        response = requests.get(
            f"{BACKEND_URL}/api/ai/training-data",
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Retrieval successful!")
            print(f"📊 Total records: {result.get('total', 0)}")
            
            data = result.get('data', [])
            if data:
                print("📝 Recent entries:")
                for item in data[:3]:  # Show first 3 entries
                    print(f"  - {item.get('title')} ({item.get('status')})")
            else:
                print("📝 No training data found")
            return True
        else:
            print(f"❌ Retrieval failed with status {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing retrieval: {e}")
        return False

def test_backend_health():
    """Test if the backend is running."""
    
    try:
        print("🏥 Testing backend health...")
        
        response = requests.get(
            f"{BACKEND_URL}/api/health",
            timeout=5
        )
        
        if response.status_code == 200:
            print("✅ Backend is healthy!")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 Testing Book of Lorgar Feature")
    print("=" * 40)
    
    # Test backend health first
    if not test_backend_health():
        print("\n❌ Backend is not available. Please check if the server is running.")
        return
    
    # Test upload functionality
    upload_success = test_upload_training_data()
    
    # Test retrieval functionality
    retrieval_success = test_get_training_data()
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    print(f"✅ Upload: {'PASS' if upload_success else 'FAIL'}")
    print(f"✅ Retrieval: {'PASS' if retrieval_success else 'FAIL'}")
    
    if upload_success and retrieval_success:
        print("\n🎉 All tests passed! Book of Lorgar is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the backend logs.")

if __name__ == "__main__":
    main() 