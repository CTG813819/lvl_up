#!/usr/bin/env python3
"""
Test Conquest AI with bypassed validation
"""

import subprocess
import json

def run_ssh_command(command):
    """Run SSH command on EC2"""
    ssh_cmd = f'ssh -i "New.pem" ubuntu@34.202.215.209 "{command}"'
    result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr

def test_conquest_with_timeout():
    """Test Conquest app creation with timeout"""
    print("🧪 Testing Conquest app creation with timeout...")
    
    # Test with timeout
    success, output, error = run_ssh_command("timeout 10 curl -X POST http://localhost:4000/api/conquest/create-app -H 'Content-Type: application/json' -d @/home/ubuntu/test_app_request.json")
    
    if success:
        print("✅ Conquest app creation completed within timeout")
        print(f"Response: {output}")
        return True
    else:
        print("❌ Conquest app creation timed out or failed")
        print(f"Error: {error}")
        return False

def test_conquest_statistics_after():
    """Test Conquest statistics after app creation attempt"""
    print("\n🧪 Testing Conquest statistics after app creation...")
    
    success, output, error = run_ssh_command("curl -s http://localhost:4000/api/conquest/statistics")
    if success and output.strip():
        print("✅ Conquest statistics after app creation:")
        print(f"Response: {output}")
    else:
        print(f"❌ Failed to get statistics: {error}")

def test_imperium_trigger():
    """Test Imperium trigger to see if it generates proposals"""
    print("\n🧪 Testing Imperium trigger...")
    
    # Trigger Imperium scan
    success, output, error = run_ssh_command("curl -X POST http://localhost:4000/api/imperium/trigger-scan")
    if success:
        print("✅ Imperium scan triggered")
        print(f"Response: {output}")
    else:
        print(f"❌ Imperium scan failed: {error}")
    
    # Wait a moment and check status
    import time
    time.sleep(2)
    
    success, output, error = run_ssh_command("curl -s http://localhost:4000/api/imperium/status")
    if success and output.strip():
        print("✅ Imperium status after trigger:")
        print(f"Response: {output}")

def main():
    """Main test function"""
    print("🚀 Testing Conquest AI with bypassed validation...")
    
    test_conquest_with_timeout()
    test_conquest_statistics_after()
    test_imperium_trigger()
    
    print("\n📊 Test Summary:")
    print("✅ Basic functionality tested")
    print("⚠️ Conquest app creation may need optimization")

if __name__ == "__main__":
    main() 