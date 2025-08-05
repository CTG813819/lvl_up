#!/usr/bin/env python3
"""
Simple test script to verify AI services can be initialized and answer prompts
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def test_ai_initialization():
    """Test if AI services can be initialized properly"""
    print("🧪 Testing AI service initialization...")
    
    try:
        # Test Imperium AI initialization
        print("\n⚡ Testing Imperium AI initialization...")
        from app.services.imperium_ai_service import ImperiumAIService
        imperium_service = await ImperiumAIService.initialize()
        print("✅ Imperium AI initialized successfully")
        
        # Test Guardian AI initialization
        print("\n🛡️ Testing Guardian AI initialization...")
        from app.services.guardian_ai_service import GuardianAIService
        guardian_service = await GuardianAIService.initialize()
        print("✅ Guardian AI initialized successfully")
        
        # Test Sandbox AI initialization
        print("\n🔬 Testing Sandbox AI initialization...")
        from app.services.sandbox_ai_service import SandboxAIService
        sandbox_service = await SandboxAIService.initialize()
        print("✅ Sandbox AI initialized successfully")
        
        # Test Conquest AI initialization
        print("\n🐉 Testing Conquest AI initialization...")
        from app.services.conquest_ai_service import ConquestAIService
        conquest_service = await ConquestAIService.initialize()
        print("✅ Conquest AI initialized successfully")
        
        print("\n✅ All AI services initialized successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing AI initialization: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_simple_answers():
    """Test if AI services can provide simple answers"""
    print("\n🧪 Testing simple AI answers...")
    
    try:
        # Test Imperium AI with a simple prompt
        print("\n⚡ Testing Imperium AI simple answer...")
        from app.services.imperium_ai_service import ImperiumAIService
        imperium_service = await ImperiumAIService.initialize()
        
        # Use a very simple prompt to avoid token limits
        imperium_answer = await imperium_service.answer_prompt("Hello")
        print(f"✅ Imperium AI answered: {imperium_answer[:50]}...")
        
        # Test Guardian AI with a simple prompt
        print("\n🛡️ Testing Guardian AI simple answer...")
        from app.services.guardian_ai_service import GuardianAIService
        guardian_service = await GuardianAIService.initialize()
        
        guardian_answer = await guardian_service.answer_prompt("Hi")
        print(f"✅ Guardian AI answered: {guardian_answer[:50]}...")
        
        # Test Sandbox AI with a simple prompt
        print("\n🔬 Testing Sandbox AI simple answer...")
        from app.services.sandbox_ai_service import SandboxAIService
        sandbox_service = await SandboxAIService.initialize()
        
        sandbox_answer = await sandbox_service.answer_prompt("Test")
        print(f"✅ Sandbox AI answered: {sandbox_answer[:50]}...")
        
        # Test Conquest AI with a simple prompt
        print("\n🐉 Testing Conquest AI simple answer...")
        from app.services.conquest_ai_service import ConquestAIService
        conquest_service = await ConquestAIService.initialize()
        
        conquest_answer = await conquest_service.answer_prompt("Hello")
        print(f"✅ Conquest AI answered: {conquest_answer[:50]}...")
        
        print("\n✅ All AI services provided answers!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing simple answers: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🚀 Starting simple AI service tests...")
    
    # Test 1: AI initialization
    test1_result = await test_ai_initialization()
    
    # Test 2: Simple answers
    test2_result = await test_simple_answers()
    
    if test1_result and test2_result:
        print("\n✅ All tests passed! AI services are working properly.")
        print("\n🎉 The AIs should now be able to pass tests and improve!")
    else:
        print("\n❌ Some tests failed. Check the issues above.")
    
    return test1_result and test2_result

if __name__ == "__main__":
    asyncio.run(main()) 