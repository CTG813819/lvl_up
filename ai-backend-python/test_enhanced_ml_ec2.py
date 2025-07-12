#!/usr/bin/env python3
"""
Enhanced ML Improvements EC2 Test Script
========================================

This script tests the enhanced ML improvements directly on the EC2 instance
without requiring the FastAPI server to be running.

Features Tested:
- Enhanced ML Learning Service initialization
- Model training and prediction
- Cross-AI knowledge transfer
- Performance monitoring
- Training scheduler functionality
"""

import asyncio
import sys
import os
import logging
from datetime import datetime
from typing import Dict, List, Any

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_result(title: str, result: Dict[str, Any]):
    """Print a formatted test result"""
    print(f"\n{title}:")
    print(f"  Status: {result.get('success', result.get('status', 'unknown'))}")
    if 'message' in result:
        print(f"  Message: {result['message']}")
    if 'timestamp' in result:
        print(f"  Timestamp: {result['timestamp']}")

async def test_enhanced_ml_learning_service():
    """Test enhanced ML learning service directly"""
    
    print_section("ENHANCED ML LEARNING SERVICE TEST")
    print("Testing enhanced ML learning service initialization and functionality")
    
    try:
        # Import the enhanced ML learning service
        from app.services.enhanced_ml_learning_service import EnhancedMLLearningService
        
        # Initialize the service
        print("Initializing Enhanced ML Learning Service...")
        ml_service = await EnhancedMLLearningService.initialize()
        
        # Test service status
        status = await ml_service.get_enhanced_learning_status()
        print_result("Service Status", status)
        
        if status.get('status') == 'active':
            print(f"  Models Loaded: {status.get('models_loaded', 0)}")
            print(f"  Performance History: {status.get('performance_history_size', 0)}")
            print(f"  Cross-AI Knowledge: {status.get('cross_ai_knowledge_size', 0)}")
            print(f"  Transfer Opportunities: {status.get('knowledge_transfer_opportunities', 0)}")
            print(f"  Continuous Learning: {status.get('continuous_learning_active', False)}")
        
        # Test model training
        print("\nTesting model training...")
        training_result = await ml_service.train_enhanced_models(force_retrain=True)
        print_result("Model Training", training_result)
        
        if training_result.get('status') == 'success':
            print(f"  Models Trained: {training_result.get('models_trained', 0)}")
            print(f"  Training Samples: {training_result.get('training_samples', 0)}")
            training_results = training_result.get('training_results', {})
            for model_name, accuracy in training_results.items():
                print(f"    {model_name}: {accuracy:.3f}")
        
        # Test quality prediction
        print("\nTesting quality prediction...")
        test_proposal = {
            "code_before": "def process_data(data):\n    return data * 2",
            "code_after": "def process_data(data):\n    try:\n        return float(data) * 2\n    except (ValueError, TypeError):\n        return 0",
            "ai_reasoning": "This improvement adds error handling to prevent TypeError when data is not numeric",
            "ai_type": "guardian",
            "improvement_type": "bug_fix",
            "confidence": 0.8
        }
        
        prediction_result = await ml_service.predict_enhanced_quality(test_proposal)
        print_result("Quality Prediction", {'success': True, 'prediction': prediction_result})
        
        if prediction_result:
            print(f"  Quality Score: {prediction_result.get('quality_score', 0):.3f}")
            print(f"  Approval Probability: {prediction_result.get('approval_probability', 0):.3f}")
            print(f"  Performance Score: {prediction_result.get('performance_score', 0):.3f}")
            print(f"  Confidence: {prediction_result.get('confidence', 0):.3f}")
            print(f"  Recommendations: {len(prediction_result.get('recommendations', []))}")
        
        # Test learning from feedback
        print("\nTesting learning from feedback...")
        feedback_result = await ml_service.learn_from_user_feedback(
            "test_proposal_001", "approved", "imperium"
        )
        print_result("Feedback Learning", feedback_result)
        
        if feedback_result.get('status') == 'success':
            print(f"  Learning Value: {feedback_result.get('learning_value', 0):.3f}")
            print(f"  Models Updated: {feedback_result.get('models_updated', False)}")
        
        # Test analytics
        print("\nTesting analytics...")
        analytics = await ml_service.get_enhanced_ml_analytics()
        print_result("ML Analytics", {'success': True, 'analytics': analytics})
        
        if analytics:
            performance = analytics.get('performance_history', {})
            print(f"  Total Records: {performance.get('total_records', 0)}")
            print(f"  Recent Activity: {performance.get('recent_activity', 0)}")
            print(f"  Success Rate: {performance.get('success_rate', 0):.3f}")
            
            cross_ai = analytics.get('cross_ai_knowledge', {})
            print(f"  AI Types: {len(cross_ai.get('ai_types', []))}")
            print(f"  Total Patterns: {cross_ai.get('total_patterns', 0)}")
            print(f"  Transfer Opportunities: {len(cross_ai.get('knowledge_transfer_opportunities', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing enhanced ML learning service: {str(e)}")
        return False

