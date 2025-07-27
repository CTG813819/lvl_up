#!/usr/bin/env python3
"""
Fix SQLAlchemy _static_cache_key Error
Resolve the SQLAlchemy compatibility issue causing _static_cache_key errors
"""

import subprocess
import sys
import time
import json
from datetime import datetime

class SQLAlchemyFixer:
    def __init__(self):
        self.fixes_applied = []
        self.issues_found = []
        self.current_sqlalchemy_version = None
        self.target_sqlalchemy_version = "2.0.23"

    def check_current_sqlalchemy_version(self):
        """Check current SQLAlchemy version"""
        print("🔍 Checking current SQLAlchemy version...")
        try:
            result = subprocess.run([
                "python3", "-c",
                "import sqlalchemy; print(f'Current: {sqlalchemy.__version__}')"
            ], capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                self.current_sqlalchemy_version = result.stdout.strip()
                print(f"📊 {self.current_sqlalchemy_version}")
                
                if "1.4" in self.current_sqlalchemy_version:
                    print("⚠️ SQLAlchemy 1.4.x detected - this causes _static_cache_key errors")
                    self.issues_found.append("SQLAlchemy 1.4.x is incompatible")
                    return True
                elif "2.0" in self.current_sqlalchemy_version:
                    print("✅ SQLAlchemy 2.0.x detected - should be compatible")
                    return False
                else:
                    print("❓ Unknown SQLAlchemy version")
                    return True
            else:
                print("❌ Could not check SQLAlchemy version")
                return True
        except Exception as e:
            print(f"❌ Error checking SQLAlchemy: {str(e)}")
            return True

    def upgrade_sqlalchemy(self):
        """Upgrade SQLAlchemy to compatible version"""
        print("📦 Upgrading SQLAlchemy to compatible version...")
        try:
            # First, try to uninstall current version
            print("🗑️ Uninstalling current SQLAlchemy...")
            uninstall_result = subprocess.run([
                "pip3", "uninstall", "sqlalchemy", "-y", "--break-system-packages"
            ], capture_output=True, text=True, timeout=30)
            
            # Install compatible version
            print(f"📦 Installing SQLAlchemy {self.target_sqlalchemy_version}...")
            install_result = subprocess.run([
                "pip3", "install", f"sqlalchemy=={self.target_sqlalchemy_version}", "--break-system-packages"
            ], capture_output=True, text=True, timeout=60)
            
            if install_result.returncode == 0:
                print("✅ SQLAlchemy upgraded successfully")
                self.fixes_applied.append(f"Upgraded SQLAlchemy to {self.target_sqlalchemy_version}")
                return True
            else:
                print(f"❌ Failed to upgrade SQLAlchemy: {install_result.stderr}")
                self.issues_found.append(f"Failed to upgrade SQLAlchemy: {install_result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error upgrading SQLAlchemy: {str(e)}")
            self.issues_found.append(f"Error upgrading SQLAlchemy: {str(e)}")
            return False

    def restart_backend_service(self):
        """Restart the backend service"""
        print("🔄 Restarting backend service...")
        try:
            # Stop the service
            stop_result = subprocess.run([
                "sudo", "systemctl", "stop", "ultimate_start"
            ], capture_output=True, text=True, timeout=30)
            
            if stop_result.returncode != 0:
                print(f"⚠️ Warning: Could not stop service: {stop_result.stderr}")
            
            # Wait a moment
            time.sleep(3)
            
            # Start the service
            start_result = subprocess.run([
                "sudo", "systemctl", "start", "ultimate_start"
            ], capture_output=True, text=True, timeout=30)
            
            if start_result.returncode == 0:
                print("✅ Backend service restarted successfully")
                self.fixes_applied.append("Restarted backend service")
                return True
            else:
                print(f"❌ Failed to restart service: {start_result.stderr}")
                self.issues_found.append(f"Failed to restart service: {start_result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error restarting service: {str(e)}")
            self.issues_found.append(f"Error restarting service: {str(e)}")
            return False

    def check_service_status(self):
        """Check if the service is running properly"""
        print("🔍 Checking service status...")
        try:
            result = subprocess.run([
                "sudo", "systemctl", "status", "ultimate_start", "--no-pager"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Service is running")
                return True
            else:
                print(f"❌ Service is not running properly: {result.stdout}")
                return False
        except Exception as e:
            print(f"❌ Error checking service status: {str(e)}")
            return False

    def test_database_connection(self):
        """Test database connection after fix"""
        print("🔍 Testing database connection...")
        try:
            result = subprocess.run([
                "python3", "-c",
                """
import sqlalchemy
from sqlalchemy import create_engine, text
try:
    engine = create_engine('postgresql://user:password@localhost/dbname')
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        print('Database connection successful')
except Exception as e:
    print(f'Database connection failed: {e}')
"""
            ], capture_output=True, text=True, timeout=30)
            
            if "Database connection successful" in result.stdout:
                print("✅ Database connection test passed")
                return True
            else:
                print(f"❌ Database connection test failed: {result.stdout}")
                return False
        except Exception as e:
            print(f"❌ Error testing database connection: {str(e)}")
            return False

    def check_logs_for_errors(self):
        """Check recent logs for _static_cache_key errors"""
        print("🔍 Checking recent logs for errors...")
        try:
            result = subprocess.run([
                "sudo", "journalctl", "-u", "ultimate_start", "--since", "5 minutes ago", "--no-pager"
            ], capture_output=True, text=True, timeout=30)
            
            if "_static_cache_key" in result.stdout:
                print("⚠️ _static_cache_key errors still present in recent logs")
                return False
            else:
                print("✅ No _static_cache_key errors in recent logs")
                return True
        except Exception as e:
            print(f"❌ Error checking logs: {str(e)}")
            return False

    def run_comprehensive_fix(self):
        """Run the complete fix process"""
        print("🚀 Starting SQLAlchemy _static_cache_key fix...")
        print(f"⏰ Timestamp: {datetime.now().isoformat()}")
        
        # Step 1: Check current version
        needs_upgrade = self.check_current_sqlalchemy_version()
        
        if needs_upgrade:
            # Step 2: Upgrade SQLAlchemy
            upgrade_success = self.upgrade_sqlalchemy()
            
            if upgrade_success:
                # Step 3: Restart service
                restart_success = self.restart_backend_service()
                
                if restart_success:
                    # Step 4: Wait for service to stabilize
                    print("⏳ Waiting for service to stabilize...")
                    time.sleep(10)
                    
                    # Step 5: Check service status
                    service_ok = self.check_service_status()
                    
                    # Step 6: Check logs for errors
                    logs_ok = self.check_logs_for_errors()
                    
                    if service_ok and logs_ok:
                        print("✅ Fix completed successfully!")
                    else:
                        print("⚠️ Fix completed but some issues remain")
                else:
                    print("❌ Failed to restart service after upgrade")
            else:
                print("❌ Failed to upgrade SQLAlchemy")
        else:
            print("✅ SQLAlchemy version is already compatible")
        
        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate fix summary"""
        print("\n" + "="*60)
        print("🔧 SQLALCHEMY _STATIC_CACHE_KEY FIX SUMMARY")
        print("="*60)
        
        print(f"📊 Current SQLAlchemy Version: {self.current_sqlalchemy_version}")
        print(f"🎯 Target SQLAlchemy Version: {self.target_sqlalchemy_version}")
        
        print(f"\n✅ Fixes Applied ({len(self.fixes_applied)}):")
        for fix in self.fixes_applied:
            print(f"   • {fix}")
        
        if self.issues_found:
            print(f"\n❌ Issues Found ({len(self.issues_found)}):")
            for issue in self.issues_found:
                print(f"   • {issue}")
        
        # Save detailed results
        results = {
            "timestamp": datetime.now().isoformat(),
            "current_sqlalchemy_version": self.current_sqlalchemy_version,
            "target_sqlalchemy_version": self.target_sqlalchemy_version,
            "fixes_applied": self.fixes_applied,
            "issues_found": self.issues_found
        }
        
        with open('sqlalchemy_fix_report.json', 'w') as f:
            json.dump(results, f, indent=2)
            
        print(f"\n📄 Detailed report saved to: sqlalchemy_fix_report.json")
        
        if len(self.issues_found) == 0:
            print("🎉 SQLAlchemy _static_cache_key error should be resolved!")
        else:
            print("⚠️ Some issues remain - manual intervention may be required")

def main():
    fixer = SQLAlchemyFixer()
    fixer.run_comprehensive_fix()

if __name__ == "__main__":
    main() 