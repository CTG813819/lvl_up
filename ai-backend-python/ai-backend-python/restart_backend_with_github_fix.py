#!/usr/bin/env python3
"""
Restart backend with GitHub fixes applied
"""

import subprocess
import time
import requests

def restart_backend():
    """Restart the backend service"""
    print("🔄 Restarting backend service...")
    
    try:
        # Restart the service
        result = subprocess.run([
            "ssh", "-i", "lvl_up_key.pem", 
            "ubuntu@34.202.215.209", 
            "sudo systemctl restart ai-backend-python"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Backend service restarted successfully")
        else:
            print(f"❌ Failed to restart backend: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ SSH command timed out")
        return False
    except FileNotFoundError:
        print("❌ SSH key file not found")
        return False
    
    # Wait for service to start
    print("⏳ Waiting for backend to start...")
    time.sleep(10)
    
    return True

def test_backend():
    """Test if backend is responding"""
    print("🧪 Testing backend connectivity...")
    
    try:
        response = requests.get(
            "http://34.202.215.209:8000/api/imperium/agents",
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Backend is responding correctly")
            return True
        else:
            print(f"❌ Backend returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend connection failed: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Starting backend restart with GitHub fixes...")
    
    # Restart backend
    if not restart_backend():
        print("❌ Failed to restart backend")
        return
    
    # Test backend
    if test_backend():
        print("🎉 Backend is working with GitHub fixes applied!")
    else:
        print("⚠️ Backend may need more time to start or has issues")

if __name__ == "__main__":
    main() 