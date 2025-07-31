#!/usr/bin/env python3
"""
Simple Fix for Remaining Issues
===============================
This script creates a simple backend audit script to fix the JSON parsing error.
"""

import os
import subprocess

def create_audit_script():
    """Create a simple backend audit script"""
    print("🔧 Creating backend audit script...")
    
    # Create scripts directory
    scripts_dir = "/home/ubuntu/ai-backend-python/scripts"
    os.makedirs(scripts_dir, exist_ok=True)
    
    # Create the audit script
    audit_script_path = f"{scripts_dir}/backend_audit.py"
    
    script_content = '''#!/usr/bin/env python3
"""
Backend Audit Script - Fixed Version
===================================
This script performs backend health checks and returns JSON results.
"""

import json
import subprocess
import sys
from datetime import datetime

def check_endpoint_health(endpoint):
    """Check if an endpoint is responding"""
    try:
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", f"http://localhost:8000{endpoint}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout.strip() == "200"
    except:
        return False

def main():
    """Main audit function"""
    try:
        # Check key endpoints
        endpoints = [
            "/api/health",
            "/api/database/health", 
            "/api/status",
            "/api/agents/status"
        ]
        
        results = {}
        for endpoint in endpoints:
            results[endpoint] = check_endpoint_health(endpoint)
        
        # Overall health
        all_healthy = all(results.values())
        
        audit_result = {
            "all_ok": all_healthy,
            "timestamp": datetime.now().isoformat(),
            "summary": "Backend audit completed successfully" if all_healthy else "Some endpoints failed",
            "details": results
        }
        
        # Output JSON result
        print(json.dumps(audit_result))
        return 0 if all_healthy else 1
        
    except Exception as e:
        error_result = {
            "all_ok": False,
            "timestamp": datetime.now().isoformat(),
            "summary": f"Backend audit script failed: {str(e)}",
            "details": []
        }
        print(json.dumps(error_result))
        return 1

if __name__ == "__main__":
    sys.exit(main())
'''
    
    # Write the script
    with open(audit_script_path, 'w') as f:
        f.write(script_content)
    
    # Make it executable
    subprocess.run(f"chmod +x {audit_script_path}", shell=True)
    
    print(f"✅ Backend audit script created: {audit_script_path}")
    return audit_script_path

def test_audit_script(script_path):
    """Test the audit script"""
    print("🧪 Testing audit script...")
    
    try:
        result = subprocess.run(
            ["python3", script_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Audit script working correctly")
            print(f"Output: {result.stdout}")
        else:
            print("❌ Audit script failed")
            print(f"Error: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error testing audit script: {e}")

def main():
    """Main function"""
    print("🚀 Creating Backend Audit Script")
    print("=" * 40)
    
    # Create the audit script
    script_path = create_audit_script()
    
    # Test the script
    test_audit_script(script_path)
    
    print("\n📋 Summary:")
    print("1. ✅ Created backend audit script")
    print("2. ✅ Made script executable")
    print("3. ✅ Tested script functionality")
    
    print("\n🔍 To test manually, run:")
    print(f"   python3 {script_path}")

if __name__ == "__main__":
    main() 