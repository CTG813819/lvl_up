#!/usr/bin/env python3
"""
Test Flutter App Endpoints
Tests the specific endpoints that the Flutter app is trying to access
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

# Backend URL
BACKEND_URL = "http://34.202.215.209:8000"

async def test_flutter_endpoints():
    """Test the endpoints that the Flutter app is trying to access"""
    print("🔍 Testing Flutter App Endpoints...")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Agents data endpoint (AI_GROWTH_ANALYTICS_PROVIDER)
        print("\n1. Testing /api/imperium/agents (Agents Data)")
        try:
            start_time = time.time()
            async with session.get(f"{BACKEND_URL}/api/imperium/agents", timeout=aiohttp.ClientTimeout(total=45)) as response:
                elapsed = time.time() - start_time
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Success: {response.status} in {elapsed:.2f}s")
                    print(f"   Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    if 'agents' in data:
                        agents = data['agents']
                        print(f"   Agents count: {len(agents)}")
                        for agent_id, agent_data in list(agents.items())[:3]:  # Show first 3
                            print(f"   - {agent_id}: {agent_data.get('status', 'N/A')}")
                else:
                    print(f"❌ Failed: {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text[:200]}...")
        except asyncio.TimeoutError:
            print(f"❌ Timeout after 45 seconds")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        # Test 2: Growth analysis endpoint
        print("\n2. Testing /api/growth/analysis (Growth Analysis)")
        try:
            start_time = time.time()
            async with session.get(f"{BACKEND_URL}/api/growth/analysis", timeout=aiohttp.ClientTimeout(total=45)) as response:
                elapsed = time.time() - start_time
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Success: {response.status} in {elapsed:.2f}s")
                    print(f"   Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                else:
                    print(f"❌ Failed: {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text[:200]}...")
        except asyncio.TimeoutError:
            print(f"❌ Timeout after 45 seconds")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        # Test 3: Growth insights endpoint
        print("\n3. Testing /api/growth/insights (Growth Insights)")
        try:
            start_time = time.time()
            async with session.get(f"{BACKEND_URL}/api/growth/insights", timeout=aiohttp.ClientTimeout(total=45)) as response:
                elapsed = time.time() - start_time
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Success: {response.status} in {elapsed:.2f}s")
                    print(f"   Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                else:
                    print(f"❌ Failed: {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text[:200]}...")
        except asyncio.TimeoutError:
            print(f"❌ Timeout after 45 seconds")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        # Test 4: Learning data endpoint (Recent Activity)
        print("\n4. Testing /api/learning/data (Recent Activity)")
        try:
            start_time = time.time()
            async with session.get(f"{BACKEND_URL}/api/learning/data", timeout=aiohttp.ClientTimeout(total=45)) as response:
                elapsed = time.time() - start_time
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Success: {response.status} in {elapsed:.2f}s")
                    print(f"   Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                else:
                    print(f"❌ Failed: {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text[:200]}...")
        except asyncio.TimeoutError:
            print(f"❌ Timeout after 45 seconds")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        # Test 5: Imperium status endpoint
        print("\n5. Testing /api/imperium/status (Imperium Status)")
        try:
            start_time = time.time()
            async with session.get(f"{BACKEND_URL}/api/imperium/status", timeout=aiohttp.ClientTimeout(total=45)) as response:
                elapsed = time.time() - start_time
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Success: {response.status} in {elapsed:.2f}s")
                    print(f"   Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                else:
                    print(f"❌ Failed: {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text[:200]}...")
        except asyncio.TimeoutError:
            print(f"❌ Timeout after 45 seconds")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 Flutter Endpoint Testing Complete")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_flutter_endpoints()) 