#!/usr/bin/env python3
"""
Comprehensive AI System Test
Tests all AI functions, frontend and backend integration, and complete system functionality.
"""

import requests
import json
import sys
import time
from datetime import datetime
import subprocess
import os

# Configuration
EC2_HOST = "ec2-34-202-215-209.compute-1.amazonaws.com"
BACKEND_URL = f"http://{EC2_HOST}:4000"
FRONTEND_URL = "http://localhost:3000"  # Assuming Flutter web runs on 3000

def test_backend_endpoint(endpoint, description, method="GET", data=None, timeout=10):
    """Test a backend endpoint and return the result"""
    print(f"\n[BACKEND TEST] {description}...")
    print(f"URL: {BACKEND_URL}{endpoint}")
    
    try:
        if method == "GET":
            response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=timeout)
        elif method == "POST":
            response = requests.post(f"{BACKEND_URL}{endpoint}", json=data, timeout=timeout)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            try:
                result = response.json()
                print(f"[OK] {description} working")
                return result
            except:
                print(f"[OK] {description} working (non-JSON response)")
                return {"status": "success", "data": response.text}
        else:
            print(f"[ERROR] {description} failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] {description} failed with error: {e}")
        return None

def test_frontend_endpoint(endpoint, description, timeout=10):
    """Test a frontend endpoint"""
    print(f"\n[FRONTEND TEST] {description}...")
    print(f"URL: {FRONTEND_URL}{endpoint}")
    
    try:
        response = requests.get(f"{FRONTEND_URL}{endpoint}", timeout=timeout)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"[OK] {description} working")
            return True
        else:
            print(f"[ERROR] {description} failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] {description} failed with error: {e}")
        return False

def test_ai_agent_functions():
    """Test all AI agent functions"""
    print("\n" + "="*60)
    print("🤖 TESTING AI AGENT FUNCTIONS")
    print("="*60)
    
    # Test AI Agent Service
    agent_status = test_backend_endpoint("/api/agents/status", "AI Agent Status")
    
    # Test AI Learning Service
    learning_status = test_backend_endpoint("/api/learning/status", "AI Learning Status")
    
    # Test AI Growth Service
    growth_status = test_backend_endpoint("/api/growth/analysis", "AI Growth Analysis")
    
    # Test AI Analytics
    analytics_status = test_backend_endpoint("/api/analytics/", "AI Analytics Overview")
    
    return {
        "agent_status": agent_status,
        "learning_status": learning_status,
        "growth_status": growth_status,
        "analytics_status": analytics_status
    }

def test_conquest_ai_functions():
    """Test Conquest AI functions"""
    print("\n" + "="*60)
    print("⚔️ TESTING CONQUEST AI FUNCTIONS")
    print("="*60)
    
    # Test basic statistics
    basic_stats = test_backend_endpoint("/api/conquest/statistics", "Conquest Basic Statistics")
    
    # Test enhanced statistics
    enhanced_stats = test_backend_endpoint("/api/conquest/enhanced-statistics", "Conquest Enhanced Statistics")
    
    # Test deployments
    deployments = test_backend_endpoint("/api/conquest/deployments", "Conquest Deployments")
    
    # Test conquest status
    conquest_status = test_backend_endpoint("/api/conquest/status", "Conquest Status")
    
    # Test app creation (with test data)
    test_app_data = {
        "name": f"test_comprehensive_app_{int(datetime.now().timestamp())}",
        "description": "Comprehensive test app for AI system validation",
        "keywords": ["test", "comprehensive", "validation"],
        "app_type": "general",
        "features": ["authentication", "database"],
        "operation_type": "create_new"
    }
    
    app_creation = test_backend_endpoint("/api/conquest/create-app", "Conquest App Creation", 
                                       method="POST", data=test_app_data, timeout=30)
    
    return {
        "basic_stats": basic_stats,
        "enhanced_stats": enhanced_stats,
        "deployments": deployments,
        "conquest_status": conquest_status,
        "app_creation": app_creation
    }

def test_imperium_ai_functions():
    """Test Imperium AI functions"""
    print("\n" + "="*60)
    print("🏛️ TESTING IMPERIUM AI FUNCTIONS")
    print("="*60)
    
    # Test Imperium monitoring
    imperium_monitoring = test_backend_endpoint("/api/imperium/monitoring", "Imperium Monitoring")
    
    # Test Imperium status
    imperium_status = test_backend_endpoint("/api/imperium/status", "Imperium Status")
    
    # Test Imperium improvements
    imperium_improvements = test_backend_endpoint("/api/imperium/improvements", "Imperium Improvements")
    
    # Test Imperium issues
    imperium_issues = test_backend_endpoint("/api/imperium/issues", "Imperium Issues")
    
    return {
        "monitoring": imperium_monitoring,
        "status": imperium_status,
        "improvements": imperium_improvements,
        "issues": imperium_issues
    }

