#!/usr/bin/env python3
"""
Test script to verify AI services are working properly after fixes
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def test_ai_services():
    """Test if AI services can answer prompts properly"""
    print("🧪 Testing AI services...")
    
    try:
        # Test Imperium AI
        print("\n⚡ Testing Imperium AI...")
        from app.services.imperium_ai_service import ImperiumAIService
        imperium_service = await ImperiumAIService.initialize()
        imperium_answer = await imperium_service.answer_prompt("What is code optimization?")
        print(f"✅ Imperium AI answered: {imperium_answer[:100]}...")
        
        # Test Guardian AI
        print("\n🛡️ Testing Guardian AI...")
        from app.services.guardian_ai_service import GuardianAIService
        guardian_service = await GuardianAIService.initialize()
        guardian_answer = await guardian_service.answer_prompt("What is security analysis?")
        print(f"✅ Guardian AI answered: {guardian_answer[:100]}...")
        
        # Test Sandbox AI
        print("\n🔬 Testing Sandbox AI...")
        from app.services.sandbox_ai_service import SandboxAIService
        sandbox_service = await SandboxAIService.initialize()
        sandbox_answer = await sandbox_service.answer_prompt("What is experimentation?")
        print(f"✅ Sandbox AI answered: {sandbox_answer[:100]}...")
        
        # Test Conquest AI
        print("\n🐉 Testing Conquest AI...")
        from app.services.conquest_ai_service import ConquestAIService
        conquest_service = await ConquestAIService.initialize()
        conquest_answer = await conquest_service.answer_prompt("What is app creation?")
        print(f"✅ Conquest AI answered: {conquest_answer[:100]}...")
        
        print("\n✅ All AI services are working properly!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing AI services: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_custody_protocol():
    """Test if custody protocol can execute tests properly"""
    print("\n🧪 Testing Custody Protocol Service...")
    
    try:
        from app.services.custody_protocol_service import CustodyProtocolService
        
        # Initialize custody service
        custody_service = await CustodyProtocolService.initialize()
        
        # Create a simple test
        test = {
            "type": "single",
            "ai_types": ["imperium"],
            "scenario": "Explain what code optimization means and provide an example.",
            "difficulty": "basic",
            "complexity": "x1"
        }
        
        print(f"📝 Executing test: {test['scenario'][:50]}...")
        
        # Execute test
        result = await custody_service.execute_test(test)
        
        print(f"✅ Test executed successfully!")
        print(f"📈 Score: {result.get('score', 'NOT_FOUND')}")
        print(f"✅ Passed: {result.get('passed', 'NOT_FOUND')}")
        print(f"📝 Answer: {result.get('evaluation', {}).get('feedback', 'NOT_FOUND')[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing custody protocol: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🚀 Starting AI service tests...")
    
    # Test 1: AI services
    test1_result = await test_ai_services()
    
    # Test 2: Custody protocol
    test2_result = await test_custody_protocol()
    
    if test1_result and test2_result:
        print("\n✅ All tests passed! AI services are working properly.")
    else:
        print("\n❌ Some tests failed. Check the issues above.")
    
    return test1_result and test2_result

if __name__ == "__main__":
    asyncio.run(main()) 