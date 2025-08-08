#!/usr/bin/env python3
"""
Comprehensive Railway Endpoint Test
Tests all major endpoints to ensure they're working correctly after deployment.
"""

import requests
import json
import time
from datetime import datetime
import sys

# Railway URL from your deployment
RAILWAY_URL = "https://lvlup-production.up.railway.app"

def test_endpoint(method, endpoint, data=None, expected_status=200, description=""):
    """Test a single endpoint"""
    url = f"{RAILWAY_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
            
        if response.status_code == expected_status:
            print(f"✅ {method} {endpoint} - {description}")
            return True
        else:
            print(f"❌ {method} {endpoint} - Expected {expected_status}, got {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {method} {endpoint} - Connection error: {str(e)}")
        return False

def main():
    """Test all major endpoints"""
    print("🚀 Railway Endpoint Comprehensive Test")
    print("=" * 60)
    print(f"Testing Railway URL: {RAILWAY_URL}")
    print(f"Test started at: {datetime.now()}")
    print("=" * 60)
    
    # List of endpoints to test
    tests = [
        # Health endpoints
        ("GET", "/ping", None, 200, "Basic ping health check"),
        ("GET", "/health", None, 200, "Main health check"),
        ("GET", "/api/health", None, 200, "API health check"),
        
        # Core API endpoints
        ("GET", "/api/proposals/", None, 200, "Proposals list"),
        ("GET", "/api/agents/status", None, 200, "Agent status"),
        ("GET", "/api/learning/insights", None, 200, "Learning insights"),
        ("GET", "/api/analytics/metrics", None, 200, "Analytics metrics"),
        
        # AI Service endpoints
        ("GET", "/api/ai/status", None, 200, "AI service status"),
        ("GET", "/api/project-horus/status", None, 200, "Project Horus status"),
        ("GET", "/api/project-warmaster/status", None, 200, "Project Warmaster status"),
        ("GET", "/api/custodes-ai/status", None, 200, "Custodes AI status"),
        ("GET", "/api/olympic-ai/status", None, 200, "Olympic AI status"),
        
        # System endpoints
        ("GET", "/api/system/status", None, 200, "System status"),
        ("GET", "/api/agent-metrics/leaderboard", None, 200, "Agent metrics leaderboard"),
        
        # Guardian and Security
        ("GET", "/api/guardian/status", None, 200, "Guardian system status"),
        ("GET", "/api/custody/status", None, 200, "Custody protocol status"),
        
        # Imperium and Learning
        ("GET", "/api/imperium/status", None, 200, "Imperium system status"),
        ("GET", "/api/learning/status", None, 200, "Learning system status"),
        
        # Additional services
        ("GET", "/api/conquest/status", None, 200, "Conquest system status"),
        ("GET", "/api/sandbox/status", None, 200, "Sandbox system status"),
        ("GET", "/api/codex/status", None, 200, "Codex system status"),
    ]
    
    # Run all tests
    passed = 0
    failed = 0
    
    for method, endpoint, data, expected_status, description in tests:
        if test_endpoint(method, endpoint, data, expected_status, description):
            passed += 1
        else:
            failed += 1
        time.sleep(0.5)  # Small delay between requests
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL ENDPOINTS WORKING PERFECTLY!")
        print("Your Railway deployment is fully functional!")
    elif failed < 5:
        print(f"\n⚠️  Most endpoints working, {failed} minor issues to investigate")
    else:
        print(f"\n🔧 Multiple endpoints need attention ({failed} failures)")
    
    print(f"\nTest completed at: {datetime.now()}")
    return failed == 0

if __name__ == "__main__":
    # First, try to detect the Railway URL automatically
    print("🔍 Attempting to detect Railway URL...")
    
    # You can also test locally first
    local_test = input("Test locally first? (y/n): ").lower().strip() == 'y'
    
    if local_test:
        test_url = "http://localhost:8000"
        print(f"Testing locally: {test_url}")
    else:
        railway_url = input("Enter your Railway app URL (or press Enter to use default): ").strip()
        test_url = railway_url if railway_url else RAILWAY_URL
        print(f"Testing Railway: {test_url}")
    
    # Update the global URL for testing
    global RAILWAY_URL
    RAILWAY_URL = test_url
    
    success = main()
    sys.exit(0 if success else 1)