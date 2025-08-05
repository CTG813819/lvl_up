#!/usr/bin/env python3
"""
Test Adversarial AI Responses
Tests that AIs are responding to enhanced adversarial testing with coding problems
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.enhanced_adversarial_testing_service import EnhancedAdversarialTestingService
from app.services.agent_metrics_service import AgentMetricsService

class AdversarialAITester:
    def __init__(self):
        self.enhanced_testing_service = None
        self.agent_metrics_service = None
        self.test_results = []
        
    async def initialize(self):
        """Initialize the testing services"""
        print("🔧 Initializing Adversarial AI Tester...")
        
        # Initialize enhanced adversarial testing service
        self.enhanced_testing_service = EnhancedAdversarialTestingService()
        await self.enhanced_testing_service.initialize()
        
        # Initialize agent metrics service
        self.agent_metrics_service = AgentMetricsService()
        await self.agent_metrics_service.initialize()
        
        print("✅ Adversarial AI Tester initialized successfully")
    
    async def test_ai_responses(self, ai_types: List[str] = None):
        """Test AI responses to adversarial scenarios"""
        if ai_types is None:
            ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        print(f"\n🧪 Testing AI Responses for: {', '.join(ai_types)}")
        print("=" * 60)
        
        # Test different scenario types
        scenario_types = [
            "system_level",
            "complex_problem_solving", 
            "security_challenges",
            "creative_tasks"
        ]
        
        for scenario_type in scenario_types:
            print(f"\n📋 Testing {scenario_type} scenarios...")
            
            # Generate scenario
            scenario = await self.enhanced_testing_service.generate_diverse_adversarial_scenario(
                ai_types=ai_types,
                target_domain=scenario_type
            )
            
            if not scenario or "error" in scenario:
                print(f"❌ Failed to generate {scenario_type} scenario: {scenario.get('error', 'Unknown error')}")
                continue
            
            print(f"✅ Generated {scenario_type} scenario: {scenario.get('name', 'Unknown')}")
            
            # Execute test
            test_result = await self.enhanced_testing_service.execute_diverse_adversarial_test(scenario)
            
            if not test_result or "error" in test_result:
                print(f"❌ Failed to execute {scenario_type} test: {test_result.get('error', 'Unknown error')}")
                continue
            
            # Analyze results
            await self._analyze_test_results(scenario_type, test_result)
            
            # Store results
            self.test_results.append({
                "scenario_type": scenario_type,
                "scenario": scenario,
                "test_result": test_result,
                "timestamp": datetime.utcnow().isoformat()
            })
    
    async def _analyze_test_results(self, scenario_type: str, test_result: Dict[str, Any]):
        """Analyze test results for AI responses"""
        print(f"\n📊 Analyzing {scenario_type} test results...")
        
        # Check AI responses
        ai_responses = test_result.get("ai_responses", {})
        
        if not ai_responses:
            print("❌ No AI responses found in test results")
            return
        
        print(f"📝 Found responses from {len(ai_responses)} AIs:")
        
        for ai_type, response in ai_responses.items():
            print(f"\n🤖 {ai_type.upper()} AI Response:")
            
            # Check response quality
            if "error" in response:
                print(f"   ❌ Error: {response['error']}")
                continue
            
            approach = response.get("approach", "")
            response_method = response.get("response_method", "unknown")
            has_code = response.get("has_code", False)
            has_algorithm = response.get("has_algorithm", False)
            
            print(f"   ✅ Response Method: {response_method}")
            print(f"   📝 Has Code: {has_code}")
            print(f"   🧮 Has Algorithm: {has_algorithm}")
            
            # Check response length
            response_length = len(approach) if approach else 0
            print(f"   📏 Response Length: {response_length} characters")
            
            # Check for coding content
            if has_code:
                print("   💻 Contains code examples")
            if has_algorithm:
                print("   �� Contains algorithm descriptions")
            
            # Check evaluation
            evaluation = test_result.get("evaluations", {}).get(ai_type, {})
            if evaluation:
                overall_score = evaluation.get("overall_score", 0)
                passed = evaluation.get("passed", False)
                print(f"   🎯 Overall Score: {overall_score}/100")
                print(f"   ✅ Passed: {passed}")
    
    async def test_token_limit_bypass(self):
        """Test that AIs can bypass token limits for adversarial testing"""
        print(f"\n🔓 Testing Token Limit Bypass...")
        print("=" * 60)
        
        # Test with different AI types
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        for ai_type in ai_types:
            print(f"\n🧪 Testing {ai_type} AI token limit bypass...")
            
            # Create a simple scenario to test response generation
            test_scenario = {
                "domain": "system_level",
                "complexity": "intermediate",
                "description": "Test scenario for token limit bypass",
                "details": {
                    "problem_statement": "Implement a simple REST API with authentication",
                    "environment_setup": "Python Flask environment",
                    "challenges": ["Authentication", "API design", "Error handling"],
                    "deliverables": ["Flask app", "API documentation", "Tests"],
                    "evaluation_criteria": ["Code quality", "Security", "Documentation"],
                    "timeline": "1 hour"
                }
            }
            
            try:
                # Test direct response generation
                response = await self.enhanced_testing_service._get_ai_scenario_response(ai_type, test_scenario)
                
                if response and "error" not in response:
                    print(f"   ✅ {ai_type} AI generated response successfully")
                    print(f"   📝 Response Method: {response.get('response_method', 'unknown')}")
                    print(f"   💻 Has Code: {response.get('has_code', False)}")
                else:
                    print(f"   ❌ {ai_type} AI failed to generate response: {response.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"   ❌ {ai_type} AI exception: {str(e)}")
    
    async def test_coding_problems_inclusion(self):
        """Test that scenarios include coding problems"""
        print(f"\n💻 Testing Coding Problems Inclusion...")
        print("=" * 60)
        
        # Test different scenario types
        scenario_types = [
            "system_level",
            "complex_problem_solving",
            "security_challenges",
            "creative_tasks"
        ]
        
        for scenario_type in scenario_types:
            print(f"\n📋 Testing {scenario_type} coding problems...")
            
            # Generate scenario
            scenario = await self.enhanced_testing_service.generate_diverse_adversarial_scenario(
                ai_types=["imperium"],
                target_domain=scenario_type
            )
            
            if not scenario or "error" in scenario:
                print(f"   ❌ Failed to generate {scenario_type} scenario")
                continue
            
            # Check for coding content
            has_coding_challenge = "coding_challenge" in scenario
            has_problem_statement = "problem_statement" in scenario.get("details", {})
            has_environment_setup = "environment_setup" in scenario.get("details", {})
            
            print(f"   ✅ Scenario: {scenario.get('name', 'Unknown')}")
            print(f"   💻 Has Coding Challenge: {has_coding_challenge}")
            print(f"   📝 Has Problem Statement: {has_problem_statement}")
            print(f"   🔧 Has Environment Setup: {has_environment_setup}")
            
            # Check deliverables for coding requirements
            deliverables = scenario.get("details", {}).get("deliverables", [])
            coding_deliverables = [d for d in deliverables if any(keyword in d.lower() for keyword in ["code", "script", "api", "implementation", "app"])]
            
            print(f"   📦 Coding Deliverables: {len(coding_deliverables)}/{len(deliverables)}")
            for deliverable in coding_deliverables:
                print(f"      - {deliverable}")
    
    async def generate_test_report(self):
        """Generate a comprehensive test report"""
        print(f"\n📊 Generating Test Report...")
        print("=" * 60)
        
        report = {
            "test_timestamp": datetime.utcnow().isoformat(),
            "total_tests": len(self.test_results),
            "successful_tests": 0,
            "failed_tests": 0,
            "ai_response_summary": {},
            "coding_problems_summary": {},
            "recommendations": []
        }
        
        # Analyze test results
        for test in self.test_results:
            scenario_type = test["scenario_type"]
            test_result = test["test_result"]
            
            if "error" in test_result:
                report["failed_tests"] += 1
                continue
            
            report["successful_tests"] += 1
            
            # Analyze AI responses
            ai_responses = test_result.get("ai_responses", {})
            for ai_type, response in ai_responses.items():
                if ai_type not in report["ai_response_summary"]:
                    report["ai_response_summary"][ai_type] = {
                        "total_responses": 0,
                        "successful_responses": 0,
                        "responses_with_code": 0,
                        "responses_with_algorithms": 0,
                        "average_score": 0,
                        "response_methods": {}
                    }
                
                summary = report["ai_response_summary"][ai_type]
                summary["total_responses"] += 1
                
                if "error" not in response:
                    summary["successful_responses"] += 1
                    
                    if response.get("has_code", False):
                        summary["responses_with_code"] += 1
                    
                    if response.get("has_algorithm", False):
                        summary["responses_with_algorithms"] += 1
                    
                    # Track response methods
                    method = response.get("response_method", "unknown")
                    summary["response_methods"][method] = summary["response_methods"].get(method, 0) + 1
                
                # Calculate average score
                evaluation = test_result.get("evaluations", {}).get(ai_type, {})
                if evaluation:
                    score = evaluation.get("overall_score", 0)
                    summary["average_score"] = (summary["average_score"] * (summary["successful_responses"] - 1) + score) / summary["successful_responses"]
        
        # Generate recommendations
        for ai_type, summary in report["ai_response_summary"].items():
            success_rate = summary["successful_responses"] / summary["total_responses"] if summary["total_responses"] > 0 else 0
            code_rate = summary["responses_with_code"] / summary["successful_responses"] if summary["successful_responses"] > 0 else 0
            
            if success_rate < 0.8:
                report["recommendations"].append(f"{ai_type} AI has low response success rate ({success_rate:.1%}) - check token limits and fallback mechanisms")
            
            if code_rate < 0.5:
                report["recommendations"].append(f"{ai_type} AI has low code generation rate ({code_rate:.1%}) - improve coding challenge prompts")
        
        # Print report
        print(f"\n📈 Test Report Summary:")
        print(f"   Total Tests: {report['total_tests']}")
        print(f"   Successful: {report['successful_tests']}")
        print(f"   Failed: {report['failed_tests']}")
        print(f"   Success Rate: {report['successful_tests']/report['total_tests']:.1%}" if report['total_tests'] > 0 else "   Success Rate: N/A")
        
        print(f"\n🤖 AI Response Summary:")
        for ai_type, summary in report["ai_response_summary"].items():
            success_rate = summary["successful_responses"] / summary["total_responses"] if summary["total_responses"] > 0 else 0
            code_rate = summary["responses_with_code"] / summary["successful_responses"] if summary["successful_responses"] > 0 else 0
            
            print(f"   {ai_type.upper()}:")
            print(f"     Success Rate: {success_rate:.1%}")
            print(f"     Code Generation: {code_rate:.1%}")
            print(f"     Average Score: {summary['average_score']:.1f}/100")
            print(f"     Response Methods: {', '.join(summary['response_methods'].keys())}")
        
        if report["recommendations"]:
            print(f"\n💡 Recommendations:")
            for recommendation in report["recommendations"]:
                print(f"   - {recommendation}")
        
        # Save report
        report_file = f"adversarial_test_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Test report saved to: {report_file}")
        
        return report

async def main():
    """Main test function"""
    print("🚀 Starting Adversarial AI Response Testing")
    print("=" * 60)
    
    tester = AdversarialAITester()
    
    try:
        # Initialize tester
        await tester.initialize()
        
        # Test AI responses
        await tester.test_ai_responses()
        
        # Test token limit bypass
        await tester.test_token_limit_bypass()
        
        # Test coding problems inclusion
        await tester.test_coding_problems_inclusion()
        
        # Generate test report
        await tester.generate_test_report()
        
        print(f"\n✅ Adversarial AI Response Testing completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Testing failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 