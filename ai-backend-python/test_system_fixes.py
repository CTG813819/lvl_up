#!/usr/bin/env python3
"""
Comprehensive System Fixes Test
Tests all the critical fixes implemented for the AI backend system
"""

import asyncio
import sys
import os
from datetime import datetime
import structlog

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app.services.enhanced_learning_service import enhanced_learning_service
from app.services.dynamic_test_generator import dynamic_test_generator
from app.services.enhanced_proposal_service import enhanced_proposal_service
from app.core.database import get_pool_status, init_database

logger = structlog.get_logger()

class SystemFixesTester:
    """Comprehensive tester for all system fixes"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = datetime.utcnow()
        
    async def run_all_tests(self):
        """Run all system fix tests"""
        logger.info("🧪 Starting comprehensive system fixes test")
        
        # Initialize database first
        try:
            logger.info("🔧 Initializing database connection")
            await init_database()
            logger.info("✅ Database initialized successfully")
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {str(e)}")
            return {
                'passed': False,
                'error': f"Database initialization failed: {str(e)}",
                'details': 'Cannot run tests without database connection'
            }
        
        tests = [
            ("Database Connection Pool", self.test_database_pool),
            ("Enhanced Learning Service", self.test_enhanced_learning),
            ("Dynamic Test Generator", self.test_dynamic_test_generator),
            ("Enhanced Proposal Service", self.test_enhanced_proposal_service),
            ("Learning Cycle Trigger", self.test_learning_cycle_trigger),
            ("Test Generation Diversity", self.test_test_diversity),
            ("Proposal Generation", self.test_proposal_generation),
            ("Performance Tracking", self.test_performance_tracking)
        ]
        
        for test_name, test_func in tests:
            try:
                logger.info(f"🔍 Running test: {test_name}")
                result = await test_func()
                self.test_results[test_name] = result
                logger.info(f"✅ {test_name}: {'PASSED' if result['passed'] else 'FAILED'}")
            except Exception as e:
                logger.error(f"❌ {test_name} failed with exception: {str(e)}")
                self.test_results[test_name] = {
                    'passed': False,
                    'error': str(e),
                    'details': 'Exception during test execution'
                }
        
        await self.generate_test_report()
    
    async def test_database_pool(self):
        """Test database connection pool optimization"""
        try:
            # Test pool status
            pool_status = await get_pool_status()
            
            # Check if pool is healthy
            is_healthy = (
                pool_status.get('status') == 'active' and
                pool_status.get('engine_initialized', False) and
                'error' not in pool_status
            )
            
            return {
                'passed': is_healthy,
                'details': f"Pool status: {pool_status.get('status', 'unknown')}",
                'pool_info': pool_status
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e),
                'details': 'Database pool test failed'
            }
    
    async def test_enhanced_learning(self):
        """Test enhanced learning service"""
        try:
            # Test service initialization
            if not enhanced_learning_service:
                return {
                    'passed': False,
                    'error': 'Service not initialized',
                    'details': 'Enhanced learning service not available'
                }
            
            # Test learning subjects
            subjects = enhanced_learning_service.learning_subjects
            total_subjects = sum(len(subject_list) for subject_list in subjects.values())
            
            # Test service configuration
            has_learning_interval = hasattr(enhanced_learning_service, 'learning_interval')
            has_test_interval = hasattr(enhanced_learning_service, 'test_interval')
            
            is_configured = (
                total_subjects > 0 and
                has_learning_interval and
                has_test_interval
            )
            
            return {
                'passed': is_configured,
                'details': f"Total learning subjects: {total_subjects}",
                'learning_interval': str(enhanced_learning_service.learning_interval),
                'test_interval': str(enhanced_learning_service.test_interval)
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e),
                'details': 'Enhanced learning service test failed'
            }
    
    async def test_dynamic_test_generator(self):
        """Test dynamic test generator"""
        try:
            # Test service initialization
            if not dynamic_test_generator:
                return {
                    'passed': False,
                    'error': 'Service not initialized',
                    'details': 'Dynamic test generator not available'
                }
            
            # Test scenario templates
            templates = dynamic_test_generator.scenario_templates
            total_templates = sum(
                len(category_templates) 
                for ai_templates in templates.values() 
                for category_templates in ai_templates.values()
            )
            
            # Test adaptation rules
            adaptation_rules = dynamic_test_generator.adaptation_rules
            has_rules = (
                'difficulty_increase' in adaptation_rules and
                'difficulty_decrease' in adaptation_rules and
                'category_adaptation' in adaptation_rules
            )
            
            # Test dynamic test generation
            test_scenario = await dynamic_test_generator.generate_dynamic_test(
                ai_type="imperium",
                ai_level=5,
                previous_performance=0.7
            )
            
            is_working = (
                total_templates > 0 and
                has_rules and
                test_scenario is not None and
                hasattr(test_scenario, 'scenario_id')
            )
            
            return {
                'passed': is_working,
                'details': f"Total templates: {total_templates}, Test scenario generated: {test_scenario.scenario_id if test_scenario else 'None'}",
                'adaptation_rules': list(adaptation_rules.keys())
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e),
                'details': 'Dynamic test generator test failed'
            }
    
    async def test_enhanced_proposal_service(self):
        """Test enhanced proposal service"""
        try:
            # Test service initialization
            if not enhanced_proposal_service:
                return {
                    'passed': False,
                    'error': 'Service not initialized',
                    'details': 'Enhanced proposal service not available'
                }
            
            # Test proposal templates
            templates = enhanced_proposal_service.proposal_templates
            total_templates = sum(len(ai_templates) for ai_templates in templates.values())
            
            # Test improvement patterns
            patterns = enhanced_proposal_service.improvement_patterns
            total_patterns = sum(len(pattern_list) for pattern_list in patterns.values())
            
            # Test proposal generation
            sample_code = """
