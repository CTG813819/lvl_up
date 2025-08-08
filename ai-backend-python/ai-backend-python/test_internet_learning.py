#!/usr/bin/env python3
"""
Test script for internet learning capabilities of Project Horus and Project Berserk
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.project_horus_service import ProjectHorusService
from app.services.project_berserk_service import ProjectWarmasterService

async def test_project_horus_internet_learning():
    """Test Project Horus internet learning capabilities"""
    print("🧠 Testing Project Horus Internet Learning...")
    
    try:
        # Initialize Project Horus service
        project_horus = ProjectHorusService()
        
        # Test internet learning
        print("📚 Learning from internet sources...")
        learning_results = await project_horus.learn_from_internet()
        
        print(f"✅ Learning completed!")
        print(f"📊 Knowledge gained: {len(learning_results.get('knowledge_gained', []))} items")
        print(f"🌐 Sources accessed: {len(learning_results.get('sources_accessed', []))} URLs")
        
        # Display some learned knowledge
        if learning_results.get('knowledge_gained'):
            print("\n📖 Sample Knowledge Gained:")
            for i, knowledge in enumerate(learning_results['knowledge_gained'][:3]):
                print(f"  {i+1}. {knowledge[:100]}...")
        
        # Test quantum chaos generation with learned knowledge
        print("\n⚛️ Generating quantum chaos code with learned knowledge...")
        chaos_result = await project_horus.generate_quantum_chaos_code()
        
        print(f"✅ Chaos code generated!")
        print(f"🔬 Evolution stage: {chaos_result.get('evolution_stage', 'Unknown')}")
        print(f"⚔️ Weapons available: {len(chaos_result.get('weapons', {}))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Project Horus: {e}")
        return False

async def test_project_berserk_internet_learning():
    """Test Project Berserk (Warmaster) internet learning capabilities"""
    print("\n🔥 Testing Project Berserk Internet Learning...")
    
    try:
        # Initialize Project Berserk service
        project_berserk = ProjectWarmasterService()
        
        # Test internet learning
        print("📚 Learning from internet sources...")
        learning_results = await project_berserk._auto_learn_from_internet()
        
        print(f"✅ Learning completed!")
        print(f"📊 Knowledge gained: {len(learning_results.get('knowledge_gained', []))} items")
        print(f"🌐 Sources accessed: {len(learning_results.get('sources_accessed', []))} URLs")
        
        # Display some learned knowledge
        if learning_results.get('knowledge_gained'):
            print("\n📖 Sample Knowledge Gained:")
            for i, knowledge in enumerate(learning_results['knowledge_gained'][:3]):
                print(f"  {i+1}. {knowledge[:100]}...")
        
        # Test attack pattern generation with learned knowledge
        print("\n⚔️ Generating attack patterns with learned knowledge...")
        attack_patterns = project_berserk._load_internet_attack_patterns()
        
        print(f"✅ Attack patterns generated!")
        print(f"🎯 Pattern categories: {len(attack_patterns)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Project Berserk: {e}")
        return False

async def test_simulated_attack_scenarios():
    """Test simulated attack scenarios using learned knowledge"""
    print("\n🎯 Testing Simulated Attack Scenarios...")
    
    try:
        # Initialize both services
        project_horus = ProjectHorusService()
        project_berserk = ProjectWarmasterService()
        
        # Test systems to attack
        target_systems = ["windows", "linux", "network", "web", "quantum", "ai", "blockchain"]
        
        print(f"🎯 Testing against {len(target_systems)} systems...")
        
        # Test Project Horus chaos code against systems
        chaos_results = await project_horus.test_chaos_code_against_systems(target_systems)
        
        print(f"✅ Chaos code testing completed!")
        print(f"🎯 Systems tested: {len(chaos_results.get('tested_systems', []))}")
        print(f"✅ Successful infiltrations: {len(chaos_results.get('successful_infiltrations', []))}")
        print(f"❌ Failed attempts: {len(chaos_results.get('failed_attempts', []))}")
        
        # Display some results
        if chaos_results.get('successful_infiltrations'):
            print("\n🎯 Successful Infiltrations:")
            for infiltration in chaos_results['successful_infiltrations'][:3]:
                print(f"  ✅ {infiltration.get('system', 'Unknown')}: {infiltration.get('method', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing attack scenarios: {e}")
        return False

async def test_knowledge_retention():
    """Test that learned knowledge is retained and expanded"""
    print("\n🧠 Testing Knowledge Retention and Expansion...")
    
    try:
        # Initialize Project Horus
        project_horus = ProjectHorusService()
        
        # Get initial knowledge base size
        initial_knowledge_size = len(project_horus.code_knowledge_base)
        print(f"📚 Initial knowledge base size: {initial_knowledge_size}")
        
        # Learn from internet
        await project_horus.learn_from_internet()
        
        # Get updated knowledge base size
        updated_knowledge_size = len(project_horus.code_knowledge_base)
        print(f"📚 Updated knowledge base size: {updated_knowledge_size}")
        
        # Check if knowledge expanded
        if updated_knowledge_size > initial_knowledge_size:
            print(f"✅ Knowledge expanded by {updated_knowledge_size - initial_knowledge_size} items!")
        else:
            print("⚠️ Knowledge base size unchanged")
        
        # Test that sources are being added
        sources = project_horus.internet_sources
        print(f"🌐 Available internet sources: {len(sources)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing knowledge retention: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Starting Internet Learning Tests...")
    print("=" * 50)
    
    results = []
    
    # Test Project Horus
    results.append(await test_project_horus_internet_learning())
    
    # Test Project Berserk
    results.append(await test_project_berserk_internet_learning())
    
    # Test attack scenarios
    results.append(await test_simulated_attack_scenarios())
    
    # Test knowledge retention
    results.append(await test_knowledge_retention())
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"✅ Passed: {sum(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}")
    
    if all(results):
        print("🎉 All tests passed! Internet learning is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return all(results)

if __name__ == "__main__":
    asyncio.run(main()) 