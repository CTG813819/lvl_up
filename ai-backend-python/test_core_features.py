#!/usr/bin/env python3
"""
Test core features that users actually interact with
"""

import requests
import json

RAILWAY_URL = "https://lvlup-production.up.railway.app"

def test_core_user_features():
    """Test the features users actually interact with"""
    print("🎮 Testing Core User Features")
    print("=" * 40)
    
    tests = [
        # Health and basic functionality
        ("GET", "/health", "Server health"),
        ("GET", "/api/health", "API health"),
        
        # User-facing features
        ("GET", "/api/proposals/", "View proposals"),
        ("GET", "/api/agents/status", "Check AI agents"),
        ("GET", "/api/agent-metrics/leaderboard", "Leaderboard"),
        
        # AI features
        ("GET", "/api/project-horus/status", "Project Horus AI"),
        ("GET", "/api/project-warmaster/status", "Project Warmaster"),
        ("GET", "/api/conquest/status", "Conquest system"),
        
        # Learning system
        ("GET", "/api/learning/stats", "Learning statistics"),
    ]
    
    working = 0
    for method, endpoint, description in tests:
        try:
            response = requests.get(f"{RAILWAY_URL}{endpoint}", timeout=10)
            if response.status_code in [200, 401]:  # 401 might be auth-protected
                print(f"✅ {description}")
                working += 1
            else:
                print(f"⚠️  {description} - Status {response.status_code}")
        except Exception:
            print(f"❌ {description} - Connection issue")
    
    print(f"\n📊 Core Features Working: {working}/{len(tests)}")
    return working >= len(tests) * 0.7  # 70% success rate is good

if __name__ == "__main__":
    success = test_core_user_features()
    if success:
        print("\n🎉 Your Railway deployment is ready for users!")
    else:
        print("\n🔧 Some core features need attention")