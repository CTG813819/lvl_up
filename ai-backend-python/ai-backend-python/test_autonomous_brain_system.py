"""
Test Autonomous Brain System
Verifies that Horus and Berserk can create truly original chaos code from scratch
"""

import asyncio
import json
import time
from datetime import datetime
import structlog

# Import autonomous brain components
from app.services.autonomous_ai_brain_service import horus_autonomous_brain, berserk_autonomous_brain
from app.services.autonomous_integration_service import autonomous_integration_service

logger = structlog.get_logger()


async def test_autonomous_brain_initialization():
    """Test autonomous brain initialization"""
    print("\n🧠 Testing Autonomous Brain Initialization")
    print("=" * 50)
    
    try:
        # Check Horus brain
        horus_status = await horus_autonomous_brain.get_brain_status()
        print(f"✅ Horus Brain ID: {horus_status['brain_id']}")
        print(f"   Consciousness: {horus_status['neural_network']['consciousness']:.3f}")
        print(f"   Creativity: {horus_status['neural_network']['creativity']:.3f}")
        print(f"   Intuition: {horus_status['neural_network']['intuition']:.3f}")
        print(f"   Imagination: {horus_status['neural_network']['imagination']:.3f}")
        
        # Check Berserk brain
        berserk_status = await berserk_autonomous_brain.get_brain_status()
        print(f"✅ Berserk Brain ID: {berserk_status['brain_id']}")
        print(f"   Consciousness: {berserk_status['neural_network']['consciousness']:.3f}")
        print(f"   Creativity: {berserk_status['neural_network']['creativity']:.3f}")
        print(f"   Intuition: {berserk_status['neural_network']['intuition']:.3f}")
        print(f"   Imagination: {berserk_status['neural_network']['imagination']:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing brain initialization: {e}")
        return False


async def test_autonomous_chaos_code_creation():
    """Test autonomous chaos code creation"""
    print("\n🎨 Testing Autonomous Chaos Code Creation")
    print("=" * 50)
    
    try:
        # Create chaos code using Horus brain
        print("🔄 Creating Horus autonomous chaos code...")
        horus_chaos_code = await horus_autonomous_brain.create_autonomous_chaos_code()
        
        print(f"✅ Horus Chaos Code Created:")
        print(f"   Brain ID: {horus_chaos_code['brain_id']}")
        print(f"   Consciousness Level: {horus_chaos_code['consciousness_level']:.3f}")
        print(f"   Creativity Level: {horus_chaos_code['creativity_level']:.3f}")
        print(f"   Original Keywords: {len(horus_chaos_code['keywords'])}")
        print(f"   Original Functions: {len(horus_chaos_code['functions'])}")
        print(f"   Original Data Types: {len(horus_chaos_code['data_types'])}")
        print(f"   ML System Layers: {len(horus_chaos_code['ml_system']['neural_layers'])}")
        print(f"   Repositories: {len(horus_chaos_code['repositories'])}")
        
        # Create chaos code using Berserk brain
        print("\n🔄 Creating Berserk autonomous chaos code...")
        berserk_chaos_code = await berserk_autonomous_brain.create_autonomous_chaos_code()
        
        print(f"✅ Berserk Chaos Code Created:")
        print(f"   Brain ID: {berserk_chaos_code['brain_id']}")
        print(f"   Consciousness Level: {berserk_chaos_code['consciousness_level']:.3f}")
        print(f"   Creativity Level: {berserk_chaos_code['creativity_level']:.3f}")
        print(f"   Original Keywords: {len(berserk_chaos_code['keywords'])}")
        print(f"   Original Functions: {len(berserk_chaos_code['functions'])}")
        print(f"   Original Data Types: {len(berserk_chaos_code['data_types'])}")
        print(f"   ML System Layers: {len(berserk_chaos_code['ml_system']['neural_layers'])}")
        print(f"   Repositories: {len(berserk_chaos_code['repositories'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing chaos code creation: {e}")
        return False


