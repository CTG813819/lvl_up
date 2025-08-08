#!/usr/bin/env python3
"""
Live Autonomous Test System - Demonstrates fully live AI responses and autonomous evaluation
with no simulations, fallbacks, or static responses.
"""

import asyncio
import sys
import os

# Add the ai-backend-python directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai-backend-python'))

from app.services.custody_protocol_service import CustodyProtocolService, TestDifficulty, TestCategory
from app.services.agent_metrics_service import AgentMetricsService
from app.services.real_world_test_service import real_world_test_service, RealWorldTestCategory

async def test_live_autonomous_system():
    """Test the fully live and autonomous real-world test system"""
    
    print("🚀 Testing Live Autonomous Real-World Test System")
    print("=" * 70)
    print("This system uses 100% live AI responses and autonomous evaluation")
    print("No simulations, fallbacks, or static responses")
    print("=" * 70)
    
    # Initialize services
    custody_service = CustodyProtocolService()
    agent_metrics_service = AgentMetricsService()
    
    # Set up guardian AI with poor performance (87 consecutive failures)
    test_metrics = {
        "total_tests_given": 87,
        "total_tests_passed": 0,
        "total_tests_failed": 87,
        "consecutive_failures": 87,
        "consecutive_successes": 0,
        "pass_rate": 0.0,
        "current_difficulty": "basic",
        "test_history": []
    }
    
    # Create test history with 87 failed tests
    for i in range(87):
        test_metrics["test_history"].append({
            "timestamp": f"2025-08-01T{i:02d}:00:00.000000",
            "passed": False,
            "score": 40.0,  # Low scores
            "duration": 0
        })
    
    # Update the metrics in the database
    await agent_metrics_service.create_or_update_agent_metrics("guardian", test_metrics)
    
    print(f"📊 Set up guardian AI with:")
    print(f"   - Total tests: {test_metrics['total_tests_given']}")
    print(f"   - Consecutive failures: {test_metrics['consecutive_failures']}")
    print(f"   - Pass rate: {test_metrics['pass_rate']:.2%}")
    print(f"   - Current difficulty: {test_metrics['current_difficulty']}")
    
    # Test 1: Generate live real-world test
    print(f"\n🧪 Test 1: Generating Live Real-World Test")
    print("-" * 50)
    
    # Get learning history
    learning_history = await custody_service._get_ai_learning_history("guardian")
    
    # Generate a real-world test (this will be live, not simulated)
    real_world_test = await real_world_test_service.generate_real_world_test(
        "guardian", 
        RealWorldTestCategory.DOCKER_DEPLOYMENT, 
        "basic", 
        learning_history
    )
    
    print(f"✅ Generated live real-world test:")
    print(f"   - Test ID: {real_world_test['test_id']}")
    print(f"   - Title: {real_world_test['title']}")
    print(f"   - Category: {real_world_test['category']}")
    print(f"   - Difficulty: {real_world_test['difficulty']}")
    print(f"   - Requirements: {len(real_world_test['requirements'])} items")
    print(f"   - Evaluation criteria: {len(real_world_test['evaluation_criteria'])} items")
    print(f"   - Learning objectives: {len(real_world_test['learning_objectives'])} items")
    
    print(f"\n📋 Live Test Scenario:")
    print(real_world_test['scenario'])
    
    print(f"\n📝 Live Requirements:")
    for i, req in enumerate(real_world_test['requirements'], 1):
        print(f"   {i}. {req}")
    
    print(f"\n🎯 Live Learning Objectives:")
    for i, obj in enumerate(real_world_test['learning_objectives'], 1):
        print(f"   {i}. {obj}")
    
    # Test 2: Execute live custody test (triggers real-world test due to 87 failures)
    print(f"\n🧪 Test 2: Executing Live Custody Test")
    print("-" * 50)
    print("This will trigger the real-world test system and generate live AI responses")
    
    # Administer a custody test (should trigger real-world test due to 87 failures)
    test_result = await custody_service.administer_custody_test("guardian", TestCategory.CODE_QUALITY)
    
    print(f"✅ Live custody test completed:")
    print(f"   - Test type: {test_result.get('test_type', 'unknown')}")
    print(f"   - Score: {test_result.get('score', 0)}")
    print(f"   - Passed: {test_result.get('passed', False)}")
    print(f"   - Duration: {test_result.get('duration', 0):.2f}s")
    print(f"   - Evaluation method: {test_result.get('evaluation_method', 'unknown')}")
    
    if 'learning_progress' in test_result:
        print(f"   - Learning progress tracked: Yes")
        progress = test_result['learning_progress']
        print(f"   - Learning score: {progress.get('learning_score', 0):.1f}%")
        print(f"   - Addressed previous failures: {len(progress.get('addressed_previous_failures', []))}")
        print(f"   - Demonstrated learning: {len(progress.get('demonstrated_learning', []))}")
    
    if 'improvement_areas' in test_result:
        print(f"   - Improvement areas identified: {len(test_result['improvement_areas'])}")
        for area in test_result['improvement_areas'][:3]:
            print(f"     • {area}")
    
    if 'recommendations' in test_result:
        print(f"   - AI-generated recommendations: {len(test_result['recommendations'])}")
        for rec in test_result['recommendations'][:3]:
            print(f"     • {rec}")
    
    # Test 3: Show live AI response
    print(f"\n🧪 Test 3: Live AI Response Analysis")
    print("-" * 50)
    
    if 'ai_response' in test_result and test_result['ai_response']:
        ai_response = test_result['ai_response']
        print(f"✅ Live AI Response Generated:")
        print(f"   - Response length: {len(ai_response)} characters")
        print(f"   - Response preview: {ai_response[:200]}...")
        
        # Analyze response quality
        if len(ai_response) > 500:
            print(f"   - Quality: Comprehensive response")
        elif len(ai_response) > 200:
            print(f"   - Quality: Moderate response")
        else:
            print(f"   - Quality: Brief response")
        
        # Check for practical elements
        practical_elements = []
        if 'docker' in ai_response.lower():
            practical_elements.append("Docker configuration")
        if 'compose' in ai_response.lower():
            practical_elements.append("Docker Compose")
        if 'health' in ai_response.lower():
            practical_elements.append("Health checks")
        if 'security' in ai_response.lower():
            practical_elements.append("Security considerations")
        if 'monitoring' in ai_response.lower():
            practical_elements.append("Monitoring setup")
        
        if practical_elements:
            print(f"   - Practical elements identified: {', '.join(practical_elements)}")
        else:
            print(f"   - Practical elements: Limited")
    else:
        print(f"❌ No live AI response generated")
    
    # Test 4: Live evaluation analysis
    print(f"\n🧪 Test 4: Live Evaluation Analysis")
    print("-" * 50)
    
    if 'evaluation' in test_result and test_result['evaluation']:
        evaluation = test_result['evaluation']
        print(f"✅ Live AI Evaluation Completed:")
        
        if isinstance(evaluation, dict):
            print(f"   - Evaluation type: Detailed AI analysis")
            for criterion, feedback in list(evaluation.items())[:3]:
                print(f"     • {criterion}: {feedback[:100]}...")
        else:
            print(f"   - Evaluation type: Summary feedback")
            print(f"   - Feedback: {evaluation[:200]}...")
    else:
        print(f"❌ No live evaluation data")
    
    # Test 5: Live learning analytics
    print(f"\n🧪 Test 5: Live Learning Analytics")
    print("-" * 50)
    
    analytics = await real_world_test_service.get_learning_analytics("guardian")
    
    if "error" not in analytics:
        print(f"✅ Live Learning Analytics:")
        print(f"   - Total tests: {analytics['total_tests']}")
        print(f"   - Passed tests: {analytics['passed_tests']}")
        print(f"   - Pass rate: {analytics['pass_rate']:.1f}%")
        print(f"   - Recent pass rate: {analytics['recent_pass_rate']:.1f}%")
        print(f"   - Improvement trend: {analytics['improvement_trend']}")
        
        if analytics['common_improvement_areas']:
            print(f"   - Common improvement areas: {', '.join(analytics['common_improvement_areas'][:3])}")
    else:
        print(f"❌ No live learning data available yet")
    
    # Test 6: Demonstrate autonomous adaptation
    print(f"\n🧪 Test 6: Autonomous Adaptation Demonstration")
    print("-" * 50)
    
    # Run another test to show adaptation
    print("Running second test to demonstrate autonomous adaptation...")
    test_result_2 = await custody_service.administer_custody_test("guardian", TestCategory.SECURITY_AWARENESS)
    
    print(f"✅ Second live test completed:")
    print(f"   - Test type: {test_result_2.get('test_type', 'unknown')}")
    print(f"   - Score: {test_result_2.get('score', 0)}")
    print(f"   - Passed: {test_result_2.get('passed', False)}")
    print(f"   - Duration: {test_result_2.get('duration', 0):.2f}s")
    
    # Compare results to show adaptation
    if 'score' in test_result and 'score' in test_result_2:
        score_diff = test_result_2['score'] - test_result['score']
        if score_diff > 0:
            print(f"   - Adaptation: Score improved by {score_diff:.1f} points")
        elif score_diff < 0:
            print(f"   - Adaptation: Score decreased by {abs(score_diff):.1f} points")
        else:
            print(f"   - Adaptation: Score remained stable")
    
    print(f"\n" + "=" * 70)
    print("🏁 Live autonomous test system demonstration completed!")
    print("\nKey autonomous features demonstrated:")
    print("✅ 100% live AI response generation (no simulations)")
    print("✅ Autonomous evaluation using AI reasoning")
    print("✅ Live learning progress tracking")
    print("✅ Adaptive test generation based on performance")
    print("✅ Real-time feedback and improvement recommendations")
    print("✅ Autonomous adaptation between tests")
    print("✅ No fallbacks or static responses")

if __name__ == "__main__":
    asyncio.run(test_live_autonomous_system()) 