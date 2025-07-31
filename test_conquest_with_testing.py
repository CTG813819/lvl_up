#!/usr/bin/env python3
"""
Test script for Conquest AI with testing infrastructure
Tests app creation with proper testing setup and verifies testing status
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "http://ec2-34-202-215-209.compute-1.amazonaws.com:4001"
GITHUB_TOKEN = "ghp_1234567890abcdef"  # Replace with actual token

async def test_conquest_with_testing():
    """Test Conquest AI app creation with testing infrastructure"""
    
    print("🧪 Testing Conquest AI with Testing Infrastructure")
    print("=" * 60)
    
    # Test data
    app_data = {
        "name": "Test App With Testing",
        "description": "A comprehensive test app to verify testing infrastructure",
        "keywords": ["testing", "flutter", "automation", "quality"],
        "operation_type": "create_new"
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            # 1. Create new app with testing
            print("\n1️⃣ Creating new app with testing infrastructure...")
            
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
            
            # 2. Wait for app creation to complete
            print("\n2️⃣ Waiting for app creation to complete...")
            await asyncio.sleep(10)
            
            # 3. Check deployment status
            print("\n3️⃣ Checking deployment status...")
            
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
                        build_logs = app_deployment.get('build_logs', {})
                        if isinstance(build_logs, str):
                            try:
                                build_logs = json.loads(build_logs)
                            except:
                                build_logs = {}
                        
                        print(f"   Build Logs: {json.dumps(build_logs, indent=2)}")
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
                        if any(keyword in message for keyword in ["test", "testing", "analyze", "format"]):
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
            
            # 5. Verify GitHub repository was created with testing
            print("\n5️⃣ Verifying GitHub repository with testing setup...")
            
            if app_deployment and app_deployment.get('repository_url'):
                repo_url = app_deployment['repository_url']
                repo_name = repo_url.split('/')[-1]
                owner = repo_url.split('/')[-2]
                
                # Check repository contents
                async with session.get(
                    f"https://api.github.com/repos/{owner}/{repo_name}/contents",
                    headers={"Authorization": f"token {GITHUB_TOKEN}"}
                ) as response:
                    if response.status == 200:
                        contents = await response.json()
                        files = [item['name'] for item in contents]
                        
                        print(f"✅ Repository files: {files}")
                        
                        # Check for testing files
                        test_files = [f for f in files if 'test' in f.lower()]
                        if test_files:
                            print(f"✅ Found test files: {test_files}")
                        else:
                            print("⚠️ No test files found")
                        
                        # Check for GitHub Actions workflow
                        workflow_files = [f for f in files if f.endswith('.yml') or f.endswith('.yaml')]
                        if workflow_files:
                            print(f"✅ Found workflow files: {workflow_files}")
                        else:
                            print("⚠️ No workflow files found")
                    else:
                        print(f"❌ Failed to check repository: {response.status}")
            
            # 6. Test the pubspec.yaml fix
            print("\n6️⃣ Testing pubspec.yaml fix...")
            
            if app_deployment and app_deployment.get('repository_url'):
                # Check pubspec.yaml content
                async with session.get(
                    f"https://api.github.com/repos/{owner}/{repo_name}/contents/pubspec.yaml",
                    headers={"Authorization": f"token {GITHUB_TOKEN}"}
                ) as response:
                    if response.status == 200:
                        pubspec_data = await response.json()
                        import base64
                        content = base64.b64decode(pubspec_data['content']).decode('utf-8')
                        
                        print("✅ pubspec.yaml content:")
                        print(content)
                        
                        # Check for duplicate flutter keys
                        flutter_lines = [line for line in content.split('\n') if 'flutter:' in line]
                        if len(flutter_lines) > 1:
                            print("❌ Found duplicate flutter keys in pubspec.yaml")
                        else:
                            print("✅ No duplicate flutter keys found")
                        
                        # Check for integration_test dependency
                        if 'integration_test:' in content:
                            print("✅ integration_test dependency found")
                        else:
                            print("⚠️ integration_test dependency not found")
                    else:
                        print(f"❌ Failed to get pubspec.yaml: {response.status}")
            
            print("\n" + "=" * 60)
            print("🎉 Conquest AI Testing Infrastructure Test Complete!")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(test_conquest_with_testing()) 