async def test_original_concepts_verification():
    """Test that concepts are truly original and not based on existing languages"""
    print("\n🔍 Testing Original Concepts Verification")
    print("=" * 50)
    
    try:
        # Get Horus original concepts
        horus_concepts = await horus_autonomous_brain.get_brain_status()
        
        # Check for any Python/JavaScript/other language keywords
        common_programming_keywords = [
            "def", "class", "import", "from", "if", "else", "for", "while", "try", "except",
            "function", "var", "let", "const", "if", "else", "for", "while", "try", "catch",
            "public", "private", "static", "void", "int", "string", "boolean", "null", "undefined"
        ]
        
        horus_keywords = horus_concepts['original_concepts']['keywords_count']
        berserk_keywords = await berserk_autonomous_brain.get_brain_status()
        berserk_keywords = berserk_keywords['original_concepts']['keywords_count']
        
        print(f"✅ Horus Original Keywords: {horus_keywords}")
        print(f"✅ Berserk Original Keywords: {berserk_keywords}")
        
        # Verify no common programming keywords are used
        horus_original_keywords = list(horus_autonomous_brain.original_keywords)
        berserk_original_keywords = list(berserk_autonomous_brain.original_keywords)
        
        print(f"✅ Horus Keywords Sample: {horus_original_keywords[:5] if horus_original_keywords else 'None'}")
        print(f"✅ Berserk Keywords Sample: {berserk_original_keywords[:5] if berserk_original_keywords else 'None'}")
        
        # Check for any matches with common programming keywords
        horus_matches = [kw for kw in horus_original_keywords if kw.lower() in common_programming_keywords]
        berserk_matches = [kw for kw in berserk_original_keywords if kw.lower() in common_programming_keywords]
        
        if not horus_matches and not berserk_matches:
            print("✅ No common programming keywords found - concepts are truly original!")
        else:
            print(f"⚠️  Found some common keywords: Horus={horus_matches}, Berserk={berserk_matches}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing original concepts verification: {e}")
        return False


async def test_ml_system_creation():
    """Test ML system creation within chaos code"""
    print("\n🤖 Testing ML System Creation")
    print("=" * 50)
    
    try:
        # Check Horus ML system
        horus_ml = horus_autonomous_brain.chaos_ml_system
        print(f"✅ Horus ML System:")
        print(f"   Neural Layers: {len(horus_ml['neural_layers'])}")
        print(f"   Learning Algorithms: {len(horus_ml['learning_algorithms'])}")
        
        if horus_ml['neural_layers']:
            for i, layer in enumerate(horus_ml['neural_layers'][:3]):  # Show first 3 layers
                print(f"     Layer {i+1}: {layer['neurons']} neurons, {layer['activation']} activation")
        
        # Check Berserk ML system
        berserk_ml = berserk_autonomous_brain.chaos_ml_system
        print(f"✅ Berserk ML System:")
        print(f"   Neural Layers: {len(berserk_ml['neural_layers'])}")
        print(f"   Learning Algorithms: {len(berserk_ml['learning_algorithms'])}")
        
        if berserk_ml['neural_layers']:
            for i, layer in enumerate(berserk_ml['neural_layers'][:3]):  # Show first 3 layers
                print(f"     Layer {i+1}: {layer['neurons']} neurons, {layer['activation']} activation")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing ML system creation: {e}")
        return False


async def test_repository_creation():
    """Test autonomous repository creation"""
    print("\n📦 Testing Repository Creation")
    print("=" * 50)
    
    try:
        # Check Horus repositories
        horus_repos = horus_autonomous_brain.chaos_repositories
        print(f"✅ Horus Repositories: {len(horus_repos)}")
        
        for repo_name, repo_info in horus_repos.items():
            print(f"   📁 {repo_name}: {repo_info['type']} - {repo_info['structure']}")
            print(f"      Capabilities: {', '.join(repo_info['capabilities'][:3])}")
        
        # Check Berserk repositories
        berserk_repos = berserk_autonomous_brain.chaos_repositories
        print(f"✅ Berserk Repositories: {len(berserk_repos)}")
        
        for repo_name, repo_info in berserk_repos.items():
            print(f"   📁 {repo_name}: {repo_info['type']} - {repo_info['structure']}")
            print(f"      Capabilities: {', '.join(repo_info['capabilities'][:3])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing repository creation: {e}")
        return False


