#!/usr/bin/env python3
"""
Test Conquest AI Fixes
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

# EC2 Configuration
EC2_BASE_URL = "http://34.202.215.209:4000"

async def test_conquest_ai_fixes():
    """Test the Conquest AI fixes"""
    print("🔧 Testing Conquest AI Fixes...")
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Progress logs with longer timeout
        print("\n1. Testing Progress Logs (should work with longer timeout)")
        try:
            async with session.get(f"{EC2_BASE_URL}/api/conquest/progress-logs", timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Success: Progress logs retrieved in {response.headers.get('X-Response-Time', 'N/A')}")
                    print(f"   Status: {data.get('status', 'N/A')}")
                    print(f"   Logs Count: {len(data.get('logs', []))}")
                else:
                    print(f"❌ Failed: Status {response.status}")
        except asyncio.TimeoutError:
            print("❌ Timeout: Progress logs still timing out")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        # Test 2: App creation with proper JSON format
        print("\n2. Testing App Creation with Proper JSON Format")
        try:
            app_data = {
                "name": "TestAppFixed",
                "description": "A test app to verify the fixes work correctly",
                "keywords": ["test", "flutter", "fix"],
                "app_type": "flutter"
            }
            
            async with session.post(
                f"{EC2_BASE_URL}/api/conquest/create-app",
                json=app_data,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Success: App creation worked!")
                    print(f"   App ID: {data.get('app_id', 'N/A')}")
                    print(f"   Status: {data.get('status', 'N/A')}")
                elif response.status == 422:
                    error_data = await response.json()
                    print(f"⚠️ Validation Error: {error_data.get('detail', 'Unknown validation error')}")
                else:
                    print(f"❌ Failed: Status {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        # Test 3: Check deployments after app creation
        print("\n3. Testing Deployments After App Creation")
        try:
            async with session.get(f"{EC2_BASE_URL}/api/conquest/deployments") as response:
                if response.status == 200:
                    data = await response.json()
                    deployments = data.get('deployments', [])
                    print(f"✅ Success: Found {len(deployments)} deployments")
                    if deployments:
                        for i, deployment in enumerate(deployments[:3]):
                            print(f"   {i+1}. {deployment.get('app_name', 'N/A')} - {deployment.get('status', 'N/A')}")
                    else:
                        print("   No deployments found (this is expected if app creation failed)")
                else:
                    print(f"❌ Failed: Status {response.status}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        # Test 4: Check enhanced statistics
        print("\n4. Testing Enhanced Statistics")
        try:
            async with session.get(f"{EC2_BASE_URL}/api/conquest/enhanced-statistics") as response:
                if response.status == 200:
                    data = await response.json()
                    stats = data.get('statistics', {})
                    overview = stats.get('overview', {})
                    print(f"✅ Success: Enhanced statistics retrieved")
                    print(f"   Total Apps: {overview.get('total_apps', 0)}")
                    print(f"   Completed Apps: {overview.get('completed_apps', 0)}")
                    print(f"   Success Rate: {overview.get('success_rate', 0)}%")
                else:
                    print(f"❌ Failed: Status {response.status}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

async def main():
    """Run the test"""
    print("🚀 Testing Conquest AI Fixes")
    print("=" * 50)
    
    await test_conquest_ai_fixes()
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")
    print("\nSummary of fixes:")
    print("- Progress logs timeout increased from 5 to 15 seconds")
    print("- App creation JSON format improved with validation")
    print("- Better error handling for backend responses")
    print("- Enhanced logging for debugging")

if __name__ == "__main__":
    asyncio.run(main()) 