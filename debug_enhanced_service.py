#!/usr/bin/env python3
"""
Debug Enhanced Adversarial Testing Service
Test the service endpoints to identify the internal server error
"""

import asyncio
import aiohttp
import json
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_enhanced_service():
    """Test the enhanced adversarial testing service endpoints"""
    print("🔍 Debugging Enhanced Adversarial Testing Service")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Health endpoint
        print("1. Testing health endpoint...")
        try:
            async with session.get('http://localhost:8001/health') as response:
                if response.status == 200:
                    health_data = await response.json()
                    print(f"✅ Health check passed: {health_data}")
                else:
                    print(f"❌ Health check failed: {response.status}")
                    return
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return
        
        # Test 2: Domains endpoint
        print("\n2. Testing domains endpoint...")
        try:
            async with session.get('http://localhost:8001/domains') as response:
                if response.status == 200:
                    domains_data = await response.json()
                    print(f"✅ Domains endpoint working: {len(domains_data.get('domains', []))} domains")
                else:
                    print(f"❌ Domains endpoint failed: {response.status}")
        except Exception as e:
            print(f"❌ Domains endpoint error: {e}")
        
        # Test 3: Complexities endpoint
        print("\n3. Testing complexities endpoint...")
        try:
            async with session.get('http://localhost:8001/complexities') as response:
                if response.status == 200:
                    complexities_data = await response.json()
                    print(f"✅ Complexities endpoint working: {len(complexities_data.get('complexities', []))} complexities")
                else:
                    print(f"❌ Complexities endpoint failed: {response.status}")
        except Exception as e:
            print(f"❌ Complexities endpoint error: {e}")
        
        # Test 4: Generate and execute endpoint with minimal payload
        print("\n4. Testing generate-and-execute endpoint...")
        test_payload = {
            "ai_types": ["imperium", "guardian"],
            "target_domain": "system_level",
            "complexity": "basic"
        }
        
        print(f"📤 Sending payload: {json.dumps(test_payload, indent=2)}")
        
        try:
            async with session.post(
                'http://localhost:8001/generate-and-execute',
                json=test_payload,
                headers={'Content-Type': 'application/json'}
            ) as response:
                print(f"📊 Response status: {response.status}")
                print(f"📊 Response headers: {dict(response.headers)}")
                
                response_text = await response.text()
                print(f"📊 Response body: {response_text[:500]}...")
                
                if response.status == 200:
                    try:
                        result = await response.json()
                        print(f"✅ Generate-and-execute successful!")
                        print(f"📊 Result keys: {list(result.keys())}")
                    except Exception as e:
                        print(f"❌ JSON parsing error: {e}")
                else:
                    print(f"❌ Generate-and-execute failed with status {response.status}")
                    
        except Exception as e:
            print(f"❌ Generate-and-execute error: {e}")
        
        # Test 5: Recent scenarios endpoint
        print("\n5. Testing recent-scenarios endpoint...")
        try:
            async with session.get('http://localhost:8001/recent-scenarios') as response:
                if response.status == 200:
                    scenarios_data = await response.json()
                    print(f"✅ Recent scenarios endpoint working")
                else:
                    print(f"❌ Recent scenarios endpoint failed: {response.status}")
        except Exception as e:
            print(f"❌ Recent scenarios endpoint error: {e}")

async def main():
    """Main function"""
    try:
        await test_enhanced_service()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 