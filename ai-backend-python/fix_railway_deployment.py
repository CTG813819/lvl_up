#!/usr/bin/env python3
"""
Fix Railway deployment issues and ensure system runs properly
"""

import os
import sys
import subprocess
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