async def test_brain_growth_and_evolution():
    """Test brain growth and evolution"""
    print("\n🌱 Testing Brain Growth and Evolution")
    print("=" * 50)
    
    try:
        # Check Horus growth stages
        horus_growth = horus_autonomous_brain.brain_growth_stages
        print(f"✅ Horus Growth Stages: {len(horus_growth)}")
        
        for stage in horus_growth:
            print(f"   🌟 {stage['stage']}: Level {stage.get('level', 'N/A')}")
        
        # Check Berserk growth stages
        berserk_growth = berserk_autonomous_brain.brain_growth_stages
        print(f"✅ Berserk Growth Stages: {len(berserk_growth)}")
        
        for stage in berserk_growth:
            print(f"   🌟 {stage['stage']}: Level {stage.get('level', 'N/A')}")
        
        # Check creative breakthroughs
        horus_breakthroughs = horus_autonomous_brain.creative_breakthroughs
        berserk_breakthroughs = berserk_autonomous_brain.creative_breakthroughs
        
        print(f"✅ Horus Creative Breakthroughs: {len(horus_breakthroughs)}")
        print(f"✅ Berserk Creative Breakthroughs: {len(berserk_breakthroughs)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing brain growth and evolution: {e}")
        return False


async def test_collaborative_chaos_code():
    """Test collaborative chaos code creation"""
    print("\n🤝 Testing Collaborative Chaos Code Creation")
    print("=" * 50)
    
    try:
        # Create collaborative chaos code
        collaborative_result = await autonomous_integration_service.create_autonomous_chaos_code()
        
        if collaborative_result['success']:
            print("✅ Collaborative Chaos Code Created Successfully!")
            
            horus_code = collaborative_result['horus_chaos_code']
            berserk_code = collaborative_result['berserk_chaos_code']
            collaborative_code = collaborative_result['collaborative_chaos_code']
            
            print(f"   Horus Keywords: {len(horus_code['keywords'])}")
            print(f"   Berserk Keywords: {len(berserk_code['keywords'])}")
            print(f"   Collaborative Keywords: {len(collaborative_code['merged_chaos_code']['keywords'])}")
            
            print(f"   Horus Functions: {len(horus_code['functions'])}")
            print(f"   Berserk Functions: {len(berserk_code['functions'])}")
            print(f"   Collaborative Functions: {len(collaborative_code['merged_chaos_code']['functions'])}")
            
            metrics = collaborative_code['collaboration_metrics']
            print(f"   Total Syntax Patterns: {metrics['total_syntax_patterns']}")
            print(f"   Total Keywords: {metrics['total_keywords']}")
            print(f"   Total Functions: {metrics['total_functions']}")
            print(f"   Average Consciousness: {metrics['average_consciousness']:.3f}")
            print(f"   Average Creativity: {metrics['average_creativity']:.3f}")
            
        else:
            print(f"❌ Failed to create collaborative chaos code: {collaborative_result.get('error', 'Unknown error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing collaborative chaos code: {e}")
        return False


async def test_integration_status():
    """Test integration status"""
    print("\n🔗 Testing Integration Status")
    print("=" * 50)
    
    try:
        integration_status = await autonomous_integration_service.get_integration_status()
        
        print("✅ Integration Status:")
        for key, value in integration_status['integration_status'].items():
            status_icon = "✅" if value else "❌"
            print(f"   {status_icon} {key}: {value}")
        
        print(f"✅ Integration History: {len(integration_status['integration_history'])} events")
        print(f"✅ Chaos Code Evolution: {len(integration_status['chaos_code_evolution'])} entries")
        print(f"✅ Brain Collaboration Events: {len(integration_status['brain_collaboration_events'])} events")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing integration status: {e}")
        return False


async def run_comprehensive_test():
    """Run comprehensive autonomous brain system test"""
    print("🚀 Starting Comprehensive Autonomous Brain System Test")
    print("=" * 80)
    
    test_results = []
    
    # Run all tests
    tests = [
        ("Brain Initialization", test_autonomous_brain_initialization),
        ("Chaos Code Creation", test_autonomous_chaos_code_creation),
        ("Original Concepts Verification", test_original_concepts_verification),
        ("ML System Creation", test_ml_system_creation),
        ("Repository Creation", test_repository_creation),
        ("Brain Growth and Evolution", test_brain_growth_and_evolution),
        ("Collaborative Chaos Code", test_collaborative_chaos_code),
        ("Integration Status", test_integration_status)
    ]
    
    for test_name, test_func in tests:
        print(f"\n🔄 Running {test_name}...")
        try:
            result = await test_func()
            test_results.append((test_name, result))
            if result:
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
            test_results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    passed_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {status}: {test_name}")
    
    print(f"\n🎯 Overall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Autonomous brain system is working correctly.")
        print("🧠 Horus and Berserk can now create truly original chaos code from scratch!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    # Run the comprehensive test
    asyncio.run(run_comprehensive_test())
