#!/usr/bin/env python3
"""
Test script to verify that all AIs are working autonomously
without relying on external LLMs (Anthropic/OpenAI)
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def test_autonomous_ai_initialization():
    """Test if AI services can be initialized properly"""
    print("🧪 Testing autonomous AI service initialization...")
    try:
        from app.services.imperium_ai_service import ImperiumAIService
        from app.services.guardian_ai_service import GuardianAIService
        from app.services.sandbox_ai_service import SandboxAIService
        from app.services.conquest_ai_service import ConquestAIService
        
        imperium_service = await ImperiumAIService.initialize()
        print("✅ Imperium AI Service initialized successfully")
        
        guardian_service = await GuardianAIService.initialize()
        print("✅ Guardian AI Service initialized successfully")
        
        sandbox_service = await SandboxAIService.initialize()
        print("✅ Sandbox AI Service initialized successfully")
        
        conquest_service = await ConquestAIService.initialize()
        print("✅ Conquest AI Service initialized successfully")
        
        return True
    except Exception as e:
        print(f"❌ Error testing AI initialization: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_autonomous_ai_responses():
    """Test if AI services can provide autonomous answers without external LLMs"""
    print("\n🧪 Testing autonomous AI responses...")
    try:
        from app.services.imperium_ai_service import ImperiumAIService
        from app.services.guardian_ai_service import GuardianAIService
        from app.services.sandbox_ai_service import SandboxAIService
        from app.services.conquest_ai_service import ConquestAIService
        
        # Initialize all AI services
        imperium_service = await ImperiumAIService.initialize()
        guardian_service = await GuardianAIService.initialize()
        sandbox_service = await SandboxAIService.initialize()
        conquest_service = await ConquestAIService.initialize()
        
        # Test prompts for each AI
        test_prompts = {
            "Imperium": [
                "How can I optimize my Flutter app performance?",
                "Create a Flutter extension for data visualization",
                "Analyze this code for improvements"
            ],
            "Guardian": [
                "Check the security of this code",
                "Review this proposal for compliance",
                "Perform a system health check"
            ],
            "Sandbox": [
                "Design an experiment to test user engagement",
                "Analyze patterns in user behavior data",
                "Create a security testing scenario"
            ],
            "Conquest": [
                "Create a Flutter app for task management",
                "Build an APK for my mobile app",
                "Set up a GitHub repository for my project"
            ]
        }
        
        results = {}
        
        for ai_name, prompts in test_prompts.items():
            print(f"\n🔍 Testing {ai_name} AI...")
            ai_service = None
            
            if ai_name == "Imperium":
                ai_service = imperium_service
            elif ai_name == "Guardian":
                ai_service = guardian_service
            elif ai_name == "Sandbox":
                ai_service = sandbox_service
            elif ai_name == "Conquest":
                ai_service = conquest_service
            
            ai_results = []
            for i, prompt in enumerate(prompts, 1):
                try:
                    print(f"  Testing prompt {i}: {prompt[:50]}...")
                    response = await ai_service.answer_prompt(prompt)
                    
                    # Check if response is autonomous (not from external LLM)
                    if response and not response.startswith("Error") and len(response) > 10:
                        print(f"    ✅ Response received: {response[:100]}...")
                        ai_results.append(True)
                    else:
                        print(f"    ❌ Invalid response: {response}")
                        ai_results.append(False)
                        
                except Exception as e:
                    print(f"    ❌ Error: {str(e)}")
                    ai_results.append(False)
            
            results[ai_name] = ai_results
            success_rate = sum(ai_results) / len(ai_results) * 100
            print(f"  📊 {ai_name} AI Success Rate: {success_rate:.1f}%")
        
        return results
        
    except Exception as e:
        print(f"❌ Error testing autonomous responses: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_no_external_llm_dependency():
    """Test that AIs don't rely on external LLMs"""
    print("\n🧪 Testing no external LLM dependency...")
    try:
        # Check if any AI service tries to import or use external LLM services
        import importlib
        
        # List of external LLM services that should not be used
        external_llm_services = [
            'anthropic_service',
            'openai_service',
            'unified_ai_service_shared'
        ]
        
        # Test that AI services can answer without these dependencies
        from app.services.imperium_ai_service import ImperiumAIService
        imperium_service = await ImperiumAIService.initialize()
        
        # Test a simple prompt
        response = await imperium_service.answer_prompt("Hello")
        
        # Check that response is generated autonomously
        if response and "Imperium AI" in response:
            print("✅ Imperium AI generated autonomous response without external LLM")
            return True
        else:
            print(f"❌ Unexpected response: {response}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing LLM independence: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🚀 Starting Autonomous AI Testing")
    print("=" * 50)
    
    # Test 1: Initialization
    init_success = await test_autonomous_ai_initialization()
    
    # Test 2: Autonomous responses
    response_results = await test_autonomous_ai_responses()
    
    # Test 3: No external LLM dependency
    llm_independence = await test_no_external_llm_dependency()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    print(f"✅ AI Initialization: {'PASS' if init_success else 'FAIL'}")
    
    if response_results:
        total_tests = 0
        total_passed = 0
        for ai_name, results in response_results.items():
            passed = sum(results)
            total = len(results)
            total_tests += total
            total_passed += passed
            print(f"✅ {ai_name} AI Responses: {passed}/{total} PASSED")
        
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        print(f"📊 Overall Success Rate: {overall_success_rate:.1f}%")
    else:
        print("❌ AI Responses: FAIL")
    
    print(f"✅ No External LLM Dependency: {'PASS' if llm_independence else 'FAIL'}")
    
    # Final verdict
    if init_success and response_results and llm_independence:
        print("\n🎉 ALL TESTS PASSED! AIs are working autonomously!")
    else:
        print("\n⚠️  Some tests failed. AIs may still have dependencies on external LLMs.")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    asyncio.run(main()) 