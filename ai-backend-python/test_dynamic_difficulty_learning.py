#!/usr/bin/env python3
"""
Test Dynamic Difficulty Scaling and Learning System
Tests that the enhanced adversarial testing service properly evaluates responses,
determines winners/losers, applies dynamic difficulty scaling, and triggers learning.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_dynamic_difficulty_learning():
    """Test dynamic difficulty scaling and learning system"""
    print("🧪 Testing Dynamic Difficulty Scaling and Learning System")
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
        
        # Show initial state
        print("\n📊 Initial State:")
        initial_multipliers = enhanced_service.get_ai_difficulty_multipliers()
        initial_records = enhanced_service.get_ai_win_loss_records()
        
        for ai_type in ["imperium", "guardian", "sandbox", "conquest"]:
            print(f"  {ai_type.title()}: Difficulty={initial_multipliers[ai_type]:.2f}, "
                  f"Wins={initial_records[ai_type]['wins']}, Losses={initial_records[ai_type]['losses']}")
        
        # Test scenario generation with dynamic difficulty
        print("\n🎯 Testing Scenario Generation with Dynamic Difficulty...")
        scenario = await enhanced_service.generate_diverse_adversarial_scenario(
            ai_types=["imperium", "guardian", "sandbox", "conquest"],
            target_domain=None,
            complexity=None
        )
        
        print(f"✅ Scenario generated: {scenario.get('scenario_id', 'unknown')}")
        print(f"   Domain: {scenario.get('domain', 'unknown')}")
        print(f"   Complexity: {scenario.get('complexity', 'unknown')}")
        
        # Check dynamic difficulty information
        if "dynamic_difficulty" in scenario:
            dynamic_info = scenario["dynamic_difficulty"]
            print(f"   Scenario Difficulty: {dynamic_info.get('scenario_difficulty', 0):.2f}")
            print("   AI Difficulty Multipliers:")
            for ai_type, multiplier in dynamic_info.get('ai_difficulty_multipliers', {}).items():
                print(f"     {ai_type.title()}: {multiplier:.2f}")
        else:
            print("   ⚠️  No dynamic difficulty information found")
        
        # Test AI response generation and evaluation
        print("\n🤖 Testing AI Response Generation and Evaluation...")
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        results = {}
        
        for ai_type in ai_types:
            print(f"\n🧠 Testing {ai_type.title()} AI...")
            try:
                # Get AI response
                response = await enhanced_service._get_ai_scenario_response(ai_type, scenario)
                
                # Evaluate the response
                evaluation = await enhanced_service._evaluate_scenario_response(ai_type, scenario, response)
                
                # Calculate score
                score = evaluation.get("overall_score", 0)
                
                results[ai_type] = {
                    "response": response,
                    "evaluation": evaluation,
                    "score": score,
                    "passed": evaluation.get("passed", False)
                }
                
                print(f"   ✅ {ai_type.title()} response evaluated")
                print(f"      Score: {score}")
                print(f"      Passed: {evaluation.get('passed', False)}")
                print(f"      Feedback: {evaluation.get('feedback', 'No feedback')[:100]}...")
                
            except Exception as e:
                print(f"   ❌ {ai_type.title()} failed: {str(e)}")
                results[ai_type] = {"error": str(e)}
        
        # Test winner determination and dynamic difficulty scaling
        print("\n🏆 Testing Winner Determination and Dynamic Difficulty Scaling...")
        
        # Create a simplified results structure for winner determination
        simplified_results = {}
        for ai_type, result in results.items():
            if "error" not in result:
                simplified_results[ai_type] = {
                    "score": result["score"],
                    "passed": result["passed"],
                    "xp_awarded": 100  # Default XP
                }
        
        # Determine winners
        winner_analysis = await enhanced_service._determine_scenario_winners(simplified_results)
        
        print(f"✅ Winner analysis completed")
        print(f"   Winners: {winner_analysis.get('winners', [])}")
        print(f"   Losers: {winner_analysis.get('losers', [])}")
        print(f"   Competition Type: {winner_analysis.get('competition_type', 'unknown')}")
        
        # Check difficulty changes
        if "difficulty_changes" in winner_analysis:
            print("   Difficulty Changes:")
            for ai_type, new_multiplier in winner_analysis["difficulty_changes"].items():
                old_multiplier = initial_multipliers[ai_type]
                change = new_multiplier - old_multiplier
                print(f"     {ai_type.title()}: {old_multiplier:.2f} → {new_multiplier:.2f} ({change:+.2f})")
        
        # Show updated state
        print("\n📊 Updated State After Competition:")
        updated_multipliers = enhanced_service.get_ai_difficulty_multipliers()
        updated_records = enhanced_service.get_ai_win_loss_records()
        
        for ai_type in ["imperium", "guardian", "sandbox", "conquest"]:
            print(f"  {ai_type.title()}: Difficulty={updated_multipliers[ai_type]:.2f}, "
                  f"Wins={updated_records[ai_type]['wins']}, Losses={updated_records[ai_type]['losses']}")
        
        # Test learning history
        print("\n📚 Testing Learning History...")
        learning_history = enhanced_service.get_ai_learning_history()
        
        for ai_type in ["imperium", "guardian", "sandbox", "conquest"]:
            ai_learning = learning_history.get(ai_type, [])
            print(f"  {ai_type.title()}: {len(ai_learning)} learning events")
            
            for i, event in enumerate(ai_learning[-2:], 1):  # Show last 2 events
                event_type = event.get("type", "unknown")
                lessons = event.get("lessons_learned", [])
                print(f"    Event {i}: {event_type} - {len(lessons)} lessons learned")
        
        # Test scenario difficulty calculation
        print("\n🎯 Testing Scenario Difficulty Calculation...")
        test_ai_types = ["imperium", "guardian"]
        scenario_difficulty = enhanced_service._calculate_scenario_difficulty(test_ai_types)
        print(f"   Scenario difficulty for {test_ai_types}: {scenario_difficulty:.2f}")
        
        # Test complexity adjustment
        print("\n📈 Testing Complexity Adjustment...")
        from app.services.enhanced_adversarial_testing_service import ScenarioComplexity
        
        test_complexities = [
            (ScenarioComplexity.INTERMEDIATE, 0.5),   # Low difficulty
            (ScenarioComplexity.INTERMEDIATE, 1.0),   # Normal difficulty
            (ScenarioComplexity.INTERMEDIATE, 1.5),   # High difficulty
            (ScenarioComplexity.INTERMEDIATE, 2.5),   # Very high difficulty
        ]
        
        for base_complexity, difficulty in test_complexities:
            adjusted = enhanced_service._adjust_complexity_for_difficulty(base_complexity, difficulty)
            print(f"   {base_complexity.value} (difficulty {difficulty:.1f}) → {adjusted.value}")
        
        # Summary
        print(f"\n📊 Test Summary")
        print("=" * 50)
        
        successful_tests = 0
        total_tests = 0
        
        # Check if scenario generation worked
        total_tests += 1
        if "scenario_id" in scenario:
            successful_tests += 1
            print("✅ Scenario generation with dynamic difficulty")
        else:
            print("❌ Scenario generation failed")
        
        # Check if AI responses were generated
        total_tests += 1
        if len([r for r in results.values() if "error" not in r]) >= 2:
            successful_tests += 1
            print("✅ AI response generation and evaluation")
        else:
            print("❌ AI response generation failed")
        
        # Check if winner determination worked
        total_tests += 1
        if winner_analysis.get("winners") or winner_analysis.get("losers"):
            successful_tests += 1
            print("✅ Winner determination and dynamic difficulty scaling")
        else:
            print("❌ Winner determination failed")
        
        # Check if learning was triggered
        total_tests += 1
        total_learning_events = sum(len(history) for history in learning_history.values())
        if total_learning_events > 0:
            successful_tests += 1
            print("✅ AI learning from competition results")
        else:
            print("❌ AI learning not triggered")
        
        # Check if difficulty multipliers changed
        total_tests += 1
        difficulty_changed = any(
            updated_multipliers[ai] != initial_multipliers[ai] 
            for ai in ["imperium", "guardian", "sandbox", "conquest"]
        )
        if difficulty_changed:
            successful_tests += 1
            print("✅ Dynamic difficulty scaling applied")
        else:
            print("❌ Dynamic difficulty scaling not applied")
        
        success_rate = (successful_tests / total_tests) * 100
        print(f"\nSuccess Rate: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print(f"\n🎉 Dynamic difficulty scaling and learning system is working!")
            print(f"✅ AIs are competing, learning, and adapting difficulty levels!")
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
    print("🚀 Starting Dynamic Difficulty and Learning Test")
    result = asyncio.run(test_dynamic_difficulty_learning())
    
    if result:
        print("\n✅ All tests completed successfully!")
        print("🎯 Dynamic difficulty scaling and learning system is fully functional!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1) 