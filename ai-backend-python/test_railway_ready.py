#!/usr/bin/env python3
"""
Railway Deployment Readiness Test
This script validates that the ai-backend is properly configured for Railway deployment.
"""

import os
import sys
import asyncio
import subprocess
import time
import requests
from pathlib import Path

def check_configuration_files():
    """Check that all necessary configuration files exist and are properly configured"""
    print("🔍 Checking configuration files...")
    
    required_files = [
        "main_unified.py",
        "requirements.txt", 
        "railway.toml",
        "nixpacks.toml",
        "Dockerfile",
        "Procfile"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    print("✅ All required configuration files exist")
    return True

def check_railway_toml():
    """Validate railway.toml configuration"""
    print("🔍 Checking railway.toml configuration...")
    
    try:
        with open("railway.toml", "r") as f:
            content = f.read()
            
        # Check for critical configurations
        checks = [
            ("$PORT" in content, "Uses $PORT environment variable"),
            ("healthcheckPath" in content, "Has health check path defined"),
            ("uvicorn main_unified:app" in content, "Uses correct uvicorn command"),
            ("--host 0.0.0.0" in content, "Binds to all interfaces"),
        ]
        
        all_passed = True
        for check, description in checks:
            if check:
                print(f"  ✅ {description}")
            else:
                print(f"  ❌ {description}")
                all_passed = False
                
        return all_passed
        
    except Exception as e:
        print(f"❌ Error reading railway.toml: {e}")
        return False

def check_main_unified():
    """Check that main_unified.py has required endpoints"""
    print("🔍 Checking main_unified.py...")
    
    try:
        with open("main_unified.py", "r", encoding="utf-8") as f:
            content = f.read()
            
        # Check for critical endpoints
        checks = [
            ('@app.get("/ping")' in content, "Has /ping endpoint"),
            ('@app.get("/health")' in content, "Has /health endpoint"),
            ('os.environ.get("PORT")' in content, "Reads PORT environment variable"),
            ('uvicorn.run(' in content, "Has uvicorn startup code"),
        ]
        
        all_passed = True
        for check, description in checks:
            if check:
                print(f"  ✅ {description}")
            else:
                print(f"  ❌ {description}")
                all_passed = False
                
        return all_passed
        
    except Exception as e:
        print(f"❌ Error reading main_unified.py: {e}")
        return False

def test_local_startup():
    """Test that the application can start locally"""
    print("🚀 Testing local startup...")
    
    # Set a test port
    os.environ["PORT"] = "8000"
    
    try:
        # Start the server in background
        print("  Starting server...")
        process = subprocess.Popen([
            sys.executable, "-c", 
            "import uvicorn; uvicorn.run('main_unified:app', host='0.0.0.0', port=8000, log_level='info')"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(3)
        
        # Test endpoints
        endpoints_to_test = ["/ping", "/health", "/api/health"]
        all_passed = True
        
        for endpoint in endpoints_to_test:
            try:
                response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
                if response.status_code == 200:
                    print(f"  ✅ {endpoint} responds correctly")
                else:
                    print(f"  ❌ {endpoint} returned status {response.status_code}")
                    all_passed = False
            except requests.exceptions.RequestException as e:
                print(f"  ❌ {endpoint} failed: {e}")
                all_passed = False
        
        # Stop the server
        process.terminate()
        process.wait(timeout=5)
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Local startup test failed: {e}")
        try:
            process.terminate()
        except:
            pass
        return False

def check_dependencies():
    """Check that all required dependencies are in requirements.txt"""
    print("🔍 Checking dependencies...")
    
    try:
        with open("requirements.txt", "r") as f:
            requirements = f.read().lower()
            
        critical_deps = [
            "fastapi",
            "uvicorn", 
            "pydantic",
            "sqlalchemy",
            "asyncpg"
        ]
        
        missing_deps = []
        for dep in critical_deps:
            if dep not in requirements:
                missing_deps.append(dep)
        
        if missing_deps:
            print(f"❌ Missing critical dependencies: {missing_deps}")
            return False
        
        print("✅ All critical dependencies present")
        return True
        
    except Exception as e:
        print(f"❌ Error checking dependencies: {e}")
        return False

def main():
    """Run all Railway readiness tests"""
    print("🚀 Railway Deployment Readiness Test")
    print("=" * 50)
    
    tests = [
        ("Configuration Files", check_configuration_files),
        ("Railway.toml", check_railway_toml),
        ("Main Unified", check_main_unified),
        ("Dependencies", check_dependencies),
        ("Local Startup", test_local_startup),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        result = test_func()
        results.append(result)
        
    print("\n" + "=" * 50)
    print("🎯 FINAL RESULTS:")
    
    if all(results):
        print("✅ ALL TESTS PASSED - READY FOR RAILWAY DEPLOYMENT!")
        print("\nNext steps:")
        print("1. Commit these changes to git")
        print("2. Push to your Railway-connected repository")
        print("3. Railway should deploy successfully")
        return 0
    else:
        print("❌ SOME TESTS FAILED - NOT READY FOR DEPLOYMENT")
        print("\nPlease fix the issues above before deploying to Railway")
        return 1

if __name__ == "__main__":
    sys.exit(main())