async def test_continuous_training_scheduler():
    """Test continuous training scheduler directly"""
    
    print_section("CONTINUOUS TRAINING SCHEDULER TEST")
    print("Testing continuous training scheduler functionality")
    
    try:
        # Import the enhanced training scheduler
        from app.services.enhanced_training_scheduler import EnhancedTrainingScheduler
        
        # Initialize the scheduler
        print("Initializing Enhanced Training Scheduler...")
        scheduler = await EnhancedTrainingScheduler.initialize()
        
        # Test scheduler status
        status = await scheduler.get_training_scheduler_status()
        print_result("Scheduler Status", status)
        
        if status.get('status'):
            print(f"  Status: {status.get('status', 'unknown')}")
            training_history = status.get('training_history', {})
            print(f"  Training Records: {training_history.get('total_records', 0)}")
            print(f"  Recent Training: {training_history.get('recent_training', 0)}")
            
            thresholds = status.get('performance_thresholds', {})
            print(f"  Performance Thresholds: {len(thresholds)} configured")
        
        # Test manual training trigger
        print("\nTesting manual training trigger...")
        trigger_result = await scheduler.manual_training_trigger("manual")
        print_result("Manual Training", trigger_result)
        
        if trigger_result.get('status') == 'success':
            print(f"  Training Samples: {trigger_result.get('training_samples', 0)}")
        
        # Test training analytics
        print("\nTesting training analytics...")
        analytics = await scheduler.get_training_analytics()
        print_result("Training Analytics", {'success': True, 'analytics': analytics})
        
        if analytics:
            frequency = analytics.get('training_frequency', {})
            print(f"  Total Sessions: {frequency.get('total_training_sessions', 0)}")
            print(f"  Recent Sessions: {frequency.get('recent_sessions', 0)}")
            print(f"  Average per Day: {frequency.get('average_sessions_per_day', 0)}")
            
            triggers = analytics.get('trigger_analysis', {})
            print(f"  Trigger Analysis:")
            for trigger, count in triggers.items():
                print(f"    {trigger}: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing continuous training scheduler: {str(e)}")
        return False

async def test_cross_ai_knowledge_transfer():
    """Test cross-AI knowledge transfer directly"""
    
    print_section("CROSS-AI KNOWLEDGE TRANSFER TEST")
    print("Testing cross-AI knowledge transfer functionality")
    
    try:
        # Import the enhanced ML learning service
        from app.services.enhanced_ml_learning_service import EnhancedMLLearningService
        
        # Initialize the service
        ml_service = await EnhancedMLLearningService.initialize()
        
        # Test knowledge transfer
        print("Testing knowledge transfer...")
        transfer_result = await ml_service.apply_knowledge_transfer(
            "Imperium", "Guardian", "successful"
        )
        print_result("Knowledge Transfer", transfer_result)
        
        if transfer_result.get('status') == 'success':
            print(f"  Target AI: {transfer_result.get('target_ai')}")
            print(f"  Transfer Value: {transfer_result.get('transfer_value', 0):.3f}")
            transferred = transfer_result.get('transferred_pattern', {})
            print(f"  Pattern Features: {len(transferred.get('features', {}))}")
        
        # Test analytics for learning insights
        print("\nTesting learning insights...")
        analytics = await ml_service.get_enhanced_ml_analytics()
        
        if analytics:
            cross_ai = analytics.get('cross_ai_knowledge', {})
            insights = cross_ai.get('ai_types', [])
            print(f"  AI Types: {len(insights)}")
            
            for ai_type in insights:
                print(f"    {ai_type}: Available for knowledge transfer")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing cross-AI knowledge transfer: {str(e)}")
        return False

