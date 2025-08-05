#!/usr/bin/env python3
"""
Test Project Warmaster Service with Gunicorn
============================================

This script tests the Project Warmaster service running on gunicorn.
"""

import requests
import socket
import time

EC2_HOST = "34.202.215.209"
PROJECT_WARMASTER_PORT = 8003

def test_port_connectivity():
    """Test if port 8003 is reachable"""
    print("🔍 Testing Project Warmaster connectivity...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((EC2_HOST, PROJECT_WARMASTER_PORT))
        sock.close()
        
        if result == 0:
            print("✅ Port 8003 is reachable")
            return True
        else:
            print("❌ Port 8003 is not reachable")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_http_endpoints():
    """Test HTTP endpoints"""
    print("\n🌐 Testing HTTP endpoints...")
    
    endpoints = [
        ("/api/project-warmaster/status", "Project Warmaster Status"),
        ("/docs", "Project Warmaster Docs"),
        ("/api/project-warmaster/repository-types", "Repository Types"),
    ]
    
    for endpoint, description in endpoints:
        try:
            url = f"http://{EC2_HOST}:{PROJECT_WARMASTER_PORT}{endpoint}"
            print(f"🔍 Testing {description}...")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {description} - Status: {response.status_code}")
                if endpoint == "/api/project-warmaster/status":
                    try:
                        data = response.json()
                        print(f"📊 Response data: {data}")
                    except:
                        print(f"📄 Response text: {response.text[:200]}...")
            else:
                print(f"⚠️ {description} - Status: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ {description} - Timeout")
        except requests.exceptions.ConnectionError:
            print(f"🔌 {description} - Connection Error")
        except Exception as e:
            print(f"❌ {description} - Error: {e}")

def main():
    print("🧪 Testing Project Warmaster Service with Gunicorn")
    print("=" * 50)
    
    # Test port connectivity
    if test_port_connectivity():
        # Test HTTP endpoints
        test_http_endpoints()
    else:
        print("\n❌ Cannot test HTTP endpoints - port is not reachable")
    
    print("\n📋 Summary:")
    print("=" * 30)
    print("If the service is working:")
    print("✅ Port 8003 should be reachable")
    print("✅ HTTP endpoints should return 200 status")
    print("✅ The Flutter app should be able to connect")

if __name__ == "__main__":
    main()