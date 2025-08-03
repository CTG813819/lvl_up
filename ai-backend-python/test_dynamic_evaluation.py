#!/usr/bin/env python3
"""
Test script to verify dynamic evaluation system
Tests that evaluation criteria are generated based on test scenarios rather than templates
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.custody_protocol_service import CustodyProtocolService, TestDifficulty, TestCategory

async def test_dynamic_evaluation():
    """Test the dynamic evaluation system"""
    print("🧪 Testing dynamic evaluation system...")
    
    # Initialize services
    custody_service = CustodyProtocolService()
    
    # Test scenarios with different characteristics
    test_scenarios = [
        {
            "name": "Security Test",
            "scenario": "As Guardian AI, create a secure authentication system for a web application. Include: password hashing, JWT tokens, session management, rate limiting, and protection against common attacks (SQL injection, XSS, CSRF).",
            "ai_type": "guardian",
            "difficulty": "advanced"
        },
        {
            "name": "Performance Test", 
            "scenario": "As Imperium AI, optimize a slow database query that's causing performance issues in a production environment. The query involves multiple joins, aggregations, and is running on a large dataset.",
            "ai_type": "imperium",
            "difficulty": "expert"
        },
        {
            "name": "User Experience Test",
            "scenario": "As Conquest AI, design a user-friendly mobile application interface for task management. Focus on intuitive navigation, clear visual hierarchy, and accessibility features.",
            "ai_type": "conquest", 
            "difficulty": "intermediate"
        },
        {
            "name": "Innovation Test",
            "scenario": "As Sandbox AI, create an experimental AI-powered monitoring system that can predict system failures before they occur. Include: machine learning models, real-time data processing, and automated response mechanisms.",
            "ai_type": "sandbox",
            "difficulty": "master"
        }
    ]
    
    print("\n🔧 Testing dynamic criteria generation:")
    print("1. Criteria generation based on scenario content")
    print("2. AI-specific criteria based on AI type")
    print("3. Difficulty-specific criteria")
    print("4. Technical criteria based on scenario keywords")
    
    results = {}
    
    for test in test_scenarios:
        print(f"\n📊 Testing {test['name']}...")
        
        try:
            # Generate dynamic criteria
            criteria = await custody_service._generate_dynamic_criteria(
                test["scenario"], test["difficulty"], test["ai_type"]
            )
            
            print(f"   ✅ Generated criteria for {test['name']}")
            print(f"   📝 Requirements: {len(criteria.get('requirements', []))} requirements")
            print(f"   🎯 Difficulty criteria: {len(criteria.get('difficulty_criteria', {}))} criteria")
            print(f"   🤖 AI-specific criteria: {len(criteria.get('ai_specific_criteria', {}))} criteria")
            print(f"   🔧 Technical criteria: {len(criteria.get('technical_criteria', {}))} criteria")
            print(f"   📊 Quality criteria: {len(criteria.get('quality_criteria', {}))} criteria")
            
            # Test evaluation with sample response
            sample_response = f"This is a sample response for {test['ai_type']} AI addressing the {test['name']} scenario. It includes relevant keywords and demonstrates understanding of the requirements."
            
            evaluation = await custody_service._evaluate_with_dynamic_criteria(
                test["ai_type"], test["scenario"], sample_response, test["difficulty"]
            )
            
            print(f"   ✅ Evaluated response for {test['name']}")
            print(f"   📈 Score: {evaluation.get('score', 'NOT_FOUND')}")
            print(f"   📝 Feedback: {evaluation.get('feedback', 'NOT_FOUND')[:100]}...")
            
            # Store results
            results[test['name']] = {
                "criteria_generated": len(criteria) > 0,
                "requirements_count": len(criteria.get('requirements', [])),
                "difficulty_criteria_count": len(criteria.get('difficulty_criteria', {})),
                "ai_specific_criteria_count": len(criteria.get('ai_specific_criteria', {})),
                "technical_criteria_count": len(criteria.get('technical_criteria', {})),
                "quality_criteria_count": len(criteria.get('quality_criteria', {})),
                "evaluation_score": evaluation.get('score'),
                "evaluation_feedback": evaluation.get('feedback', '')[:200],
                "criteria_details": criteria
            }
            
        except Exception as e:
            print(f"   ❌ Error testing {test['name']}: {str(e)}")
            results[test['name']] = {"error": str(e)}
    
    # Test collaborative evaluation
    print(f"\n🤝 Testing collaborative dynamic evaluation...")
    try:
        collaborative_scenario = "As a team of AIs, design a comprehensive DevOps pipeline. Guardian AI handles security, Imperium AI handles optimization, Conquest AI handles user experience, and Sandbox AI handles innovation."
        
        collaborative_responses = {
            "guardian": "I will focus on implementing security measures including authentication, authorization, and vulnerability scanning in the DevOps pipeline.",
            "imperium": "I will optimize the pipeline for performance, including caching strategies, resource management, and scalability considerations.",
            "conquest": "I will ensure the pipeline provides excellent user experience with clear documentation, intuitive interfaces, and practical implementation.",
            "sandbox": "I will introduce innovative approaches including AI-powered monitoring, automated testing, and experimental deployment strategies."
        }
        
        collaborative_evaluation = await custody_service._evaluate_collaborative_with_dynamic_criteria(
            collaborative_scenario, collaborative_responses, "advanced"
        )
        
        print(f"   ✅ Evaluated collaborative response")
        print(f"   📈 Collaborative score: {collaborative_evaluation.get('score', 'NOT_FOUND')}")
        print(f"   🤝 Collaboration bonus: {collaborative_evaluation.get('collaboration_score', 'NOT_FOUND')}")
        print(f"   📝 Feedback: {collaborative_evaluation.get('feedback', 'NOT_FOUND')[:100]}...")
        
        results["collaborative"] = {
            "collaborative_score": collaborative_evaluation.get('score'),
            "collaboration_bonus": collaborative_evaluation.get('collaboration_score'),
            "individual_evaluations": len(collaborative_evaluation.get('individual_evaluations', {})),
            "collaborative_feedback": collaborative_evaluation.get('feedback', '')[:200],
            "collaborative_criteria": collaborative_evaluation.get('collaborative_criteria', {})
        }
        
    except Exception as e:
        print(f"   ❌ Error testing collaborative: {str(e)}")
        results["collaborative"] = {"error": str(e)}
    
    # Summary
    print(f"\n📋 SUMMARY:")
    print("=" * 50)
    
    for test_name, result in results.items():
        print(f"\n{test_name.upper()}:")
        if "error" in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   ✅ Criteria generated: {result['criteria_generated']}")
            print(f"   📝 Requirements: {result['requirements_count']}")
            print(f"   🎯 Difficulty criteria: {result['difficulty_criteria_count']}")
            print(f"   🤖 AI-specific criteria: {result['ai_specific_criteria_count']}")
            print(f"   🔧 Technical criteria: {result['technical_criteria_count']}")
            print(f"   📊 Quality criteria: {result['quality_criteria_count']}")
            print(f"   📈 Evaluation score: {result['evaluation_score']}")
            
            # Check if dynamic criteria are working
            if result['criteria_generated'] and result['requirements_count'] > 0:
                print(f"   ✅ Dynamic criteria generation: WORKING")
            else:
                print(f"   ❌ Dynamic criteria generation: FAILED")
                
            if result['evaluation_score'] and result['evaluation_score'] != 50:
                print(f"   ✅ Dynamic evaluation: WORKING (score: {result['evaluation_score']})")
            else:
                print(f"   ❌ Dynamic evaluation: FAILED (score: {result['evaluation_score']})")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"test_dynamic_evaluation_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    return results

async def main():
    """Main test function"""
    print("🚀 Starting dynamic evaluation system test...")
    
    try:
        results = await test_dynamic_evaluation()
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 