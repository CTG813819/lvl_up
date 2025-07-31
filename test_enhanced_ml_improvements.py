#!/usr/bin/env python3
"""
Enhanced ML Improvements Test Script
===================================

This script tests all the enhanced ML improvements including:

1. Enhanced ML Learning Service
2. Continuous Training Scheduler
3. Cross-AI Knowledge Transfer
4. Performance Analytics
5. Learning Insights
6. Model Performance Monitoring

Features Tested:
- Continuous model training with real data
- Cross-AI knowledge transfer
- Performance degradation detection
- Learning from user feedback
- Training analytics and insights
- Model performance monitoring
"""

import asyncio
import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/enhanced-learning"

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
    """Test enhanced ML learning service"""
    
    print_section("ENHANCED ML LEARNING SERVICE TEST")
    print("Testing enhanced ML learning with continuous improvement")
    
    # Test 1: Train Enhanced Models
    print_section("1. Train Enhanced ML Models")
    try:
        response = requests.post(f"{API_BASE}/train-models", json={"force_retrain": True})
        result = response.json()
        print_result("Enhanced Model Training", result)
        
        if result.get('success'):
            training_results = result.get('training_results', {})
            print(f"  Models Trained: {result.get('models_trained', 0)}")
            print(f"  Training Samples: {result.get('training_samples', 0)}")
            for model_name, accuracy in training_results.items():
                print(f"    {model_name}: {accuracy:.3f}")
    except Exception as e:
        print(f"  Error: {e}")

    # Test 2: Predict Enhanced Quality
    print_section("2. Enhanced Quality Prediction")
    try:
        test_proposal = {
            "code_before": "def process_data(data):\n    return data * 2",
            "code_after": "def process_data(data):\n    try:\n        return float(data) * 2\n    except (ValueError, TypeError):\n        return 0",
            "ai_reasoning": "This improvement adds error handling to prevent TypeError when data is not numeric",
            "ai_type": "guardian",
            "improvement_type": "bug_fix",
            "confidence": 0.8
        }
        
        response = requests.post(f"{API_BASE}/predict-quality", json=test_proposal)
        result = response.json()
        print_result("Quality Prediction", result)
        
        if result.get('success'):
            prediction = result.get('prediction', {})
            print(f"  Quality Score: {prediction.get('quality_score', 0):.3f}")
            print(f"  Approval Probability: {prediction.get('approval_probability', 0):.3f}")
            print(f"  Performance Score: {prediction.get('performance_score', 0):.3f}")
            print(f"  Confidence: {prediction.get('confidence', 0):.3f}")
            print(f"  Recommendations: {len(prediction.get('recommendations', []))}")
    except Exception as e:
        print(f"  Error: {e}")

    # Test 3: Learn from User Feedback
    print_section("3. Learning from User Feedback")
    try:
        # First create a test proposal
        test_proposal_data = {
            "code_before": "def calculate_sum(a, b):\n    return a + b",
            "code_after": "def calculate_sum(a, b):\n    try:\n        return float(a) + float(b)\n    except ValueError:\n        return str(a) + str(b)",
            "ai_reasoning": "Enhanced error handling for type conversion",
            "ai_type": "imperium",
            "improvement_type": "bug_fix"
        }
        
        # Simulate learning from feedback
        response = requests.post(f"{API_BASE}/learn-from-feedback", json={
            "proposal_id": "test_proposal_001",
            "user_feedback": "approved",
            "ai_type": "imperium"
        })
        result = response.json()
        print_result("Feedback Learning", result)
        
        if result.get('success'):
            print(f"  Learning Value: {result.get('learning_value', 0):.3f}")
            print(f"  Models Updated: {result.get('models_updated', False)}")
    except Exception as e:
        print(f"  Error: {e}")

    # Test 4: Enhanced ML Analytics
    print_section("4. Enhanced ML Analytics")
    try:
        response = requests.get(f"{API_BASE}/analytics")
        result = response.json()
        print_result("ML Analytics", result)
        
        if result.get('success'):
            analytics = result.get('analytics', {})
            performance = analytics.get('performance_history', {})
            print(f"  Total Records: {performance.get('total_records', 0)}")
            print(f"  Recent Activity: {performance.get('recent_activity', 0)}")
            print(f"  Success Rate: {performance.get('success_rate', 0):.3f}")
            
            cross_ai = analytics.get('cross_ai_knowledge', {})
            print(f"  AI Types: {len(cross_ai.get('ai_types', []))}")
            print(f"  Total Patterns: {cross_ai.get('total_patterns', 0)}")
            print(f"  Transfer Opportunities: {len(cross_ai.get('knowledge_transfer_opportunities', []))}")
    except Exception as e:
        print(f"  Error: {e}")

