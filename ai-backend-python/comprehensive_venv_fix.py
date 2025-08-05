#!/usr/bin/env python3
"""
Comprehensive Virtual Environment Fix
====================================
This script completely recreates the virtual environment and restores all packages
from scratch to fix corruption issues.
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path

def run_command(cmd, cwd=None, check=True):
    """Run a command and return the result"""
    print(f"🔄 Running: {cmd}")
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            check=check,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(f"✅ Output: {result.stdout}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"❌ Stderr: {e.stderr}")
        return e

def main():
    print("🔧 Comprehensive Virtual Environment Fix")
    print("=" * 50)
    
    # Get the backend directory
    backend_dir = "/home/ubuntu/ai-backend-python"
    venv_dir = os.path.join(backend_dir, "venv")
    
    print(f"📁 Backend directory: {backend_dir}")
    print(f"🐍 Virtual environment: {venv_dir}")
    
    # Step 1: Deactivate current venv if active
    print("\n1️⃣ Deactivating current virtual environment...")
    if 'VIRTUAL_ENV' in os.environ:
        print("⚠️  Virtual environment is active, deactivating...")
        # Remove VIRTUAL_ENV from environment
        if 'VIRTUAL_ENV' in os.environ:
            del os.environ['VIRTUAL_ENV']
        if 'PATH' in os.environ:
            # Remove venv/bin from PATH
            path_parts = os.environ['PATH'].split(':')
            path_parts = [p for p in path_parts if 'venv/bin' not in p]
            os.environ['PATH'] = ':'.join(path_parts)
    
    # Step 2: Remove corrupted virtual environment
    print("\n2️⃣ Removing corrupted virtual environment...")
    if os.path.exists(venv_dir):
        print(f"🗑️  Removing {venv_dir}")
        shutil.rmtree(venv_dir)
        print("✅ Virtual environment removed")
    else:
        print("✅ Virtual environment doesn't exist")
    
    # Step 3: Create new virtual environment
    print("\n3️⃣ Creating new virtual environment...")
    result = run_command(f"python3 -m venv {venv_dir}", cwd=backend_dir)
    if result.returncode != 0:
        print("❌ Failed to create virtual environment")
        return False
    
    print("✅ Virtual environment created")
    
    # Step 4: Activate virtual environment and upgrade pip
    print("\n4️⃣ Upgrading pip in new virtual environment...")
    pip_cmd = f"{venv_dir}/bin/pip"
    result = run_command(f"{pip_cmd} install --upgrade pip")
    if result.returncode != 0:
        print("❌ Failed to upgrade pip")
        return False
    
    print("✅ Pip upgraded")
    
    # Step 5: Install all required packages
    print("\n5️⃣ Installing required packages...")
    
    # Core packages
    core_packages = [
        "fastapi",
        "uvicorn[standard]",
        "sqlalchemy",
        "psycopg2-binary",
        "python-multipart",
        "python-jose[cryptography]",
        "passlib[bcrypt]",
        "python-dotenv",
        "requests",
        "aiofiles",
        "pydantic",
        "pydantic-settings"
    ]
    
    for package in core_packages:
        print(f"📦 Installing {package}...")
        result = run_command(f"{pip_cmd} install {package}")
        if result.returncode != 0:
            print(f"❌ Failed to install {package}")
            return False
        print(f"✅ {package} installed")
    
    # Step 6: Install additional packages if requirements.txt exists
    requirements_file = os.path.join(backend_dir, "requirements.txt")
    if os.path.exists(requirements_file):
        print(f"\n6️⃣ Installing packages from {requirements_file}...")
        result = run_command(f"{pip_cmd} install -r {requirements_file}")
        if result.returncode != 0:
            print("❌ Failed to install requirements")
            return False
        print("✅ Requirements installed")
    
    # Step 7: Verify installation
    print("\n7️⃣ Verifying installation...")
    
    # Test FastAPI import
    test_script = f"""
import sys
sys.path.insert(0, '{backend_dir}')

try:
    import fastapi
    print("✅ FastAPI imported successfully")
    print(f"📦 FastAPI version: {{fastapi.__version__}}")
except Exception as e:
    print(f"❌ FastAPI import failed: {{e}}")
    sys.exit(1)

try:
    import uvicorn
    print("✅ Uvicorn imported successfully")
except Exception as e:
    print(f"❌ Uvicorn import failed: {{e}}")
    sys.exit(1)

try:
    import sqlalchemy
    print("✅ SQLAlchemy imported successfully")
except Exception as e:
    print(f"❌ SQLAlchemy import failed: {{e}}")
    sys.exit(1)

print("✅ All core packages imported successfully")
"""
    
    test_file = os.path.join(backend_dir, "test_imports.py")
    with open(test_file, 'w') as f:
        f.write(test_script)
    
    result = run_command(f"{venv_dir}/bin/python {test_file}")
    os.remove(test_file)
    
    if result.returncode != 0:
        print("❌ Package verification failed")
        return False
    
    print("✅ All packages verified successfully")
    
    # Step 8: Test the main application
    print("\n8️⃣ Testing main application...")
    main_file = os.path.join(backend_dir, "app", "main.py")
    if os.path.exists(main_file):
        result = run_command(f"{venv_dir}/bin/python -c \"import sys; sys.path.insert(0, '{backend_dir}'); from app.main import app; print('✅ Main app imported successfully')\"")
        if result.returncode != 0:
            print("❌ Main app import failed")
            return False
        print("✅ Main application test passed")
    
    print("\n🎉 Virtual environment fix completed successfully!")
    print(f"🐍 Virtual environment: {venv_dir}")
    print(f"📦 Python: {venv_dir}/bin/python")
    print(f"📦 Pip: {venv_dir}/bin/pip")
    
    # Step 9: Create activation script
    activation_script = f"""#!/bin/bash
# Virtual Environment Activation Script
echo "🔧 Activating virtual environment..."
export VIRTUAL_ENV="{venv_dir}"
export PATH="$VIRTUAL_ENV/bin:$PATH"
unset PYTHONHOME
echo "✅ Virtual environment activated"
echo "🐍 Python: $(which python)"
echo "📦 Pip: $(which pip)"
"""
    
    activation_file = os.path.join(backend_dir, "activate_venv.sh")
    with open(activation_file, 'w') as f:
        f.write(activation_script)
    
    os.chmod(activation_file, 0o755)
    print(f"📝 Activation script created: {activation_file}")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Virtual environment fix completed successfully!")
        print("🚀 You can now start your services:")
        print(f"   cd /home/ubuntu/ai-backend-python")
        print(f"   source venv/bin/activate")
        print(f"   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
    else:
        print("\n❌ Virtual environment fix failed!")
        sys.exit(1) 