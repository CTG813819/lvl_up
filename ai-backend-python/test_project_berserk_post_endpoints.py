#!/usr/bin/env python3
"""
Test Project Berserk POST endpoints that the Flutter app needs
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_project_berserk_post_endpoints():
    """Test Project Berserk POST endpoints with proper HTTP methods"""
    
    railway_url = "https://lvlup-production.up.railway.app"
    
    print("🧠 Testing Project Berserk POST Endpoints on Railway")
    print("=" * 60)
    
    # POST endpoints that need testing
    post_endpoints = [
        # Action endpoints that should use POST
        ("/api/project-warmaster/generate-chaos-code", {}),
        ("/api/project-warmaster/build-chaos-repository", {"repository_type": "auto"}),
        ("/api/project-warmaster/create-self-extension", {"extension_type": "auto"}),
        ("/api/project-warmaster/create-chapter", {"chapter_type": "activity_log"}),
        ("/api/project-warmaster/stealth-assimilation", {"user_id": "user_001"}),
        ("/api/project-warmaster/living-system-cycle", {}),
        ("/api/project-warmaster/internet-learning", {}),
        ("/api/project-warmaster/offline-learning", {}),
        ("/api/project-warmaster/learn", {"topics": ["Flutter", "AI"]}),
        ("/api/project-warmaster/self-improve", {}),
    ]
    
    # GET endpoints that should work
    get_endpoints = [
        "/api/project-warmaster/live-chaos-stream",
        "/api/project-warmaster/chaos-code-status", 
        "/api/project-warmaster/autonomous-chaos-code",
        "/api/project-warmaster/real-time-building-status",
        "/api/project-warmaster/offline-versions",
        "/api/project-warmaster/brain-visualization",
        "/api/project-warmaster/status",
        "/api/project-warmaster/capabilities",
    ]
    
    working_features = []
    broken_features = []
    
    async with aiohttp.ClientSession() as session:
        print("\n🔄 Testing POST Endpoints:")
        print("-" * 40)
        
        for endpoint, payload in post_endpoints:
            try:
                url = f"{railway_url}{endpoint}"
                print(f"\n🔍 POST {endpoint}")
                
                async with session.post(
                    url, 
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=15
                ) as response:
                    status = response.status
                    
                    if status == 200:
                        try:
                            data = await response.json()
                            print(f"✅ POST {endpoint}: OK ({status})")
                            working_features.append(f"POST {endpoint}")
                            
                            # Show key data
                            if 'message' in data:
                                print(f"   📝 Message: {data['message']}")
                        except:
                            text = await response.text()
                            print(f"✅ POST {endpoint}: OK ({status})")
                            working_features.append(f"POST {endpoint}")
                    else:
                        error_text = await response.text()
                        print(f"❌ POST {endpoint}: Error {status}")
                        print(f"   Error: {error_text[:100]}...")
                        broken_features.append(f"POST {endpoint} ({status})")
                        
            except asyncio.TimeoutError:
                print(f"⏰ POST {endpoint}: Timeout")
                broken_features.append(f"POST {endpoint} (timeout)")
            except Exception as e:
                print(f"❌ POST {endpoint}: Exception - {str(e)}")
                broken_features.append(f"POST {endpoint} (exception)")
        
        print("\n📊 Testing GET Endpoints:")
        print("-" * 40)
        
        for endpoint in get_endpoints:
            try:
                url = f"{railway_url}{endpoint}"
                print(f"\n🔍 GET {endpoint}")
                
                async with session.get(url, timeout=10) as response:
                    status = response.status
                    
                    if status == 200:
                        try:
                            data = await response.json()
                            print(f"✅ GET {endpoint}: OK ({status})")
                            working_features.append(f"GET {endpoint}")
                            
                            # Show live data for key endpoints
                            if 'live-chaos-stream' in endpoint:
                                if 'chaos_stream' in data:
                                    print(f"   🔥 Live chaos code available!")
                            elif 'real-time-building' in endpoint:
                                if 'status' in data:
                                    print(f"   🏗️ Building status: {data.get('status', 'unknown')}")
                        except:
                            print(f"✅ GET {endpoint}: OK ({status})")
                            working_features.append(f"GET {endpoint}")
                    else:
                        print(f"❌ GET {endpoint}: Error {status}")
                        broken_features.append(f"GET {endpoint} ({status})")
                        
            except Exception as e:
                print(f"❌ GET {endpoint}: Exception - {str(e)}")
                broken_features.append(f"GET {endpoint} (exception)")
    
    print(f"\n🎯 Feature Test Summary")
    print("=" * 50)
    print(f"✅ Working features: {len(working_features)}")
    for feature in working_features:
        print(f"   ✅ {feature}")
    
    print(f"\n❌ Broken features: {len(broken_features)}")
    for feature in broken_features:
        print(f"   ❌ {feature}")
    
    print(f"\n🔧 Flutter App Fixes Needed:")
    if working_features:
        print("   📱 Update Flutter screen to use POST for action buttons")
        print("   🔄 Connect chaos stream to working GET endpoints")
        print("   🧠 Brain visualization should work (GET endpoint OK)")
    
    if broken_features:
        print("   🛠️ Fix server errors in backend")
        print("   ⚡ Add error handling for failed endpoints")
        
    print(f"\n🎯 Test completed at {datetime.now()}")

if __name__ == "__main__":
    asyncio.run(test_project_berserk_post_endpoints())