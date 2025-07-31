#!/usr/bin/env python3
"""
Quick Package Fix
================
Quickly install essential missing packages
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
    print("🔧 Quick Package Fix")
    print("=" * 30)
    
    # Install essential packages
    print("\n📦 Installing essential packages...")
    packages = [
        "numpy",
        "pandas",
        "scikit-learn",
        "fastapi",
        "uvicorn"
    ]
    
    for package in packages:
        print(f"\n📦 Installing {package}...")
        if run_cmd(f"pip install {package}"):
            print(f"✅ {package} installed")
        else:
            print(f"❌ Failed to install {package}")
            return False
    
    # Test numpy import
    print("\n🧪 Testing numpy import...")
    if run_cmd("python3 -c 'import numpy; print(\"numpy imported successfully\")'"):
        print("✅ numpy imported successfully")
    else:
        print("❌ numpy import failed")
        return False
    
    print("\n🎉 Quick package fix complete!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 