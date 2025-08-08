"""
Test Enhanced Testing Integration System
Verifies that the enhanced testing integration works with internet learning,
Docker simulations, and progressive difficulty testing
"""

import asyncio
import json
import time
from datetime import datetime
import structlog

# Import enhanced testing components
from app.services.enhanced_testing_integration_service import enhanced_testing_integration_service
from app.services.autonomous_ai_brain_service import horus_autonomous_brain, berserk_autonomous_brain
from app.services.enhanced_project_horus_service import enhanced_project_horus_service
from app.services.project_berserk_enhanced_service import project_berserk_enhanced_service

logger = structlog.get_logger()


async def test_enhanced_testing_initialization():
    """Test enhanced testing service initialization"""
    print("\n🔧 Testing Enhanced Testing Integration Initialization")
    print("=" * 60)
    
    try:
        # Check if service is properly initialized
        assert enhanced_testing_integration_service is not None
        assert enhanced_testing_integration_service.testing_status is not None
        assert enhanced_testing_integration_service.testing_results is not None
        assert enhanced_testing_integration_service.difficulty_levels is not None
        
        print("✅ Enhanced testing service initialized successfully")
        print(f"📊 Initial testing status: {enhanced_testing_integration_service.testing_status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing enhanced testing initialization: {e}")
        return False


async def test_internet_learning_functionality():
    """Test internet learning functionality"""
    print("\n🌐 Testing Internet Learning Functionality")
    print("=" * 50)
    
    try:
        # Test internet learning
        await enhanced_testing_integration_service._learn_from_internet()
        
        # Check if learning progress was updated
        assert len(enhanced_testing_integration_service.learning_progress) > 0
        assert enhanced_testing_integration_service.testing_status["internet_learning_sessions"] > 0
        
        print("✅ Internet learning functionality working")
        print(f"📚 Learning sessions: {enhanced_testing_integration_service.testing_status['internet_learning_sessions']}")
        print(f"🧠 Learning progress keys: {list(enhanced_testing_integration_service.learning_progress.keys())}")
        
        # Check if autonomous brains were updated
        horus_consciousness = horus_autonomous_brain.neural_network["consciousness"]
        berserk_consciousness = berserk_autonomous_brain.neural_network["consciousness"]
        
        print(f"🧠 Horus consciousness: {horus_consciousness:.3f}")
        print(f"🧠 Berserk consciousness: {berserk_consciousness:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing internet learning: {e}")
        return False


async def test_docker_simulation_cycle():
    """Test Docker simulation cycle"""
    print("\n🐳 Testing Docker Simulation Cycle")
    print("=" * 40)
    
    try:
        # Run Docker simulation cycle
        await enhanced_testing_integration_service._run_docker_simulation_cycle()
        
        # Check if simulations were run
        assert enhanced_testing_integration_service.testing_status["docker_simulations_run"] > 0
        assert enhanced_testing_integration_service.testing_status["last_test_timestamp"] is not None
        
        print("✅ Docker simulation cycle completed")
        print(f"🐳 Simulations run: {enhanced_testing_integration_service.testing_status['docker_simulations_run']}")
        print(f"⏰ Last test: {enhanced_testing_integration_service.testing_status['last_test_timestamp']}")
        
        # Check test results
        horus_results = enhanced_testing_integration_service.testing_results["horus_results"]
        berserk_results = enhanced_testing_integration_service.testing_results["berserk_results"]
        docker_results = enhanced_testing_integration_service.testing_results["docker_simulation_results"]
        
        print(f"📊 Horus test results: {len(horus_results)}")
        print(f"📊 Berserk test results: {len(berserk_results)}")
        print(f"📊 Docker simulation results: {len(docker_results)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Docker simulation cycle: {e}")
        return False