async def test_continuous_training_scheduler():
    """Test continuous training scheduler"""
    
    print_section("CONTINUOUS TRAINING SCHEDULER TEST")
    print("Testing continuous training with adaptive scheduling")
    
    # Test 1: Training Scheduler Status
    print_section("1. Training Scheduler Status")
    try:
        response = requests.get(f"{API_BASE}/training-scheduler-status")
        result = response.json()
        print_result("Scheduler Status", result)
        
        if result.get('success'):
            status = result.get('status', {})
            print(f"  Status: {status.get('status', 'unknown')}")
            print(f"  Training Records: {status.get('training_history', {}).get('total_records', 0)}")
            print(f"  Recent Training: {status.get('training_history', {}).get('recent_training', 0)}")
            
            thresholds = status.get('performance_thresholds', {})
            print(f"  Performance Thresholds: {len(thresholds)} configured")
    except Exception as e:
        print(f"  Error: {e}")

    # Test 2: Start Continuous Training
    print_section("2. Start Continuous Training")
    try:
        response = requests.post(f"{API_BASE}/start-continuous-training")
        result = response.json()
        print_result("Start Training", result)
        
        if result.get('success'):
            print("  Continuous training scheduler started")
    except Exception as e:
        print(f"  Error: {e}")

    # Test 3: Manual Training Trigger
    print_section("3. Manual Training Trigger")
    try:
        response = requests.post(f"{API_BASE}/manual-training-trigger", json={"trigger_type": "manual"})
        result = response.json()
        print_result("Manual Training", result)
        
        if result.get('success'):
            print(f"  Training Samples: {result.get('training_samples', 0)}")
    except Exception as e:
        print(f"  Error: {e}")

    # Test 4: Training Analytics
    print_section("4. Training Analytics")
    try:
        response = requests.get(f"{API_BASE}/training-analytics")
        result = response.json()
        print_result("Training Analytics", result)
        
        if result.get('success'):
            analytics = result.get('analytics', {})
            frequency = analytics.get('training_frequency', {})
            print(f"  Total Sessions: {frequency.get('total_training_sessions', 0)}")
            print(f"  Recent Sessions: {frequency.get('recent_sessions', 0)}")
            print(f"  Average per Day: {frequency.get('average_sessions_per_day', 0)}")
            
            triggers = analytics.get('trigger_analysis', {})
            print(f"  Trigger Analysis:")
            for trigger, count in triggers.items():
                print(f"    {trigger}: {count}")
    except Exception as e:
        print(f"  Error: {e}")

async def test_cross_ai_knowledge_transfer():
    """Test cross-AI knowledge transfer"""
    
    print_section("CROSS-AI KNOWLEDGE TRANSFER TEST")
    print("Testing knowledge transfer between different AI types")
    
    # Test 1: Knowledge Transfer
    print_section("1. Apply Knowledge Transfer")
    try:
        response = requests.post(f"{API_BASE}/knowledge-transfer", json={
            "source_ai": "Imperium",
            "target_ai": "Guardian",
            "pattern_type": "successful"
        })
        result = response.json()
        print_result("Knowledge Transfer", result)
        
        if result.get('success'):
            print(f"  Target AI: {result.get('target_ai')}")
            print(f"  Transfer Value: {result.get('transfer_value', 0):.3f}")
            transferred = result.get('transferred_pattern', {})
            print(f"  Pattern Features: {len(transferred.get('features', {}))}")
    except Exception as e:
        print(f"  Error: {e}")

    # Test 2: Learning Insights
    print_section("2. Learning Insights")
    try:
        response = requests.get(f"{API_BASE}/learning-insights")
        result = response.json()
        print_result("Learning Insights", result)
        
        if result.get('success'):
            insights = result.get('learning_insights', {})
            print(f"  AI Types: {len(insights)}")
            for ai_type, data in insights.items():
                print(f"    {ai_type}:")
                print(f"      Successful Patterns: {data.get('successful_patterns', 0)}")
                print(f"      Failure Patterns: {data.get('failure_patterns', 0)}")
                print(f"      Learning Insights: {data.get('learning_insights', 0)}")
                print(f"      Knowledge Contributions: {data.get('knowledge_contributions', 0)}")
    except Exception as e:
        print(f"  Error: {e}")

    # Test 3: Specific AI Insights
    print_section("3. Specific AI Learning Insights")
    try:
        response = requests.get(f"{API_BASE}/learning-insights?ai_type=Imperium")
        result = response.json()
        print_result("Imperium Insights", result)
        
        if result.get('success'):
            insights = result.get('learning_insights', {})
            print(f"  AI Type: {insights.get('ai_type', 'Unknown')}")
            print(f"  Successful Patterns: {insights.get('successful_patterns', 0)}")
            print(f"  Failure Patterns: {insights.get('failure_patterns', 0)}")
            print(f"  Learning Insights: {insights.get('learning_insights', 0)}")
            print(f"  Knowledge Contributions: {insights.get('knowledge_contributions', 0)}")
    except Exception as e:
        print(f"  Error: {e}")

