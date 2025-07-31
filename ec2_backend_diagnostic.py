#!/usr/bin/env python3
"""
EC2 Backend Diagnostic Script
Checks backend services and helps fix issues
"""

import subprocess
import json
import time
from datetime import datetime

class EC2BackendDiagnostic:
    def __init__(self):
        self.ssh_key = "C:\\projects\\lvl_up\\New.pem"
        self.host = "ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com"
        self.backend_path = "/home/ubuntu/ai-backend"

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

    def check_backend_services(self):
        """Check what backend services are running"""
        print("🔍 Checking Backend Services...")
        
        # Check running processes
        stdout, stderr, code = self.run_ssh_command("ps aux | grep -E '(python|uvicorn|streamlit)' | grep -v grep")
        if code == 0 and stdout.strip():
            print("✅ Found running Python processes:")
            for line in stdout.strip().split('\n'):
                print(f"   📋 {line}")
        else:
            print("❌ No Python processes found running")
        
        # Check systemd services
        stdout, stderr, code = self.run_ssh_command("systemctl list-units --type=service --state=running | grep -E '(imperium|backend|streamlit)'")
        if code == 0 and stdout.strip():
            print("✅ Found running systemd services:")
            for line in stdout.strip().split('\n'):
                print(f"   🔧 {line}")
        else:
            print("❌ No relevant systemd services found")
        
        # Check listening ports
        stdout, stderr, code = self.run_ssh_command("netstat -tlnp | grep -E ':(8000|4000|8501)'")
        if code == 0 and stdout.strip():
            print("✅ Found listening ports:")
            for line in stdout.strip().split('\n'):
                print(f"   🌐 {line}")
        else:
            print("❌ No services listening on expected ports")

    def check_backend_files(self):
        """Check backend file structure"""
        print("\n📁 Checking Backend Files...")
        
        # Check if backend directory exists
        stdout, stderr, code = self.run_ssh_command(f"ls -la {self.backend_path}")
        if code == 0:
            print(f"✅ Backend directory exists at {self.backend_path}")
            print("📋 Directory contents:")
            for line in stdout.strip().split('\n'):
                if line.strip():
                    print(f"   {line}")
        else:
            print(f"❌ Backend directory not found at {self.backend_path}")
        
        # Check for main.py
        stdout, stderr, code = self.run_ssh_command(f"ls -la {self.backend_path}/main.py")
        if code == 0:
            print("✅ main.py found")
        else:
            print("❌ main.py not found")
        
        # Check for requirements.txt
        stdout, stderr, code = self.run_ssh_command(f"ls -la {self.backend_path}/requirements.txt")
        if code == 0:
            print("✅ requirements.txt found")
        else:
            print("❌ requirements.txt not found")

    def check_backend_logs(self):
        """Check backend logs"""
        print("\n📋 Checking Backend Logs...")
        
        # Check system logs
        stdout, stderr, code = self.run_ssh_command("journalctl -u imperium-backend --no-pager -n 20")
        if code == 0 and stdout.strip():
            print("📋 System logs for imperium-backend:")
            for line in stdout.strip().split('\n'):
                print(f"   {line}")
        else:
            print("❌ No system logs found for imperium-backend")
        
        # Check for log files in backend directory
        stdout, stderr, code = self.run_ssh_command(f"find {self.backend_path} -name '*.log' -type f")
        if code == 0 and stdout.strip():
            print("📋 Log files found:")
            for log_file in stdout.strip().split('\n'):
                if log_file.strip():
                    print(f"   📄 {log_file}")
                    # Show last few lines
                    stdout2, stderr2, code2 = self.run_ssh_command(f"tail -10 '{log_file}'")
                    if code2 == 0 and stdout2.strip():
                        print("   Recent log entries:")
                        for line in stdout2.strip().split('\n'):
                            print(f"      {line}")
        else:
            print("❌ No log files found")

    def check_backend_config(self):
        """Check backend configuration"""
        print("\n⚙️ Checking Backend Configuration...")
        
        # Check if there's a config file
        stdout, stderr, code = self.run_ssh_command(f"find {self.backend_path} -name '*.py' -exec grep -l 'app = FastAPI\|uvicorn.run' {{}} \\;")
        if code == 0 and stdout.strip():
            print("✅ Found FastAPI/uvicorn configuration in:")
            for file in stdout.strip().split('\n'):
                if file.strip():
                    print(f"   📄 {file}")
                    # Show relevant lines
                    stdout2, stderr2, code2 = self.run_ssh_command(f"grep -n 'app = FastAPI\|uvicorn.run' '{file}'")
                    if code2 == 0 and stdout2.strip():
                        for line in stdout2.strip().split('\n'):
                            print(f"      {line}")
        else:
            print("❌ No FastAPI/uvicorn configuration found")

    def check_available_endpoints(self):
        """Check what endpoints are actually available"""
        print("\n🔗 Checking Available Endpoints...")
        
        # Test the working endpoint to see what's available
        stdout, stderr, code = self.run_ssh_command(f"curl -s http://localhost:8000/api/imperium/persistence/learning-analytics")
        if code == 0 and stdout.strip():
            print("✅ Working endpoint response:")
            try:
                data = json.loads(stdout)
                print(f"   📊 Response keys: {list(data.keys())}")
                if 'data' in data:
                    print(f"   📈 Data array length: {len(data['data']) if isinstance(data['data'], list) else 'Not a list'}")
            except:
                print(f"   📄 Raw response: {stdout[:200]}...")
        
        # Check if there are any other working endpoints
        test_endpoints = [
            "/",
            "/docs",
            "/openapi.json",
            "/api",
            "/api/imperium",
            "/api/imperium/persistence",
        ]
        
        for endpoint in test_endpoints:
            stdout, stderr, code = self.run_ssh_command(f"curl -s -o /dev/null -w '%{{http_code}}' http://localhost:8000{endpoint}")
            if code == 0 and stdout.strip() != "000":
                print(f"✅ Endpoint {endpoint} returns status {stdout.strip()}")

    def suggest_fixes(self):
        """Suggest fixes based on findings"""
        print("\n🔧 Suggested Fixes:")
        
        print("1. 🚀 Start the backend service:")
        print("   ssh -i New.pem ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com")
        print("   cd /home/ubuntu/ai-backend")
        print("   python3 -m uvicorn main:app --host 0.0.0.0 --port 8000")
        
        print("\n2. 📊 Start the Streamlit dashboard:")
        print("   streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0")
        
        print("\n3. 🔧 Create a systemd service for persistence:")
        print("   sudo nano /etc/systemd/system/imperium-backend.service")
        print("   [Unit]")
        print("   Description=Imperium Backend")
        print("   After=network.target")
        print("   [Service]")
        print("   Type=simple")
        print("   User=ubuntu")
        print("   WorkingDirectory=/home/ubuntu/ai-backend")
        print("   ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000")
        print("   Restart=always")
        print("   [Install]")
        print("   WantedBy=multi-user.target")
        
        print("\n4. 🔄 Enable and start the service:")
        print("   sudo systemctl enable imperium-backend")
        print("   sudo systemctl start imperium-backend")
        print("   sudo systemctl status imperium-backend")

    def run_diagnostic(self):
        """Run complete diagnostic"""
        print("🚀 Starting EC2 Backend Diagnostic...")
        print(f"⏰ Diagnostic started at: {datetime.now().isoformat()}")
        
        self.check_backend_services()
        self.check_backend_files()
        self.check_backend_logs()
        self.check_backend_config()
        self.check_available_endpoints()
        self.suggest_fixes()
        
        print(f"\n✅ Diagnostic completed at: {datetime.now().isoformat()}")

def main():
    diagnostic = EC2BackendDiagnostic()
    diagnostic.run_diagnostic()

if __name__ == "__main__":
    main() 