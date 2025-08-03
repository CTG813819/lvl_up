#!/usr/bin/env python3
"""
Comprehensive test script to verify custody protocol fixes
Tests difficulty logging, score variation, AI-specific evaluation, and threshold adjustment
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.custody_protocol_service import CustodyProtocolService, TestDifficulty, TestCategory
from app.services.agent_metrics_service import AgentMetricsService

async def test_comprehensive_fixes():
    """Test all custody protocol fixes"""
    print("🧪 Testing comprehensive custody protocol fixes...")
    
    # Initialize services
    custody_service = CustodyProtocolService()
    agent_metrics_service = AgentMetricsService()
    
    # Test AI types
    test_ais = ["conquest", "guardian", "imperium", "sandbox"]
    
    results = {}
    
    for ai_type in test_ais:
        print(f"\n🔍 Testing {ai_type.upper()} AI...")
        
        # Get initial metrics
        initial_metrics = await agent_metrics_service.get_custody_metrics(ai_type)
        print(f"  Initial metrics: {initial_metrics}")
        
        # Administer a test
        test_result = await custody_service.administer_custody_test(ai_type)
        print(f"  Test result: {json.dumps(test_result, default=str, indent=2)}")
        
        # Check if difficulty is properly set
        difficulty = test_result.get('difficulty', 'unknown')
        print(f"  Test difficulty: {difficulty}")
        
        # Get updated metrics
        updated_metrics = await agent_metrics_service.get_custody_metrics(ai_type)
        print(f"  Updated metrics: {updated_metrics}")
        
        # Check test history for difficulty
        test_history = updated_metrics.get('test_history', [])
        if test_history:
            latest_entry = test_history[-1]
            difficulty_in_history = latest_entry.get('difficulty', 'unknown')
            print(f"  Difficulty in history: {difficulty_in_history}")
            
            # Verify difficulty is not "unknown"
            if difficulty_in_history != "unknown":
                print(f"  ✅ SUCCESS: Difficulty properly logged as {difficulty_in_history}")
            else:
                print(f"  ❌ FAILURE: Difficulty still showing as 'unknown'")
        
        # Check score variation
        score = test_result.get('score', 0)
        print(f"  Test score: {score}")
        
        # Check threshold adjustment
        threshold = test_result.get('threshold', 0)
        print(f"  Test threshold: {threshold}")
        
        # Store results
        results[ai_type] = {
            'score': score,
            'threshold': threshold,
            'difficulty': difficulty,
            'passed': test_result.get('passed', False)
        }
    
    # Analyze results
    print(f"\n📊 Analysis of test results:")
    print(f"  Scores: {[results[ai]['score'] for ai in test_ais]}")
    print(f"  Thresholds: {[results[ai]['threshold'] for ai in test_ais]}")
    print(f"  Difficulties: {[results[ai]['difficulty'] for ai in test_ais]}")
    
    # Check for score variation
    scores = [results[ai]['score'] for ai in test_ais]
    if len(set(scores)) > 1:
        print(f"  ✅ SUCCESS: Scores are varied ({scores})")
    else:
        print(f"  ❌ FAILURE: All scores are the same ({scores})")
    
    # Check for appropriate thresholds
    thresholds = [results[ai]['threshold'] for ai in test_ais]
    if all(t <= 70 for t in thresholds):
        print(f"  ✅ SUCCESS: Thresholds are reasonable ({thresholds})")
    else:
        print(f"  ❌ FAILURE: Some thresholds are too high ({thresholds})")
    
    # Check for proper difficulty logging
    difficulties = [results[ai]['difficulty'] for ai in test_ais]
    if all(d != "unknown" for d in difficulties):
        print(f"  ✅ SUCCESS: All difficulties properly logged ({difficulties})")
    else:
        print(f"  ❌ FAILURE: Some difficulties still unknown ({difficulties})")
    
    return results

async def test_ai_specific_evaluation():
    """Test that AIs get different scores based on their type"""
    print(f"\n🎯 Testing AI-specific evaluation...")
    
    custody_service = CustodyProtocolService()
    
    # Test the same scenario for different AIs
    test_scenario = {
        "scenario": "Create a simple web application",
        "test_type": "knowledge_verification",
        "difficulty": "basic"
    }
    
    scores = {}
    
    for ai_type in ["conquest", "guardian", "imperium", "sandbox"]:
        print(f"  Testing {ai_type} with same scenario...")
        
        # Simulate evaluation
        evaluation_result = await custody_service._perform_autonomous_evaluation(
            ai_type, test_scenario, TestDifficulty.BASIC, TestCategory.KNOWLEDGE_VERIFICATION,
            f"Response from {ai_type} AI", [], []
        )
        
        score = evaluation_result.get('score', 0)
        scores[ai_type] = score
        print(f"    Score: {score}")
    
    # Check for variation
    unique_scores = len(set(scores.values()))
    print(f"  Unique scores: {unique_scores}/4")
    
    if unique_scores > 1:
        print(f"  ✅ SUCCESS: AI-specific evaluation working")
    else:
        print(f"  ❌ FAILURE: All AIs getting same scores")
    
    return scores

async def main():
    """Run all comprehensive tests"""
    print("🚀 Starting comprehensive custody protocol fix verification...")
    
    try:
        # Test comprehensive fixes
        results = await test_comprehensive_fixes()
        
        # Test AI-specific evaluation
        ai_scores = await test_ai_specific_evaluation()
        
        print(f"\n🎉 Comprehensive test completed!")
        print(f"  Results: {json.dumps(results, default=str, indent=2)}")
        print(f"  AI Scores: {ai_scores}")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
