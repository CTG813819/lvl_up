#!/usr/bin/env python3
"""
Railway Deployment Fix Script
Helps diagnose and fix common Railway deployment issues
"""

import os
import sys
import subprocess
import requests
import json
from pathlib import Path

def check_railway_deployment():
    """Check if Railway deployment is working"""
    print("🔍 Checking Railway deployment...")
    
    railway_url = "https://lvlup-production.up.railway.app"
    test_endpoints = [
        "/health",
        "/api/health", 
        "/api/status"
    ]
    
    for endpoint in test_endpoints:
        try:
            response = requests.get(f"{railway_url}{endpoint}", timeout=10)
            print(f"✅ {endpoint}: {response.status_code}")
            if response.status_code == 200:
                print(f"📄 Response: {response.text[:100]}...")
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")
    
    print("\n📋 Analysis:")
    print("• If all endpoints return 404: FastAPI app not starting")
    print("• If connection errors: Railway service not running")
    print("• If some work: Partial deployment issue")

def check_local_app():
    """Check if the local app can start properly"""
    print("\n🔍 Testing local app startup...")
    
    # Check if we're in the right directory
    if not Path("app/main.py").exists():
        print("❌ app/main.py not found. Make sure you're in ai-backend-python directory")
        return False
    
    # Check if requirements are installed
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI and uvicorn available")
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Run: pip install -r requirements.txt")
        return False
    
    # Check environment variables
    required_env_vars = ["DATABASE_URL"]
    missing_vars = []
    
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️ Missing environment variables: {missing_vars}")
        print("Set these in Railway dashboard or .env file")
    else:
        print("✅ Environment variables look good")
    
    return True

def generate_railway_fix_commands():
    """Generate commands to fix Railway deployment"""
    print("\n🔧 Railway Fix Commands:")
    print("\n1. Check Railway logs:")
    print("   • Go to Railway dashboard")
    print("   • Click on your service")
    print("   • Check 'Deployments' tab for errors")
    
    print("\n2. Verify environment variables in Railway:")
    print("   • Go to your service settings")
    print("   • Check 'Variables' tab")
    print("   • Ensure DATABASE_URL is set")
    
    print("\n3. Force redeploy:")
    print("   • In Railway dashboard, click 'Deploy'")
    print("   • Or push to your connected Git repository")
    
    print("\n4. Check Procfile:")
    print("   • Ensure it contains: web: python start.py")
    print("   • Verify start.py exists and is correct")
    
    print("\n5. Test locally:")
    print("   • cd ai-backend-python")
    print("   • python start.py")
    print("   • Should start on http://localhost:8000")

def create_debug_script():
    """Create a debug script for Railway"""
    debug_script = """#!/usr/bin/env python3
import os
import sys
import traceback

print("🔍 Railway Debug Script")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")
print(f"Environment variables: {dict(os.environ)}")

try:
    print("\\n📦 Testing imports...")
    import fastapi
    import uvicorn
    import sqlalchemy
    print("✅ All imports successful")
except Exception as e:
    print(f"❌ Import error: {e}")
    traceback.print_exc()

try:
    print("\\n🚀 Testing app startup...")
    from app.main import app
    print("✅ App import successful")
except Exception as e:
    print(f"❌ App import error: {e}")
    traceback.print_exc()

print("\\n🎯 Debug complete")
"""
    
    with open("railway_debug.py", "w") as f:
        f.write(debug_script)
    
    print("✅ Created railway_debug.py")
    print("Run this on Railway to debug startup issues")

def main():
    print("🚀 Railway Deployment Fix Script")
    print("=" * 50)
    
    # Check current deployment
    check_railway_deployment()
    
    # Check local setup
    if check_local_app():
        print("✅ Local setup looks good")
    else:
        print("❌ Local setup has issues")
    
    # Generate fix commands
    generate_railway_fix_commands()
    
    # Create debug script
    create_debug_script()
    
    print("\n🎯 Next Steps:")
    print("1. Check Railway dashboard for deployment errors")
    print("2. Verify environment variables are set")
    print("3. Test the app locally first")
    print("4. Use railway_debug.py to debug startup issues")

if __name__ == "__main__":
    main() 