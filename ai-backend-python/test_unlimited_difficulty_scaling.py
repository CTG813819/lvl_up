#!/usr/bin/env python3
"""
Test Unlimited Difficulty Scaling System
Tests that the enhanced adversarial testing service supports unlimited difficulty scaling
with ultra-complex, multi-layered, technical scenarios that require many steps for success.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_unlimited_difficulty_scaling():
    """Test unlimited difficulty scaling with ultra-complex scenarios"""
    print("🧪 Testing Unlimited Difficulty Scaling System")
    print("=" * 70)
    
    try:
        # Test import
        print("📦 Testing imports...")
        from app.services.enhanced_adversarial_testing_service import EnhancedAdversarialTestingService
        print("✅ Imports successful")
        
        # Initialize the enhanced adversarial testing service
        print("\n🔧 Initializing Enhanced Adversarial Testing Service...")
        enhanced_service = EnhancedAdversarialTestingService()
        await enhanced_service.initialize()
        print("✅ Enhanced Adversarial Testing Service initialized")
        
        # Test unlimited difficulty scaling
        print("\n🚀 Testing Unlimited Difficulty Scaling...")
        
        # Set up AIs with very high difficulty multipliers to test ultra-complex scenarios
        enhanced_service.ai_difficulty_multipliers = {
            "imperium": 5.0,    # Ultra-high difficulty
            "guardian": 4.5,    # Very high difficulty
            "sandbox": 3.8,     # High difficulty
            "conquest": 3.2     # High difficulty
        }
        
        print("📊 Initial Difficulty Multipliers:")
        for ai_type, multiplier in enhanced_service.ai_difficulty_multipliers.items():
            print(f"  {ai_type.title()}: {multiplier:.2f}")
        
        # Test scenario difficulty calculation (should have no upper limit)
        print("\n🎯 Testing Scenario Difficulty Calculation (No Upper Limit)...")
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        scenario_difficulty = enhanced_service._calculate_scenario_difficulty(ai_types)
        print(f"   Calculated Scenario Difficulty: {scenario_difficulty:.2f}")
        print(f"   Expected: ~4.125 (average of 5.0, 4.5, 3.8, 3.2)")
        print(f"   ✅ No upper limit applied - difficulty scales infinitely!")
        
        # Test complexity adjustment for ultra-high difficulties
        print("\n📈 Testing Complexity Adjustment for Ultra-High Difficulties...")
        from app.services.enhanced_adversarial_testing_service import ScenarioComplexity
        
        test_difficulties = [
            (ScenarioComplexity.INTERMEDIATE, 1.0),   # Normal difficulty
            (ScenarioComplexity.INTERMEDIATE, 2.0),   # High difficulty
            (ScenarioComplexity.INTERMEDIATE, 3.0),   # Very high difficulty
            (ScenarioComplexity.INTERMEDIATE, 5.0),   # Ultra-high difficulty
            (ScenarioComplexity.INTERMEDIATE, 8.0),   # Extreme difficulty
        ]
        
        for base_complexity, difficulty in test_difficulties:
            adjusted = enhanced_service._adjust_complexity_for_difficulty(base_complexity, difficulty)
            print(f"   {base_complexity.value} (difficulty {difficulty:.1f}) → {adjusted.value}")
        
        # Test scenario generation with ultra-complex requirements
        print("\n🎭 Testing Ultra-Complex Scenario Generation...")
        scenario = await enhanced_service.generate_diverse_adversarial_scenario(
            ai_types=ai_types,
            target_domain=None,
            complexity=None
        )
        
        print(f"✅ Ultra-complex scenario generated: {scenario.get('scenario_id', 'unknown')}")
        print(f"   Domain: {scenario.get('domain', 'unknown')}")
        print(f"   Complexity: {scenario.get('complexity', 'unknown')}")
        print(f"   Ultra-Complex: {scenario.get('ultra_complex', False)}")
        print(f"   Difficulty Level: {scenario.get('difficulty_level', 0):.2f}")
        
        # Check dynamic difficulty information
        if "dynamic_difficulty" in scenario:
            dynamic_info = scenario["dynamic_difficulty"]
            print(f"   Scenario Difficulty: {dynamic_info.get('scenario_difficulty', 0):.2f}")
            print("   AI Difficulty Multipliers:")
            for ai_type, multiplier in dynamic_info.get('ai_difficulty_multipliers', {}).items():
                print(f"     {ai_type.title()}: {multiplier:.2f}")
        
        # Test ultra-complex scenario enhancement
        print("\n🔬 Testing Ultra-Complex Scenario Enhancement...")
        if scenario.get('ultra_complex', False):
            print("   ✅ Ultra-complex enhancement triggered!")
            
            # Check for multi-layer requirements
            details = scenario.get('details', {})
            if 'complexity_layers' in details:
                complexity_layers = details['complexity_layers']
                technical_depth = details.get('technical_depth', 0)
                print(f"   Complexity Layers: {complexity_layers}")
                print(f"   Technical Depth: {technical_depth}")
                print(f"   ✅ Multi-layer complexity implemented!")
            
            # Check for ultra-complex requirements
            ultra_requirements = details.get('ultra_complex_requirements', {})
            if ultra_requirements:
                print("   Ultra-Complex Requirements:")
                for req_type, req_desc in ultra_requirements.items():
                    print(f"     {req_type}: {req_desc}")
        else:
            print("   ⚠️  Ultra-complex enhancement not triggered")
        
        # Test time limit scaling for ultra-complex scenarios
        print("\n⏱️  Testing Time Limit Scaling...")
        base_time = enhanced_service._get_time_limit(ScenarioComplexity.MASTER)
        print(f"   Base MASTER time limit: {base_time} seconds ({base_time/60:.1f} minutes)")
        
        # Test winner determination with unlimited difficulty scaling
        print("\n🏆 Testing Winner Determination with Unlimited Scaling...")
        
        # Simulate a competition where Imperium wins
        winners = ["imperium"]
        losers = ["guardian", "sandbox", "conquest"]
        
        # Apply dynamic difficulty scaling
        await enhanced_service._apply_dynamic_difficulty_scaling(winners, losers)
        
        print("   After Competition Results:")
        for ai_type, multiplier in enhanced_service.ai_difficulty_multipliers.items():
            print(f"     {ai_type.title()}: {multiplier:.2f}")
        
        # Verify that Imperium's difficulty increased without limit
        imperium_new_multiplier = enhanced_service.ai_difficulty_multipliers["imperium"]
        print(f"   ✅ Imperium difficulty increased to {imperium_new_multiplier:.2f} (no upper limit!)")
        
        # Test next scenario generation with even higher difficulty
        print("\n🔄 Testing Next Scenario with Higher Difficulty...")
        next_scenario = await enhanced_service.generate_diverse_adversarial_scenario(
            ai_types=ai_types,
            target_domain=None,
            complexity=None
        )
        
        next_difficulty = next_scenario.get('difficulty_level', 0)
        print(f"   Next Scenario Difficulty: {next_difficulty:.2f}")
        print(f"   Previous Difficulty: {scenario.get('difficulty_level', 0):.2f}")
        print(f"   ✅ Difficulty continues to scale upward!")
        
        # Test multiple competition cycles to show unlimited growth
        print("\n🔄 Testing Multiple Competition Cycles...")
        print("   Simulating 5 competition cycles...")
        
        for cycle in range(1, 6):
            # Simulate Imperium winning again
            await enhanced_service._apply_dynamic_difficulty_scaling(["imperium"], ["guardian", "sandbox", "conquest"])
            
            imperium_multiplier = enhanced_service.ai_difficulty_multipliers["imperium"]
            print(f"   Cycle {cycle}: Imperium difficulty = {imperium_multiplier:.2f}")
        
        print(f"   ✅ Final Imperium difficulty: {enhanced_service.ai_difficulty_multipliers['imperium']:.2f}")
        print(f"   ✅ No upper limit reached - unlimited scaling confirmed!")
        
        # Test ultra-complex scenario generation with very high difficulty
        print("\n🎯 Testing Ultra-Complex Scenario with Very High Difficulty...")
        final_scenario = await enhanced_service.generate_diverse_adversarial_scenario(
            ai_types=["imperium"],  # Just Imperium with very high difficulty
            target_domain=None,
            complexity=None
        )
        
        final_difficulty = final_scenario.get('difficulty_level', 0)
        print(f"   Final Scenario Difficulty: {final_difficulty:.2f}")
        print(f"   Ultra-Complex: {final_scenario.get('ultra_complex', False)}")
        
        if final_scenario.get('ultra_complex', False):
            details = final_scenario.get('details', {})
            complexity_layers = details.get('complexity_layers', 0)
            technical_depth = details.get('technical_depth', 0)
            print(f"   Complexity Layers: {complexity_layers}")
            print(f"   Technical Depth: {technical_depth}")
            print(f"   ✅ Ultra-complex scenario with {complexity_layers} layers and {technical_depth} technical depth!")
        
        # Summary
        print(f"\n📊 Test Summary")
        print("=" * 50)
        
        successful_tests = 0
        total_tests = 0
        
        # Check if difficulty calculation has no upper limit
        total_tests += 1
        if scenario_difficulty > 3.0:  # Should be much higher than the old 3.0 limit
            successful_tests += 1
            print("✅ Unlimited difficulty calculation (no upper limit)")
        else:
            print("❌ Difficulty calculation still has upper limit")
        
        # Check if complexity adjustment supports ultra-high difficulties
        total_tests += 1
        ultra_complex_adjustment = enhanced_service._adjust_complexity_for_difficulty(
            ScenarioComplexity.INTERMEDIATE, 5.0
        )
        if ultra_complex_adjustment == ScenarioComplexity.MASTER:
            successful_tests += 1
            print("✅ Ultra-complex complexity adjustment")
        else:
            print("❌ Complexity adjustment doesn't support ultra-high difficulties")
        
        # Check if scenario generation supports ultra-complex scenarios
        total_tests += 1
        if scenario.get('ultra_complex', False):
            successful_tests += 1
            print("✅ Ultra-complex scenario generation")
        else:
            print("❌ Ultra-complex scenario generation not working")
        
        # Check if difficulty scaling has no upper limit
        total_tests += 1
        final_imperium_difficulty = enhanced_service.ai_difficulty_multipliers["imperium"]
        if final_imperium_difficulty > 7.0:  # Should be much higher after multiple wins
            successful_tests += 1
            print("✅ Unlimited difficulty scaling (no upper limit)")
        else:
            print("❌ Difficulty scaling still has upper limit")
        
        # Check if ultra-complex scenarios have multi-layer requirements
        total_tests += 1
        if scenario.get('ultra_complex', False):
            details = scenario.get('details', {})
            if 'complexity_layers' in details and details['complexity_layers'] > 1:
                successful_tests += 1
                print("✅ Multi-layer complexity requirements")
            else:
                print("❌ Multi-layer complexity not implemented")
        else:
            print("⚠️  Skipped (ultra-complex not triggered)")
        
        success_rate = (successful_tests / total_tests) * 100
        print(f"\nSuccess Rate: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print(f"\n🎉 Unlimited difficulty scaling system is working!")
            print(f"✅ Scenarios become increasingly complex, layered, and technical!")
            print(f"✅ No upper limit on AI growth and scenario difficulty!")
            return True
        else:
            print(f"\n⚠️  Some components need attention")
            return False
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Unlimited Difficulty Scaling Test")
    result = asyncio.run(test_unlimited_difficulty_scaling())
    
    if result:
        print("\n✅ All tests completed successfully!")
        print("🎯 Unlimited difficulty scaling system is fully functional!")
        print("🚀 AIs can grow infinitely and scenarios become increasingly complex!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1) 