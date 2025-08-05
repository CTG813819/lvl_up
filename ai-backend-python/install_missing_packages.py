#!/usr/bin/env python3
"""
Install Missing Packages
=======================
Install missing packages for the backend server
"""

import subprocess
import sys

def run_cmd(cmd):
    print(f"🔄 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ Success: {result.stdout.strip()}")
        return True
    else:
        print(f"❌ Error: {result.stderr.strip()}")
        return False

def main():
    print("🔧 Install Missing Packages")
    print("=" * 40)
    
    # Activate virtual environment
    print("\n🔧 Activating virtual environment...")
    venv_path = "/home/ubuntu/ai-backend-python/venv"
    if not run_cmd(f"source {venv_path}/bin/activate"):
        print("❌ Failed to activate virtual environment")
        return False
    
    # Install missing packages
    print("\n📦 Installing missing packages...")
    packages = [
        "numpy",
        "pandas", 
        "scikit-learn",
        "matplotlib",
        "seaborn",
        "plotly",
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "asyncpg",
        "psycopg2-binary",
        "python-multipart",
        "python-jose[cryptography]",
        "passlib[bcrypt]",
        "python-dotenv",
        "requests",
        "aiohttp",
        "structlog",
        "psutil"
    ]
    
    for package in packages:
        print(f"\n📦 Installing {package}...")
        install_cmd = f"cd /home/ubuntu/ai-backend-python && {venv_path}/bin/pip install {package}"
        if run_cmd(install_cmd):
            print(f"✅ {package} installed successfully")
        else:
            print(f"❌ Failed to install {package}")
            return False
    
    # Test the imports
    print("\n🧪 Testing imports...")
    test_cmd = f"cd /home/ubuntu/ai-backend-python && {venv_path}/bin/python -c 'import numpy; import pandas; import sklearn; print(\"All packages imported successfully\")'"
    if run_cmd(test_cmd):
        print("✅ All packages imported successfully")
    else:
        print("❌ Import test failed")
        return False
    
    print("\n🎉 Package installation complete!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 