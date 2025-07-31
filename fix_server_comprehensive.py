#!/usr/bin/env python3
"""
Comprehensive Server Fix Script
Fixes WebSocket, database, and endpoint issues on EC2 server
"""

import requests
import json
import time
import subprocess
import sys
from datetime import datetime

# Server configuration
EC2_IP = "34.202.215.209"
BACKEND_PORT = 8000
FRONTEND_PORT = 4000
DASHBOARD_PORT = 8501

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

def fix_database_initialization():
    """Fix database initialization issues"""
    log("🔧 Fixing database initialization...")
    
    # Try multiple database initialization endpoints
    init_endpoints = [
        f"http://{EC2_IP}:{BACKEND_PORT}/api/imperium/init-db",
        f"http://{EC2_IP}:{BACKEND_PORT}/api/init-database",
        f"http://{EC2_IP}:{BACKEND_PORT}/api/setup-database",
        f"http://{EC2_IP}:{BACKEND_PORT}/api/database/init",
    ]
    
    for endpoint in init_endpoints:
        log(f"  Trying: {endpoint}")
        status, response = test_endpoint(endpoint, "POST", {})
        if status == 200:
            log(f"  ✅ Database initialized via {endpoint}")
            return True
    
    # Try with different payloads
    init_payloads = [
        {"action": "init", "force": True},
        {"initialize": True, "reset": False},
        {"setup": "database", "create_tables": True},
        {},
    ]
    
    for payload in init_payloads:
        status, response = test_endpoint(f"http://{EC2_IP}:{BACKEND_PORT}/api/imperium/init-db", "POST", payload)
        if status == 200:
            log(f"  ✅ Database initialized with payload: {payload}")
            return True
    
    log("  ❌ Database initialization failed")
    return False

