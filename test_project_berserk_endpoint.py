#!/usr/bin/env python3
"""
Test Project Berserk (Warmaster) endpoints including brain visualization
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_project_berserk_endpoints():
    """Test Project Berserk endpoints on Railway"""
    
    railway_url = "https://lvlup-production.up.railway.app"
    
    print("🧠 Testing Project Berserk (Warmaster) Endpoints on Railway")
    print("=" * 60)
    
    # Test endpoints
    endpoints = [
        "/api/project-warmaster/status",
        "/api/project-warmaster/brain-visualization",
        "/api/project-warmaster/capabilities",
        "/api/project-warmaster/learning-sessions",
    ]
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints:
            try:
                url = f"{railway_url}{endpoint}"
                print(f"\n🔍 Testing: {url}")
                
                async with session.get(url, timeout=10) as response:
                    status = response.status
                    content_type = response.headers.get('content-type', 'unknown')
                    
                    if status == 200:
                        try:
                            data = await response.json()
                            print(f"✅ {endpoint}: OK ({status})")
                            print(f"   Content-Type: {content_type}")
                            
                            # Special handling for brain visualization
                            if 'brain-visualization' in endpoint:
                                print("   🧠 BRAIN VISUALIZATION DATA:")
                                if 'data' in data:
                                    brain_data = data['data']
                                    for key, value in brain_data.items():
                                        print(f"      {key}: {value}")
                                else:
                                    print(f"      Raw data: {json.dumps(data, indent=2)[:300]}...")
                            else:
                                print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
                        except:
                            text = await response.text()
                            print(f"✅ {endpoint}: OK ({status}) - Text response")
                            print(f"   Response: {text[:200]}...")
                    else:
                        print(f"❌ {endpoint}: Error {status}")
                        
            except asyncio.TimeoutError:
                print(f"⏰ {endpoint}: Timeout")
            except Exception as e:
                print(f"❌ {endpoint}: Exception - {str(e)}")
    
    print(f"\n🎯 Test completed at {datetime.now()}")

if __name__ == "__main__":
    asyncio.run(test_project_berserk_endpoints())