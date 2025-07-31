#!/usr/bin/env python3
"""
Install Feedparser
=================
Install missing feedparser and related packages
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
    print("🔧 Install Feedparser")
    print("=" * 30)
    
    # Install missing packages
    print("\n📦 Installing missing packages...")
    packages = [
        "feedparser",
        "beautifulsoup4",
        "lxml",
        "requests-html",
        "selenium",
        "webdriver-manager"
    ]
    
    for package in packages:
        print(f"\n📦 Installing {package}...")
        if run_cmd(f"pip install {package}"):
            print(f"✅ {package} installed successfully")
        else:
            print(f"⚠️  Failed to install {package}, continuing...")
    
    # Test feedparser import
    print("\n🧪 Testing feedparser import...")
    if run_cmd("python3 -c 'import feedparser; print(\"feedparser imported successfully\")'"):
        print("✅ feedparser imported successfully")
    else:
        print("❌ feedparser import failed")
        return False
    
    # Restart the backend service
    print("\n🔄 Restarting backend service...")
    run_cmd("sudo systemctl restart ai-backend-python")
    
    # Wait and check status
    import time
    time.sleep(5)
    
    print("\n🔍 Checking service status...")
    run_cmd("sudo systemctl status ai-backend-python --no-pager")
    
    print("\n🎉 Feedparser installation complete!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 