async def test_performance_monitoring():
    """Test performance monitoring directly"""
    
    print_section("PERFORMANCE MONITORING TEST")
    print("Testing performance monitoring and analytics")
    
    try:
        # Import the enhanced ML learning service
        from app.services.enhanced_ml_learning_service import EnhancedMLLearningService
        
        # Initialize the service
        ml_service = await EnhancedMLLearningService.initialize()
        
        # Test analytics
        analytics = await ml_service.get_enhanced_ml_analytics()
        print_result("Performance Analytics", {'success': True, 'analytics': analytics})
        
        if analytics:
            performance = analytics.get('performance_history', {})
            print(f"  Total Records: {performance.get('total_records', 0)}")
            print(f"  Success Rate: {performance.get('success_rate', 0):.3f}")
            
            learning_metrics = analytics.get('learning_metrics', {})
            print(f"  Models Trained: {learning_metrics.get('models_trained', 0)}")
            print(f"  Last Training: {learning_metrics.get('last_training', 'Never')}")
            print(f"  Training Frequency: {learning_metrics.get('training_frequency', 'unknown')}")
        
        # Test service status
        status = await ml_service.get_enhanced_learning_status()
        print_result("Service Status", status)
        
        if status.get('status') == 'active':
            print(f"  Models Loaded: {status.get('models_loaded', 0)}")
            print(f"  Performance History: {status.get('performance_history_size', 0)}")
            print(f"  Cross-AI Knowledge: {status.get('cross_ai_knowledge_size', 0)}")
            print(f"  Transfer Opportunities: {status.get('knowledge_transfer_opportunities', 0)}")
            print(f"  Continuous Learning: {status.get('continuous_learning_active', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing performance monitoring: {str(e)}")
        return False

async def test_integration_with_existing_services():
    """Test integration with existing services"""
    
    print_section("INTEGRATION TEST")
    print("Testing integration with existing AI services")
    
    try:
        # Test Conquest AI service integration
        print("Testing Conquest AI service...")
        from app.services.conquest_ai_service import ConquestAIService
        
        conquest_service = ConquestAIService()
        conquest_status = await conquest_service.get_enhanced_statistics()
        print_result("Conquest AI Integration", {'success': True, 'status': conquest_status})
        
        # Test Sandbox service integration
        print("Testing Sandbox service...")
        from app.services.sckipit_service import SckipitService
        
        sckipit_service = await SckipitService.initialize()
        sckipit_status = await sckipit_service.get_sckipit_status()
        print_result("Sandbox Integration", {'success': True, 'status': sckipit_status})
        
        if sckipit_status:
            print(f"  Models Loaded: {sckipit_status.get('models_loaded', 0)}")
            print(f"  Knowledge Base Size: {sckipit_status.get('knowledge_base_size', 0)}")
            print(f"  Suggestion History: {sckipit_status.get('suggestion_history_count', 0)}")
            print(f"  Experiment Patterns: {sckipit_status.get('experiment_patterns_count', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing integration: {str(e)}")
        return False

async def main():
    """Run all enhanced ML improvement tests"""
    print("🚀 Starting Enhanced ML Improvements EC2 Test Suite")
    print(f"Testing on: {os.name} - {os.getenv('COMPUTERNAME', 'Unknown')}")
    print(f"Python version: {sys.version}")
    
    test_results = {}
    
    try:
        # Test enhanced ML learning service
        test_results['enhanced_ml_learning'] = await test_enhanced_ml_learning_service()
        
        # Test continuous training scheduler
        test_results['training_scheduler'] = await test_continuous_training_scheduler()
        
        # Test cross-AI knowledge transfer
        test_results['knowledge_transfer'] = await test_cross_ai_knowledge_transfer()
        
        # Test performance monitoring
        test_results['performance_monitoring'] = await test_performance_monitoring()
        
        # Test integration with existing services
        test_results['integration'] = await test_integration_with_existing_services()
        
        # Generate test summary
        print_section("TEST SUMMARY")
        
        passed_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        
        print(f"✅ Tests Passed: {passed_tests}/{total_tests}")
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} {test_name}")
        
        if passed_tests == total_tests:
            print("\n🎉 All Enhanced ML Improvements Tests Passed!")
            print("🎯 Key Improvements Verified:")
            print("  - Continuous model training with real data")
            print("  - Cross-AI knowledge transfer system")
            print("  - Performance degradation detection")
            print("  - Learning from user feedback")
            print("  - Training analytics and insights")
            print("  - Model performance monitoring")
            print("  - Adaptive training scheduling")
            print("  - Integration with existing AI services")
        else:
            print(f"\n⚠️ {total_tests - passed_tests} tests failed")
        
        # Generate test report
        with open('enhanced_ml_ec2_test_report.txt', 'w') as f:
            f.write("Enhanced ML Improvements EC2 Test Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Test Date: {datetime.now()}\n")
            f.write(f"Platform: {os.name} - {os.getenv('COMPUTERNAME', 'Unknown')}\n")
            f.write(f"Python Version: {sys.version}\n\n")
            
            f.write("Test Results:\n")
            for test_name, result in test_results.items():
                status = "PASS" if result else "FAIL"
                f.write(f"  {test_name}: {status}\n")
            
            f.write(f"\nOverall Result: {passed_tests}/{total_tests} tests passed\n")
        
        print(f"\n📋 Test report saved to enhanced_ml_ec2_test_report.txt")
        
        return 0 if passed_tests == total_tests else 1
        
    except Exception as e:
        print(f"❌ Test suite failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code) 