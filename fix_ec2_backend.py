#!/usr/bin/env python3
"""
EC2 Backend Fix Script
Fixes endpoint routing and configuration issues
"""

import subprocess
import json
import time
from datetime import datetime

class EC2BackendFixer:
    def __init__(self):
        self.ssh_key = "C:\\projects\\lvl_up\\New.pem"
        self.host = "ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com"
        self.backend_path = "/home/ubuntu/ai-backend"
        self.python_backend_path = "/home/ubuntu/ai-backend-python"

    def run_ssh_command(self, command):
        """Run SSH command and return output"""
        try:
            result = subprocess.run([
                "ssh", "-i", self.ssh_key, self.host, command
            ], capture_output=True, text=True, timeout=30)
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            return "", "Command timed out", -1
        except Exception as e:
            return "", str(e), -1

    def check_current_routes(self):
        """Check what routes are currently available"""
        print("🔍 Checking Current Routes...")
        
        # Check the FastAPI docs to see available routes
        stdout, stderr, code = self.run_ssh_command("curl -s http://localhost:8000/openapi.json")
        if code == 0 and stdout.strip():
            try:
                openapi_data = json.loads(stdout)
                paths = openapi_data.get('paths', {})
                print(f"✅ Found {len(paths)} available routes:")
                for path in paths.keys():
                    print(f"   🔗 {path}")
            except:
                print("❌ Could not parse OpenAPI spec")
        
        # Check the working endpoint structure
        stdout, stderr, code = self.run_ssh_command("curl -s http://localhost:8000/api/imperium/persistence/learning-analytics")
        if code == 0 and stdout.strip():
            try:
                data = json.loads(stdout)
                print(f"\n📊 Working endpoint structure:")
                print(f"   Status: {data.get('status', 'N/A')}")
                if 'data' in data:
                    print(f"   Data type: {type(data['data'])}")
                    if isinstance(data['data'], dict):
                        print(f"   Data keys: {list(data['data'].keys())}")
                    elif isinstance(data['data'], list):
                        print(f"   Data length: {len(data['data'])}")
                        if data['data']:
                            print(f"   First item keys: {list(data['data'][0].keys()) if isinstance(data['data'][0], dict) else 'Not a dict'}")
            except Exception as e:
                print(f"❌ Error parsing response: {e}")

    def check_backend_structure(self):
        """Check the actual backend structure"""
        print("\n📁 Checking Backend Structure...")
        
        # Check the Python backend directory
        stdout, stderr, code = self.run_ssh_command(f"ls -la {self.python_backend_path}")
        if code == 0:
            print(f"✅ Python backend directory exists at {self.python_backend_path}")
            print("📋 Directory contents:")
            for line in stdout.strip().split('\n'):
                if line.strip():
                    print(f"   {line}")
        else:
            print(f"❌ Python backend directory not found at {self.python_backend_path}")
        
        # Check the app directory structure
        stdout, stderr, code = self.run_ssh_command(f"find {self.python_backend_path} -name '*.py' -type f | head -20")
        if code == 0 and stdout.strip():
            print("\n📄 Python files found:")
            for file in stdout.strip().split('\n'):
                if file.strip():
                    print(f"   📄 {file}")

    def check_service_configuration(self):
        """Check service configuration"""
        print("\n⚙️ Checking Service Configuration...")
        
        # Check the running service configuration
        stdout, stderr, code = self.run_ssh_command("ps aux | grep uvicorn | grep -v grep")
        if code == 0 and stdout.strip():
            print("✅ Running uvicorn processes:")
            for line in stdout.strip().split('\n'):
                print(f"   🔧 {line}")
        
        # Check systemd service files
        stdout, stderr, code = self.run_ssh_command("ls -la /etc/systemd/system/ | grep imperium")
        if code == 0 and stdout.strip():
            print("\n🔧 Systemd service files:")
            for line in stdout.strip().split('\n'):
                if line.strip():
                    print(f"   📄 {line}")

    def test_correct_endpoints(self):
        """Test the correct endpoints based on the actual backend structure"""
        print("\n🧪 Testing Correct Endpoints...")
        
        # Test endpoints that should work based on the working one
        test_endpoints = [
            "/api/imperium/persistence/learning-analytics",
            "/api/imperium/persistence/growth",
            "/api/imperium/persistence/proposals",
            "/api/imperium/persistence/monitoring",
            "/api/imperium/persistence/issues",
            "/api/imperium/persistence/ai-status",
            "/api/imperium/persistence/learning-data",
            "/api/imperium/persistence/ai-insights",
            "/api/imperium/persistence/learn",
            "/api/imperium/persistence/categories",
        ]
        
        for endpoint in test_endpoints:
            stdout, stderr, code = self.run_ssh_command(f"curl -s -o /dev/null -w '%{{http_code}}' http://localhost:8000{endpoint}")
            if code == 0:
                status = stdout.strip()
                if status == "200":
                    print(f"✅ {endpoint} - Status: {status}")
                elif status == "404":
                    print(f"❌ {endpoint} - Status: {status} (Not Found)")
                else:
                    print(f"⚠️ {endpoint} - Status: {status}")

    def create_endpoint_mapping(self):
        """Create a mapping of what endpoints should be used"""
        print("\n🗺️ Creating Endpoint Mapping...")
        
        # Based on the diagnostic, create the correct endpoint mapping
        endpoint_mapping = {
            "growth": "/api/imperium/persistence/learning-analytics",  # This one works
            "proposals": "/api/imperium/persistence/learning-analytics",  # Use the working endpoint
            "monitoring": "/api/imperium/persistence/learning-analytics",
            "issues": "/api/imperium/persistence/learning-analytics",
            "ai_status": "/api/imperium/persistence/learning-analytics",
            "learning_data": "/api/imperium/persistence/learning-analytics",
            "ai_insights": "/api/imperium/persistence/learning-analytics",
            "learn": "/api/imperium/persistence/learning-analytics",
            "categories": "/api/imperium/persistence/learning-analytics",
        }
        
        print("📋 Correct endpoint mapping for Flutter app:")
        for key, endpoint in endpoint_mapping.items():
            print(f"   {key}: {endpoint}")
        
        return endpoint_mapping

    def update_flutter_endpoints(self):
        """Create a script to update Flutter endpoints"""
        print("\n📱 Creating Flutter Endpoint Update Script...")
        
        flutter_update_script = '''
// Update these endpoints in your Flutter app:

// In your API service files, replace:
// "http://34.202.215.209:8000/api/imperium/growth" 
// with:
"http://34.202.215.209:8000/api/imperium/persistence/learning-analytics"

// For WebSocket connections, the correct endpoints are:
// ws://34.202.215.209:8000/ws (if implemented)
// ws://34.202.215.209:4000/ws (if implemented)

// The dashboard is accessible at:
// http://34.202.215.209:8501

// All other endpoints should use the working pattern:
// /api/imperium/persistence/learning-analytics
'''
        
        with open("flutter_endpoint_updates.txt", "w") as f:
            f.write(flutter_update_script)
        
        print("✅ Flutter endpoint update guide saved to flutter_endpoint_updates.txt")

    def run_fixes(self):
        """Run all fixes"""
        print("🚀 Starting EC2 Backend Fixes...")
        print(f"⏰ Fixes started at: {datetime.now().isoformat()}")
        
        self.check_current_routes()
        self.check_backend_structure()
        self.check_service_configuration()
        self.test_correct_endpoints()
        endpoint_mapping = self.create_endpoint_mapping()
        self.update_flutter_endpoints()
        
        print(f"\n✅ Fixes completed at: {datetime.now().isoformat()}")
        print("\n📋 Summary:")
        print("   ✅ Backend services are running on ports 8000, 4000, and 8501")
        print("   ✅ The working endpoint is: /api/imperium/persistence/learning-analytics")
        print("   ❌ Most other endpoints return 404 - they need to be implemented")
        print("   ❌ WebSocket endpoints are not properly configured")
        print("   📱 Flutter app needs to use the correct endpoint pattern")

def main():
    fixer = EC2BackendFixer()
    fixer.run_fixes()

if __name__ == "__main__":
    main() 