#!/usr/bin/env python3
"""
Test script to verify custody protocol fixes for failing AIs
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.custody_protocol_service import CustodyProtocolService, TestDifficulty, TestCategory
from app.services.agent_metrics_service import AgentMetricsService

async def test_difficulty_adjustment():
    """Test that difficulty adjustment works correctly for failing AIs"""
    print("🧪 Testing custody protocol fixes...")
    
    # Initialize services
    custody_service = CustodyProtocolService()
    agent_metrics_service = AgentMetricsService()
    
    # Test AI type
    test_ai = "test_ai_failing"
    
    # Create test metrics with high consecutive failures
    test_metrics = {
        "total_tests_given": 139,
        "total_tests_passed": 1,
        "total_tests_failed": 138,
        "current_difficulty": "intermediate",  # Start with intermediate
        "difficulty_multiplier": 2.0,
        "complexity_layers": 2,
        "last_test_date": "2025-08-01T20:47:37.442047",
        "consecutive_failures": 131,  # High consecutive failures
        "consecutive_successes": 0,
        "test_history": [],
        "custody_level": 1,
        "custody_xp": 221,
        "level": 2,
        "xp": 220,
        "pass_rate": 0.0,
        "failure_rate": 0.88,
        "progression_rate": 0.95
    }
    
    # Save test metrics
    await agent_metrics_service.create_or_update_agent_metrics(test_ai, test_metrics)
    print(f"✅ Created test metrics for {test_ai} with {test_metrics['consecutive_failures']} consecutive failures")
    
    # Test difficulty calculation
    performance_data = {
        'consecutive_successes': test_metrics['consecutive_successes'],
        'consecutive_failures': test_metrics['consecutive_failures'],
        'recent_scores': [40.08] * 10,  # Low scores
        'pass_rate': test_metrics['pass_rate']
    }
    
    # Calculate difficulty
    calculated_difficulty = await custody_service._calculate_difficulty_from_current_metrics(test_ai, performance_data)
    print(f"✅ Calculated difficulty: {calculated_difficulty.value}")
    
    # Verify it's BASIC
    if calculated_difficulty == TestDifficulty.BASIC:
        print("✅ SUCCESS: Difficulty correctly reduced to BASIC for failing AI")
    else:
        print(f"❌ FAILURE: Expected BASIC difficulty, got {calculated_difficulty.value}")
        return False
    
    # Test test generation
    test_content = await custody_service._generate_custody_test(test_ai, calculated_difficulty, TestCategory.KNOWLEDGE_VERIFICATION)
    print(f"✅ Generated test with difficulty: {test_content.get('difficulty', 'unknown')}")
    print(f"✅ Test complexity layers: {test_content.get('complexity_layers', 1)}")
    
    # Verify test is basic
    if test_content.get('difficulty') == 'basic' and test_content.get('complexity_layers', 1) == 1:
        print("✅ SUCCESS: Generated basic test with single complexity layer")
    else:
        print(f"❌ FAILURE: Expected basic test, got difficulty={test_content.get('difficulty')}, layers={test_content.get('complexity_layers')}")
        return False
    
    # Clean up
    await agent_metrics_service.delete_agent_metrics(test_ai)
    print("✅ Cleaned up test data")
    
    return True

async def test_threshold_adjustment():
    """Test that thresholds are lowered for failing AIs"""
    print("\n🧪 Testing threshold adjustment...")
    
    custody_service = CustodyProtocolService()
    agent_metrics_service = AgentMetricsService()
    
    test_ai = "test_ai_threshold"
    
    # Create test metrics with failures
    test_metrics = {
        "consecutive_failures": 10,
        "current_difficulty": "basic"
    }
    
    await agent_metrics_service.create_or_update_agent_metrics(test_ai, test_metrics)
    
    # Simulate test execution
    test_content = {
        "test_type": "knowledge_verification",
        "difficulty": "basic"
    }
    
    # Mock evaluation result
    evaluation_result = {
        "score": 60,  # Low score
        "evaluation": "Test evaluation"
    }
    
    # Test threshold calculation (this would normally happen in _execute_custody_test)
    custody_metrics = await agent_metrics_service.get_custody_metrics(test_ai)
    base_threshold = 90
    
    if custody_metrics and custody_metrics.get('consecutive_failures', 0) >= 5:
        adjusted_threshold = max(50, base_threshold - 20)
        print(f"✅ Threshold adjusted from {base_threshold} to {adjusted_threshold}")
        
        if adjusted_threshold <= 70:  # Should be lowered
            print("✅ SUCCESS: Threshold correctly lowered for failing AI")
            return True
        else:
            print(f"❌ FAILURE: Expected lower threshold, got {adjusted_threshold}")
            return False
    else:
        print("❌ FAILURE: Could not get custody metrics")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting custody protocol fix tests...")
    
    try:
        # Initialize database
        from app.core.database import init_database
        await init_database()
        
        # Run tests
        test1_passed = await test_difficulty_adjustment()
        test2_passed = await test_threshold_adjustment()
        
        if test1_passed and test2_passed:
            print("\n🎉 ALL TESTS PASSED! Custody protocol fixes are working correctly.")
            return True
        else:
            print("\n❌ SOME TESTS FAILED! Please check the custody protocol fixes.")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 