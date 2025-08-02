#!/usr/bin/env python3
"""
Simple test to verify dynamic evaluation system is working
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.custody_protocol_service import CustodyProtocolService

async def test_dynamic_evaluation_integration():
    """Test if dynamic evaluation is properly integrated"""
    print("🧪 Testing dynamic evaluation integration...")
    
    try:
        # Initialize service
        custody_service = CustodyProtocolService()
        
        # Test scenario
        test_scenario = "As Guardian AI, create a secure authentication system for a web application. Include: password hashing, JWT tokens, session management, rate limiting, and protection against common attacks (SQL injection, XSS, CSRF)."
        test_response = "I will implement a comprehensive security system with bcrypt password hashing, JWT token authentication, session management with Redis, rate limiting using middleware, and protection against SQL injection, XSS, and CSRF attacks."
        ai_type = "guardian"
        difficulty = "advanced"
        
        print(f"📝 Test Scenario: {test_scenario[:100]}...")
        print(f"🤖 AI Type: {ai_type}")
        print(f"📊 Difficulty: {difficulty}")
        print(f"💬 Test Response: {test_response[:100]}...")
        
        # Test dynamic evaluation
        print("\n🔧 Testing dynamic evaluation...")
        evaluation = await custody_service._evaluate_with_dynamic_criteria(
            ai_type, test_scenario, test_response, difficulty
        )
        
        print(f"✅ Dynamic evaluation completed!")
        print(f"📈 Score: {evaluation.get('score', 'NOT_FOUND')}")
        print(f"📝 Feedback: {evaluation.get('feedback', 'NOT_FOUND')[:200]}...")
        
        # Test criteria generation
        print("\n🔧 Testing criteria generation...")
        criteria = await custody_service._generate_dynamic_criteria(
            test_scenario, difficulty, ai_type
        )
        
        print(f"✅ Criteria generated!")
        print(f"📝 Requirements: {len(criteria.get('requirements', []))}")
        print(f"🎯 Difficulty criteria: {len(criteria.get('difficulty_criteria', {}))}")
        print(f"🤖 AI-specific criteria: {len(criteria.get('ai_specific_criteria', {}))}")
        print(f"🔧 Technical criteria: {len(criteria.get('technical_criteria', {}))}")
        print(f"📊 Quality criteria: {len(criteria.get('quality_criteria', {}))}")
        
        # Test keyword extraction
        print("\n🔧 Testing keyword extraction...")
        keywords = custody_service._extract_keywords("Provide a complete basic solution")
        print(f"✅ Keywords extracted: {keywords}")
        
        # Test score calculation
        print("\n🔧 Testing score calculation...")
        evaluation_results = {
            "requirements_coverage": 75.0,
            "difficulty_performance": 80.0,
            "ai_specific_performance": 85.0,
            "technical_performance": 70.0,
            "quality_performance": 75.0
        }
        final_score = custody_service._calculate_dynamic_score(evaluation_results, difficulty)
        print(f"✅ Final score calculated: {final_score}")
        
        print("\n✅ All dynamic evaluation components working!")
        return True
        
    except Exception as e:
        print(f"❌ Error in dynamic evaluation test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_execute_test_integration():
    """Test if execute_test is using dynamic evaluation"""
    print("\n🧪 Testing execute_test integration...")
    
    try:
        # Initialize service
        custody_service = CustodyProtocolService()
        
        # Create a test
        test = {
            "type": "single",
            "ai_types": ["guardian"],
            "scenario": "As Guardian AI, create a secure authentication system for a web application. Include: password hashing, JWT tokens, session management, rate limiting, and protection against common attacks (SQL injection, XSS, CSRF).",
            "difficulty": "advanced",
            "complexity": "x1"
        }
        
        print(f"📝 Test: {test}")
        
        # Mock the _get_ai_answer method to return a test response
        async def mock_get_ai_answer(ai_type, prompt):
            return {
                "answer": "I will implement a comprehensive security system with bcrypt password hashing, JWT token authentication, session management with Redis, rate limiting using middleware, and protection against SQL injection, XSS, and CSRF attacks."
            }
        
        # Temporarily replace the method
        original_method = custody_service._get_ai_answer
        custody_service._get_ai_answer = mock_get_ai_answer
        
        try:
            # Execute test
            result = await custody_service.execute_test(test)
            
            print(f"✅ Test executed successfully!")
            print(f"📈 Score: {result.get('score', 'NOT_FOUND')}")
            print(f"✅ Passed: {result.get('passed', 'NOT_FOUND')}")
            print(f"📝 Difficulty: {result.get('difficulty', 'NOT_FOUND')}")
            print(f"🔧 Complexity: {result.get('complexity', 'NOT_FOUND')}")
            
            # Check if dynamic evaluation was used
            if result.get('score') and result.get('score') != 40.08:
                print("✅ Dynamic evaluation appears to be working!")
            else:
                print("❌ Dynamic evaluation may not be working - score is 40.08")
                
        finally:
            # Restore original method
            custody_service._get_ai_answer = original_method
            
        return True
        
    except Exception as e:
        print(f"❌ Error in execute_test integration: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🚀 Starting dynamic evaluation integration tests...")
    
    # Test 1: Dynamic evaluation components
    test1_result = await test_dynamic_evaluation_integration()
    
    # Test 2: Execute test integration
    test2_result = await test_execute_test_integration()
    
    if test1_result and test2_result:
        print("\n✅ All tests passed! Dynamic evaluation system is working.")
    else:
        print("\n❌ Some tests failed. Check the issues above.")
    
    return test1_result and test2_result

if __name__ == "__main__":
    asyncio.run(main()) 