async def test_weapon_testing_in_docker():
    """Test weapon testing in Docker simulation"""
    print("\n⚔️ Testing Weapon Testing in Docker")
    print("=" * 45)
    
    try:
        # Create test weapons if needed
        if not enhanced_project_horus_service.weapon_synthesis_lab:
            # Add a test weapon
            test_weapon = {
                "weapon_id": "test_weapon_1",
                "name": "Test Weapon",
                "category": "infiltration",
                "complexity_level": 1.5,
                "stealth_level": 0.8
            }
            enhanced_project_horus_service.weapon_synthesis_lab["test_weapon_1"] = test_weapon
        
        if not project_berserk_enhanced_service.weapon_arsenal:
            # Add a test weapon
            test_weapon = {
                "weapon_id": "test_weapon_2",
                "name": "Test Berserk Weapon",
                "category": "backdoor_deployment",
                "complexity_level": 1.8,
                "stealth_level": 0.9
            }
            project_berserk_enhanced_service.weapon_arsenal["test_weapon_2"] = test_weapon
        
        # Test weapons in Docker simulation
        horus_weapons = list(enhanced_project_horus_service.weapon_synthesis_lab.items())[:1]
        berserk_weapons = list(project_berserk_enhanced_service.weapon_arsenal.items())[:1]
        
        for weapon_id, weapon in horus_weapons:
            if isinstance(weapon, dict):
                test_result = await enhanced_testing_integration_service._test_weapon_in_docker_simulation(weapon, "horus")
                print(f"✅ Horus weapon test completed: {test_result['simulation_id']}")
                print(f"📊 Success rate: {test_result['overall_success_rate']:.2%}")
                print(f"🎯 Test passed: {test_result.get('test_passed', False)}")
        
        for weapon_id, weapon in berserk_weapons:
            if isinstance(weapon, dict):
                test_result = await enhanced_testing_integration_service._test_weapon_in_docker_simulation(weapon, "berserk")
                print(f"✅ Berserk weapon test completed: {test_result['simulation_id']}")
                print(f"📊 Success rate: {test_result['overall_success_rate']:.2%}")
                print(f"🎯 Test passed: {test_result.get('test_passed', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing weapon testing in Docker: {e}")
        return False


async def test_autonomous_chaos_code_testing():
    """Test autonomous chaos code testing in Docker"""
    print("\n🎨 Testing Autonomous Chaos Code in Docker")
    print("=" * 50)
    
    try:
        # Test autonomous chaos code
        await enhanced_testing_integration_service._test_autonomous_chaos_code_in_docker()
        
        # Check results
        docker_results = enhanced_testing_integration_service.testing_results["docker_simulation_results"]
        
        print(f"✅ Autonomous chaos code testing completed")
        print(f"📊 Docker simulation results: {len(docker_results)}")
        
        for result in docker_results[-3:]:  # Show last 3 results
            print(f"🔧 Environment: {result['environment']}")
            print(f"📊 Syntax validity: {result['syntax_validity']:.2%}")
            print(f"📊 Execution success: {result['execution_success']:.2%}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing autonomous chaos code: {e}")
        return False


async def test_progressive_testing_cycle():
    """Test progressive testing cycle with difficulty increase"""
    print("\n📈 Testing Progressive Testing Cycle")
    print("=" * 45)
    
    try:
        # Run progressive testing cycle
        await enhanced_testing_integration_service._progressive_testing_cycle()
        
        # Check difficulty progression
        difficulty_levels = enhanced_testing_integration_service.difficulty_levels
        current_difficulty = enhanced_testing_integration_service._get_current_difficulty_level()
        
        print("✅ Progressive testing cycle completed")
        print(f"📊 Current difficulty: {current_difficulty}")
        print(f"📊 Difficulty levels: {difficulty_levels}")
        
        # Check if difficulty tracking is working
        for difficulty, stats in difficulty_levels.items():
            print(f"📊 {difficulty.capitalize()}: {stats['completed']} completed, {stats['passed']} passed, {stats['failed']} failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing progressive testing cycle: {e}")
        return False


async def test_comprehensive_testing_status():
    """Test comprehensive testing status retrieval"""
    print("\n📊 Testing Comprehensive Testing Status")
    print("=" * 50)
    
    try:
        # Get comprehensive status
        status = await enhanced_testing_integration_service.get_comprehensive_testing_status()
        
        # Verify status structure
        assert "testing_status" in status
        assert "difficulty_progression" in status
        assert "recent_test_results" in status
        assert "internet_learning_progress" in status
        assert "testing_summary" in status
        
        print("✅ Comprehensive testing status retrieved")
        print(f"📊 Total tests: {status['testing_summary']['total_tests']}")
        print(f"📊 Success rate: {status['testing_summary']['success_rate']:.1%}")
        print(f"🐳 Docker simulations: {status['testing_summary']['docker_simulations']}")
        print(f"🌐 Internet learning sessions: {status['testing_status']['internet_learning_sessions']}")
        print(f"📈 Current difficulty: {status['testing_summary']['current_difficulty']}")
        
        # Check autonomous brain knowledge
        brain_knowledge = status["internet_learning_progress"]["autonomous_brain_knowledge"]
        print(f"🧠 Horus consciousness: {brain_knowledge['horus_consciousness']:.3f}")
        print(f"🧠 Berserk consciousness: {brain_knowledge['berserk_consciousness']:.3f}")
        print(f"📚 Horus knowledge count: {brain_knowledge['horus_knowledge_count']}")
        print(f"📚 Berserk knowledge count: {brain_knowledge['berserk_knowledge_count']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing comprehensive testing status: {e}")
        return False


