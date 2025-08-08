#!/usr/bin/env python3
"""
Test script to check if the failing endpoints are now working
"""

import asyncio
import httpx
import json
from datetime import datetime

# Test endpoints that were failing
ENDPOINTS_TO_TEST = [
    ("GET", "/api/project-warmaster/status", "Project Berserk Status"),
    ("GET", "/api/project-horus-v2/charos-stream", "Project Horus v2 Charos Stream"),
    ("GET", "/api/enhanced-testing/status", "Enhanced Testing Status"),
    ("GET", "/api/enhanced-testing/autonomous-weapons", "Autonomous Weapons"),
    ("GET", "/api/ai-integration/weapons", "AI Integration Weapons System"),
    ("GET", "/api/project-warmaster/live-chaos-stream", "Project Berserk Chaos Stream"),
]

async def test_endpoint(base_url: str, method: str, endpoint: str, description: str):
    """Test a single endpoint"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            if method == "GET":
                response = await client.get(f"{base_url}{endpoint}")
            else:
                response = await client.post(f"{base_url}{endpoint}")
            
            print(f"✅ {description}: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
            else:
                print(f"   Error: {response.text[:200]}...")
                
    except Exception as e:
        print(f"❌ {description}: Error - {str(e)}")

async def test_all_endpoints():
    """Test all failing endpoints"""
    base_url = "https://compassionate-truth-production-2fcd.up.railway.app"  # Railway backend
    
    print(f"🔍 Testing failing endpoints at {base_url}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)
    
    for method, endpoint, description in ENDPOINTS_TO_TEST:
        await test_endpoint(base_url, method, endpoint, description)
        print("-" * 40)
    
    print("=" * 80)
    print("✅ Endpoint testing completed!")

if __name__ == "__main__":
    asyncio.run(test_all_endpoints())
