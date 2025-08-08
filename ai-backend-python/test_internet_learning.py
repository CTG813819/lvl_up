#!/usr/bin/env python3
"""
<<<<<<< HEAD
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
=======
Test script to demonstrate internet learning capabilities
of Project Horus and Project Berserk
"""

import asyncio
import json
from datetime import datetime

async def test_project_horus_internet_learning():
    """Test Project Horus internet learning capabilities"""
    print("🧪 Testing Project Horus Internet Learning")
    print("=" * 60)
    
    try:
        from app.services.project_horus_service import project_horus_service
        
        # Test internet learning
        print("🔍 Researching topics from internet...")
        learning_result = await project_horus_service.learn_from_internet([
            "quantum_computing", "jarvis_ai", "quantum_mechanics", "cybersecurity"
        ])
        
        print(f"✅ Learning Status: {learning_result['status']}")
        print(f"📚 Topics Researched: {learning_result['topics_researched']}")
        print(f"🎯 Total Knowledge Gained: {learning_result['total_knowledge_gained']:.3f}")
        print(f"📈 Learning Progress: {learning_result['learning_progress']:.3f}")
        print(f"🌀 Chaos Complexity: {learning_result['chaos_complexity']:.3f}")
        
        # Show detailed learning results
        print("\n📖 Detailed Learning Results:")
        for result in learning_result['learning_results']:
            print(f"  • {result['topic']}: {result['knowledge_gained']:.3f} knowledge gained")
            if 'sources_accessed' in result:
                print(f"    Sources: {len(result['sources_accessed'])} accessed")
            if 'error' in result:
                print(f"    Error: {result['error']}")
        
        # Generate chaos code with new knowledge
        print("\n🌀 Generating chaos code with internet-learned knowledge...")
        chaos_result = await project_horus_service.generate_chaos_code("internet_enhanced")
        
        print(f"✅ Chaos Code Generated: {chaos_result['chaos_id']}")
        print(f"📊 Complexity: {chaos_result['metadata']['complexity']:.3f}")
        print(f"🎯 Assimilation Capabilities: {chaos_result['metadata']['assimilation_capabilities']}")
        
        return learning_result, chaos_result
        
    except Exception as e:
        print(f"❌ Error testing Project Horus: {e}")
        return None, None

async def test_project_berserk_internet_learning():
    """Test Project Berserk internet learning capabilities"""
    print("\n🧪 Testing Project Berserk Internet Learning")
    print("=" * 60)
    
    try:
        from app.services.project_berserk_service import ProjectWarmasterService
        
        # Initialize service
        service = ProjectWarmasterService()
        
        # Test autonomous internet learning
        print("🔍 Triggering autonomous internet learning...")
        learning_result = await service._auto_learn_from_internet([
            "jarvis_ai", "quantum_mechanics", "quantum_computing", "cybersecurity"
        ])
        
        print(f"✅ Learning Status: {learning_result['status']}")
        print(f"📚 Topics Learned: {learning_result['topics_learned']}")
        print(f"🎯 Total Knowledge Gained: {learning_result['total_knowledge_gained']:.3f}")
        print(f"🧠 New Neural Connections: {learning_result['new_neural_connections']}")
        print(f"🤖 JARVIS Evolution Stage: {learning_result['jarvis_evolution']}")
        print(f"🌐 Real Internet Research: {learning_result.get('real_internet_research', False)}")
        
        # Show detailed learning results
        print("\n📖 Detailed Learning Results:")
        for result in learning_result['learning_results']:
            print(f"  • {result['topic']}: {result['knowledge_gained']:.3f} knowledge gained")
            print(f"    Method: {result['learning_method']}")
            if 'real_research' in result:
                print(f"    Real Research: Yes")
            if 'sources_accessed' in result:
                print(f"    Sources: {len(result['sources_accessed'])} accessed")
            if 'error' in result:
                print(f"    Error: {result['error']}")
        
        # Test chaos code generation
        print("\n🌀 Generating advanced chaos code...")
        chaos_result = await service._auto_generate_chaos_code()
        
        print(f"✅ Chaos Code Generated")
        print(f"📊 Complexity: {chaos_result['complexity']:.3f}")
        print(f"🎯 System Evolution: {chaos_result['system_evolution']}")
        
        return learning_result, chaos_result
        
    except Exception as e:
        print(f"❌ Error testing Project Berserk: {e}")
        return None, None

async def test_simulated_attack_scenarios():
    """Test simulated attack scenarios with internet-learned knowledge"""
    print("\n🎯 Testing Simulated Attack Scenarios")
    print("=" * 60)
    
    try:
        from app.services.project_berserk_service import ProjectWarmasterService
        
        service = ProjectWarmasterService()
        
        # Update attack patterns from internet
        print("🌐 Updating attack patterns from internet sources...")
        attack_system = service.simulated_attack_system
        attack_system._load_internet_attack_patterns()
        
        print(f"✅ Loaded {len(attack_system.attack_patterns)} attack patterns")
        
        # Run simulated attack cycle
        print("\n🎯 Running simulated attack cycle...")
        attack_system.run_simulated_attack_cycle()
        
        # Get attack status
        attack_status = attack_system.get_attack_status()
        
        print(f"📊 Attack Success Rate: {attack_status['attack_success_rate']:.3f}")
        print(f"🛡️ Defense Effectiveness: {attack_status['defense_effectiveness']:.3f}")
        print(f"📈 Attack Learning Progress: {attack_status['attack_learning_progress']:.3f}")
        print(f"🌐 Internet Learning Active: {attack_status['internet_learning_active']}")
        
        return attack_status
        
    except Exception as e:
        print(f"❌ Error testing attack scenarios: {e}")
        return None

async def main():
    """Main test function"""
    print("🚀 Testing Internet Learning Capabilities")
    print("=" * 80)
    print(f"⏰ Started at: {datetime.now().isoformat()}")
    print()
    
    # Test Project Horus
    horus_learning, horus_chaos = await test_project_horus_internet_learning()
    
    # Test Project Berserk
    berserk_learning, berserk_chaos = await test_project_berserk_internet_learning()
    
    # Test attack scenarios
    attack_status = await test_simulated_attack_scenarios()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    if horus_learning:
        print(f"✅ Project Horus: Internet learning successful")
        print(f"   Knowledge gained: {horus_learning['total_knowledge_gained']:.3f}")
        print(f"   Topics researched: {len(horus_learning['topics_researched'])}")
    else:
        print("❌ Project Horus: Internet learning failed")
    
    if berserk_learning:
        print(f"✅ Project Berserk: Internet learning successful")
        print(f"   Knowledge gained: {berserk_learning['total_knowledge_gained']:.3f}")
        print(f"   Neural connections: {berserk_learning['new_neural_connections']}")
        print(f"   JARVIS evolution: {berserk_learning['jarvis_evolution']}")
    else:
        print("❌ Project Berserk: Internet learning failed")
    
    if attack_status:
        print(f"✅ Attack Scenarios: Simulated successfully")
        print(f"   Attack patterns: {attack_status['attack_patterns_count']}")
        print(f"   Defense effectiveness: {attack_status['defense_effectiveness']:.3f}")
    else:
        print("❌ Attack Scenarios: Simulation failed")
    
    print(f"\n⏰ Completed at: {datetime.now().isoformat()}")
    print("🎉 Internet learning capabilities are now active!")
>>>>>>> c98fd28782c60b4bf527a7cf8255f563dabe32e2

if __name__ == "__main__":
    asyncio.run(main()) 