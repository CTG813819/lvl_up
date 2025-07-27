#!/usr/bin/env python3
"""
Test Custodes Protocol Endpoints
================================

This script tests the custody protocol endpoints to ensure they're working correctly.
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Backend URL
BACKEND_URL = "http://34.202.215.209:8000"

async def test_custody_endpoints():
    """Test all custody protocol endpoints"""
    print("🛡️ Testing Custodes Protocol Endpoints")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Get custody protocol overview
        print("\n1. Testing GET /api/custody")
        try:
            async with session.get(f"{BACKEND_URL}/api/custody") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Success: {data.get('message', 'No message')}")
                    print(f"   Features: {data.get('features', [])}")
                else:
                    print(f"   ❌ Failed: {await response.text()}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        # Test 2: Get custody analytics
        print("\n2. Testing GET /api/custody/analytics")
        try:
            async with session.get(f"{BACKEND_URL}/api/custody/analytics") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Success: Analytics retrieved")
                    analytics = data.get('data', {})
                    print(f"   Overall metrics: {analytics.get('overall_metrics', {})}")
                    print(f"   AI metrics: {list(analytics.get('ai_specific_metrics', {}).keys())}")
                else:
                    print(f"   ❌ Failed: {await response.text()}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        # Test 3: Test AI status for each AI type
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        for ai_type in ai_types:
            print(f"\n3. Testing GET /api/custody/test/{ai_type}/status")
            try:
                async with session.get(f"{BACKEND_URL}/api/custody/test/{ai_type}/status") as response:
                    print(f"   Status: {response.status}")
                    if response.status == 200:
                        data = await response.json()
                        print(f"   ✅ Success: {ai_type} status retrieved")
                        ai_data = data.get('data', {})
                        print(f"   Tests given: {ai_data.get('total_tests_given', 0)}")
                        print(f"   Tests passed: {ai_data.get('total_tests_passed', 0)}")
                        print(f"   Custody level: {ai_data.get('custody_level', 1)}")
                    else:
                        print(f"   ❌ Failed: {await response.text()}")
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        # Test 4: Test force test endpoint (for imperium only)
        print(f"\n4. Testing POST /api/custody/test/imperium/force")
        try:
            async with session.post(f"{BACKEND_URL}/api/custody/test/imperium/force") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Success: Force test initiated")
                    print(f"   Result: {data.get('data', {}).get('message', 'No message')}")
                else:
                    print(f"   ❌ Failed: {await response.text()}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        # Test 5: Test eligibility endpoint
        print(f"\n5. Testing GET /api/custody/eligibility/imperium")
        try:
            async with session.get(f"{BACKEND_URL}/api/custody/eligibility/imperium") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Success: Eligibility checked")
                    eligibility = data.get('data', {})
                    print(f"   Can level up: {eligibility.get('can_level_up', False)}")
                    print(f"   Can create proposals: {eligibility.get('can_create_proposals', False)}")
                else:
                    print(f"   ❌ Failed: {await response.text()}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_custody_endpoints()) 