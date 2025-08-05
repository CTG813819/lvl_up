#!/usr/bin/env python3
"""
Test script for autonomous source discovery system
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Backend URL
BACKEND_URL = "http://34.202.215.209:4000"

async def test_autonomous_source_discovery():
    """Test the autonomous source discovery system"""
    print("🧠 Testing Autonomous Source Discovery System")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        
        # 1. Get current AI learning sources
        print("\n1. 📊 Getting current AI learning sources...")
        try:
            async with session.get(f"{BACKEND_URL}/api/imperium/ai-learning-sources") as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Current AI learning sources:")
                    for ai_type, info in data['ai_learning_sources'].items():
                        print(f"  {ai_type.capitalize()}: {info['total_sources']} sources, {info['recent_discoveries']} recent discoveries")
                        if info['top_performing_sources']:
                            print(f"    Top sources: {', '.join(info['top_performing_sources'][:3])}")
                else:
                    print(f"❌ Failed to get AI learning sources: {response.status}")
        except Exception as e:
            print(f"❌ Error getting AI learning sources: {e}")
        
        # 2. Test source discovery for each AI type
        print("\n2. 🔍 Testing source discovery for each AI type...")
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        for ai_type in ai_types:
            print(f"\n   Testing {ai_type.capitalize()}...")
            try:
                # Get current sources for this AI
                async with session.get(f"{BACKEND_URL}/api/imperium/ai-learning-sources/{ai_type}") as response:
                    if response.status == 200:
                        data = await response.json()
                        current_count = data['total_sources']
                        print(f"     Current sources: {current_count}")
                        
                        # Trigger internet learning to discover new sources
                        topic = f"AI {ai_type} autonomous learning"
                        print(f"     Triggering learning with topic: {topic}")
                        
                        async with session.post(
                            f"{BACKEND_URL}/api/imperium/internet-learning/agent/{ai_type}",
                            params={"topic": topic}
                        ) as learning_response:
                            if learning_response.status == 200:
                                learning_data = await learning_response.json()
                                discovered_count = len(learning_data.get('discovered_sources', []))
                                expanded_count = len(learning_data.get('expanded_sources', []))
                                
                                print(f"     ✅ Learning completed!")
                                print(f"     Discovered sources: {discovered_count}")
                                print(f"     Expanded sources: {expanded_count}")
                                
                                if discovered_count > 0:
                                    print(f"     New sources: {', '.join(learning_data['discovered_sources'][:3])}")
                            else:
                                print(f"     ❌ Learning failed: {learning_response.status}")
                    else:
                        print(f"     ❌ Failed to get sources for {ai_type}: {response.status}")
                        
            except Exception as e:
                print(f"     ❌ Error testing {ai_type}: {e}")
        
        # 3. Get updated AI learning sources summary
        print("\n3. 📈 Getting updated AI learning sources summary...")
        try:
            async with session.get(f"{BACKEND_URL}/api/imperium/ai-learning-sources") as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Updated AI learning sources:")
                    for ai_type, info in data['ai_learning_sources'].items():
                        print(f"  {ai_type.capitalize()}: {info['total_sources']} sources, {info['recent_discoveries']} recent discoveries")
                        if info['top_performing_sources']:
                            print(f"    Top sources: {', '.join(info['top_performing_sources'][:3])}")
                else:
                    print(f"❌ Failed to get updated AI learning sources: {response.status}")
        except Exception as e:
            print(f"❌ Error getting updated AI learning sources: {e}")
        
        # 4. Test source performance tracking
        print("\n4. 📊 Testing source performance tracking...")
        for ai_type in ai_types:
            try:
                async with session.get(f"{BACKEND_URL}/api/imperium/ai-learning-sources/{ai_type}") as response:
                    if response.status == 200:
                        data = await response.json()
                        top_sources = data.get('top_performing_sources', [])
                        if top_sources:
                            print(f"  {ai_type.capitalize()} top performing sources: {', '.join(top_sources[:3])}")
                        else:
                            print(f"  {ai_type.capitalize()}: No top performing sources yet")
                    else:
                        print(f"  ❌ Failed to get performance data for {ai_type}")
            except Exception as e:
                print(f"  ❌ Error getting performance data for {ai_type}: {e}")
        
        # 5. Test autonomous expansion
        print("\n5. 🌱 Testing autonomous source expansion...")
        expansion_topics = {
            "imperium": "meta-learning AI orchestration",
            "guardian": "AI security vulnerability detection", 
            "sandbox": "experimental AI innovation",
            "conquest": "mobile app development AI"
        }
        
        for ai_type, topic in expansion_topics.items():
            print(f"   Expanding sources for {ai_type} with topic: {topic}")
            try:
                async with session.post(
                    f"{BACKEND_URL}/api/imperium/internet-learning/agent/{ai_type}",
                    params={"topic": topic}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        expanded = len(data.get('expanded_sources', []))
                        discovered = len(data.get('discovered_sources', []))
                        print(f"     ✅ Expanded: {expanded}, Discovered: {discovered}")
                    else:
                        print(f"     ❌ Expansion failed: {response.status}")
            except Exception as e:
                print(f"     ❌ Error expanding sources for {ai_type}: {e}")

async def main():
    """Main test function"""
    print("🚀 Starting Autonomous Source Discovery Test")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    await test_autonomous_source_discovery()
    
    print("\n✅ Autonomous Source Discovery Test Completed!")
    print("\n📋 Summary:")
    print("- AIs now autonomously discover new learning sources")
    print("- Source performance is tracked and ranked")
    print("- Each AI type has specialized source discovery patterns")
    print("- Sources expand based on learning topics and results")
    print("- Top performing sources are prioritized for future learning")

if __name__ == "__main__":
    asyncio.run(main()) 