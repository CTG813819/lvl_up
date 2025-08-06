#!/usr/bin/env python3
"""
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

if __name__ == "__main__":
    asyncio.run(main()) 