#!/usr/bin/env python3
"""
Script to restart the imperium service and clear Python cache
"""

import os
import subprocess
import sys

def run_command(cmd):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(f"✅ {cmd}")
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"⚠️  {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running {cmd}: {e}")
        return False

def main():
    print("🔄 Restarting Imperium Service...")
    
    # Stop the service
    run_command("sudo systemctl stop imperium-monitoring")
    
    # Clear Python cache
    print("🧹 Clearing Python cache...")
    cache_dirs = [
        "~/ai-backend-python/__pycache__",
        "~/ai-backend-python/app/__pycache__",
        "~/ai-backend-python/app/services/__pycache__",
        "~/ai-backend-python/app/routers/__pycache__"
    ]
    
    for cache_dir in cache_dirs:
        run_command(f"rm -rf {cache_dir}")
    
    # Test the import directly
    print("🧪 Testing trusted_sources import...")
    test_script = '''
import sys
sys.path.insert(0, '/home/ubuntu/ai-backend-python')
try:
    from app.services.trusted_sources import get_trusted_sources, add_trusted_source, remove_trusted_source
    print("✅ All functions imported successfully!")
    print(f"get_trusted_sources: {get_trusted_sources}")
except Exception as e:
    print(f"❌ Import error: {e}")
'''
    
    with open('/tmp/test_import.py', 'w') as f:
        f.write(test_script)
    
    run_command("cd ~/ai-backend-python && python3 /tmp/test_import.py")
    
    # Start the service
    print("🚀 Starting Imperium service...")
    run_command("sudo systemctl start imperium-monitoring")
    
    # Check status
    print("📊 Service status:")
    run_command("sudo systemctl status imperium-monitoring --no-pager")
    
    # Check logs
    print("📋 Recent logs:")
    run_command("sudo journalctl -u imperium-monitoring -n 5 --no-pager")
    
    print("✅ Restart complete!")

if __name__ == "__main__":
    main() 