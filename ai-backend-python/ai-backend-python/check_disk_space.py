#!/usr/bin/env python3
"""
Check Disk Space
================
Check disk space and clean up if needed
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
    print("🔧 Check Disk Space")
    print("=" * 30)
    
    # Check disk space
    print("\n💾 Checking disk space...")
    run_cmd("df -h")
    
    # Check inode usage
    print("\n📊 Checking inode usage...")
    run_cmd("df -i")
    
    # Check largest directories
    print("\n📁 Checking largest directories...")
    run_cmd("du -h --max-depth=1 /home/ubuntu/ | sort -hr | head -10")
    
    # Check if we can free up space
    print("\n🧹 Checking for cleanup opportunities...")
    run_cmd("sudo apt-get clean")
    run_cmd("sudo apt-get autoremove -y")
    
    # Clear pip cache
    print("\n🗑️  Clearing pip cache...")
    run_cmd("pip cache purge")
    
    # Check space after cleanup
    print("\n💾 Checking disk space after cleanup...")
    run_cmd("df -h")
    
    print("\n🎉 Disk space check complete!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 