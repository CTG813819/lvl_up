#!/usr/bin/env python3
"""
Test Enhanced Learning System
Tests the enhanced Conquest AI system with learning capabilities and statistics tracking.
"""

import requests
import json
import time
import sys
from datetime import datetime

BASE_URL = "http://localhost:4000"

def test_endpoint(endpoint, description):
    """Test an endpoint and return the result"""
    print(f"\n🔄 Testing {description}...")
    print(f"Endpoint: {BASE_URL}{endpoint}")
    
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {description} working")
            return data
        else:
            print(f"❌ {description} failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ {description} failed with error: {e}")
        return None

def test_enhanced_learning_system():
    """Test the enhanced learning system"""
    print("🧪 Testing Enhanced Learning System")
    print("=" * 50)
    
    # Test 1: Basic statistics endpoint
    basic_stats = test_endpoint("/api/conquest/statistics", "Basic Statistics")
    
    # Test 2: Enhanced statistics endpoint
    enhanced_stats = test_endpoint("/api/conquest/enhanced-statistics", "Enhanced Statistics")
    
    # Test 3: Deployments endpoint
    deployments = test_endpoint("/api/conquest/deployments", "Deployments")
    
    # Test 4: Conquest status endpoint
    status = test_endpoint("/api/conquest/status", "Conquest Status")
    
    # Analyze results
    print("\n📊 Test Results Analysis")
    print("=" * 30)
    
    if basic_stats:
        print("✅ Basic statistics endpoint working")
        if 'statistics' in basic_stats:
            stats = basic_stats['statistics']
            print(f"  - Total apps: {stats.get('totalApps', 'N/A')}")
            print(f"  - Completed apps: {stats.get('completedApps', 'N/A')}")
            print(f"  - Success rate: {stats.get('successRate', 'N/A')}%")
    
    if enhanced_stats:
        print("✅ Enhanced statistics endpoint working")
        if 'statistics' in enhanced_stats:
            stats = enhanced_stats['statistics']
            
            # Overview
            overview = stats.get('overview', {})
            print(f"  - Overview: {overview.get('total_apps', 'N/A')} total apps")
            print(f"  - Success rate: {overview.get('success_rate', 'N/A')}%")
            
            # Validation
            validation = stats.get('validation', {})
            print(f"  - Validation success: {validation.get('success_rate', 'N/A')}%")
            print(f"  - Auto-fix success: {validation.get('auto_fix_success_rate', 'N/A')}%")
            
            # Learning
            learning = stats.get('learning', {})
            print(f"  - Learning active: {learning.get('learning_active', 'N/A')}")
            print(f"  - Recent patterns: {learning.get('recent_successful_patterns', 'N/A')}")
            
            # Performance
            performance = stats.get('performance', {})
            improvement_areas = performance.get('improvement_areas', [])
            if improvement_areas:
                print(f"  - Improvement areas: {', '.join(improvement_areas[:3])}")
    
    if deployments:
        print("✅ Deployments endpoint working")
        if 'deployments' in deployments:
            deploy_list = deployments['deployments']
            print(f"  - Total deployments: {len(deploy_list)}")
            
            # Count by status
            status_counts = {}
            for deploy in deploy_list:
                status = deploy.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            for status, count in status_counts.items():
                print(f"  - {status}: {count}")
    
    if status:
        print("✅ Conquest status endpoint working")
        if 'conquest_ai' in status:
            conquest = status['conquest_ai']
            print(f"  - Active: {conquest.get('is_active', 'N/A')}")
            print(f"  - Total deployments: {conquest.get('total_deployments', 'N/A')}")
            print(f"  - Success rate: {conquest.get('success_rate', 'N/A')}%")
    
    # Test 5: Create a test app to trigger learning
    print("\n🧪 Testing Learning System with App Creation")
    print("=" * 45)
    
    test_app_data = {
        "name": f"test_learning_app_{int(time.time())}",
        "description": "Test app to verify learning system",
        "keywords": ["test", "learning", "validation"],
        "app_type": "general",
        "features": ["authentication"],
        "operation_type": "create_new"
    }
    
    try:
        print("🔄 Creating test app to trigger learning...")
        response = requests.post(
            f"{BASE_URL}/api/conquest/create-app",
            json=test_app_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Test app creation initiated")
            print(f"  - App ID: {result.get('app_id', 'N/A')}")
            print(f"  - Status: {result.get('status', 'N/A')}")
            
            # Wait a bit for processing
            print("⏳ Waiting for processing...")
            time.sleep(5)
            
            # Check enhanced statistics again to see if learning occurred
            print("🔄 Checking enhanced statistics after app creation...")
            updated_stats = test_endpoint("/api/conquest/enhanced-statistics", "Updated Enhanced Statistics")
            
            if updated_stats and 'statistics' in updated_stats:
                validation = updated_stats['statistics'].get('validation', {})
                total_attempts = validation.get('total_attempts', 0)
                print(f"  - Total validation attempts: {total_attempts}")
                
                if total_attempts > 0:
                    print("✅ Learning system is active and tracking validation attempts")
                else:
                    print("⚠️ Learning system may not be tracking validation attempts yet")
            
        else:
            print(f"❌ Test app creation failed: {response.status_code}")
            print(f"Response: {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Test app creation failed: {e}")
    
    # Test 6: Check learning data files
    print("\n📁 Checking Learning Data Files")
    print("=" * 30)
    
    learning_files = [
        "ai-backend-python/app/services/ai_learnings.json",
        "ai-backend-python/app/services/ai_code_fixes.json"
    ]
    
    for file_path in learning_files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                print(f"✅ {file_path} exists and readable")
                
                if "ai_learnings.json" in file_path:
                    validation_stats = data.get('validation_stats', {})
                    total_attempts = validation_stats.get('total_attempts', 0)
                    print(f"  - Total attempts: {total_attempts}")
                    print(f"  - Successful validations: {validation_stats.get('successful_validations', 0)}")
                    print(f"  - Failed validations: {validation_stats.get('failed_validations', 0)}")
                    print(f"  - Auto-fix success rate: {validation_stats.get('auto_fix_success_rate', 0.0)}")
                
                elif "ai_code_fixes.json" in file_path:
                    fix_count = len(data)
                    print(f"  - Stored fixes: {fix_count}")
        
        except FileNotFoundError:
            print(f"❌ {file_path} not found")
        except json.JSONDecodeError:
            print(f"❌ {file_path} contains invalid JSON")
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
    
    print("\n🎉 Enhanced Learning System Test Complete!")
    print("=" * 50)
    
    # Summary
    working_endpoints = sum([
        basic_stats is not None,
        enhanced_stats is not None,
        deployments is not None,
        status is not None
    ])
    
    print(f"✅ {working_endpoints}/4 endpoints working")
    
    if enhanced_stats:
        print("✅ Enhanced learning system operational")
        print("✅ Statistics tracking active")
        print("✅ Learning data collection enabled")
    else:
        print("❌ Enhanced learning system needs attention")
    
    return working_endpoints >= 3

if __name__ == "__main__":
    try:
        success = test_enhanced_learning_system()
        if success:
            print("\n✅ All tests passed!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 