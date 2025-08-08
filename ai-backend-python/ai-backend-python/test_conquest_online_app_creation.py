#!/usr/bin/env python3
"""
Test Conquest AI Online App Creation
"""

import asyncio
import aiohttp
import json

async def test_conquest_online_app_creation():
    """Test that Conquest AI can create real apps online"""
    base_url = "http://34.202.215.209:4000"
    
    print("🌐 Testing Conquest AI Online App Creation...")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Create a real app online
        print("1. Testing /api/conquest/create-app (Online Creation)")
        try:
            app_data = {
                "name": "Online Test App",
                "description": "A test app created online by Conquest AI to verify internet integration",
                "keywords": ["test", "online", "conquest", "ai", "flutter"],
                "app_type": "general",
                "features": ["authentication", "home_screen"],
                "operation_type": "create_new"
            }
            
            async with session.post(
                f"{base_url}/api/conquest/create-app",
                json=app_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Online app creation successful!")
                    print(f"   App ID: {data.get('app_id', 'Unknown')}")
                    print(f"   App Name: {data.get('app_name', 'Unknown')}")
                    print(f"   Repository URL: {data.get('repository_url', 'Unknown')}")
                    print(f"   APK URL: {data.get('apk_url', 'Unknown')}")
                    print(f"   Message: {data.get('message', 'Unknown')}")
                    
                    # Check if it's a real GitHub URL
                    repo_url = data.get('repository_url', '')
                    if 'github.com' in repo_url and 'conquest-ai' not in repo_url:
                        print(f"   🌐 REAL ONLINE REPOSITORY: {repo_url}")
                    else:
                        print(f"   ⚠️ Mock repository (fallback): {repo_url}")
                        
                else:
                    error_text = await response.text()
                    print(f"❌ Online app creation failed: {response.status}")
                    print(f"   Error: {error_text}")
        except Exception as e:
            print(f"❌ Online app creation error: {e}")
        
        # Test 2: Check deployments to see if the app was created
        print("\n2. Testing /api/conquest/deployments (Verify Online Creation)")
        try:
            async with session.get(f"{base_url}/api/conquest/deployments") as response:
                if response.status == 200:
                    data = await response.json()
                    deployments = data.get('deployments', [])
                    print(f"✅ Found {len(deployments)} deployments")
                    
                    if deployments:
                        latest = deployments[0]
                        print(f"   Latest deployment:")
                        print(f"     App: {latest.get('app_name', 'Unknown')}")
                        print(f"     Repository: {latest.get('repository_url', 'Unknown')}")
                        print(f"     APK: {latest.get('apk_url', 'Unknown')}")
                        print(f"     Status: {latest.get('status', 'Unknown')}")
                        
                        # Check if it's a real online repository
                        repo_url = latest.get('repository_url', '')
                        if 'github.com' in repo_url and 'conquest-ai' not in repo_url:
                            print(f"     🌐 REAL ONLINE REPOSITORY: {repo_url}")
                        else:
                            print(f"     ⚠️ Mock repository (fallback): {repo_url}")
                    else:
                        print("   No deployments found")
                else:
                    print(f"❌ Failed to get deployments: {response.status}")
        except Exception as e:
            print(f"❌ Deployments check error: {e}")
        
        # Test 3: Check progress logs for online activity
        print("\n3. Testing /api/conquest/progress-logs (Online Activity)")
        try:
            async with session.get(f"{base_url}/api/conquest/progress-logs") as response:
                if response.status == 200:
                    data = await response.json()
                    logs = data.get('logs', [])
                    print(f"✅ Found {len(logs)} progress logs")
                    
                    if logs:
                        latest_log = logs[0]
                        print(f"   Latest log:")
                        print(f"     App: {latest_log.get('app_name', 'Unknown')}")
                        print(f"     Status: {latest_log.get('status', 'Unknown')}")
                        print(f"     Message: {latest_log.get('message', 'Unknown')}")
                        
                        # Check for online indicators
                        message = latest_log.get('message', '').lower()
                        if any(word in message for word in ['github', 'repository', 'online', 'api']):
                            print(f"     🌐 ONLINE ACTIVITY DETECTED")
                        else:
                            print(f"     ⚠️ Local activity only")
                    else:
                        print("   No progress logs found")
                else:
                    print(f"❌ Failed to get progress logs: {response.status}")
        except Exception as e:
            print(f"❌ Progress logs check error: {e}")
    
    print("\n🎉 Conquest AI Online App Creation Testing Completed!")
    print("\n📋 Summary:")
    print("   - Conquest AI should create real GitHub repositories")
    print("   - Apps should be built using GitHub Actions")
    print("   - APKs should be available for download")
    print("   - All activity should be logged in the database")

if __name__ == "__main__":
    asyncio.run(test_conquest_online_app_creation()) 