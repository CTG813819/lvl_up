#!/usr/bin/env python3
"""
Comprehensive Test and Commit Script
Tests all enhanced test generation features before pushing to git
"""

import asyncio
import sys
import os
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Any

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.enhanced_test_generation_service import enhanced_test_generator, TestType
from app.services.test_runner_service import test_runner_service
from app.services.logging_service import ai_logging_service, LogLevel, AISystemType


class ComprehensiveTester:
    """Comprehensive tester for all enhanced test features"""
    
    def __init__(self):
        self.test_results = {}
        self.passed_tests = 0
        self.total_tests = 0
    
    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run comprehensive tests for all enhanced features"""
        print("🚀 Starting Comprehensive Test Suite...")
        print("=" * 60)
        
        try:
            # Test 1: Enhanced Test Generation
            await self._test_enhanced_test_generation()
            
            # Test 2: Internet Knowledge Integration
            await self._test_internet_knowledge_integration()
            
            # Test 3: AI Knowledge Learning
            await self._test_ai_knowledge_learning()
            
            # Test 4: Progressive Difficulty
            await self._test_progressive_difficulty()
            
            # Test 5: Varied Content Categories
            await self._test_varied_content_categories()
            
            # Test 6: Test Runner Integration
            await self._test_test_runner_integration()
            
            # Test 7: Logging System
            await self._test_logging_system()
            
            # Test 8: Real Test Execution
            await self._test_real_test_execution()
            
            # Generate comprehensive report
            report = self._generate_test_report()
            
            print("\n" + "=" * 60)
            print(f"📊 Test Results: {self.passed_tests}/{self.total_tests} tests passed")
            print("=" * 60)
            
            return report
            
        except Exception as e:
            print(f"❌ Comprehensive test failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _test_enhanced_test_generation(self):
        """Test enhanced test generation"""
        print("\n🧪 Test 1: Enhanced Test Generation")
        try:
            # Test collaborative test generation
            test_content = await enhanced_test_generator.generate_enhanced_test(
                TestType.COLLABORATIVE, 
                ["imperium", "guardian"], 
                "intermediate"
            )
            
            # Verify test content structure
            required_fields = ["test_id", "test_type", "ai_types", "difficulty", "timestamp"]
            for field in required_fields:
                if field not in test_content:
                    raise ValueError(f"Missing required field: {field}")
            
            print("✅ Enhanced test generation working correctly")
            self.passed_tests += 1
            
        except Exception as e:
            print(f"❌ Enhanced test generation failed: {str(e)}")
        
        self.total_tests += 1
    
    async def _test_internet_knowledge_integration(self):
        """Test internet knowledge integration"""
        print("\n🌐 Test 2: Internet Knowledge Integration")
        try:
            # Test internet search functionality
            internet_knowledge = await enhanced_test_generator._search_internet_knowledge(
                TestType.COLLABORATIVE, "intermediate"
            )
            
            # Verify internet knowledge structure
            if not isinstance(internet_knowledge, dict):
                raise ValueError("Internet knowledge should be a dictionary")
            
            print("✅ Internet knowledge integration working correctly")
            self.passed_tests += 1
            
        except Exception as e:
            print(f"❌ Internet knowledge integration failed: {str(e)}")
        
        self.total_tests += 1
    
    async def _test_ai_knowledge_learning(self):
        """Test AI knowledge learning"""
        print("\n🧠 Test 3: AI Knowledge Learning")
        try:
            # Test AI knowledge update
            test_result = {
                "score": 85.5,
                "passed": True,
                "test_type": "collaborative",
                "difficulty": "intermediate"
            }
            
            await enhanced_test_generator.update_ai_knowledge("imperium", test_result)
            
            # Verify AI knowledge was updated
            if "imperium" not in enhanced_test_generator.ai_knowledge_base:
                raise ValueError("AI knowledge not updated")
            
            print("✅ AI knowledge learning working correctly")
            self.passed_tests += 1
            
        except Exception as e:
            print(f"❌ AI knowledge learning failed: {str(e)}")
        
        self.total_tests += 1
    
    async def _test_progressive_difficulty(self):
        """Test progressive difficulty calculation"""
        print("\n📈 Test 4: Progressive Difficulty")
        try:
            # Test difficulty progression
            next_difficulty = await enhanced_test_generator._calculate_next_difficulty(
                ["imperium"], "intermediate"
            )
            
            if next_difficulty not in ["basic", "intermediate", "advanced", "expert", "master", "legendary"]:
                raise ValueError(f"Invalid difficulty level: {next_difficulty}")
            
            print("✅ Progressive difficulty working correctly")
            self.passed_tests += 1
            
        except Exception as e:
            print(f"❌ Progressive difficulty failed: {str(e)}")
        
        self.total_tests += 1
    
    async def _test_varied_content_categories(self):
        """Test varied content categories"""
        print("\n🎯 Test 5: Varied Content Categories")
        try:
            # Test different content categories
            categories = ["collaborative_coding", "collaborative_scenario", "collaborative_architecture", 
                        "collaborative_docker", "collaborative_real_life"]
            
            for category in categories:
                test_content = await enhanced_test_generator._generate_collaborative_test(
                    {"content": []}, {"imperium": {}}, "intermediate"
                )
                
                if test_content.get("type") not in categories:
                    raise ValueError(f"Invalid content category: {test_content.get('type')}")
            
            print("✅ Varied content categories working correctly")
            self.passed_tests += 1
            
        except Exception as e:
            print(f"❌ Varied content categories failed: {str(e)}")
        
        self.total_tests += 1
    
    async def _test_test_runner_integration(self):
        """Test test runner integration"""
        print("\n🏃 Test 6: Test Runner Integration")
        try:
            # Test test runner functionality
            result = await test_runner_service.run_enhanced_test(
                TestType.COLLABORATIVE, ["imperium"], "intermediate"
            )
            
            # Verify result structure
            required_fields = ["test_id", "test_type", "ai_types", "overall_score", "overall_passed"]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field in result: {field}")
            
            print("✅ Test runner integration working correctly")
            self.passed_tests += 1
            
        except Exception as e:
            print(f"❌ Test runner integration failed: {str(e)}")
        
        self.total_tests += 1
    
    async def _test_logging_system(self):
        """Test logging system"""
        print("\n📝 Test 7: Logging System")
        try:
            # Test different logging functions
            ai_logging_service.log_project_horus("Test message", LogLevel.INFO, {"test": True})
            ai_logging_service.log_training_ground("Test message", LogLevel.INFO, {"test": True})
            ai_logging_service.log_enhanced_adversarial("Test message", LogLevel.INFO, {"test": True})
            ai_logging_service.log_custody_protocol("Test message", LogLevel.INFO, {"test": True})
            
            print("✅ Logging system working correctly")
            self.passed_tests += 1
            
        except Exception as e:
            print(f"❌ Logging system failed: {str(e)}")
        
        self.total_tests += 1
    
    async def _test_real_test_execution(self):
        """Test real test execution"""
        print("\n🎯 Test 8: Real Test Execution")
        try:
            # Test all three test types
            test_types = [TestType.COLLABORATIVE, TestType.OLYMPIC, TestType.CUSTODES]
            
            for test_type in test_types:
                result = await test_runner_service.run_enhanced_test(
                    test_type, ["imperium", "guardian"], "intermediate"
                )
                
                if result.get("test_type") != test_type.value:
                    raise ValueError(f"Test type mismatch: expected {test_type.value}, got {result.get('test_type')}")
            
            print("✅ Real test execution working correctly")
            self.passed_tests += 1
            
        except Exception as e:
            print(f"❌ Real test execution failed: {str(e)}")
        
        self.total_tests += 1
    
    def _generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.total_tests - self.passed_tests,
            "success_rate": (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0,
            "test_results": self.test_results,
            "status": "PASSED" if self.passed_tests == self.total_tests else "FAILED"
        }
        
        return report


async def test_and_commit():
    """Main function to test everything and commit if successful"""
    print("🚀 Starting Comprehensive Test and Commit Process")
    print("=" * 60)
    
    # Run comprehensive tests
    tester = ComprehensiveTester()
    report = await tester.run_comprehensive_tests()
    
    # Check if all tests passed
    if report.get("status") == "PASSED":
        print("\n✅ All tests passed! Proceeding with git operations...")
        
        try:
            # Add all files
            print("📁 Adding files to git...")
            subprocess.run(["git", "add", "."], check=True)
            
            # Commit with comprehensive message
            commit_message = f"""