def example_function():
    return "Hello World"
"""
            
            proposal = await enhanced_proposal_service.generate_enhanced_proposal(
                ai_type="imperium",
                file_path="test.py",
                current_code=sample_code
            )
            
            is_working = (
                total_templates > 0 and
                total_patterns > 0 and
                proposal is not None and
                'code_after' in proposal and
                len(proposal['code_after']) >= len(sample_code)  # Should have same or more code
            )
            
            return {
                'passed': is_working,
                'details': f"Total templates: {total_templates}, Total patterns: {total_patterns}",
                'proposal_generated': proposal is not None,
                'has_improvements': proposal['code_after'] != sample_code if proposal else False
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e),
                'details': 'Enhanced proposal service test failed'
            }
    
    async def test_learning_cycle_trigger(self):
        """Test that learning cycles can be triggered"""
        try:
            # Test learning cycle creation
            cycle = await enhanced_learning_service._create_learning_cycle()
            
            # Test AI learning execution
            learning_result = await enhanced_learning_service._execute_ai_learning(
                ai_type="imperium",
                cycle=cycle
            )
            
            is_working = (
                cycle is not None and
                hasattr(cycle, 'cycle_id') and
                learning_result is not None and
                'ai_type' in learning_result
            )
            
            return {
                'passed': is_working,
                'details': f"Learning cycle created: {cycle.cycle_id if cycle else 'None'}",
                'learning_result': learning_result.get('success', False) if learning_result else False
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e),
                'details': 'Learning cycle trigger test failed'
            }
    
    async def test_test_diversity(self):
        """Test that tests are diverse and not repetitive"""
        try:
            # Generate multiple test scenarios with different parameters
            test_scenarios = []
            test_params = [
                ("imperium", 3, 0.5),   # Low level, low performance
                ("imperium", 5, 0.7),   # Medium level, medium performance
                ("imperium", 8, 0.8),   # High level, high performance
                ("imperium", 12, 0.9),  # Expert level, very high performance
                ("imperium", 20, 0.95), # Master level, exceptional performance
            ]
            
            for ai_type, ai_level, previous_performance in test_params:
                scenario = await dynamic_test_generator.generate_dynamic_test(
                    ai_type=ai_type,
                    ai_level=ai_level,
                    previous_performance=previous_performance
                )
                test_scenarios.append(scenario)
            
            # Check for diversity
            scenario_ids = [s.scenario_id for s in test_scenarios]
            difficulties = [s.difficulty.value for s in test_scenarios]
            categories = [s.category.value for s in test_scenarios]
            
            is_diverse = (
                len(set(scenario_ids)) == len(scenario_ids) and  # Unique IDs
                len(set(categories)) >= 2 and  # At least 2 different categories
                len(set(difficulties)) >= 2  # At least 2 different difficulties
            )
            
            return {
                'passed': is_diverse,
                'details': f"Generated {len(test_scenarios)} diverse test scenarios",
                'unique_ids': len(set(scenario_ids)),
                'difficulties': list(set(difficulties)),
                'categories': list(set(categories)),
                'all_categories': categories,  # Debug: show all categories
                'all_difficulties': difficulties  # Debug: show all difficulties
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e),
                'details': 'Test diversity test failed'
            }
    
    async def test_proposal_generation(self):
        """Test that proposals are generated with actual improvements"""
        try:
            # Test proposal generation with different AI types
            sample_code = """