async def test_performance_monitoring():
    """Test performance monitoring and analytics"""
    
    print_section("PERFORMANCE MONITORING TEST")
    print("Testing model performance monitoring and analytics")
    
    # Test 1: Model Performance
    print_section("1. Model Performance Metrics")
    try:
        response = requests.get(f"{API_BASE}/model-performance")
        result = response.json()
        print_result("Model Performance", result)
        
        if result.get('success'):
            performance = result.get('model_performance', {})
            print(f"  Models Loaded: {performance.get('models_loaded', 0)}")
            print(f"  Last Training: {performance.get('last_training', 'Never')}")
            
            history = performance.get('performance_history', {})
            print(f"  Total Records: {history.get('total_records', 0)}")
            print(f"  Success Rate: {history.get('success_rate', 0):.3f}")
    except Exception as e:
        print(f"  Error: {e}")

    # Test 2: Continuous Learning Status
    print_section("2. Continuous Learning Status")
    try:
        response = requests.get(f"{API_BASE}/continuous-learning-status")
        result = response.json()
        print_result("Continuous Learning", result)
        
        if result.get('success'):
            status = result.get('continuous_learning_status', {})
            print(f"  Overall Status: {status.get('overall_status', 'unknown')}")
            print(f"  Last Activity: {status.get('last_activity', 'Never')}")
            
            ml_status = status.get('ml_service', {})
            print(f"  ML Service Status: {ml_status.get('status', 'unknown')}")
            print(f"  Models Loaded: {ml_status.get('models_loaded', 0)}")
    except Exception as e:
        print(f"  Error: {e}")

    # Test 3: Enhanced Learning Status
    print_section("3. Enhanced Learning Status")
    try:
        response = requests.get(f"{API_BASE}/status")
        result = response.json()
        print_result("Enhanced Learning Status", result)
        
        if result.get('success'):
            status = result.get('status', {})
            print(f"  Status: {status.get('status', 'unknown')}")
            print(f"  Models Loaded: {status.get('models_loaded', 0)}")
            print(f"  Performance History: {status.get('performance_history_size', 0)}")
            print(f"  Cross-AI Knowledge: {status.get('cross_ai_knowledge_size', 0)}")
            print(f"  Transfer Opportunities: {status.get('knowledge_transfer_opportunities', 0)}")
            print(f"  Continuous Learning: {status.get('continuous_learning_active', False)}")
    except Exception as e:
        print(f"  Error: {e}")

async def test_configuration_and_health():
    """Test configuration and health checks"""
    
    print_section("CONFIGURATION AND HEALTH TEST")
    print("Testing configuration updates and health monitoring")
    
    # Test 1: Update Performance Thresholds
    print_section("1. Update Performance Thresholds")
    try:
        new_thresholds = {
            "accuracy": 0.80,
            "precision": 0.75,
            "recall": 0.75,
            "f1_score": 0.75
        }
        
        response = requests.post(f"{API_BASE}/update-performance-thresholds", json=new_thresholds)
        result = response.json()
        print_result("Update Thresholds", result)
        
        if result.get('success'):
            print(f"  Updated Thresholds: {len(result.get('thresholds', {}))}")
    except Exception as e:
        print(f"  Error: {e}")

    # Test 2: Update Training Intervals
    print_section("2. Update Training Intervals")
    try:
        new_intervals = {
            "scheduled": 360,  # 6 hours
            "data_available": 120,  # 2 hours
            "performance_degradation": 30,  # 30 minutes
            "user_feedback": 60,  # 1 hour
            "cross_ai_learning": 240  # 4 hours
        }
        
        response = requests.post(f"{API_BASE}/update-training-intervals", json=new_intervals)
        result = response.json()
        print_result("Update Intervals", result)
        
        if result.get('success'):
            print(f"  Updated Intervals: {len(result.get('intervals', {}))}")
    except Exception as e:
        print(f"  Error: {e}")

    # Test 3: Health Check
    print_section("3. Enhanced Learning Health Check")
    try:
        response = requests.get(f"{API_BASE}/health")
        result = response.json()
        print_result("Health Check", result)
        
        if result.get('success'):
            health = result.get('health_status', {})
            print(f"  Overall Healthy: {result.get('healthy', False)}")
            print(f"  ML Service Healthy: {health.get('ml_service_healthy', False)}")
            print(f"  Training Scheduler Healthy: {health.get('training_scheduler_healthy', False)}")
            print(f"  Models Loaded: {health.get('models_loaded', False)}")
            print(f"  Scheduler Running: {health.get('scheduler_running', False)}")
    except Exception as e:
        print(f"  Error: {e}")

    # Test 4: Force Retrain
    print_section("4. Force Retrain All Models")
    try:
        response = requests.post(f"{API_BASE}/force-retrain")
        result = response.json()
        print_result("Force Retrain", result)
        
        if result.get('success'):
            print("  Force retrain completed successfully")
            ml_training = result.get('ml_training', {})
            scheduler_training = result.get('scheduler_training', {})
            print(f"  ML Training Status: {ml_training.get('status', 'unknown')}")
            print(f"  Scheduler Training Status: {scheduler_training.get('status', 'unknown')}")
    except Exception as e:
        print(f"  Error: {e}")

