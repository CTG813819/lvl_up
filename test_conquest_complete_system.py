#!/usr/bin/env python3
"""
Comprehensive test script for Conquest AI complete system
Tests app creation with rigorous testing, frontend statistics, and status tracking
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "http://ec2-34-202-215-209.compute-1.amazonaws.com:4000"

async def test_conquest_complete_system():
    """Test the complete Conquest AI system with rigorous testing"""
    
    print("🧪 Testing Conquest AI Complete System")
    print("=" * 60)
    
    # Test data for a comprehensive app
    app_data = {
        "name": "Complete Test App",
        "description": "A comprehensive test app to verify the complete Conquest AI system with rigorous testing infrastructure",
        "keywords": ["testing", "flutter", "automation", "quality", "comprehensive"],
        "operation_type": "create_new"
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            # 1. Create new app with comprehensive testing
            print("\n1️⃣ Creating comprehensive test app...")
            
            async with session.post(
                f"{BACKEND_URL}/api/conquest/create-app",
                json=app_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    app_id = result.get("app_id")
                    print(f"✅ App created successfully: {app_id}")
                else:
                    error_text = await response.text()
                    print(f"❌ Failed to create app: {error_text}")
                    return
            
            # 2. Wait for app creation and testing to complete
            print("\n2️⃣ Waiting for app creation and testing to complete...")
            await asyncio.sleep(30)  # Wait longer for testing to complete
            
            # 3. Check deployment status with test results
            print("\n3️⃣ Checking deployment status with test results...")
            
            async with session.get(
                f"{BACKEND_URL}/api/conquest/deployments",
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    deployments = await response.json()
                    app_deployment = None
                    
                    for deployment in deployments.get("deployments", []):
                        if deployment.get("id") == app_id:
                            app_deployment = deployment
                            break
                    
                    if app_deployment:
                        print(f"✅ Found deployment: {app_deployment.get('app_name')}")
                        print(f"   Status: {app_deployment.get('status')}")
                        print(f"   Repository: {app_deployment.get('repository_url')}")
                        print(f"   APK URL: {app_deployment.get('apk_url')}")
                        
                        # Check for testing information
                        test_status = app_deployment.get('test_status')
                        test_output = app_deployment.get('test_output')
                        build_logs = app_deployment.get('build_logs', {})
                        
                        if isinstance(build_logs, str):
                            try:
                                build_logs = json.loads(build_logs)
                            except:
                                build_logs = {}
                        
                        print(f"   Test Status: {test_status}")
                        print(f"   Test Output: {test_output[:200] if test_output else 'None'}...")
                        print(f"   Build Logs: {json.dumps(build_logs, indent=2)}")
                        
                        # Verify test status is properly set
                        if test_status:
                            print(f"✅ Test status properly recorded: {test_status}")
                        else:
                            print("⚠️ Test status not recorded")
                            
                    else:
                        print("❌ Deployment not found")
                else:
                    error_text = await response.text()
                    print(f"❌ Failed to get deployments: {error_text}")
            
            # 4. Check progress logs for testing information
            print("\n4️⃣ Checking progress logs for testing information...")
            
            async with session.get(
                f"{BACKEND_URL}/api/conquest/progress-logs",
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    logs = await response.json()
                    testing_logs = []
                    
                    for log in logs.get("logs", []):
                        message = log.get("message", "").lower()
                        if any(keyword in message for keyword in ["test", "testing", "analyze", "format", "workflow"]):
                            testing_logs.append(log)
                    
                    if testing_logs:
                        print(f"✅ Found {len(testing_logs)} testing-related logs:")
                        for log in testing_logs[-5:]:  # Show last 5
                            print(f"   - {log.get('message')}")
                    else:
                        print("⚠️ No testing logs found")
                else:
                    error_text = await response.text()
                    print(f"❌ Failed to get progress logs: {error_text}")
            
            # 5. Test statistics API
            print("\n5️⃣ Testing statistics and analytics...")
            
            # Check if there's a statistics endpoint
            async with session.get(
                f"{BACKEND_URL}/api/conquest/statistics",
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    stats = await response.json()
                    print("✅ Statistics API available:")
                    print(f"   {json.dumps(stats, indent=2)}")
                else:
                    print("ℹ️ Statistics API not available, using deployment data")
            
            # 6. Verify comprehensive deployment data
            print("\n6️⃣ Verifying comprehensive deployment data...")
            
            if app_deployment:
                required_fields = [
                    'id', 'app_name', 'status', 'repository_url', 
                    'created_at', 'test_status', 'test_output'
                ]
                
                missing_fields = []
                for field in required_fields:
                    if field not in app_deployment or app_deployment[field] is None:
                        missing_fields.append(field)
                
                if missing_fields:
                    print(f"⚠️ Missing fields: {missing_fields}")
                else:
                    print("✅ All required fields present")
                
                # Check test status values
                valid_test_statuses = ['passed', 'failed', 'success', 'failure', 'unknown']
                if app_deployment.get('test_status') in valid_test_statuses:
                    print(f"✅ Valid test status: {app_deployment.get('test_status')}")
                else:
                    print(f"⚠️ Unexpected test status: {app_deployment.get('test_status')}")
            
            print("\n" + "=" * 60)
            print("🎉 Conquest AI Complete System Test Results:")
            print("=" * 60)
            
            if app_deployment:
                print(f"✅ App Creation: SUCCESS")
                print(f"✅ Repository: {app_deployment.get('repository_url', 'N/A')}")
                print(f"✅ Status: {app_deployment.get('status', 'N/A')}")
                print(f"✅ Test Status: {app_deployment.get('test_status', 'N/A')}")
                print(f"✅ APK Available: {'Yes' if app_deployment.get('apk_url') else 'No'}")
                
                # Summary for frontend
                print(f"\n📊 Frontend Statistics Summary:")
                print(f"   - Total Apps: {len(deployments.get('deployments', []))}")
                print(f"   - Completed: {len([d for d in deployments.get('deployments', []) if d.get('status') == 'completed'])}")
                print(f"   - Failed: {len([d for d in deployments.get('deployments', []) if d.get('status') == 'failed'])}")
                print(f"   - Tested: {len([d for d in deployments.get('deployments', []) if d.get('test_status')])}")
                print(f"   - Tests Passed: {len([d for d in deployments.get('deployments', []) if d.get('test_status') in ['passed', 'success']])}")
                print(f"   - Tests Failed: {len([d for d in deployments.get('deployments', []) if d.get('test_status') in ['failed', 'failure']])}")
            else:
                print("❌ App Creation: FAILED")
            
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(test_conquest_complete_system()) 