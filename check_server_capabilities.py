#!/usr/bin/env python3
"""
Check Server Capabilities
Discover what endpoints and features are actually available on the server
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
    """Test an endpoint and return status and response"""
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        return response.status_code, response.text, response.headers
    except Exception as e:
        return None, str(e), {}

def discover_endpoints():
    """Discover available endpoints by testing common patterns"""
    log("🔍 Discovering available endpoints...")
    
    # Test common endpoint patterns
    endpoint_patterns = [
        # Imperium endpoints
        "/api/imperium/agents",
        "/api/imperium/status", 
        "/api/imperium/dashboard",
        "/api/imperium/trusted-sources",
        "/api/imperium/internet-learning/topics",
        "/api/imperium/persistence/learning-analytics",
        "/api/imperium/growth",
        "/api/imperium/proposals",
        "/api/imperium/monitoring",
        "/api/imperium/issues",
        "/api/imperium/health",
        "/api/imperium/config",
        
        # General API endpoints
        "/api/health",
        "/api/status",
        "/api/config",
        "/api/info",
        "/api/version",
        
        # Learning endpoints
        "/api/learning/data",
        "/api/learning/metrics",
        "/api/learning/status",
        "/api/learning/insights",
        
        # Proposal endpoints
        "/api/proposals",
        "/api/proposals/ai-status",
        "/api/proposals/status",
        
        # Oath papers endpoints
        "/api/oath-papers",
        "/api/oath-papers/ai-insights",
        "/api/oath-papers/learn",
        "/api/oath-papers/categories",
        
        # WebSocket endpoints (HTTP test)
        "/ws",
        "/ws/imperium/learning-analytics",
        "/api/notifications/ws",
        "/socket.io/",
        
        # Configuration endpoints
        "/api/websocket/enable",
        "/api/cors/enable",
        "/api/config/websocket",
        "/api/config/cors",
        
        # Database endpoints
        "/api/init-database",
        "/api/setup-database",
        "/api/database/init",
        "/api/imperium/init-db",
    ]
    
    working_endpoints = []
    websocket_endpoints = []
    
    for endpoint in endpoint_patterns:
        url = f"http://{EC2_IP}:{BACKEND_PORT}{endpoint}"
        log(f"  Testing: {endpoint}")
        
        status, response, headers = test_endpoint(url)
        
        if status == 200:
            log(f"    ✅ {endpoint} - Status: {status}")
            working_endpoints.append({
                "endpoint": endpoint,
                "status": status,
                "response_length": len(response),
                "content_type": headers.get("content-type", "unknown")
            })
            
            # Check if it's a WebSocket endpoint
            if "websocket" in endpoint.lower() or endpoint.startswith("/ws"):
                websocket_endpoints.append(endpoint)
                
        elif status == 404:
            log(f"    ❌ {endpoint} - Not Found")
        elif status:
            log(f"    ⚠️ {endpoint} - Status: {status}")
        else:
            log(f"    ❌ {endpoint} - Connection failed")
        
        time.sleep(0.1)  # Small delay between requests
    
    return working_endpoints, websocket_endpoints

def analyze_working_endpoints(endpoints):
    """Analyze the working endpoints to understand server capabilities"""
    log("📊 Analyzing working endpoints...")
    
    if not endpoints:
        log("  No working endpoints found")
        return
    
    # Group by functionality
    imperium_endpoints = [e for e in endpoints if "imperium" in e["endpoint"]]
    learning_endpoints = [e for e in endpoints if "learning" in e["endpoint"]]
    proposal_endpoints = [e for e in endpoints if "proposal" in e["endpoint"]]
    config_endpoints = [e for e in endpoints if "config" in e["endpoint"]]
    health_endpoints = [e for e in endpoints if "health" in e["endpoint"]]
    
    log(f"  📈 Total working endpoints: {len(endpoints)}")
    log(f"  👑 Imperium endpoints: {len(imperium_endpoints)}")
    log(f"  🧠 Learning endpoints: {len(learning_endpoints)}")
    log(f"  📋 Proposal endpoints: {len(proposal_endpoints)}")
    log(f"  ⚙️ Config endpoints: {len(config_endpoints)}")
    log(f"  💚 Health endpoints: {len(health_endpoints)}")
    
    # Show detailed list
    log("  📋 Working endpoints:")
    for endpoint in endpoints:
        log(f"    - {endpoint['endpoint']} ({endpoint['content_type']})")

def test_websocket_upgrade():
    """Test WebSocket upgrade capabilities"""
    log("🔌 Testing WebSocket upgrade capabilities...")
    
    websocket_endpoints = [
        f"ws://{EC2_IP}:{BACKEND_PORT}/ws",
        f"ws://{EC2_IP}:{BACKEND_PORT}/ws/imperium/learning-analytics",
        f"ws://{EC2_IP}:{BACKEND_PORT}/api/notifications/ws",
        f"ws://{EC2_IP}:{BACKEND_PORT}/socket.io/",
    ]
    
    working_websockets = []
    
    for endpoint in websocket_endpoints:
        log(f"  Testing: {endpoint}")
        
        # Test HTTP upgrade request
        http_url = endpoint.replace("ws://", "http://")
        status, response, headers = test_endpoint(http_url)
        
        if status == 101:  # Switching Protocols
            log(f"    ✅ {endpoint} - WebSocket upgrade successful")
            working_websockets.append(endpoint)
        elif status == 426:  # Upgrade Required
            log(f"    ⚠️ {endpoint} - Upgrade required")
        elif status == 404:
            log(f"    ❌ {endpoint} - Not found")
        else:
            log(f"    ❌ {endpoint} - Status: {status}")
    
    return working_websockets

def check_server_info():
    """Check server information and capabilities"""
    log("ℹ️ Checking server information...")
    
    # Try to get server info
    info_endpoints = [
        "/api/info",
        "/api/version",
        "/api/status",
        "/api/health",
        "/api/config",
    ]
    
    server_info = {}
    
    for endpoint in info_endpoints:
        url = f"http://{EC2_IP}:{BACKEND_PORT}{endpoint}"
        status, response, headers = test_endpoint(url)
        
        if status == 200:
            try:
                data = json.loads(response)
                server_info[endpoint] = data
                log(f"  ✅ {endpoint}: {data}")
            except:
                server_info[endpoint] = response
                log(f"  ✅ {endpoint}: {response[:100]}...")
    
    return server_info

def main():
    """Main discovery function"""
    log("🚀 Starting server capability discovery...")
    
    # Discover endpoints
    working_endpoints, websocket_endpoints = discover_endpoints()
    
    # Analyze capabilities
    analyze_working_endpoints(working_endpoints)
    
    # Test WebSocket upgrade
    working_websockets = test_websocket_upgrade()
    
    # Check server info
    server_info = check_server_info()
    
    # Summary
    log("📋 Discovery Summary:")
    log(f"  HTTP endpoints working: {len(working_endpoints)}")
    log(f"  WebSocket endpoints found: {len(websocket_endpoints)}")
    log(f"  WebSocket upgrades working: {len(working_websockets)}")
    log(f"  Server info endpoints: {len(server_info)}")
    
    # Save results
    results = {
        "timestamp": datetime.now().isoformat(),
        "working_endpoints": working_endpoints,
        "websocket_endpoints": websocket_endpoints,
        "working_websockets": working_websockets,
        "server_info": server_info,
        "summary": {
            "http_endpoints": len(working_endpoints),
            "websocket_endpoints": len(websocket_endpoints),
            "working_websockets": len(working_websockets),
            "server_info": len(server_info)
        }
    }
    
    with open("server_capabilities.json", "w") as f:
        json.dump(results, f, indent=2)
    
    log("💾 Results saved to server_capabilities.json")
    
    # Recommendations
    log("🎯 Recommendations:")
    if len(working_endpoints) > 0:
        log("  ✅ Server has working HTTP endpoints - Flutter app should work")
    if len(working_websockets) == 0:
        log("  ⚠️ No WebSocket support - Flutter app will use HTTP polling")
    if len(server_info) > 0:
        log("  ℹ️ Server provides information endpoints")

if __name__ == "__main__":
    main() 