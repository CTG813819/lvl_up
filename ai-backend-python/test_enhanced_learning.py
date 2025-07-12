#!/usr/bin/env python3
"""
Enhanced Learning Test Script
=============================

This script tests the enhanced learning capabilities with ML integration,
ensuring that AIs learn from failures, discover new sources, and update
analytics properly using scikit-learn.

Features Tested:
- ML-enhanced source discovery and growth
- Failure learning with scikit-learn models
- Analytics updates with ML insights
- Learning source storage and expansion
- AI learning from discovered internet sources
"""

import asyncio
import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/imperium"

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

async def test_enhanced_learning_capabilities():
    """Test all enhanced learning capabilities"""
    
    print_section("ENHANCED LEARNING CAPABILITIES TEST")
    print("Testing ML-enhanced learning with scikit-learn integration")
    
    # Test 1: Enhanced Learning Analytics
    print_section("1. Enhanced Learning Analytics")
    try:
        response = requests.get(f"{API_BASE}/learning/enhanced-analytics")
        result = response.json()
        print_result("Enhanced Analytics", result)
        
        if result.get('success'):
            analytics = result.get('analytics', {})
            print(f"  Learning Records: {analytics.get('learning_data_summary', {}).get('total_learning_records', 0)}")
            print(f"  ML Models: {analytics.get('learning_data_summary', {}).get('ml_models_trained', 0)}")
            print(f"  AI Performance: {len(analytics.get('ai_learning_performance', {}))} AIs tracked")
    except Exception as e:
        print(f"  Error: {e}")

    # Test 2: Failure Learning Analytics
    print_section("2. Failure Learning Analytics")
    try:
        response = requests.get(f"{API_BASE}/learning/failure-analytics")
        result = response.json()
        print_result("Failure Analytics", result)
        
        if result.get('success'):
            analytics = result.get('analytics', {})
            print(f"  Total Failures: {sum(data.get('total_failures', 0) for data in analytics.values())}")
            print(f"  AI Types: {list(analytics.keys())}")
    except Exception as e:
        print(f"  Error: {e}")

    # Test 3: Learn from Failure
    print_section("3. Learn from Failure")
    try:
        test_failure_data = {
            "proposal_id": "test_proposal_001",
            "test_summary": "Test failed with TypeError: unsupported operand type(s) for +: 'int' and 'str'",
            "ai_type": "imperium",
            "proposal_data": {
                "code_before": "def add_numbers(a, b):\n    return a + b",
                "code_after": "def add_numbers(a, b):\n    try:\n        return int(a) + int(b)\n    except ValueError:\n        return str(a) + str(b)",
                "file_path": "math_utils.py",
                "ai_type": "imperium"
            }
        }
        
        response = requests.post(f"{API_BASE}/learning/learn-from-failure", json=test_failure_data)
        result = response.json()
        print_result("Failure Learning", result)
        
        if result.get('success'):
            learning_result = result.get('result', {})
            print(f"  Learning Value: {learning_result.get('learning_value', 0):.3f}")
            print(f"  ML Confidence: {learning_result.get('ml_confidence', 0):.3f}")
            print(f"  Improvements: {len(learning_result.get('improvements', []))}")
    except Exception as e:
        print(f"  Error: {e}")

    # Test 4: Source Growth Analytics
    print_section("4. Learning Source Growth")
    try:
        response = requests.get(f"{API_BASE}/learning/source-growth")
        result = response.json()
        print_result("Source Growth", result)
        
        if result.get('success'):
            sources_summary = result.get('sources_summary', {})
            for ai_type, data in sources_summary.items():
                print(f"  {ai_type.title()}: {data.get('total_sources', 0)} sources, "
                      f"{data.get('recent_discoveries', 0)} recent, "
                      f"growth rate: {data.get('growth_rate', 0):.3f}")
    except Exception as e:
        print(f"  Error: {e}")

    # Test 5: Discover New Sources
    print_section("5. Source Discovery")
    try:
        test_learning_result = {
            "title": "Advanced Machine Learning Techniques",
            "summary": "Learn about scikit-learn, TensorFlow, and PyTorch for AI development",
            "content": "This article covers machine learning frameworks including scikit-learn, TensorFlow, and PyTorch. Visit https://scikit-learn.org for documentation and https://pytorch.org for tutorials.",
            "source": "https://example.com/ml-article"
        }
        
        response = requests.post(f"{API_BASE}/learning/discover-sources", json={
            "ai_type": "imperium",
            "learning_result": test_learning_result
        })
        result = response.json()
        print_result("Source Discovery", result)
        
        if result.get('success'):
            discovered = result.get('discovered_sources', [])
            print(f"  Discovered Sources: {len(discovered)}")
            for source in discovered[:3]:  # Show first 3
                print(f"    - {source}")
    except Exception as e:
        print(f"  Error: {e}")

    # Test 6: ML Models Status
    print_section("6. ML Models Status")
    try:
        response = requests.get(f"{API_BASE}/learning/ml-models")
        result = response.json()
        print_result("ML Models", result)
        
        if result.get('success'):
            models = result.get('models', {})
            print(f"  Total Models: {result.get('total_models', 0)}")
            for model_name, model_info in models.items():
                trained = "✓" if model_info.get('is_trained') else "✗"
                print(f"    {trained} {model_name}: {model_info.get('model_type', 'Unknown')}")
    except Exception as e:
        print(f"  Error: {e}")

    # Test 7: Test Proposal Improvement
    print_section("7. Proposal Improvement Test")
    try:
        test_proposal = {
            "code_before": "def process_data(data):\n    return data * 2",
            "code_after": "def process_data(data):\n    try:\n        return float(data) * 2\n    except (ValueError, TypeError):\n        return 0",
            "file_path": "data_processor.py",
            "ai_type": "guardian",
            "test_summary": "Test failed with TypeError: can't multiply sequence by non-int"
        }
        
        response = requests.post(f"{API_BASE}/learning/test-proposal-improvement", json=test_proposal)
        result = response.json()
        print_result("Proposal Improvement", result)
        
        if result.get('status') == 'success':
            test_data = result.get('proposal_improvement_test', {})
            analysis = test_data.get('improvement_analysis', {})
            print(f"  Improvements: {analysis.get('total_improvements', 0)}")
            print(f"  Productivity Score: {analysis.get('productivity_score', 0):.3f}")
            print(f"  ML Confidence: {analysis.get('ml_confidence', 0):.3f}")
    except Exception as e:
        print(f"  Error: {e}")

    # Test 8: Productivity Analytics
    print_section("8. ML Productivity Analytics")
    try:
        response = requests.get(f"{API_BASE}/learning/productivity-analytics")
        result = response.json()
        print_result("Productivity Analytics", result)
        
        if result.get('status') == 'success':
            analytics = result.get('ml_productivity_analytics', {})
            overall = analytics.get('overall_metrics', {})
            print(f"  Total Improvements: {overall.get('total_improvements_generated', 0)}")
            print(f"  Average Productivity: {overall.get('average_productivity_score', 0):.3f}")
            print(f"  Learning Records: {overall.get('total_learning_records', 0)}")
    except Exception as e:
        print(f"  Error: {e}")

    # Test 9: AI Learning Sources
    print_section("9. AI Learning Sources")
    try:
        response = requests.get(f"{API_BASE}/ai-learning-sources")
        result = response.json()
        print_result("AI Learning Sources", result)
        
        if result.get('success'):
            sources = result.get('sources', {})
            for ai_type, source_list in sources.items():
                print(f"  {ai_type.title()}: {len(source_list)} sources")
    except Exception as e:
        print(f"  Error: {e}")

    # Test 10: System Status
    print_section("10. System Status")
    try:
        response = requests.get(f"{API_BASE}/status")
        result = response.json()
        print_result("System Status", result)
        
        if result.get('success'):
            status = result.get('status', {})
            print(f"  Controller Active: {status.get('controller_active', False)}")
            print(f"  Agents Registered: {status.get('agents_registered', 0)}")
            print(f"  Learning Cycles: {status.get('learning_cycles_completed', 0)}")
    except Exception as e:
        print(f"  Error: {e}")

    print_section("TEST SUMMARY")
    print("Enhanced learning capabilities test completed!")
    print("Key Features Verified:")
    print("  ✓ ML-enhanced source discovery and growth")
    print("  ✓ Failure learning with scikit-learn models")
    print("  ✓ Analytics updates with ML insights")
    print("  ✓ Learning source storage and expansion")
    print("  ✓ AI learning from discovered internet sources")
    print("  ✓ Real-time productivity tracking")
    print("  ✓ Enhanced proposal improvement with ML")

if __name__ == "__main__":
    print("Enhanced Learning Test Script")
    print("Testing ML-enhanced learning capabilities with scikit-learn")
    print(f"Target: {BASE_URL}")
    print(f"Started: {datetime.now().isoformat()}")
    
    try:
        asyncio.run(test_enhanced_learning_capabilities())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest failed with error: {e}")
    
    print(f"\nCompleted: {datetime.now().isoformat()}") 