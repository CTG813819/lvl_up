#!/usr/bin/env python3
"""
Quick Railway Endpoint Test
Tests key endpoints to verify Railway deployment is fully functional.
"""

import requests
import json
from datetime import datetime

# Your Railway URL
RAILWAY_URL = "https://lvlup-production.up.railway.app"

def test_endpoint(endpoint, description=""):
    """Test a single endpoint"""
    url = f"{RAILWAY_URL}{endpoint}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"✅ {endpoint} - {description}")
            return True
        elif response.status_code == 404:
            print(f"⚠️  {endpoint} - Not found (404) - {description}")
            return False
        else:
            print(f"❌ {endpoint} - Status {response.status_code} - {description}")
            return False
    except Exception as e:
        print(f"❌ {endpoint} - Error: {str(e)[:50]} - {description}")
        return False

def main():
    print("🚀 Quick Railway Endpoint Test")
    print("=" * 50)
    print(f"Testing: {RAILWAY_URL}")
    print(f"Time: {datetime.now()}")
    print("=" * 50)
    
    # Key endpoints to test
    endpoints = [
        ("/ping", "Basic health check"),
        ("/health", "Main health endpoint"),
        ("/api/health", "API health check"),
        ("/api/proposals/", "Proposals system"),
        ("/api/agents/status", "AI agents status"),
        ("/api/learning/insights", "Learning system"),
        ("/api/project-horus/status", "Project Horus"),
        ("/api/project-warmaster/status", "Project Warmaster"),
        ("/api/custodes-ai/status", "Custodes AI"),
        ("/api/olympic-ai/status", "Olympic AI"),
        ("/api/system/status", "System status"),
        ("/api/guardian/status", "Guardian system"),
        ("/api/custody/status", "Custody protocol"),
        ("/api/imperium/status", "Imperium system"),
        ("/api/conquest/status", "Conquest system"),
    ]
    
    passed = 0
    failed = 0
    
    for endpoint, description in endpoints:
        if test_endpoint(endpoint, description):
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 50)
    print("📊 RESULTS:")
    print(f"✅ Working: {passed}")
    print(f"❌ Issues: {failed}")
    print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL ENDPOINTS WORKING!")
        print("Your Railway deployment is fully functional!")
    elif failed <= 3:
        print(f"\n⚠️  Mostly working, {failed} endpoints need attention")
    else:
        print(f"\n🔧 Multiple issues detected ({failed} endpoints)")
    
    return failed == 0

if __name__ == "__main__":
    main()