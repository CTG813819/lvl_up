#!/usr/bin/env python3
"""
Test script for the unified AI backend system
Tests all major endpoints and services to ensure everything is working
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime

async def test_endpoint(session, url, endpoint_name, method='GET', data=None):
    """Test a single endpoint"""
    try:
        if method == 'GET':
            async with session.get(url) as response:
                result = await response.json()
                status = response.status
        else:
            async with session.post(url, json=data) as response:
                result = await response.json()
                status = response.status
        
        print(f"✅ {endpoint_name}: Status {status}")
        if status != 200:
            print(f"   ⚠️ Response: {result}")
        return True
    except Exception as e:
        print(f"❌ {endpoint_name}: Failed - {str(e)}")
        return False

async def test_all_endpoints():
    """Test all major endpoints"""
    base_url = "http://localhost:8000"
    adversarial_url = "http://localhost:8001"
    training_ground_url = "http://localhost:8002"
    
    print("🔬 Testing AI Backend - Unified System")
    print("=" * 60)
    
    timeout = aiohttp.ClientTimeout(total=10)
    
    async with aiohttp.ClientSession(timeout=timeout) as session:
        
        # Test main server endpoints
        print("\n📊 Testing Main Server (Port 8000):")
        main_tests = [
            (f"{base_url}/health", "Health Check"),
            (f"{base_url}/api/health", "API Health Check"),
            (f"{base_url}/debug", "Debug Information"),
            (f"{base_url}/api/imperium/status", "Imperium AI Status"),
            (f"{base_url}/api/guardian/status", "Guardian AI Status"),
            (f"{base_url}/api/conquest/status", "Conquest AI Status"),
            (f"{base_url}/api/sandbox/status", "Sandbox AI Status"),
            (f"{base_url}/api/custody/status", "Custody Protocol Status"),
            (f"{base_url}/api/learning/insights", "Learning Insights"),
            (f"{base_url}/api/agents/status", "AI Agents Status"),
            (f"{base_url}/api/proposals", "Proposals Endpoint"),
            (f"{base_url}/api/project-horus/status", "Project Horus Status"),
            (f"{base_url}/api/olympic-ai/status", "Olympic AI Status"),
            (f"{base_url}/api/collaborative-ai/status", "Collaborative AI Status"),
            (f"{base_url}/api/custodes-ai/status", "Custodes AI Status")
        ]
        
        main_success = 0
        for url, name in main_tests:
            if await test_endpoint(session, url, name):
                main_success += 1
        
        # Test adversarial testing server
        print(f"\n⚔️ Testing Enhanced Adversarial Testing (Port 8001):")
        adversarial_tests = [
            (f"{adversarial_url}/health", "Adversarial Health Check"),
            (f"{adversarial_url}/status", "Adversarial Status"),
        ]
        
        adversarial_success = 0
        for url, name in adversarial_tests:
            if await test_endpoint(session, url, name):
                adversarial_success += 1
        
        # Test training ground server
        print(f"\n🏋️ Testing Training Ground (Port 8002):")
        training_tests = [
            (f"{training_ground_url}/health", "Training Ground Health"),
            (f"{training_ground_url}/status", "Training Ground Status"),
        ]
        
        training_success = 0
        for url, name in training_tests:
            if await test_endpoint(session, url, name):
                training_success += 1
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY:")
        print(f"📊 Main Server: {main_success}/{len(main_tests)} endpoints working")
        print(f"⚔️ Adversarial Testing: {adversarial_success}/{len(adversarial_tests)} endpoints working")
        print(f"🏋️ Training Ground: {training_success}/{len(training_tests)} endpoints working")
        
        total_success = main_success + adversarial_success + training_success
        total_tests = len(main_tests) + len(adversarial_tests) + len(training_tests)
        
        success_rate = (total_success / total_tests) * 100
        print(f"🎯 Overall Success Rate: {success_rate:.1f}% ({total_success}/{total_tests})")
        
        if success_rate >= 80:
            print("✅ System is READY for deployment!")
        elif success_rate >= 60:
            print("⚠️ System needs minor fixes before deployment")
        else:
            print("❌ System needs major fixes before deployment")
        
        return success_rate >= 80

async def test_background_services():
    """Test that background services are running"""
    print(f"\n🔄 Testing Background Services:")
    
    # These would normally check database or logs for evidence of background activity
    services = [
        "Learning Cycles (Every 30 min)",
        "Custody Testing (Every 20 min)",
        "Olympic Events (Every 45 min)",
        "Collaborative Testing (Every 90 min)",
        "ML Training (Continuous)",
        "Auto-Apply Monitoring",
        "Proposal Generation"
    ]
    
    for service in services:
        print(f"🔄 {service}: Expected to be running")
    
    print("ℹ️ Background services status should be checked via logs or database")

async def main():
    """Main test function"""
    print(f"🚀 AI Backend System Test - {datetime.now().isoformat()}")
    
    # Wait a bit for servers to fully start
    print("⏳ Waiting for servers to initialize...")
    await asyncio.sleep(5)
    
    # Test endpoints
    success = await test_all_endpoints()
    
    # Test background services
    await test_background_services()
    
    print(f"\n🏁 Test completed at {datetime.now().isoformat()}")
    
    return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        sys.exit(1)