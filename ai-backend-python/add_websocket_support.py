#!/usr/bin/env python3
"""
Add WebSocket Support Script
Attempts to add WebSocket support to the server via HTTP configuration
"""

import requests
import json
import time
from datetime import datetime

# Server configuration
EC2_IP = "34.202.215.209"
BACKEND_PORT = 8000

def log(message):
    """Log messages with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_endpoint(url, method="GET", data=None):
    """Test an endpoint and return status"""
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        return response.status_code, response.text
    except Exception as e:
        return None, str(e)

def add_websocket_endpoints():
    """Try to add WebSocket endpoints via HTTP configuration"""
    log("🔧 Attempting to add WebSocket support...")
    
    # Try to create WebSocket endpoints by making requests
    websocket_configs = [
        # Basic WebSocket endpoint
        {
            "url": f"http://{EC2_IP}:{BACKEND_PORT}/api/websocket/create",
            "data": {
                "endpoint": "/ws",
                "type": "websocket",
                "enabled": True
            }
        },
        # Imperium learning analytics WebSocket
        {
            "url": f"http://{EC2_IP}:{BACKEND_PORT}/api/websocket/create",
            "data": {
                "endpoint": "/ws/imperium/learning-analytics",
                "type": "websocket",
                "enabled": True,
                "topic": "learning_analytics"
            }
        },
        # Notifications WebSocket
        {
            "url": f"http://{EC2_IP}:{BACKEND_PORT}/api/websocket/create",
            "data": {
                "endpoint": "/api/notifications/ws",
                "type": "websocket",
                "enabled": True,
                "topic": "notifications"
            }
        },
        # Alternative configuration endpoints
        {
            "url": f"http://{EC2_IP}:{BACKEND_PORT}/api/imperium/add-websocket",
            "data": {
                "path": "/ws/imperium/learning-analytics",
                "enabled": True
            }
        },
        {
            "url": f"http://{EC2_IP}:{BACKEND_PORT}/api/config/add-websocket",
            "data": {
                "endpoints": [
                    "/ws",
                    "/ws/imperium/learning-analytics",
                    "/api/notifications/ws"
                ]
            }
        }
    ]
    
    success_count = 0
    for config in websocket_configs:
        log(f"  Trying: {config['url']}")
        status, response = test_endpoint(config['url'], "POST", config['data'])
        
        if status == 200:
            log(f"    ✅ WebSocket endpoint created")
            success_count += 1
        elif status == 404:
            log(f"    ❌ Endpoint not found")
        elif status:
            log(f"    ⚠️ Status: {status}")
        else:
            log(f"    ❌ Connection failed")
    
    return success_count

def add_missing_endpoints():
    """Try to add commonly missing endpoints"""
    log("🔧 Attempting to add missing endpoints...")
    
    missing_endpoints = [
        # Health and status endpoints
        {
            "url": f"http://{EC2_IP}:{BACKEND_PORT}/api/health",
            "data": {"status": "healthy", "timestamp": datetime.now().isoformat()}
        },
        {
            "url": f"http://{EC2_IP}:{BACKEND_PORT}/api/status",
            "data": {"status": "running", "version": "1.0.0"}
        },
        {
            "url": f"http://{EC2_IP}:{BACKEND_PORT}/api/config",
            "data": {"websocket_enabled": False, "cors_enabled": True}
        },
        # Learning endpoints
        {
            "url": f"http://{EC2_IP}:{BACKEND_PORT}/api/learning/data",
            "data": {"data": [], "status": "available"}
        },
        {
            "url": f"http://{EC2_IP}:{BACKEND_PORT}/api/learning/metrics",
            "data": {"metrics": {}, "status": "available"}
        },
        # Proposal endpoints
        {
            "url": f"http://{EC2_IP}:{BACKEND_PORT}/api/proposals/ai-status",
            "data": {"status": "available", "ai_count": 0}
        }
    ]
    
    success_count = 0
    for endpoint in missing_endpoints:
        log(f"  Creating: {endpoint['url']}")
        
        # Try POST to create the endpoint
        status, response = test_endpoint(endpoint['url'], "POST", endpoint['data'])
        
        if status == 200:
            log(f"    ✅ Endpoint created")
            success_count += 1
        elif status == 404:
            log(f"    ❌ Endpoint not found")
        elif status:
            log(f"    ⚠️ Status: {status}")
        else:
            log(f"    ❌ Connection failed")
    
    return success_count

def test_websocket_after_changes():
    """Test WebSocket endpoints after attempting to add them"""
    log("🔌 Testing WebSocket endpoints after changes...")
    
    websocket_endpoints = [
        f"ws://{EC2_IP}:{BACKEND_PORT}/ws",
        f"ws://{EC2_IP}:{BACKEND_PORT}/ws/imperium/learning-analytics",
        f"ws://{EC2_IP}:{BACKEND_PORT}/api/notifications/ws",
    ]
    
    working_count = 0
    for endpoint in websocket_endpoints:
        log(f"  Testing: {endpoint}")
        
        # Test HTTP upgrade request
        http_url = endpoint.replace("ws://", "http://")
        status, response = test_endpoint(http_url)
        
        if status == 101:  # Switching Protocols
            log(f"    ✅ WebSocket upgrade successful")
            working_count += 1
        elif status == 426:  # Upgrade Required
            log(f"    ⚠️ Upgrade required")
        elif status == 404:
            log(f"    ❌ Not found")
        else:
            log(f"    ❌ Status: {status}")
    
    return working_count

def main():
    """Main function to add WebSocket support"""
    log("🚀 Starting WebSocket support addition...")
    
    # Test initial WebSocket state
    log("📊 Testing initial WebSocket state...")
    initial_websockets = test_websocket_after_changes()
    log(f"  Initial WebSocket endpoints working: {initial_websockets}")
    
    # Try to add WebSocket support
    websocket_added = add_websocket_endpoints()
    
    # Try to add missing endpoints
    endpoints_added = add_missing_endpoints()
    
    # Wait for changes to take effect
    log("⏳ Waiting for changes to take effect...")
    time.sleep(3)
    
    # Test final WebSocket state
    log("📊 Testing final WebSocket state...")
    final_websockets = test_websocket_after_changes()
    
    # Summary
    log("📋 WebSocket Addition Summary:")
    log(f"  WebSocket endpoints added: {websocket_added}")
    log(f"  Missing endpoints added: {endpoints_added}")
    log(f"  WebSocket endpoints working: {initial_websockets} → {final_websockets}")
    
    if final_websockets > initial_websockets:
        log("✅ WebSocket support successfully added!")
    else:
        log("⚠️ WebSocket support may need manual server configuration")
    
    # Save results
    results = {
        "timestamp": datetime.now().isoformat(),
        "websocket_endpoints_added": websocket_added,
        "missing_endpoints_added": endpoints_added,
        "initial_websockets": initial_websockets,
        "final_websockets": final_websockets,
        "success": final_websockets > initial_websockets
    }
    
    with open("websocket_addition_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    log("💾 Results saved to websocket_addition_results.json")
    
    # Recommendations
    log("🎯 Recommendations:")
    if final_websockets > initial_websockets:
        log("  ✅ WebSocket support added - Flutter app can enable WebSocket connections")
    else:
        log("  ⚠️ WebSocket support not available - Flutter app should continue with HTTP polling")
        log("  💡 Consider manual server configuration for WebSocket support")

if __name__ == "__main__":
    main() 