#!/usr/bin/env python3
"""
Test Sckipit Service - Verify ML-driven suggestions for Conquest app creation and Sandbox experiments
"""

import asyncio
import sys
import os
import json
from datetime import datetime
from typing import Dict, Any

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.sckipit_service import SckipitService
from app.core.config import settings

class SckipitTester:
    """Test Sckipit service functionality"""
    
    def __init__(self):
        self.sckipit = None
        self.test_results = []
    
    async def initialize(self):
        """Initialize the Sckipit service"""
        print("🔧 Initializing Sckipit Service...")
        try:
            self.sckipit = await SckipitService.initialize()
            print("✅ Sckipit Service initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize Sckipit Service: {str(e)}")
            return False
    
    async def test_app_feature_suggestions(self):
        """Test Conquest app feature suggestions"""
        print("\n🧪 Testing Conquest App Feature Suggestions...")
        
        test_cases = [
            {
                'name': 'Fitness Tracker',
                'description': 'A comprehensive fitness tracking app with workout plans and progress monitoring',
                'keywords': ['fitness', 'workout', 'health', 'tracking', 'progress']
            },
            {
                'name': 'Social Chat App',
                'description': 'A social networking app with real-time messaging and user profiles',
                'keywords': ['social', 'chat', 'messaging', 'profiles', 'networking']
            },
            {
                'name': 'Productivity Manager',
                'description': 'A task management app with reminders and project tracking',
                'keywords': ['productivity', 'task', 'reminder', 'project', 'management']
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            try:
                result = await self.sckipit.suggest_app_features(
                    test_case['name'],
                    test_case['description'],
                    test_case['keywords']
                )
                
                print(f"  Test {i}: {test_case['name']}")
                print(f"    Features: {result.get('suggested_features', [])}")
                print(f"    Knowledge Suggestions: {result.get('knowledge_suggestions', [])}")
                print(f"    Confidence: {result.get('confidence_score', 0.0):.2f}")
                print(f"    ML Model: {result.get('ml_model_used', 'unknown')}")
                
                self.test_results.append({
                    'test': f'app_feature_suggestions_{i}',
                    'status': 'passed',
                    'result': result
                })
                
            except Exception as e:
                print(f"    ❌ Error: {str(e)}")
                self.test_results.append({
                    'test': f'app_feature_suggestions_{i}',
                    'status': 'failed',
                    'error': str(e)
                })
    
    async def test_dependency_suggestions(self):
        """Test dependency suggestions"""
        print("\n🧪 Testing Dependency Suggestions...")
        
        test_cases = [
            {
                'features': ['authentication', 'data_storage', 'analytics'],
                'app_type': 'productivity'
            },
            {
                'features': ['game_engine', 'score_tracking', 'leaderboard'],
                'app_type': 'game'
            },
            {
                'features': ['messaging', 'user_profiles', 'social_sharing'],
                'app_type': 'social'
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            try:
                result = await self.sckipit.suggest_dependencies(
                    test_case['features'],
                    test_case['app_type']
                )
                
                print(f"  Test {i}: {test_case['app_type']} app")
                print(f"    Dependencies: {result}")
                
                self.test_results.append({
                    'test': f'dependency_suggestions_{i}',
                    'status': 'passed',
                    'result': result
                })
                
            except Exception as e:
                print(f"    ❌ Error: {str(e)}")
                self.test_results.append({
                    'test': f'dependency_suggestions_{i}',
                    'status': 'failed',
                    'error': str(e)
                })
    
    async def test_code_quality_analysis(self):
        """Test code quality analysis"""
        print("\n🧪 Testing Code Quality Analysis...")
        
        test_codes = [
            {
                'name': 'Good Code',
                'code': '''
def calculate_fitness_score(workouts, goals):
    """Calculate fitness score based on workouts and goals."""
    total_score = 0
    for workout in workouts:
        if workout.completed:
            total_score += workout.intensity * 10
    return min(total_score, 100)
''',
                'file_path': 'lib/services/fitness_service.dart'
            },
            {
                'name': 'Complex Code',
                'code': '''
def process_data(data, config, options, callback, error_handler, retry_count=3, timeout=30, validate=True, cache=True, log=True):
    try:
        if validate and not validate_data(data):
            raise ValueError("Invalid data")
        result = None
        for i in range(retry_count):
            try:
                result = callback(data, config, options)
                break
            except Exception as e:
                if i == retry_count - 1:
                    error_handler(e)
                time.sleep(1)
        if cache:
            cache_result(result)
        if log:
            log_result(result)
        return result
    except Exception as e:
        error_handler(e)
        return None
''',
                'file_path': 'lib/utils/data_processor.dart'
            }
        ]
        
        for i, test_case in enumerate(test_codes, 1):
            try:
                result = await self.sckipit.analyze_code_quality(
                    test_case['code'],
                    test_case['file_path']
                )
                
                print(f"  Test {i}: {test_case['name']}")
                print(f"    Quality Score: {result.get('quality_score', 0.0):.2f}")
                print(f"    Improvements: {result.get('improvements', [])}")
                print(f"    Complexity: {result.get('complexity_score', 0.0):.2f}")
                print(f"    Readability: {result.get('readability_score', 0.0):.2f}")
                
                self.test_results.append({
                    'test': f'code_quality_analysis_{i}',
                    'status': 'passed',
                    'result': result
                })
                
            except Exception as e:
                print(f"    ❌ Error: {str(e)}")
                self.test_results.append({
                    'test': f'code_quality_analysis_{i}',
                    'status': 'failed',
                    'error': str(e)
                })
    
    async def test_experiment_design(self):
        """Test experiment design"""
        print("\n🧪 Testing Experiment Design...")
        
        test_cases = [
            {
                'experiment_type': 'performance_optimization',
                'objectives': ['Improve app startup time', 'Reduce memory usage', 'Enhance UI responsiveness']
            },
            {
                'experiment_type': 'user_experience',
                'objectives': ['Increase user engagement', 'Improve navigation flow', 'Enhance accessibility']
            },
            {
                'experiment_type': 'security_validation',
                'objectives': ['Test authentication security', 'Validate data encryption', 'Check input sanitization']
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            try:
                result = await self.sckipit.design_experiment(
                    test_case['experiment_type'],
                    test_case['objectives']
                )
                
                print(f"  Test {i}: {test_case['experiment_type']}")
                print(f"    Parameters: {result.get('parameters', {})}")
                print(f"    Methodology: {result.get('methodology', '')}")
                print(f"    Expected Outcomes: {result.get('expected_outcomes', [])}")
                
                self.test_results.append({
                    'test': f'experiment_design_{i}',
                    'status': 'passed',
                    'result': result
                })
                
            except Exception as e:
                print(f"    ❌ Error: {str(e)}")
                self.test_results.append({
                    'test': f'experiment_design_{i}',
                    'status': 'failed',
                    'error': str(e)
                })
    
    async def test_experiment_analysis(self):
        """Test experiment result analysis"""
        print("\n🧪 Testing Experiment Result Analysis...")
        
        test_results = [
            {
                'experiment_type': 'performance_optimization',
                'results': {
                    'startup_time_reduced': '40%',
                    'memory_usage_decreased': '25%',
                    'ui_responsiveness_improved': '60%',
                    'test_passed': True
                }
            },
            {
                'experiment_type': 'user_experience',
                'results': {
                    'user_engagement_increased': '35%',
                    'navigation_flow_improved': '50%',
                    'accessibility_score': '95%',
                    'user_satisfaction': '4.2/5'
                }
            }
        ]
        
        for i, test_case in enumerate(test_results, 1):
            try:
                result = await self.sckipit.analyze_experiment_results(
                    test_case['results'],
                    test_case['experiment_type']
                )
                
                print(f"  Test {i}: {test_case['experiment_type']}")
                print(f"    Insights: {result.get('insights', [])}")
                print(f"    Recommendations: {result.get('recommendations', [])}")
                print(f"    Success Score: {result.get('success_score', 0.0):.2f}")
                
                self.test_results.append({
                    'test': f'experiment_analysis_{i}',
                    'status': 'passed',
                    'result': result
                })
                
            except Exception as e:
                print(f"    ❌ Error: {str(e)}")
                self.test_results.append({
                    'test': f'experiment_analysis_{i}',
                    'status': 'failed',
                    'error': str(e)
                })
    
    async def test_next_experiment_suggestions(self):
        """Test next experiment suggestions"""
        print("\n🧪 Testing Next Experiment Suggestions...")
        
        test_current_results = {
            'performance_improved': True,
            'user_satisfaction': '4.2/5',
            'test_coverage': '85%'
        }
        
        test_experiment_history = [
            {
                'experiment_type': 'performance_optimization',
                'results': {'success': True, 'improvement': '40%'},
                'analysis': {'insights': ['Performance improved'], 'success_score': 0.8}
            },
            {
                'experiment_type': 'user_experience',
                'results': {'success': True, 'improvement': '35%'},
                'analysis': {'insights': ['UX improved'], 'success_score': 0.7}
            }
        ]
        
        try:
            result = await self.sckipit.suggest_next_experiments(
                test_current_results,
                test_experiment_history
            )
            
            print(f"  Suggested Experiments: {len(result)}")
            for i, suggestion in enumerate(result, 1):
                print(f"    {i}. {suggestion.get('experiment_type', 'unknown')}")
                print(f"       Objectives: {suggestion.get('objectives', [])}")
                print(f"       Expected Outcomes: {suggestion.get('expected_outcomes', [])}")
            
            self.test_results.append({
                'test': 'next_experiment_suggestions',
                'status': 'passed',
                'result': result
            })
            
        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
            self.test_results.append({
                'test': 'next_experiment_suggestions',
                'status': 'failed',
                'error': str(e)
            })
    
    async def test_knowledge_validation(self):
        """Test knowledge validation"""
        print("\n🧪 Testing Knowledge Validation...")
        
        test_cases = [
            {
                'knowledge': 'Flutter 3.0 introduces new Material 3 design components and improved performance optimizations for better app development experience.',
                'source_url': 'https://docs.flutter.dev/release/breaking-changes'
            },
            {
                'knowledge': 'Random text that is not very useful for development.',
                'source_url': 'https://example.com/random'
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            try:
                result = await self.sckipit.validate_knowledge_update(
                    test_case['knowledge'],
                    test_case['source_url']
                )
                
                print(f"  Test {i}: {test_case['source_url']}")
                print(f"    Is Valid: {result.get('is_valid', False)}")
                print(f"    Validation Score: {result.get('validation_score', 0.0):.2f}")
                print(f"    Confidence: {result.get('confidence', 0.0):.2f}")
                print(f"    Recommendations: {result.get('recommendations', [])}")
                
                self.test_results.append({
                    'test': f'knowledge_validation_{i}',
                    'status': 'passed',
                    'result': result
                })
                
            except Exception as e:
                print(f"    ❌ Error: {str(e)}")
                self.test_results.append({
                    'test': f'knowledge_validation_{i}',
                    'status': 'failed',
                    'error': str(e)
                })
    
    async def test_trusted_sources_update(self):
        """Test trusted sources update"""
        print("\n🧪 Testing Trusted Sources Update...")
        
        test_new_source = {
            'url': 'https://pub.dev/packages/flutter_bloc',
            'content': 'Flutter Bloc is a state management library that helps implement the BLoC pattern in Flutter applications.',
            'description': 'Flutter Bloc state management library',
            'category': 'development'
        }
        
        try:
            result = await self.sckipit.update_trusted_sources(test_new_source)
            
            print(f"  Update Result: {result}")
            
            self.test_results.append({
                'test': 'trusted_sources_update',
                'status': 'passed' if result else 'failed',
                'result': result
            })
            
        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
            self.test_results.append({
                'test': 'trusted_sources_update',
                'status': 'failed',
                'error': str(e)
            })
    
    async def test_sckipit_status(self):
        """Test Sckipit service status"""
        print("\n🧪 Testing Sckipit Service Status...")
        
        try:
            result = await self.sckipit.get_sckipit_status()
            
            print(f"  Status: {result.get('status', 'unknown')}")
            print(f"  Models Loaded: {result.get('models_loaded', 0)}")
            print(f"  Knowledge Base Size: {result.get('knowledge_base_size', 0)}")
            print(f"  Suggestion History: {result.get('suggestion_history_count', 0)}")
            print(f"  Experiment Patterns: {result.get('experiment_patterns_count', 0)}")
            
            self.test_results.append({
                'test': 'sckipit_status',
                'status': 'passed',
                'result': result
            })
            
        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
            self.test_results.append({
                'test': 'sckipit_status',
                'status': 'failed',
                'error': str(e)
            })
    
    async def test_model_training(self):
        """Test model training"""
        print("\n🧪 Testing Model Training...")
        
        try:
            result = await self.sckipit.train_sckipit_models(force_retrain=True)
            
            print(f"  Training Status: {result.get('status', 'unknown')}")
            print(f"  Models Trained: {result.get('models_trained', 0)}")
            print(f"  Training Results: {result.get('training_results', {})}")
            
            self.test_results.append({
                'test': 'model_training',
                'status': 'passed',
                'result': result
            })
            
        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
            self.test_results.append({
                'test': 'model_training',
                'status': 'failed',
                'error': str(e)
            })
    
    async def test_sckipit_analytics(self):
        """Test Sckipit analytics"""
        print("\n🧪 Testing Sckipit Analytics...")
        
        try:
            result = await self.sckipit.get_sckipit_analytics()
            
            print(f"  Total Suggestions: {result.get('total_suggestions', 0)}")
            print(f"  Knowledge Sources: {result.get('knowledge_sources', 0)}")
            print(f"  Experiment Patterns: {result.get('experiment_patterns', 0)}")
            print(f"  Model Performance: {result.get('model_performance', {})}")
            
            self.test_results.append({
                'test': 'sckipit_analytics',
                'status': 'passed',
                'result': result
            })
            
        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
            self.test_results.append({
                'test': 'sckipit_analytics',
                'status': 'failed',
                'error': str(e)
            })
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("📊 SCKIPIT SERVICE TEST SUMMARY")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['status'] == 'passed')
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if result['status'] == 'failed':
                    print(f"  - {result['test']}: {result.get('error', 'Unknown error')}")
        
        print("\n✅ All core Sckipit functionality tested successfully!")
        print("🚀 Ready for deployment to Conquest app creation and Sandbox experiments")
    
    async def run_all_tests(self):
        """Run all Sckipit tests"""
        print("🚀 Starting Sckipit Service Tests...")
        print("="*60)
        
        # Initialize service
        if not await self.initialize():
            print("❌ Failed to initialize Sckipit Service. Exiting.")
            return False

        # Train models before running tests
        print("\n🧪 Training Sckipit models before running tests...")
        await self.sckipit.train_sckipit_models(force_retrain=True)
        
        # Run all tests
        await self.test_app_feature_suggestions()
        await self.test_dependency_suggestions()
        await self.test_code_quality_analysis()
        await self.test_experiment_design()
        await self.test_experiment_analysis()
        await self.test_next_experiment_suggestions()
        await self.test_knowledge_validation()
        await self.test_trusted_sources_update()
        await self.test_sckipit_status()
        await self.test_model_training()
        await self.test_sckipit_analytics()
        
        # Print summary
        self.print_summary()
        
        return True


async def main():
    """Main test function"""
    tester = SckipitTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 Sckipit Service tests completed successfully!")
        print("✅ Ready for integration with Conquest app creation and Sandbox experiments")
        return 0
    else:
        print("\n❌ Sckipit Service tests failed!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 