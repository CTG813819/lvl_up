#!/usr/bin/env python3
"""
Test script to verify adaptive difficulty adjustment works when AI starts at higher difficulty.
This will test the guardian AI starting at ADVANCED difficulty with consecutive failures.
"""

import asyncio
import sys
import os

# Add the ai-backend-python directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai-backend-python'))

from app.services.custody_protocol_service import CustodyProtocolService, TestDifficulty
from app.services.agent_metrics_service import AgentMetricsService

async def test_adaptive_difficulty_advanced():
    """Test adaptive difficulty adjustment for guardian AI starting at ADVANCED difficulty"""
    
    print("🧪 Testing Adaptive Difficulty Adjustment (Advanced → Basic)")
    print("=" * 60)
    
    # Initialize services
    custody_service = CustodyProtocolService()
    agent_metrics_service = AgentMetricsService()
    
    # Set up test data for guardian starting at ADVANCED difficulty with 10 consecutive failures
    test_metrics = {
        "total_tests_given": 10,
        "total_tests_passed": 0,
        "total_tests_failed": 10,
        "consecutive_failures": 10,
        "consecutive_successes": 0,
        "pass_rate": 0.0,
        "current_difficulty": "advanced",  # Start at ADVANCED
        "test_history": []
    }
    
    # Create test history with 10 failed tests
    for i in range(10):
        test_metrics["test_history"].append({
            "timestamp": f"2025-08-01T{i:02d}:00:00.000000",
            "passed": False,
            "score": 30.0,  # Low scores
            "duration": 0
        })
    
    # Update the metrics in the database
    await agent_metrics_service.create_or_update_agent_metrics("guardian", test_metrics)
    
    print(f"📊 Set up guardian AI with:")
    print(f"   - Total tests: {test_metrics['total_tests_given']}")
    print(f"   - Consecutive failures: {test_metrics['consecutive_failures']}")
    print(f"   - Pass rate: {test_metrics['pass_rate']:.2%}")
    print(f"   - Current difficulty: {test_metrics['current_difficulty']}")
    
    # Test the difficulty calculation
    ai_level = await custody_service._get_ai_level("guardian")
    print(f"🤖 AI Level: {ai_level}")
    
    # Prepare performance data
    recent_performance = {
        'consecutive_successes': test_metrics['consecutive_successes'],
        'consecutive_failures': test_metrics['consecutive_failures'],
        'pass_rate': test_metrics['pass_rate'],
        'recent_scores': [test['score'] for test in test_metrics['test_history'][-5:]]
    }
    
    print(f"📈 Performance data:")
    print(f"   - Consecutive failures: {recent_performance['consecutive_failures']}")
    print(f"   - Pass rate: {recent_performance['pass_rate']:.2%}")
    print(f"   - Recent scores: {recent_performance['recent_scores']}")
    
    # Calculate difficulty with performance adjustment
    base_difficulty = custody_service._get_base_difficulty_from_level(ai_level)
    adjusted_difficulty = custody_service._calculate_test_difficulty(ai_level, recent_performance)
    
    print(f"🎯 Difficulty Analysis:")
    print(f"   - Base difficulty (from level): {base_difficulty.value}")
    print(f"   - Adjusted difficulty: {adjusted_difficulty.value}")
    
    # Test the adjustment logic directly
    print(f"\n🔍 Testing Adjustment Logic:")
    adjustment_result = custody_service._adjust_difficulty_based_on_performance(base_difficulty, recent_performance)
    print(f"   - Adjustment result: {adjustment_result.value}")
    
    # Check if difficulty should be decreased
    if recent_performance['consecutive_failures'] >= 5:
        print(f"✅ Should decrease difficulty (10 failures >= 5)")
    else:
        print(f"❌ Should not decrease difficulty (10 failures < 5)")
    
    # Check if the adjusted difficulty is different from base
    if adjusted_difficulty != base_difficulty:
        print(f"✅ Difficulty adjusted: {base_difficulty.value} → {adjusted_difficulty.value}")
    else:
        print(f"❌ Difficulty not adjusted: {base_difficulty.value}")
    
    # Test with different starting difficulties
    print(f"\n🧪 Testing Different Starting Difficulties:")
    
    test_scenarios = [
        {"difficulty": "intermediate", "failures": 5, "expected": "basic"},
        {"difficulty": "advanced", "failures": 5, "expected": "intermediate"},
        {"difficulty": "expert", "failures": 5, "expected": "advanced"},
        {"difficulty": "master", "failures": 5, "expected": "expert"},
        {"difficulty": "legendary", "failures": 5, "expected": "master"},
    ]
    
    for scenario in test_scenarios:
        # Use the actual TestDifficulty enum from the service
        current_difficulty = TestDifficulty(scenario["difficulty"])
        
        # Test performance data
        test_performance = {
            'consecutive_successes': 0,
            'consecutive_failures': scenario["failures"],
            'pass_rate': 0.0,
            'recent_scores': [30.0] * 5
        }
        
        # Test adjustment
        result = custody_service._adjust_difficulty_based_on_performance(current_difficulty, test_performance)
        expected = TestDifficulty(scenario["expected"])
        
        print(f"   - {scenario['difficulty']} → {result.value} (expected: {expected.value})")
        if result.value == expected.value:
            print(f"     ✅ Correct adjustment")
        else:
            print(f"     ❌ Incorrect adjustment")
    
    print("\n" + "=" * 60)
    print("🏁 Test completed!")

if __name__ == "__main__":
    asyncio.run(test_adaptive_difficulty_advanced()) 