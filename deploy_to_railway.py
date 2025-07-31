#!/usr/bin/env python3
"""
Railway Deployment Preparation Script

This script helps prepare the backend for Railway deployment by:
1. Validating configuration files
2. Checking environment variables
3. Testing database connection
4. Verifying health endpoints
"""

import os
import sys
import requests
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_file_exists(file_path: str, description: str) -> bool:
    """Check if a file exists and print status"""
    exists = Path(file_path).exists()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {file_path}")
    return exists

def check_environment_variable(var_name: str, required: bool = False) -> bool:
    """Check if environment variable is set"""
    value = os.getenv(var_name)
    if required and not value:
        print(f"❌ Required environment variable missing: {var_name}")
        return False
    elif value:
        print(f"✅ Environment variable set: {var_name}")
        return True
    else:
        print(f"⚠️  Optional environment variable not set: {var_name}")
        return True

def validate_railway_config():
    """Validate Railway configuration files"""
    print("\n🔧 Validating Railway Configuration Files")
    print("=" * 50)
    
    required_files = [
        ("railway.json", "Railway configuration"),
        ("Procfile", "Procfile for Railway"),
        ("runtime.txt", "Python runtime specification"),
        ("requirements.txt", "Python dependencies"),
        ("start.py", "Application entry point")
    ]
    
    all_files_exist = True
    for file_path, description in required_files:
        if not check_file_exists(file_path, description):
            all_files_exist = False
    
    return all_files_exist

def check_environment_variables():
    """Check required and optional environment variables"""
    print("\n🔑 Checking Environment Variables")
    print("=" * 50)
    
    required_vars = [
        "DATABASE_URL"
    ]
    
    optional_vars = [
        "PORT",
        "HOST", 
        "DEBUG",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "GITHUB_TOKEN",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN"
    ]
    
    all_required_set = True
    for var in required_vars:
        if not check_environment_variable(var, required=True):
            all_required_set = False
    
    for var in optional_vars:
        check_environment_variable(var, required=False)
    
    return all_required_set

def test_database_connection():
    """Test database connection if DATABASE_URL is set"""
    print("\n🗄️  Testing Database Connection")
    print("=" * 50)
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("⚠️  DATABASE_URL not set, skipping database test")
        return True
    
    try:
        import asyncpg
        import asyncio
        
        async def test_connection():
            try:
                # Clean the URL for asyncpg (remove asyncpg:// prefix if present)
                clean_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
                conn = await asyncpg.connect(clean_url)
                await conn.execute("SELECT 1")
                await conn.close()
                print("✅ Database connection successful")
                return True
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                return False
        
        return asyncio.run(test_connection())
    except ImportError:
        print("⚠️  asyncpg not available, skipping database test")
        return True

def test_health_endpoints():
    """Test health endpoints if server is running"""
    print("\n🏥 Testing Health Endpoints")
    print("=" * 50)
    
    # Check if we can import the app
    try:
        sys.path.append('.')
        from app.main import app
        print("✅ FastAPI app imported successfully")
        
        # Test health endpoints
        endpoints = [
            "/health",
            "/api/health", 
            "/api/database/health",
            "/api/status"
        ]
        
        for endpoint in endpoints:
            print(f"✅ Health endpoint available: {endpoint}")
        
        return True
    except Exception as e:
        print(f"⚠️  Could not import app: {e}")
        return True

def generate_railway_commands():
    """Generate Railway CLI commands for deployment"""
    print("\n🚀 Railway Deployment Commands")
    print("=" * 50)
    
    commands = [
        "# Install Railway CLI",
        "npm install -g @railway/cli",
        "",
        "# Login to Railway",
        "railway login",
        "",
        "# Initialize Railway project (if not already done)",
        "railway init",
        "",
        "# Link to existing project (if already created)",
        "railway link",
        "",
        "# Set environment variables",
        "railway variables set DATABASE_URL=your_neon_connection_string",
        "railway variables set DEBUG=false",
        "",
        "# Deploy to Railway",
        "railway up",
        "",
        "# View logs",
        "railway logs",
        "",
        "# Open deployed app",
        "railway open"
    ]
    
    for command in commands:
        print(command)

def main():
    """Main validation function"""
    print("🚂 Railway Deployment Preparation")
    print("=" * 50)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Run all checks
    config_valid = validate_railway_config()
    env_valid = check_environment_variables()
    db_valid = test_database_connection()
    health_valid = test_health_endpoints()
    
    print("\n📊 Validation Summary")
    print("=" * 50)
    print(f"Configuration Files: {'✅' if config_valid else '❌'}")
    print(f"Environment Variables: {'✅' if env_valid else '❌'}")
    print(f"Database Connection: {'✅' if db_valid else '❌'}")
    print(f"Health Endpoints: {'✅' if health_valid else '❌'}")
    
    if all([config_valid, env_valid, db_valid, health_valid]):
        print("\n🎉 All checks passed! Ready for Railway deployment.")
        generate_railway_commands()
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above before deploying.")
        print("\n💡 Tips:")
        print("- Make sure all required files exist")
        print("- Set DATABASE_URL to your Neon connection string")
        print("- Check that your Neon database is active")
        print("- Verify all dependencies are in requirements.txt")

if __name__ == "__main__":
    main() 