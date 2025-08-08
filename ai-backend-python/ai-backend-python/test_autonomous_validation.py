#!/usr/bin/env python3
"""
Test script for Conquest AI Autonomous Validation
Tests that the backend now runs local validation before pushing to GitHub
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_autonomous_validation():
    """Test Conquest AI with autonomous validation"""
    
    print("🧪 Testing Conquest AI Autonomous Validation")
    print("=" * 50)
    
    # Test data for a simple app with unique name
    import time
    timestamp = int(time.time())
    test_app_data = {
        "name": f"AutoValidationTest{timestamp}",
        "description": "A test app to verify autonomous validation is working",
        "keywords": ["test", "validation", "autonomous", "flutter", "quality"],
        "features": ["authentication", "settings", "navigation"]
    }
    
    try:
        # Test 1: Create app with autonomous validation
        print("\n1️⃣ Creating app with autonomous validation...")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://ec2-34-202-215-209.compute-1.amazonaws.com:4001/api/conquest/create-app",
                json=test_app_data,
                timeout=aiohttp.ClientTimeout(total=300)  # 5 minutes timeout
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ App creation response: {json.dumps(result, indent=2)}")
                    
                    if result.get("status") == "success":
                        print("✅ App created successfully with autonomous validation!")
                        
                        # Check if validation results are included
                        if "validation_results" in result:
                            print("✅ Validation results included in response")
                        else:
                            print("⚠️ No validation results in response")
                            
                    elif result.get("status") == "error":
                        print(f"❌ App creation failed: {result.get('message')}")
                        if "validation_results" in result:
                            print(f"🔍 Validation results: {json.dumps(result['validation_results'], indent=2)}")
                            
                else:
                    error_text = await response.text()
                    print(f"❌ HTTP {response.status}: {error_text}")
        
        # Test 2: Check deployments to see validation status
        print("\n2️⃣ Checking deployments for validation status...")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "http://ec2-34-202-215-209.compute-1.amazonaws.com:4001/api/conquest/deployments"
            ) as response:
                
                if response.status == 200:
                    deployments = await response.json()
                    print(f"✅ Deployments response: {json.dumps(deployments, indent=2)}")
                    
                    if deployments.get("status") == "success" and deployments.get("deployments"):
                        latest = deployments["deployments"][0]
                        print(f"📊 Latest deployment: {latest['app_name']} - Status: {latest['status']}")
                        
                        # Check if build logs contain validation info
                        if "build_logs" in latest:
                            try:
                                build_logs = json.loads(latest["build_logs"])
                                if "validation_results" in build_logs:
                                    print("✅ Validation results found in build logs")
                                    print(f"🔍 Validation details: {json.dumps(build_logs['validation_results'], indent=2)}")
                                else:
                                    print("⚠️ No validation results in build logs")
                            except:
                                print("⚠️ Could not parse build logs")
                    else:
                        print("⚠️ No deployments found")
                        
                else:
                    error_text = await response.text()
                    print(f"❌ HTTP {response.status}: {error_text}")
        
        # Test 3: Check progress logs
        print("\n3️⃣ Checking progress logs...")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "http://ec2-34-202-215-209.compute-1.amazonaws.com:4001/api/conquest/progress-logs"
            ) as response:
                
                if response.status == 200:
                    logs = await response.json()
                    print(f"✅ Progress logs: {len(logs)} entries found")
                    
                    # Look for validation-related logs
                    validation_logs = []
                    for log in logs:
                        if isinstance(log, dict) and "message" in log:
                            if "validation" in log["message"].lower():
                                validation_logs.append(log)
                        elif isinstance(log, str) and "validation" in log.lower():
                            validation_logs.append({"message": log})
                    
                    if validation_logs:
                        print(f"🔍 Found {len(validation_logs)} validation-related logs:")
                        for log in validation_logs[-3:]:  # Show last 3
                            print(f"   - {log.get('message', str(log))}")
                    else:
                        print("⚠️ No validation-related logs found")
                        
                else:
                    error_text = await response.text()
                    print(f"❌ HTTP {response.status}: {error_text}")
        
        print("\n🎉 Autonomous Validation Test Complete!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_autonomous_validation()) 