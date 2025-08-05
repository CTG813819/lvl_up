#!/usr/bin/env python3
"""
Emergency Disk Cleanup
======================
Free up disk space quickly
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
    print("🚨 Emergency Disk Cleanup")
    print("=" * 40)
    
    # Show initial disk usage
    print("\n💾 Initial disk usage:")
    run_cmd("df -h")
    
    # Remove old backups (1.5GB)
    print("\n🗑️  Removing old backups...")
    run_cmd("rm -rf /home/ubuntu/backup_before_enhanced_learning_20250706_*")
    
    # Clear package cache
    print("\n📦 Clearing package cache...")
    run_cmd("sudo apt-get clean")
    run_cmd("sudo apt-get autoremove -y")
    
    # Clear pip cache
    print("\n🐍 Clearing pip cache...")
    run_cmd("pip cache purge")
    
    # Remove Flutter cache (2.3GB)
    print("\n📱 Removing Flutter cache...")
    run_cmd("rm -rf /home/ubuntu/.flutter")
    
    # Clear system logs
    print("\n📋 Clearing old logs...")
    run_cmd("sudo find /var/log -name '*.log' -mtime +3 -delete")
    run_cmd("sudo journalctl --vacuum-time=3d")
    
    # Clear temporary files
    print("\n🗂️  Clearing temp files...")
    run_cmd("sudo rm -rf /tmp/*")
    run_cmd("sudo rm -rf /var/tmp/*")
    
    # Show final disk usage
    print("\n💾 Final disk usage:")
    run_cmd("df -h")
    
    print("\n🎉 Emergency cleanup complete!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 