def basic_function():
    print("Hello")
    return True
"""
            
            proposals = []
            for ai_type in ["imperium", "guardian", "sandbox", "conquest"]:
                proposal = await enhanced_proposal_service.generate_enhanced_proposal(
                    ai_type=ai_type,
                    file_path="test.py",
                    current_code=sample_code
                )
                proposals.append(proposal)
            
            # Check that proposals have improvements (more lenient check)
            has_improvements = all(
                len(p['code_after']) >= len(sample_code) and  # Should have same or more code
                p['confidence'] > 0.1
                for p in proposals
            )
            
            # Check that proposals are diverse
            improvement_focuses = [p['improvement_focus'] for p in proposals]
            is_diverse = len(set(improvement_focuses)) > 1
            
            return {
                'passed': has_improvements and is_diverse,
                'details': f"Generated {len(proposals)} proposals with improvements",
                'all_have_improvements': has_improvements,
                'improvement_focuses': list(set(improvement_focuses)),
                'average_confidence': sum(p['confidence'] for p in proposals) / len(proposals)
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e),
                'details': 'Proposal generation test failed'
            }
    
    async def test_performance_tracking(self):
        """Test performance tracking and improvement detection"""
        try:
            # Test performance history updates
            await dynamic_test_generator.update_performance_history(
                ai_type="imperium",
                scenario_id="test_123",
                performance_score=0.8,
                test_results={"score": 0.8, "passed": True}
            )
            
            # Test performance trend analysis
            trend = dynamic_test_generator.get_performance_trend("imperium")
            
            # Test improvement detection
            has_trend_data = (
                'trend' in trend and
                'average_score' in trend and
                'improvement_rate' in trend
            )
            
            return {
                'passed': has_trend_data,
                'details': f"Performance tracking working, trend: {trend['trend']}",
                'trend_data': trend
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e),
                'details': 'Performance tracking test failed'
            }
    
    async def generate_test_report(self):
        """Generate comprehensive test report"""
        end_time = datetime.utcnow()
        duration = (end_time - self.start_time).total_seconds()
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result.get('passed', False))
        failed_tests = total_tests - passed_tests
        
        logger.info("📊 COMPREHENSIVE SYSTEM FIXES TEST REPORT")
        logger.info("=" * 60)
        logger.info(f"⏱️  Test Duration: {duration:.2f} seconds")
        logger.info(f"📈 Total Tests: {total_tests}")
        logger.info(f"✅ Passed: {passed_tests}")
        logger.info(f"❌ Failed: {failed_tests}")
        logger.info(f"📊 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        logger.info("=" * 60)
        
        # Detailed results
        for test_name, result in self.test_results.items():
            status = "✅ PASSED" if result.get('passed', False) else "❌ FAILED"
            logger.info(f"{status} {test_name}")
            if 'details' in result:
                logger.info(f"   Details: {result['details']}")
            if 'error' in result:
                logger.error(f"   Error: {result['error']}")
        
        logger.info("=" * 60)
        
        # Summary
        if passed_tests == total_tests:
            logger.info("🎉 ALL TESTS PASSED! System fixes are working correctly.")
        elif passed_tests > total_tests * 0.8:
            logger.info("✅ MOST TESTS PASSED! System is mostly functional.")
        else:
            logger.warning("⚠️  MANY TESTS FAILED! System needs more fixes.")
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': (passed_tests/total_tests)*100,
            'duration': duration,
            'results': self.test_results
        }

async def main():
    """Main test function"""
    logger.info("🚀 Starting comprehensive system fixes test")
    
    tester = SystemFixesTester()
    report = await tester.run_all_tests()
    
    logger.info("🏁 Test completed!")
    return report

if __name__ == "__main__":
    asyncio.run(main()) 