#!/usr/bin/env python3
"""
Quick SQLAlchemy Fix for _static_cache_key Error
Simple script to fix the SQLAlchemy compatibility issue
"""

import subprocess
import sys
import time

def main():
    print("🔧 Quick SQLAlchemy Fix for _static_cache_key Error")
    print("=" * 50)
    
    try:
        # Step 1: Check current SQLAlchemy version
        print("📊 Checking current SQLAlchemy version...")
        result = subprocess.run([
            "python3", "-c", "import sqlalchemy; print(f'Current: {sqlalchemy.__version__}')"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            current_version = result.stdout.strip()
            print(f"   {current_version}")
            
            if "1.4" in current_version:
                print("⚠️ SQLAlchemy 1.4.x detected - this causes _static_cache_key errors")
                print("🔄 Upgrading to SQLAlchemy 2.0.23...")
                
                # Step 2: Uninstall current version
                print("🗑️ Uninstalling current SQLAlchemy...")
                uninstall_result = subprocess.run([
                    "pip3", "uninstall", "sqlalchemy", "-y", "--break-system-packages"
                ], capture_output=True, text=True, timeout=30)
                
                # Step 3: Install compatible version
                print("📦 Installing SQLAlchemy 2.0.23...")
                install_result = subprocess.run([
                    "pip3", "install", "sqlalchemy==2.0.23", "--break-system-packages"
                ], capture_output=True, text=True, timeout=60)
                
                if install_result.returncode == 0:
                    print("✅ SQLAlchemy upgraded successfully")
                    
                    # Step 4: Restart the service
                    print("🔄 Restarting backend service...")
                    stop_result = subprocess.run([
                        "sudo", "systemctl", "stop", "ultimate_start"
                    ], capture_output=True, text=True, timeout=30)
                    
                    time.sleep(3)
                    
                    start_result = subprocess.run([
                        "sudo", "systemctl", "start", "ultimate_start"
                    ], capture_output=True, text=True, timeout=30)
                    
                    if start_result.returncode == 0:
                        print("✅ Backend service restarted")
                        
                        # Step 5: Wait and check status
                        print("⏳ Waiting for service to stabilize...")
                        time.sleep(10)
                        
                        status_result = subprocess.run([
                            "sudo", "systemctl", "status", "ultimate_start", "--no-pager"
                        ], capture_output=True, text=True, timeout=30)
                        
                        if status_result.returncode == 0:
                            print("✅ Service is running")
                            
                            # Step 6: Check for recent errors
                            print("🔍 Checking recent logs for _static_cache_key errors...")
                            log_result = subprocess.run([
                                "sudo", "journalctl", "-u", "ultimate_start", "--since", "2 minutes ago", "--no-pager"
                            ], capture_output=True, text=True, timeout=30)
                            
                            if "_static_cache_key" in log_result.stdout:
                                print("⚠️ _static_cache_key errors still present in recent logs")
                                print("💡 The fix may take a few minutes to take effect")
                            else:
                                print("✅ No _static_cache_key errors in recent logs")
                                print("🎉 SQLAlchemy fix appears to be working!")
                        else:
                            print("❌ Service is not running properly")
                    else:
                        print("❌ Failed to restart service")
                else:
                    print(f"❌ Failed to upgrade SQLAlchemy: {install_result.stderr}")
            else:
                print("✅ SQLAlchemy version appears compatible")
        else:
            print("❌ Could not check SQLAlchemy version")
            
    except Exception as e:
        print(f"❌ Error during fix: {str(e)}")
        return 1
    
    print("\n📄 Fix completed. Monitor the logs for any remaining issues.")
    print("🔗 Check logs with: sudo journalctl -u ultimate_start -f")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 