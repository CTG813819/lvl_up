#!/usr/bin/env python3
"""
<<<<<<< HEAD
Fix Railway deployment issues and ensure system runs properly
=======
Railway Deployment Fix Script
Helps diagnose and fix common Railway deployment issues
>>>>>>> d1b3e6353067c4166fd183c12c225678794528f5
"""

import os
import sys
import subprocess
<<<<<<< HEAD
import json
from pathlib import Path

def fix_railway_deployment():
    """Fix Railway deployment configuration and issues"""
    print("🔧 Fixing Railway deployment issues...")
    
    # 1. Fix the start.py file to use correct module path
    start_content = '''#!/usr/bin/env python3
"""
Startup script for AI Backend with scikit-learn
"""

import os
import sys
import uvicorn

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting AI Backend on port {port}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
'''
    
    with open("start.py", "w") as f:
        f.write(start_content)
    
    print("✅ Fixed start.py module path")
    
    # 2. Update railway.json configuration
    railway_config = {
        "$schema": "https://railway.app/railway.schema.json",
        "build": {
            "builder": "NIXPACKS"
        },
        "deploy": {
            "startCommand": "python start.py",
            "healthcheckPath": "/health",
            "healthcheckTimeout": 300,
            "restartPolicyType": "ON_FAILURE",
            "restartPolicyMaxRetries": 10,
            "numReplicas": 1,
            "environment": {
                "LOG_LEVEL": "INFO",
                "ENABLE_AI_LOGGING": "true",
                "ENABLE_PROJECT_HORUS_LOGS": "true",
                "ENABLE_TRAINING_GROUND_LOGS": "true",
                "ENABLE_ENHANCED_ADVERSARIAL_LOGS": "true",
                "ENABLE_CUSTODY_PROTOCOL_LOGS": "true",
                "ENABLE_DYNAMIC_TEST_GENERATION": "true",
                "ENABLE_VARIED_SCORING": "true",
                "ENABLE_UNIQUE_QUESTIONS": "true",
                "PYTHONPATH": ".",
                "PYTHONIOENCODING": "utf-8"
            }
        }
    }
    
    with open("railway.json", "w") as f:
        json.dump(railway_config, f, indent=2)
    
    print("✅ Updated railway.json configuration")
    
    # 3. Create a proper Procfile
    procfile_content = "web: python start.py"
    with open("Procfile", "w") as f:
        f.write(procfile_content)
    
    print("✅ Created Procfile")
    
    # 4. Update requirements.txt to ensure all dependencies are included
    requirements = [
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "sqlalchemy==2.0.23",
        "asyncpg==0.29.0",
        "psycopg2-binary==2.9.9",
        "python-dotenv==1.0.0",
        "structlog==23.2.0",
        "requests==2.31.0",
        "scikit-learn==1.3.2",
        "numpy==1.24.3",
        "pandas==2.0.3",
        "python-multipart==0.0.6",
        "websockets==12.0",
        "aiofiles==23.2.1",
        "python-jose[cryptography]==3.3.0",
        "passlib[bcrypt]==1.7.4",
        "python-dateutil==2.8.2",
        "pydantic==2.5.0",
        "pydantic-settings==2.1.0",
        "alembic==1.12.1",
        "redis==5.0.1",
        "celery==5.3.4",
        "flower==2.0.1",
        "prometheus-client==0.19.0",
        "sentry-sdk[fastapi]==1.38.0",
        "httpx==0.25.2",
        "tenacity==8.2.3",
        "cachetools==5.3.2",
        "python-json-logger==2.0.7"
    ]
    
    with open("requirements.txt", "w") as f:
        f.write("\n".join(requirements))
    
    print("✅ Updated requirements.txt")
    
    # 5. Create a runtime.txt file
    runtime_content = "python-3.11.7"
    with open("runtime.txt", "w") as f:
        f.write(runtime_content)
    
    print("✅ Created runtime.txt")
    
    # 6. Create a .env.example file for Railway
    env_example = """# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/dbname

# AI Configuration
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Logging Configuration
LOG_LEVEL=INFO
ENABLE_AI_LOGGING=true
ENABLE_PROJECT_HORUS_LOGS=true
ENABLE_TRAINING_GROUND_LOGS=true
ENABLE_ENHANCED_ADVERSARIAL_LOGS=true
ENABLE_CUSTODY_PROTOCOL_LOGS=true
ENABLE_DYNAMIC_TEST_GENERATION=true
ENABLE_VARIED_SCORING=true
ENABLE_UNIQUE_QUESTIONS=true

# Python Configuration
PYTHONPATH=.
PYTHONIOENCODING=utf-8

# Railway Configuration
PORT=8000
"""
    
    with open("env.example", "w") as f:
        f.write(env_example)
    
    print("✅ Created env.example")
    
    # 7. Create a deployment verification script
    verify_script = '''#!/usr/bin/env python3
"""
Verify Railway deployment is working correctly
"""

import requests
import time
import sys

def verify_deployment():
    """Verify the Railway deployment is working"""
    base_url = "https://ai-backend-python-production.up.railway.app"
    
    print("🔍 Verifying Railway deployment...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {str(e)}")
        return False
    
    # Test AI endpoints
    ai_endpoints = ["/api/ai/imperium", "/api/ai/guardian", "/api/ai/sandbox", "/api/ai/conquest"]
    
    working_endpoints = 0
    for endpoint in ai_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                working_endpoints += 1
                print(f"✅ {endpoint} working")
            else:
                print(f"❌ {endpoint} failed: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} error: {str(e)}")
    
    success_rate = working_endpoints / len(ai_endpoints)
    if success_rate > 0.5:
        print(f"✅ AI endpoints test passed ({working_endpoints}/{len(ai_endpoints)})")
        return True
    else:
        print(f"❌ AI endpoints test failed ({working_endpoints}/{len(ai_endpoints)})")
        return False

if __name__ == "__main__":
    success = verify_deployment()
    sys.exit(0 if success else 1)
'''
    
    with open("verify_railway_deployment.py", "w") as f:
        f.write(verify_script)
    
    print("✅ Created deployment verification script")
    
    print("\n🎯 Railway deployment fixes completed!")
    print("📋 Next steps:")
    print("  1. Commit and push changes to Railway")
    print("  2. Run: python verify_railway_deployment.py")
    print("  3. Check Railway logs for any remaining issues")
    
    return True

if __name__ == "__main__":
    fix_railway_deployment() 
=======
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
>>>>>>> d1b3e6353067c4166fd183c12c225678794528f5
