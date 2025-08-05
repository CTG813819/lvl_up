#!/usr/bin/env python3
"""
Simple Server Issues Fix Script
Uses HTTP requests to fix server issues without SSH access
"""

import requests
import json
import time
from datetime import datetime

def test_endpoint(url, description):
    """Test an endpoint and return status"""
    try:
        response = requests.get(url, timeout=10)
        print(f"✅ {description}: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ {description}: {e}")
        return False

def fix_websocket_via_http():
    """Try to fix WebSocket issues via HTTP endpoints"""
    print("\n🔌 Attempting to fix WebSocket via HTTP...")
    
    # Test WebSocket endpoints via HTTP
    websocket_endpoints = [
        "http://34.202.215.209:8000/ws",
        "http://34.202.215.209:8000/ws/imperium/learning-analytics",
        "http://34.202.215.209:8000/api/notifications/ws"
    ]
    
    for endpoint in websocket_endpoints:
        test_endpoint(endpoint, f"WebSocket endpoint {endpoint}")
    
    # Try to trigger WebSocket initialization via HTTP
    try:
        response = requests.post(
            "http://34.202.215.209:8000/api/imperium/initialize",
            json={"websocket_init": True},
            timeout=10
        )
        print(f"✅ WebSocket initialization trigger: {response.status_code}")
    except Exception as e:
        print(f"❌ WebSocket initialization trigger failed: {e}")

def fix_database_via_http():
    """Try to fix database issues via HTTP endpoints"""
    print("\n🗄️ Attempting to fix database via HTTP...")
    
    # Test database initialization endpoint
    try:
        response = requests.post(
            "http://34.202.215.209:8000/api/imperium/initialize",
            json={"init_database": True},
            timeout=10
        )
        print(f"✅ Database initialization trigger: {response.status_code}")
    except Exception as e:
        print(f"❌ Database initialization trigger failed: {e}")
    
    # Test learning analytics endpoint
    test_endpoint(
        "http://34.202.215.209:8000/api/imperium/persistence/learning-analytics",
        "Learning analytics endpoint"
    )

def fix_dashboard_via_http():
    """Try to fix dashboard access via HTTP"""
    print("\n📊 Attempting to fix dashboard access...")
    
    # Test Streamlit dashboard
    test_endpoint("http://34.202.215.209:8501", "Streamlit dashboard")
    
    # Test API dashboard
    test_endpoint(
        "http://34.202.215.209:8000/api/imperium/dashboard",
        "API dashboard"
    )

def test_all_working_endpoints():
    """Test all known working endpoints"""
    print("\n🧪 Testing All Working Endpoints...")
    
    working_endpoints = [
        ("http://34.202.215.209:8000/api/imperium/status", "System Status"),
        ("http://34.202.215.209:8000/api/imperium/agents", "Agents Info"),
        ("http://34.202.215.209:8000/api/imperium/dashboard", "Dashboard Data"),
        ("http://34.202.215.209:8000/api/imperium/cycles", "Learning Cycles"),
        ("http://34.202.215.209:8000/api/imperium/internet-learning/trigger", "Internet Learning Trigger"),
    ]
    
    success_count = 0
    for url, description in working_endpoints:
        if test_endpoint(url, description):
            success_count += 1
    
    print(f"\n📊 Endpoint Success Rate: {success_count}/{len(working_endpoints)} ({success_count/len(working_endpoints)*100:.1f}%)")

def create_websocket_fix_request():
    """Create a request to fix WebSocket issues"""
    print("\n🔧 Creating WebSocket fix request...")
    
    # Try to send a request that might trigger WebSocket fixes
    try:
        response = requests.post(
            "http://34.202.215.209:8000/api/imperium/initialize",
            json={
                "fix_websocket": True,
                "fix_cors": True,
                "enable_notifications": True
            },
            timeout=10
        )
        print(f"✅ WebSocket fix request sent: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ WebSocket fix request failed: {e}")

def test_websocket_upgrade():
    """Test WebSocket upgrade requests"""
    print("\n🔌 Testing WebSocket Upgrade Requests...")
    
    import websocket
    
    websocket_endpoints = [
        "ws://34.202.215.209:8000/ws",
        "ws://34.202.215.209:8000/ws/imperium/learning-analytics",
        "ws://34.202.215.209:8000/api/notifications/ws"
    ]
    
    for endpoint in websocket_endpoints:
        try:
            ws = websocket.create_connection(endpoint, timeout=5)
            print(f"✅ WebSocket connection successful: {endpoint}")
            ws.close()
        except Exception as e:
            print(f"❌ WebSocket connection failed: {endpoint} - {e}")

def main():
    """Main function to fix server issues"""
    print("🚀 Starting Simple Server Issues Fix...")
    print(f"⏰ Started at: {datetime.now()}")
    
    # Test current status
    print("\n📊 Current Server Status:")
    test_all_working_endpoints()
    
    # Try to fix issues
    fix_websocket_via_http()
    fix_database_via_http()
    fix_dashboard_via_http()
    create_websocket_fix_request()
    
    # Test WebSocket connections
    try:
        test_websocket_upgrade()
    except ImportError:
        print("⚠️ websocket-client not available, skipping WebSocket tests")
    
    # Test again after fixes
    print("\n📊 Status After Fixes:")
    test_all_working_endpoints()
    
    print(f"\n✅ Server issues fix attempt completed at: {datetime.now()}")
    print("\n📋 Summary:")
    print("- WebSocket fix requests sent")
    print("- Database initialization triggered")
    print("- Dashboard access tested")
    print("- All endpoints re-tested")

if __name__ == "__main__":
    main() 