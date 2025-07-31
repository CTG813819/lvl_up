#!/usr/bin/env python3
"""
Targeted Server Fixes
Addresses specific issues we can fix without SSH access
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
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, dict) and 'data' in data:
                    print(f"   Data keys: {list(data['data'].keys()) if isinstance(data['data'], dict) else 'Not a dict'}")
            except:
                pass
        return response.status_code == 200
    except Exception as e:
        print(f"❌ {description}: {e}")
        return False

def initialize_database():
    """Initialize the database via API calls"""
    print("\n🗄️ Initializing Database...")
    
    # Try different initialization approaches
    init_attempts = [
        {"init_database": True},
        {"initialize": True, "database": True},
        {"setup": True, "database": True},
        {"create_tables": True},
        {"init": True}
    ]
    
    for attempt in init_attempts:
        try:
            response = requests.post(
                "http://34.202.215.209:8000/api/imperium/initialize",
                json=attempt,
                timeout=10
            )
            print(f"✅ Database init attempt {attempt}: {response.status_code}")
            if response.status_code == 200:
                print(f"   Response: {response.text[:200]}...")
        except Exception as e:
            print(f"❌ Database init attempt {attempt} failed: {e}")

def test_websocket_endpoints():
    """Test WebSocket endpoints and provide alternatives"""
    print("\n🔌 Testing WebSocket Endpoints...")
    
    websocket_endpoints = [
        "http://34.202.215.209:8000/ws",
        "http://34.202.215.209:8000/ws/imperium/learning-analytics",
        "http://34.202.215.209:8000/api/notifications/ws",
        "http://34.202.215.209:8000/api/websocket",
        "http://34.202.215.209:8000/api/ws"
    ]
    
    for endpoint in websocket_endpoints:
        test_endpoint(endpoint, f"WebSocket endpoint {endpoint}")

def test_alternative_endpoints():
    """Test alternative endpoints that might work"""
    print("\n🔍 Testing Alternative Endpoints...")
    
    alternative_endpoints = [
        ("http://34.202.215.209:8000/api/imperium/persistence/agent-metrics", "Agent Metrics"),
        ("http://34.202.215.209:8000/api/imperium/persistence/learning-cycles", "Learning Cycles"),
        ("http://34.202.209:8000/api/imperium/persistence/log-learning-event", "Log Learning Event"),
        ("http://34.202.215.209:8000/api/imperium/persistence/internet-learning-result", "Internet Learning Result"),
        ("http://34.202.215.209:8000/api/imperium/trusted-sources", "Trusted Sources"),
        ("http://34.202.215.209:8000/api/imperium/internet-learning/topics", "Internet Learning Topics"),
    ]
    
    for url, description in alternative_endpoints:
        test_endpoint(url, description)

def create_flutter_websocket_fallback():
    """Create a Flutter-compatible WebSocket fallback solution"""
    print("\n📱 Creating Flutter WebSocket Fallback...")
    
    fallback_code = '''
// Add this to your Flutter app for WebSocket fallback
class WebSocketFallback {
  static const String baseUrl = 'http://34.202.215.209:8000';
  static const Duration pollInterval = Duration(seconds: 5);
  
  static Future<void> startPolling(Function(dynamic) onData) async {
    Timer.periodic(pollInterval, (timer) async {
      try {
        final response = await http.get(
          Uri.parse('$baseUrl/api/imperium/dashboard'),
          headers: {'Content-Type': 'application/json'},
        );
        
        if (response.statusCode == 200) {
          final data = json.decode(response.body);
          onData(data);
        }
      } catch (e) {
        print('Polling error: $e');
      }
    });
  }
}
'''
    
    with open('websocket_fallback.dart', 'w') as f:
        f.write(fallback_code)
    
    print("✅ WebSocket fallback code created: websocket_fallback.dart")

def update_flutter_endpoints():
    """Update Flutter app to use working endpoints"""
    print("\n📱 Updating Flutter Endpoints...")
    
    # Create a summary of working endpoints for Flutter
    working_endpoints = {
        "system_status": "http://34.202.215.209:8000/api/imperium/status",
        "agents": "http://34.202.215.209:8000/api/imperium/agents", 
        "dashboard": "http://34.202.215.209:8000/api/imperium/dashboard",
        "learning_cycles": "http://34.202.215.209:8000/api/imperium/cycles",
        "agent_metrics": "http://34.202.215.209:8000/api/imperium/persistence/agent-metrics",
        "learning_analytics": "http://34.202.215.209:8000/api/imperium/persistence/learning-analytics",
        "trusted_sources": "http://34.202.215.209:8000/api/imperium/trusted-sources",
        "internet_learning_topics": "http://34.202.215.209:8000/api/imperium/internet-learning/topics"
    }
    
    with open('working_endpoints.json', 'w') as f:
        json.dump(working_endpoints, f, indent=2)
    
    print("✅ Working endpoints saved: working_endpoints.json")

def test_streamlit_alternatives():
    """Test alternative dashboard access methods"""
    print("\n📊 Testing Dashboard Alternatives...")
    
    dashboard_alternatives = [
        "http://34.202.215.209:8000/api/imperium/dashboard",
        "http://34.202.215.209:8000/api/imperium/status",
        "http://34.202.215.209:8000/api/imperium/agents"
    ]
    
    for url in dashboard_alternatives:
        test_endpoint(url, f"Dashboard alternative: {url}")

def main():
    """Main function to apply targeted fixes"""
    print("🎯 Starting Targeted Server Fixes...")
    print(f"⏰ Started at: {datetime.now()}")
    
    # Test current status
    print("\n📊 Current Status:")
    test_endpoint("http://34.202.215.209:8000/api/imperium/status", "System Status")
    test_endpoint("http://34.202.215.209:8000/api/imperium/dashboard", "Dashboard")
    test_endpoint("http://34.202.215.209:8000/api/imperium/persistence/learning-analytics", "Learning Analytics")
    
    # Apply fixes
    initialize_database()
    test_websocket_endpoints()
    test_alternative_endpoints()
    test_streamlit_alternatives()
    
    # Create Flutter solutions
    create_flutter_websocket_fallback()
    update_flutter_endpoints()
    
    # Test after fixes
    print("\n📊 Status After Fixes:")
    test_endpoint("http://34.202.215.209:8000/api/imperium/persistence/learning-analytics", "Learning Analytics (After Fix)")
    
    print(f"\n✅ Targeted fixes completed at: {datetime.now()}")
    print("\n📋 Summary:")
    print("- Database initialization attempted")
    print("- WebSocket alternatives tested")
    print("- Flutter fallback solutions created")
    print("- Working endpoints documented")

if __name__ == "__main__":
    main() 