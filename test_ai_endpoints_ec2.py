#!/usr/bin/env python3
"""
Test AI Learning Endpoints on EC2
"""

import asyncio
import aiohttp
import json

async def test_ai_endpoints():
    """Test the AI learning endpoints"""
    base_url = "http://localhost:4000"  # Test locally on EC2
    
    print("🧪 Testing AI Learning Endpoints on EC2...")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Imperium learnings
        print("1. Testing /api/conquest/ai/imperium/learnings")
        try:
            async with session.get(f"{base_url}/api/conquest/ai/imperium/learnings") as response:
                if response.status == 200:
                    data = await response.json()
                    learnings = data.get('learnings', [])
                    print(f"✅ Imperium learnings working: {len(learnings)} learnings found")
                    if learnings:
                        print(f"   First learning: {learnings[0]}")
                else:
                    error_text = await response.text()
                    print(f"❌ Imperium learnings failed: {response.status} - {error_text}")
        except Exception as e:
            print(f"❌ Imperium learnings error: {e}")
        
        # Test 2: Guardian learnings
        print("\n2. Testing /api/conquest/ai/guardian/learnings")
        try:
            async with session.get(f"{base_url}/api/conquest/ai/guardian/learnings") as response:
                if response.status == 200:
                    data = await response.json()
                    learnings = data.get('learnings', [])
                    print(f"✅ Guardian learnings working: {len(learnings)} learnings found")
                    if learnings:
                        print(f"   First learning: {learnings[0]}")
                else:
                    error_text = await response.text()
                    print(f"❌ Guardian learnings failed: {response.status} - {error_text}")
        except Exception as e:
            print(f"❌ Guardian learnings error: {e}")
        
        # Test 3: Sandbox learnings
        print("\n3. Testing /api/conquest/ai/sandbox/learnings")
        try:
            async with session.get(f"{base_url}/api/conquest/ai/sandbox/learnings") as response:
                if response.status == 200:
                    data = await response.json()
                    learnings = data.get('learnings', [])
                    print(f"✅ Sandbox learnings working: {len(learnings)} learnings found")
                    if learnings:
                        print(f"   First learning: {learnings[0]}")
                else:
                    error_text = await response.text()
                    print(f"❌ Sandbox learnings failed: {response.status} - {error_text}")
        except Exception as e:
            print(f"❌ Sandbox learnings error: {e}")
    
    print("\n🎉 AI Learning endpoints testing completed!")

if __name__ == "__main__":
    asyncio.run(test_ai_endpoints()) 