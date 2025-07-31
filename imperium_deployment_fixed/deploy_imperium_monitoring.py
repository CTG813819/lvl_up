#!/usr/bin/env python3
"""
Imperium Monitoring Service Deployment Script
Deploys and starts the Imperium monitoring service for audit data collection
"""

import os
import sys
import subprocess
import time
import json
import requests
from datetime import datetime

def check_backend_health():
    """Check if backend is running and healthy"""
    try:
        response = requests.get('http://localhost:4000/health', timeout=10)
        if response.status_code == 200:
            print("✅ Backend is healthy")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend health check failed: {e}")
        return False

def start_monitoring_service():
    """Start the monitoring service"""
    print("🚀 Starting Imperium Monitoring Service...")
    
    # Create monitoring service file
    service_content = """[Unit]
Description=Imperium Monitoring Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
ExecStart=/usr/bin/python3 /home/ubuntu/ai-backend-python/imperium_monitoring_service.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    # Write service file
    with open('/etc/systemd/system/imperium-monitoring.service', 'w') as f:
        f.write(service_content)
    
    # Reload systemd and start service
    subprocess.run(['sudo', 'systemctl', 'daemon-reload'])
    subprocess.run(['sudo', 'systemctl', 'enable', 'imperium-monitoring.service'])
    subprocess.run(['sudo', 'systemctl', 'start', 'imperium-monitoring.service'])
    
    # Check if service started successfully
    time.sleep(5)
    result = subprocess.run(['sudo', 'systemctl', 'is-active', 'imperium-monitoring.service'], 
                          capture_output=True, text=True)
    
    if result.stdout.strip() == 'active':
        print("✅ Imperium Monitoring Service started successfully")
        return True
    else:
        print(f"❌ Failed to start monitoring service: {result.stderr}")
        return False

def test_audit_endpoints():
    """Test audit endpoints to ensure they're working"""
    print("🔍 Testing audit endpoints...")
    
    endpoints = [
        'http://localhost:4000/api/imperium/status',
        'http://localhost:4000/api/guardian/health-check',
        'http://localhost:4000/api/imperium/persistence/learning-analytics',
    ]
    
    results = {}
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=10)
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK")
                results[endpoint] = {
                    'status': 'ok',
                    'status_code': response.status_code,
                    'data': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                }
            else:
                print(f"❌ {endpoint} - Status {response.status_code}")
                results[endpoint] = {
                    'status': 'error',
                    'status_code': response.status_code,
                    'error': response.text
                }
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")
            results[endpoint] = {
                'status': 'error',
                'error': str(e)
            }
    
    return results

def create_audit_test_script():
    """Create a test script to verify audit functionality"""
    test_script = """#!/usr/bin/env python3
import requests
import json
from datetime import datetime

def test_audit_system():
    base_url = "http://localhost:4000"
    
    print("🔍 Testing Imperium/Guardian Audit System...")
    
    # Test Imperium status
    try:
        response = requests.get(f"{base_url}/api/imperium/status")
        print(f"Imperium Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Imperium Data: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"Imperium test failed: {e}")
    
    # Test Guardian health check
    try:
        response = requests.post(f"{base_url}/api/guardian/health-check")
        print(f"Guardian Health: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Guardian Data: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"Guardian test failed: {e}")
    
    # Test monitoring data
    try:
        response = requests.get(f"{base_url}/api/imperium/persistence/learning-analytics")
        print(f"Monitoring Data: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Monitoring Data: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"Monitoring test failed: {e}")

if __name__ == "__main__":
    test_audit_system()
"""
    
    with open('/home/ubuntu/ai-backend-python/test_audit_system.py', 'w') as f:
        f.write(test_script)
    
    # Make executable
    os.chmod('/home/ubuntu/ai-backend-python/test_audit_system.py', 0o755)
    print("✅ Created audit test script")

def main():
    """Main deployment function"""
    print("🚀 Imperium Monitoring Service Deployment")
    print("=" * 50)
    
    # Check backend health
    if not check_backend_health():
        print("❌ Backend is not healthy. Please start the backend first.")
        return False
    
    # Start monitoring service
    if not start_monitoring_service():
        print("❌ Failed to start monitoring service")
        return False
    
    # Create test script
    create_audit_test_script()
    
    # Test endpoints
    print("\n🔍 Testing audit endpoints...")
    results = test_audit_endpoints()
    
    # Save results
    with open('/home/ubuntu/ai-backend-python/audit_test_results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'results': results
        }, f, indent=2)
    
    print("\n✅ Deployment completed!")
    print("📊 Audit test results saved to audit_test_results.json")
    print("🧪 Run test_audit_system.py to test audit functionality")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 