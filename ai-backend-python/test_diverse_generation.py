#!/usr/bin/env python3
"""
Test script to verify diverse test generation is working
"""

import requests
import json
import time

def test_diverse_generation():
    """Test if diverse test generation is working"""
    base_url = "http://ec2-34-202-215-209.compute-1.amazonaws.com:8000"
    
    print("🧪 Testing diverse test generation...")
    
    try:
        # Test 1: Check if service is running
        print("1. Checking service status...")
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Service is running")
        else:
            print(f"❌ Service returned status: {response.status_code}")
            return
        
        # Test 2: Trigger a custody test for imperium
        print("2. Triggering custody test for imperium...")
        test_response = requests.post(
            f"{base_url}/custody/test/imperium",
            json={"test_category": "knowledge_verification"},
            timeout=30
        )
        
        if test_response.status_code == 200:
            data = test_response.json()
            print("✅ Custody test triggered successfully")
            
            # Check if diverse test generation was used
            test_content = data.get("data", {}).get("test_content", {})
            test_type = test_content.get("test_type", "")
            
            print(f"📊 Test type: {test_type}")
            
            if "diverse" in test_type.lower():
                print("🎉 Diverse test generation is working!")
                print(f"📝 Scenario: {test_content.get('scenario', {}).get('title', 'N/A')}")
            else:
                print("⚠️  Diverse test generation may not be active")
                print(f"📝 Test content: {json.dumps(test_content, indent=2)}")
        else:
            print(f"❌ Failed to trigger custody test: {test_response.status_code}")
            print(f"Response: {test_response.text}")
        
        # Test 3: Check custody analytics to see XP values
        print("3. Checking custody analytics...")
        analytics_response = requests.get(f"{base_url}/custody/analytics", timeout=10)
        
        if analytics_response.status_code == 200:
            analytics_data = analytics_response.json()
            ai_metrics = analytics_data.get("data", {}).get("ai_specific_metrics", {})
            
            print("📊 Current AI metrics:")
            for ai_type, metrics in ai_metrics.items():
                xp = metrics.get("custody_xp", 0)
                level = metrics.get("level", 0)
                print(f"   {ai_type}: XP={xp}, Level={level}")
        else:
            print(f"❌ Failed to get analytics: {analytics_response.status_code}")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    test_diverse_generation() 