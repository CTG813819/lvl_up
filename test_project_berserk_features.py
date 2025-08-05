#!/usr/bin/env python3
"""
Test Project Berserk features that the Flutter app is trying to use
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_project_berserk_features():
    """Test all Project Berserk endpoints that Flutter screen is calling"""
    
    railway_url = "https://lvlup-production.up.railway.app"
    
    print("🧠 Testing Project Berserk Features on Railway")
    print("=" * 60)
    
    # Test endpoints that the Flutter screen is calling
    endpoints = [
        # Main status endpoint
        "/api/project-warmaster/status",
        
        # Chaos stream endpoints
        "/api/project-warmaster/live-chaos-stream",
        "/api/project-warmaster/chaos-code-status", 
        "/api/project-warmaster/autonomous-chaos-code",
        
        # Real-time building endpoints
        "/api/project-warmaster/real-time-building-status",
        "/api/project-warmaster/build-chaos-repository",
        "/api/project-warmaster/create-self-extension",
        
        # Chronicles/chapters endpoints  
        "/api/project-warmaster/create-chapter",
        "/api/project-warmaster/offline-versions",
        
        # Action endpoints
        "/api/project-warmaster/generate-chaos-code",
        "/api/project-warmaster/stealth-assimilation",
        "/api/project-warmaster/living-system-cycle",
        "/api/project-warmaster/internet-learning",
        "/api/project-warmaster/offline-learning",
        
        # Brain visualization (should work)
        "/api/project-warmaster/brain-visualization",
    ]
    
    working_endpoints = []
    broken_endpoints = []
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints:
            try:
                url = f"{railway_url}{endpoint}"
                print(f"\n🔍 Testing: {endpoint}")
                
                async with session.get(url, timeout=10) as response:
                    status = response.status
                    content_type = response.headers.get('content-type', 'unknown')
                    
                    if status == 200:
                        try:
                            data = await response.json()
                            print(f"✅ {endpoint}: OK ({status})")
                            working_endpoints.append(endpoint)
                            
                            # Show sample data for key endpoints
                            if 'live-chaos-stream' in endpoint or 'real-time-building' in endpoint:
                                print(f"   📊 Data preview: {json.dumps(data, indent=2)[:200]}...")
                        except:
                            text = await response.text()
                            print(f"✅ {endpoint}: OK ({status}) - Text response")
                            print(f"   Response: {text[:200]}...")
                            working_endpoints.append(endpoint)
                    else:
                        print(f"❌ {endpoint}: Error {status}")
                        broken_endpoints.append(f"{endpoint} ({status})")
                        
            except asyncio.TimeoutError:
                print(f"⏰ {endpoint}: Timeout")
                broken_endpoints.append(f"{endpoint} (timeout)")
            except Exception as e:
                print(f"❌ {endpoint}: Exception - {str(e)}")
                broken_endpoints.append(f"{endpoint} (exception)")
    
    print(f"\n🎯 Test Summary")
    print("=" * 40)
    print(f"✅ Working endpoints: {len(working_endpoints)}")
    for endpoint in working_endpoints:
        print(f"   ✅ {endpoint}")
    
    print(f"\n❌ Broken endpoints: {len(broken_endpoints)}")
    for endpoint in broken_endpoints:
        print(f"   ❌ {endpoint}")
    
    print(f"\n🔧 Recommendations:")
    if broken_endpoints:
        print("   📝 Need to implement missing endpoints in backend")
        print("   🔄 Update Flutter screen to use working endpoints")
        print("   ⚡ Add fallback/offline mode for broken features")
    else:
        print("   🎉 All endpoints working! Check Flutter implementation.")
        
    print(f"\n🎯 Test completed at {datetime.now()}")

if __name__ == "__main__":
    asyncio.run(test_project_berserk_features())