#!/usr/bin/env python3
"""
Script to restart the backend service and apply changes
"""

import subprocess
import time
import requests
import json

def restart_backend():
    """Restart the backend service"""
    print("🔄 Restarting backend service...")
    
    try:
        # Stop the service
        subprocess.run([
            "ssh", "-i", "lvl_up_key.pem", "ubuntu@34.202.215.209",
            "sudo systemctl restart ai-backend-python"
        ], check=True)
        
        print("✅ Backend service restarted")
        
        # Wait for service to start
        print("⏳ Waiting for service to start...")
        time.sleep(10)
        
        # Test the endpoints
        test_endpoints()
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error restarting backend: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_endpoints():
    """Test the updated endpoints"""
    print("🧪 Testing updated endpoints...")
    
    endpoints = [
        "http://34.202.215.209:8000/api/imperium/persistence/learning-analytics",
        "http://34.202.215.209:8000/api/imperium/agents",
        "http://34.202.215.209:8000/api/imperium/trusted-sources",
        "http://34.202.215.209:8000/api/imperium/internet-learning/topics"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {endpoint}")
                if "data" in data and "total_events" in data["data"]:
                    print(f"   Events: {data['data']['total_events']}")
                elif "agents" in data:
                    print(f"   Agents: {len(data['agents'])}")
                elif "trusted_sources" in data:
                    print(f"   Sources: {len(data['trusted_sources'])}")
                elif "topics" in data:
                    print(f"   Topics: {len(data['topics'])}")
            else:
                print(f"❌ {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")

if __name__ == "__main__":
    restart_backend() 