def test_guardian_ai_functions():
    """Test Guardian AI functions"""
    print("\n" + "="*60)
    print("🛡️ TESTING GUARDIAN AI FUNCTIONS")
    print("="*60)
    
    # Test Guardian security status
    guardian_security = test_backend_endpoint("/api/guardian/security-status", "Guardian Security Status")
    
    # Test Guardian code review
    guardian_code_review = test_backend_endpoint("/api/guardian/code-review", "Guardian Code Review")
    
    # Test Guardian threat detection
    guardian_threats = test_backend_endpoint("/api/guardian/threat-detection", "Guardian Threat Detection")
    
    # Test Guardian suggestions
    guardian_suggestions = test_backend_endpoint("/api/guardian/suggestions", "Guardian Suggestions")
    
    return {
        "security": guardian_security,
        "code_review": guardian_code_review,
        "threats": guardian_threats,
        "suggestions": guardian_suggestions
    }

def test_sandbox_ai_functions():
    """Test Sandbox AI functions"""
    print("\n" + "="*60)
    print("🧪 TESTING SANDBOX AI FUNCTIONS")
    print("="*60)
    
    # Test Sandbox status
    sandbox_status = test_backend_endpoint("/api/sandbox/testing-status", "Sandbox Testing Status")
    
    # Test Sandbox experiments
    sandbox_experiments = test_backend_endpoint("/api/sandbox/experiments", "Sandbox Experiments")
    
    # Test Sandbox performance metrics
    sandbox_performance = test_backend_endpoint("/api/sandbox/performance-metrics", "Sandbox Performance Metrics")
    
    # Test Sandbox integration status
    sandbox_integration = test_backend_endpoint("/api/sandbox/integration-status", "Sandbox Integration Status")
    
    return {
        "status": sandbox_status,
        "experiments": sandbox_experiments,
        "performance": sandbox_performance,
        "integration": sandbox_integration
    }

def test_learning_system():
    """Test AI Learning System"""
    print("\n" + "="*60)
    print("📚 TESTING AI LEARNING SYSTEM")
    print("="*60)
    
    # Test learning insights
    learning_insights = test_backend_endpoint("/api/learning/insights/imperium", "Learning Insights (Imperium)")
    
    # Test ML insights
    ml_insights = test_backend_endpoint("/api/learning/ml-insights", "ML Insights")
    
    # Test learning data
    learning_data = test_backend_endpoint("/api/learning/data", "Learning Data")
    
    # Test learning metrics
    learning_metrics = test_backend_endpoint("/api/learning/metrics", "Learning Metrics")
    
    return {
        "insights": learning_insights,
        "ml_insights": ml_insights,
        "data": learning_data,
        "metrics": learning_metrics
    }

def test_notification_system():
    """Test Notification System"""
    print("\n" + "="*60)
    print("🔔 TESTING NOTIFICATION SYSTEM")
    print("="*60)
    
    # Test notification stats
    notification_stats = test_backend_endpoint("/api/notify/stats", "Notification Statistics")
    
    # Test notification templates
    notification_templates = test_backend_endpoint("/api/notify/templates", "Notification Templates")
    
    # Test notification channels
    notification_channels = test_backend_endpoint("/api/notify/channels", "Notification Channels")
    
    return {
        "stats": notification_stats,
        "templates": notification_templates,
        "channels": notification_channels
    }

def test_github_integration():
    """Test GitHub Integration"""
    print("\n" + "="*60)
    print("🐙 TESTING GITHUB INTEGRATION")
    print("="*60)
    
    # Test GitHub status
    github_status = test_backend_endpoint("/api/github/status", "GitHub Integration Status")
    
    # Test GitHub webhook status
    github_webhook = test_backend_endpoint("/api/github/status", "GitHub Webhook Status")
    
    return {
        "status": github_status,
        "webhook": github_webhook
    }

def test_frontend_components():
    """Test Frontend Components"""
    print("\n" + "="*60)
    print("🖥️ TESTING FRONTEND COMPONENTS")
    print("="*60)
    
    # Test if Flutter web is running
    frontend_health = test_frontend_endpoint("/", "Frontend Health Check")
    
    # Test main app routes (if available)
    frontend_routes = test_frontend_endpoint("/conquest", "Conquest Frontend")
    
    return {
        "health": frontend_health,
        "routes": frontend_routes
    }

