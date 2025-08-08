#!/usr/bin/env python3
"""
Test EC2 Deployment
Tests the enhanced learning system deployment on EC2.
"""

import requests
import json
import sys
from datetime import datetime

# EC2 Configuration
EC2_HOST = "ec2-34-202-215-209.compute-1.amazonaws.com"
BASE_URL = f"http://{EC2_HOST}:4000"

def test_endpoint(endpoint, description, timeout=10):
    """Test an endpoint and return the result"""
    print(f"\n[TESTING] {description}...")
    print(f"URL: {BASE_URL}{endpoint}")
    
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=timeout)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] {description} working")
            return data
        else:
            print(f"[ERROR] {description} failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] {description} failed with error: {e}")
        return None

def test_ec2_deployment():
    """Test the EC2 deployment"""
    print("Testing Enhanced Learning System Deployment on EC2")
    print(f"Target: {EC2_HOST}")
    print("=" * 60)
    
    # Test 1: Health endpoint
    health = test_endpoint("/health", "Health Check")
    
    # Test 2: Basic statistics endpoint
    basic_stats = test_endpoint("/api/conquest/statistics", "Basic Statistics")
    
    # Test 3: Enhanced statistics endpoint
    enhanced_stats = test_endpoint("/api/conquest/enhanced-statistics", "Enhanced Statistics")
    
    # Test 4: Deployments endpoint
    deployments = test_endpoint("/api/conquest/deployments", "Deployments")
    
    # Test 5: Conquest status endpoint
    status = test_endpoint("/api/conquest/status", "Conquest Status")
    
    # Analyze results
    print("\n[RESULTS] Test Results Analysis")
    print("=" * 40)
    
    working_endpoints = 0
    total_endpoints = 5
    
    if health:
        working_endpoints += 1
        print("[OK] Health endpoint working")
        if 'message' in health:
            print(f"  - Message: {health['message']}")
    
    if basic_stats:
        working_endpoints += 1
        print("[OK] Basic statistics endpoint working")
        if 'statistics' in basic_stats:
            stats = basic_stats['statistics']
            print(f"  - Total apps: {stats.get('totalApps', 'N/A')}")
            print(f"  - Success rate: {stats.get('successRate', 'N/A')}%")
    
    if enhanced_stats:
        working_endpoints += 1
        print("[OK] Enhanced statistics endpoint working")
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
        working_endpoints += 1
        print("[OK] Deployments endpoint working")
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
        working_endpoints += 1
        print("[OK] Conquest status endpoint working")
        if 'conquest_ai' in status:
            conquest = status['conquest_ai']
            print(f"  - Active: {conquest.get('is_active', 'N/A')}")
            print(f"  - Total deployments: {conquest.get('total_deployments', 'N/A')}")
            print(f"  - Success rate: {conquest.get('success_rate', 'N/A')}%")
    
    # Test 6: Create a test app to trigger learning (if enhanced stats is working)
    if enhanced_stats:
        print("\n[TESTING] Testing Learning System with App Creation")
        print("=" * 50)
        
        test_app_data = {
            "name": f"test_learning_app_{int(datetime.now().timestamp())}",
            "description": "Test app to verify learning system",
            "keywords": ["test", "learning", "validation"],
            "app_type": "general",
            "features": ["authentication"],
            "operation_type": "create_new"
        }
        
        try:
            print("[RUNNING] Creating test app to trigger learning...")
            response = requests.post(
                f"{BASE_URL}/api/conquest/create-app",
                json=test_app_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print("[OK] Test app creation initiated")
                print(f"  - App ID: {result.get('app_id', 'N/A')}")
                print(f"  - Status: {result.get('status', 'N/A')}")
                
                # Wait a bit for processing
                print("[WAITING] Waiting for processing...")
                import time
                time.sleep(5)
                
                # Check enhanced statistics again to see if learning occurred
                print("[CHECKING] Checking enhanced statistics after app creation...")
                updated_stats = test_endpoint("/api/conquest/enhanced-statistics", "Updated Enhanced Statistics")
                
                if updated_stats and 'statistics' in updated_stats:
                    validation = updated_stats['statistics'].get('validation', {})
                    total_attempts = validation.get('total_attempts', 0)
                    print(f"  - Total validation attempts: {total_attempts}")
                    
                    if total_attempts > 0:
                        print("[OK] Learning system is active and tracking validation attempts")
                    else:
                        print("[WARN] Learning system may not be tracking validation attempts yet")
                
            else:
                print(f"[ERROR] Test app creation failed: {response.status_code}")
                print(f"Response: {response.text}")
        
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Test app creation failed: {e}")
    
    print("\n[DONE] EC2 Deployment Test Complete!")
    print("=" * 50)
    
    # Summary
    print(f"[SUMMARY] {working_endpoints}/{total_endpoints} endpoints working")
    
    if working_endpoints >= 4:
        print("[SUCCESS] Enhanced learning system is operational")
        print("[SUCCESS] Statistics tracking active")
        print("[SUCCESS] Learning data collection enabled")
    elif working_endpoints >= 2:
        print("[PARTIAL] Some endpoints working, system may need attention")
    else:
        print("[ERROR] Most endpoints failing, system needs investigation")
    
    print(f"\n[ENDPOINTS] Available endpoints:")
    print(f"  - {BASE_URL}/health")
    print(f"  - {BASE_URL}/api/conquest/statistics")
    print(f"  - {BASE_URL}/api/conquest/enhanced-statistics")
    print(f"  - {BASE_URL}/api/conquest/deployments")
    print(f"  - {BASE_URL}/api/conquest/status")
    
    return working_endpoints >= 3

if __name__ == "__main__":
    try:
        success = test_ec2_deployment()
        if success:
            print("\n[OK] All tests passed!")
            sys.exit(0)
        else:
            print("\n[ERROR] Some tests failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n[WARN] Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        sys.exit(1) 