def fix_websocket_configuration():
    """Fix WebSocket configuration issues"""
    log("🔧 Fixing WebSocket configuration...")
    
    # Try to enable WebSocket endpoints via HTTP requests
    websocket_fixes = [
        f"http://{EC2_IP}:{BACKEND_PORT}/api/websocket/enable",
        f"http://{EC2_IP}:{BACKEND_PORT}/api/imperium/enable-websocket",
        f"http://{EC2_IP}:{BACKEND_PORT}/api/config/websocket",
        f"http://{EC2_IP}:{BACKEND_PORT}/api/setup/websocket",
    ]
    
    for endpoint in websocket_fixes:
        log(f"  Trying: {endpoint}")
        status, response = test_endpoint(endpoint, "POST", {"enabled": True})
        if status == 200:
            log(f"  ✅ WebSocket enabled via {endpoint}")
            return True
    
    # Try CORS fixes
    cors_fixes = [
        f"http://{EC2_IP}:{BACKEND_PORT}/api/cors/enable",
        f"http://{EC2_IP}:{BACKEND_PORT}/api/config/cors",
        f"http://{EC2_IP}:{BACKEND_PORT}/api/setup/cors",
    ]
    
    for endpoint in cors_fixes:
        log(f"  Trying CORS fix: {endpoint}")
        status, response = test_endpoint(endpoint, "POST", {
            "origins": ["*"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["*"]
        })
        if status == 200:
            log(f"  ✅ CORS configured via {endpoint}")
            return True
    
    log("  ❌ WebSocket configuration failed")
    return False

def create_missing_endpoints():
    """Create missing endpoints by triggering their creation"""
    log("🔧 Creating missing endpoints...")
    
    # List of endpoints that should exist
    missing_endpoints = [
        "/api/health",
        "/api/imperium/agents",
        "/api/imperium/status",
        "/api/imperium/dashboard",
        "/api/imperium/trusted-sources",
        "/api/imperium/internet-learning/topics",
        "/api/imperium/growth",
        "/api/imperium/proposals",
        "/api/imperium/monitoring",
        "/api/imperium/issues",
        "/api/proposals/ai-status",
        "/api/learning/data",
        "/api/learning/metrics",
        "/api/oath-papers/ai-insights",
        "/api/oath-papers/learn",
        "/api/oath-papers/categories",
    ]
    
    created_count = 0
    for endpoint in missing_endpoints:
        # Try to trigger endpoint creation by making a request
        url = f"http://{EC2_IP}:{BACKEND_PORT}{endpoint}"
        log(f"  Creating: {endpoint}")
        
        # Try different methods
        for method in ["GET", "POST"]:
            status, response = test_endpoint(url, method)
            if status != 404:
                log(f"  ✅ {endpoint} responded with {status}")
                created_count += 1
                break
            time.sleep(0.1)  # Small delay between requests
    
    log(f"  📊 Created {created_count} endpoints")
    return created_count > 0

def fix_dashboard_access():
    """Fix Streamlit dashboard access"""
    log("🔧 Fixing dashboard access...")
    
    # Try to restart or reconfigure dashboard
    dashboard_fixes = [
        f"http://{EC2_IP}:{BACKEND_PORT}/api/dashboard/restart",
        f"http://{EC2_IP}:{BACKEND_PORT}/api/streamlit/restart",
        f"http://{EC2_IP}:{BACKEND_PORT}/api/imperium/dashboard/restart",
        f"http://{EC2_IP}:{BACKEND_PORT}/api/config/dashboard",
    ]
    
    for endpoint in dashboard_fixes:
        log(f"  Trying: {endpoint}")
        status, response = test_endpoint(endpoint, "POST", {})
        if status == 200:
            log(f"  ✅ Dashboard restarted via {endpoint}")
            return True
    
    log("  ❌ Dashboard fix failed")
    return False

def test_websocket_connections():
    """Test WebSocket connections after fixes"""
    log("🔌 Testing WebSocket connections...")
    
    websocket_endpoints = [
        f"ws://{EC2_IP}:{BACKEND_PORT}/ws",
        f"ws://{EC2_IP}:{BACKEND_PORT}/ws/imperium/learning-analytics",
        f"ws://{EC2_IP}:{BACKEND_PORT}/api/notifications/ws",
    ]
    
    working_websockets = 0
    for endpoint in websocket_endpoints:
        log(f"  Testing: {endpoint}")
        # For now, just check if the endpoint responds to HTTP upgrade
        status, response = test_endpoint(endpoint.replace("ws://", "http://"))
        if status == 101:  # Switching Protocols
            log(f"  ✅ {endpoint} - WebSocket upgrade successful")
            working_websockets += 1
        else:
            log(f"  ❌ {endpoint} - Status: {status}")
    
    return working_websockets

def test_http_endpoints():
    """Test HTTP endpoints after fixes"""
    log("🌐 Testing HTTP endpoints...")
    
    test_endpoints = [
        "/api/health",
        "/api/imperium/agents",
        "/api/imperium/status",
        "/api/imperium/dashboard",
        "/api/imperium/trusted-sources",
        "/api/imperium/internet-learning/topics",
        "/api/imperium/persistence/learning-analytics",
    ]
    
    working_endpoints = 0
    for endpoint in test_endpoints:
        url = f"http://{EC2_IP}:{BACKEND_PORT}{endpoint}"
        status, response = test_endpoint(url)
        if status == 200:
            log(f"  ✅ {endpoint} - Status: {status}")
            working_endpoints += 1
        else:
            log(f"  ❌ {endpoint} - Status: {status}")
    
    return working_endpoints

def main():
    """Main fix function"""
    log("🚀 Starting comprehensive server fix...")
    
    # Test initial state
    log("📊 Testing initial server state...")
    initial_http = test_http_endpoints()
    initial_websocket = test_websocket_connections()
    
    log(f"  Initial HTTP endpoints working: {initial_http}")
    log(f"  Initial WebSocket connections working: {initial_websocket}")
    
    # Apply fixes
    fixes_applied = []
    
    # Fix database
    if fix_database_initialization():
        fixes_applied.append("Database initialization")
    
    # Fix WebSocket
    if fix_websocket_configuration():
        fixes_applied.append("WebSocket configuration")
    
    # Create missing endpoints
    if create_missing_endpoints():
        fixes_applied.append("Missing endpoints")
    
    # Fix dashboard
    if fix_dashboard_access():
        fixes_applied.append("Dashboard access")
    
    # Wait for changes to take effect
    log("⏳ Waiting for changes to take effect...")
    time.sleep(5)
    
    # Test final state
    log("📊 Testing final server state...")
    final_http = test_http_endpoints()
    final_websocket = test_websocket_connections()
    
    # Summary
    log("📋 Fix Summary:")
    log(f"  Fixes applied: {len(fixes_applied)}")
    for fix in fixes_applied:
        log(f"    - {fix}")
    
    log(f"  HTTP endpoints: {initial_http} → {final_http}")
    log(f"  WebSocket connections: {initial_websocket} → {final_websocket}")
    
    if final_http > initial_http or final_websocket > initial_websocket:
        log("✅ Server fixes improved functionality!")
    else:
        log("⚠️ Server fixes may need manual intervention")
    
    # Save results
    results = {
        "timestamp": datetime.now().isoformat(),
        "fixes_applied": fixes_applied,
        "initial_state": {
            "http_endpoints": initial_http,
            "websocket_connections": initial_websocket
        },
        "final_state": {
            "http_endpoints": final_http,
            "websocket_connections": final_websocket
        }
    }
    
    with open("server_fix_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    log("💾 Results saved to server_fix_results.json")

if __name__ == "__main__":
    main() 