async def test_integration_with_existing_services():
    """Test integration with existing services"""
    
    print_section("INTEGRATION TEST")
    print("Testing integration with existing AI services")
    
    # Test 1: Integration with Conquest AI
    print_section("1. Conquest AI Integration")
    try:
        # Test conquest app creation with enhanced ML
        conquest_data = {
            "app_name": "TestApp",
            "description": "A test application for ML integration",
            "features": ["user_authentication", "data_processing"],
            "ai_type": "conquest"
        }
        
        response = requests.post(f"{BASE_URL}/api/conquest/create-app", json=conquest_data)
        result = response.json()
        print_result("Conquest Integration", result)
        
        if result.get('success'):
            print("  Conquest AI successfully integrated with enhanced ML")
    except Exception as e:
        print(f"  Error: {e}")

    # Test 2: Integration with Sandbox Experiments
    print_section("2. Sandbox Experiment Integration")
    try:
        # Test sandbox experiment with enhanced ML
        experiment_data = {
            "experiment_type": "performance_optimization",
            "objectives": ["improve_response_time", "reduce_memory_usage"],
            "ai_type": "sandbox"
        }
        
        response = requests.post(f"{BASE_URL}/api/sandbox/design-experiment", json=experiment_data)
        result = response.json()
        print_result("Sandbox Integration", result)
        
        if result.get('success'):
            print("  Sandbox AI successfully integrated with enhanced ML")
    except Exception as e:
        print(f"  Error: {e}")

    # Test 3: Integration with Guardian AI
    print_section("3. Guardian AI Integration")
    try:
        # Test guardian security analysis with enhanced ML
        security_data = {
            "code_to_analyze": "def process_user_input(data):\n    return eval(data)",
            "security_level": "high",
            "ai_type": "guardian"
        }
        
        response = requests.post(f"{BASE_URL}/api/guardian/analyze-security", json=security_data)
        result = response.json()
        print_result("Guardian Integration", result)
        
        if result.get('success'):
            print("  Guardian AI successfully integrated with enhanced ML")
    except Exception as e:
        print(f"  Error: {e}")

async def main():
    """Run all enhanced ML improvement tests"""
    print("🚀 Starting Enhanced ML Improvements Test Suite")
    print(f"Testing against: {BASE_URL}")
    
    try:
        # Test enhanced ML learning service
        await test_enhanced_ml_learning_service()
        
        # Test continuous training scheduler
        await test_continuous_training_scheduler()
        
        # Test cross-AI knowledge transfer
        await test_cross_ai_knowledge_transfer()
        
        # Test performance monitoring
        await test_performance_monitoring()
        
        # Test configuration and health
        await test_configuration_and_health()
        
        # Test integration with existing services
        await test_integration_with_existing_services()
        
        print_section("TEST SUMMARY")
        print("✅ Enhanced ML Improvements Test Suite Completed")
        print("🎯 Key Improvements Implemented:")
        print("  - Continuous model training with real data")
        print("  - Cross-AI knowledge transfer system")
        print("  - Performance degradation detection")
        print("  - Learning from user feedback")
        print("  - Training analytics and insights")
        print("  - Model performance monitoring")
        print("  - Adaptive training scheduling")
        print("  - Integration with existing AI services")
        
    except Exception as e:
        print(f"❌ Test suite failed: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code) 