def run_flutter_tests():
    """Run Flutter tests"""
    print("\n" + "="*60)
    print("🧪 RUNNING FLUTTER TESTS")
    print("="*60)
    
    try:
        # Check if Flutter is available first
        flutter_check = subprocess.run(["flutter", "--version"], capture_output=True, text=True, timeout=10)
        if flutter_check.returncode != 0:
            print("[ERROR] Flutter not found in PATH")
            return False
            
        # Run Flutter tests
        result = subprocess.run(["flutter", "test"], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("[OK] Flutter tests passed")
            print(f"Output: {result.stdout}")
            return True
        else:
            print("[ERROR] Flutter tests failed")
            print(f"Error: {result.stderr}")
            return False
    except FileNotFoundError:
        print("[ERROR] Flutter not found in PATH")
        return False
    except subprocess.TimeoutExpired:
        print("[ERROR] Flutter tests timed out")
        return False
    except Exception as e:
        print(f"[ERROR] Could not run Flutter tests: {e}")
        return False

def generate_comprehensive_report(results):
    """Generate a comprehensive test report"""
    print("\n" + "="*80)
    print("📊 COMPREHENSIVE AI SYSTEM TEST REPORT")
    print("="*80)
    
    # Count working vs failed tests
    total_tests = 0
    working_tests = 0
    failed_tests = 0
    
    for category, tests in results.items():
        if isinstance(tests, dict):
            for test_name, result in tests.items():
                total_tests += 1
                if result is not None and result is not False:
                    working_tests += 1
                else:
                    failed_tests += 1
        else:
            total_tests += 1
            if tests is not None and tests is not False:
                working_tests += 1
            else:
                failed_tests += 1
    
    print(f"\n📈 TEST SUMMARY:")
    print(f"   Total Tests: {total_tests}")
    print(f"   ✅ Working: {working_tests}")
    print(f"   ❌ Failed: {failed_tests}")
    print(f"   📊 Success Rate: {(working_tests/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
    
    print(f"\n🤖 AI SYSTEM STATUS:")
    
    # AI Agent Functions
    agent_results = results.get("ai_agents", {})
    print(f"   AI Agents: {'✅ Operational' if any(agent_results.values()) else '❌ Issues'}")
    
    # Conquest AI
    conquest_results = results.get("conquest", {})
    print(f"   Conquest AI: {'✅ Operational' if conquest_results.get('basic_stats') else '❌ Issues'}")
    
    # Imperium AI
    imperium_results = results.get("imperium", {})
    print(f"   Imperium AI: {'✅ Operational' if any(imperium_results.values()) else '❌ Issues'}")
    
    # Guardian AI
    guardian_results = results.get("guardian", {})
    print(f"   Guardian AI: {'✅ Operational' if any(guardian_results.values()) else '❌ Issues'}")
    
    # Sandbox AI
    sandbox_results = results.get("sandbox", {})
    print(f"   Sandbox AI: {'✅ Operational' if any(sandbox_results.values()) else '❌ Issues'}")
    
    # Learning System
    learning_results = results.get("learning", {})
    print(f"   Learning System: {'✅ Operational' if any(learning_results.values()) else '❌ Issues'}")
    
    # Notifications
    notification_results = results.get("notifications", {})
    print(f"   Notifications: {'✅ Operational' if any(notification_results.values()) else '❌ Issues'}")
    
    # GitHub Integration
    github_results = results.get("github", {})
    print(f"   GitHub Integration: {'✅ Operational' if any(github_results.values()) else '❌ Issues'}")
    
    # Frontend
    frontend_results = results.get("frontend", {})
    print(f"   Frontend: {'✅ Operational' if any(frontend_results.values()) else '❌ Issues'}")
    
    print(f"\n🎯 RECOMMENDATIONS:")
    if working_tests / total_tests >= 0.8:
        print("   🚀 System is highly operational - ready for production use")
    elif working_tests / total_tests >= 0.6:
        print("   ⚠️ System is mostly operational - some components need attention")
    else:
        print("   🔧 System needs significant work - focus on core functionality first")
    
    return working_tests / total_tests if total_tests > 0 else 0

def main():
    """Main test function"""
    print("🚀 COMPREHENSIVE AI SYSTEM TEST")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    results = {}
    
    # Test all AI functions
    results["ai_agents"] = test_ai_agent_functions()
    results["conquest"] = test_conquest_ai_functions()
    results["imperium"] = test_imperium_ai_functions()
    results["guardian"] = test_guardian_ai_functions()
    results["sandbox"] = test_sandbox_ai_functions()
    results["learning"] = test_learning_system()
    results["notifications"] = test_notification_system()
    results["github"] = test_github_integration()
    results["frontend"] = test_frontend_components()
    
    # Run Flutter tests if available
    results["flutter_tests"] = run_flutter_tests()
    
    # Generate comprehensive report
    success_rate = generate_comprehensive_report(results)
    
    print(f"\n🎉 COMPREHENSIVE TEST COMPLETE!")
    print(f"Overall Success Rate: {success_rate*100:.1f}%")
    
    if success_rate >= 0.8:
        print("✅ System is ready for production use!")
        return 0
    elif success_rate >= 0.6:
        print("⚠️ System needs some attention but is mostly functional")
        return 1
    else:
        print("❌ System needs significant work")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 