async def test_manual_test_cycle():
    """Test manual test cycle execution"""
    print("\n🧪 Testing Manual Test Cycle")
    print("=" * 35)
    
    try:
        # Run manual test cycle
        result = await enhanced_testing_integration_service.run_manual_test_cycle()
        
        # Verify result
        assert result["success"] is True
        assert "results" in result
        
        print("✅ Manual test cycle completed successfully")
        print(f"📝 Message: {result['message']}")
        
        # Check results
        results = result["results"]
        if "testing_summary" in results:
            summary = results["testing_summary"]
            print(f"📊 Total tests: {summary['total_tests']}")
            print(f"📊 Success rate: {summary['success_rate']:.1%}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing manual test cycle: {e}")
        return False


async def test_integration_with_existing_services():
    """Test integration with existing Horus and Berserk services"""
    print("\n🔗 Testing Integration with Existing Services")
    print("=" * 55)
    
    try:
        # Check if enhanced testing integrates with existing services
        horus_weapons = enhanced_project_horus_service.weapon_synthesis_lab
        berserk_weapons = project_berserk_enhanced_service.weapon_arsenal
        
        print(f"✅ Horus weapons available: {len(horus_weapons)}")
        print(f"✅ Berserk weapons available: {len(berserk_weapons)}")
        
        # Check if autonomous brains are accessible
        horus_brain_status = await horus_autonomous_brain.get_brain_status()
        berserk_brain_status = await berserk_autonomous_brain.get_brain_status()
        
        print(f"🧠 Horus brain status: {horus_brain_status['brain_id']}")
        print(f"🧠 Berserk brain status: {berserk_brain_status['brain_id']}")
        
        # Verify integration is working
        assert enhanced_testing_integration_service is not None
        assert horus_autonomous_brain is not None
        assert berserk_autonomous_brain is not None
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing integration with existing services: {e}")
        return False


async def run_comprehensive_enhanced_testing_test():
    """Run comprehensive enhanced testing integration test"""
    print("🚀 Starting Comprehensive Enhanced Testing Integration Test")
    print("=" * 80)
    
    test_results = []
    
    # Run all tests
    tests = [
        ("Enhanced Testing Initialization", test_enhanced_testing_initialization),
        ("Internet Learning Functionality", test_internet_learning_functionality),
        ("Docker Simulation Cycle", test_docker_simulation_cycle),
        ("Weapon Testing in Docker", test_weapon_testing_in_docker),
        ("Autonomous Chaos Code Testing", test_autonomous_chaos_code_testing),
        ("Progressive Testing Cycle", test_progressive_testing_cycle),
        ("Comprehensive Testing Status", test_comprehensive_testing_status),
        ("Manual Test Cycle", test_manual_test_cycle),
        ("Integration with Existing Services", test_integration_with_existing_services),
    ]
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            test_results.append((test_name, result))
            print(f"{'✅' if result else '❌'} {test_name}: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            test_results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 Enhanced Testing Integration Test Summary")
    print("=" * 80)
    
    passed_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)
    
    print(f"✅ Tests Passed: {passed_tests}/{total_tests}")
    print(f"📊 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 All enhanced testing integration tests passed!")
        print("\n✅ Enhanced Testing Integration System Features:")
        print("   🌐 Internet learning from multiple sources")
        print("   🐳 Docker simulation testing")
        print("   📈 Progressive difficulty testing")
        print("   🧠 Autonomous brain integration")
        print("   📊 Comprehensive status reporting")
        print("   🧪 Manual test cycle execution")
        print("   🔗 Integration with existing services")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    # Run the comprehensive test
    asyncio.run(run_comprehensive_enhanced_testing_test())