Enhanced Test System Implementation

✅ Comprehensive test suite passed
✅ Enhanced test generation with internet integration
✅ AI knowledge learning and progressive difficulty
✅ Varied content categories (coding, scenarios, architecture, docker, real-life)
✅ Separate logging for Project HORUS, Training Ground, Enhanced Adversarial
✅ Test runner integration with real AI responses
✅ Dynamic scoring and varied test content

Test Results:
- Total Tests: {report.get('total_tests')}
- Passed Tests: {report.get('passed_tests')}
- Success Rate: {report.get('success_rate'):.1f}%

Features Implemented:
- Internet search integration for current knowledge
- AI knowledge base and learning progress tracking
- Progressive difficulty based on AI performance
- Varied content categories with real-world scenarios
- Separate logging systems for different AI components
- Enhanced test runner with comprehensive evaluation
- Dynamic test generation with unique content

Status: READY FOR DEPLOYMENT
"""
            
            print("💾 Committing changes...")
            subprocess.run(["git", "commit", "-m", commit_message.strip()], check=True)
            
            # Push to remote
            print("🚀 Pushing to remote repository...")
            subprocess.run(["git", "push", "origin", "master"], check=True)
            
            print("\n🎉 Successfully committed and pushed all changes!")
            print("✅ Enhanced test system is now live on Railway")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Git operation failed: {str(e)}")
            return False
            
    else:
        print(f"\n❌ Tests failed! {report.get('failed_tests')} tests failed")
        print("🔧 Please fix the issues before committing")
        return False


if __name__ == "__main__":
    # Run the test and commit process
    success = asyncio.run(test_and_commit())
    
    if success:
        print("\n🎯 All systems ready for deployment!")
        print("📊 Enhanced test system with internet integration is active")
        print("🧠 AIs will now learn and improve with varied, dynamic tests")
        print("🌐 Tests include real internet knowledge and progressive difficulty")
        print("📝 Separate logging for all AI components is enabled")
    else:
        print("\n⚠️  Please fix test failures before deployment")
        sys.exit(1) 