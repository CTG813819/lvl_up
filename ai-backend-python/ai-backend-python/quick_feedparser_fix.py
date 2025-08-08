#!/usr/bin/env python3
"""
Quick Feedparser Fix
====================
Quickly install feedparser and restart the service
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
    print("🔧 Quick Feedparser Fix")
    print("=" * 30)
    
    # Install feedparser
    print("\n📦 Installing feedparser...")
    if run_cmd("pip install feedparser"):
        print("✅ feedparser installed successfully")
    else:
        print("❌ Failed to install feedparser")
        return False
    
    # Test import
    print("\n🧪 Testing feedparser import...")
    if run_cmd("python3 -c 'import feedparser; print(\"feedparser imported successfully\")'"):
        print("✅ feedparser imported successfully")
    else:
        print("❌ feedparser import failed")
        return False
    
    # Restart the service
    print("\n🔄 Restarting service...")
    run_cmd("sudo systemctl restart ai-backend-python")
    
    # Wait and check
    import time
    time.sleep(5)
    
    print("\n🔍 Checking service status...")
    run_cmd("sudo systemctl status ai-backend-python --no-pager")
    
    print("\n🎉 Feedparser fix complete!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 