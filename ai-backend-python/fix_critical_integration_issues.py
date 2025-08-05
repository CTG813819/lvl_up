#!/usr/bin/env python3
"""
Critical Frontend-Backend Integration Issues Fix
Addresses the specific issues found in the comprehensive check
"""

import asyncio
import aiohttp
import json
import sys
import os
import subprocess
import time
from datetime import datetime

class CriticalIssuesFixer:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.fixes_applied = []
        self.issues_found = []
        
    async def fix_sqlalchemy_version(self):
        """Fix SQLAlchemy version to resolve _static_cache_key errors"""
        print("🔧 Fixing SQLAlchemy version...")
        try:
            # Check current version
            result = subprocess.run([
                "python3", "-c", 
                "import sqlalchemy; print(f'Current: {sqlalchemy.__version__}')"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                current_version = result.stdout.strip()
                print(f"📊 {current_version}")
                
                # SQLAlchemy 1.4.50 is causing issues, upgrade to 2.0+
                if "1.4" in current_version:
                    print("🔄 Upgrading SQLAlchemy to 2.0+...")
                    subprocess.run([
                        "pip3", "install", "sqlalchemy>=2.0.0", "--force-reinstall"
                    ], check=True)
                    self.fixes_applied.append("SQLAlchemy upgraded to 2.0+")
                    print("✅ SQLAlchemy upgraded")
                else:
                    print("✅ SQLAlchemy version is already compatible")
            else:
                print("❌ Could not check SQLAlchemy version")
                
        except Exception as e:
            print(f"❌ Error fixing SQLAlchemy: {str(e)}")
            self.issues_found.append(f"SQLAlchemy fix error: {str(e)}")

    async def fix_database_import_issue(self):
        """Fix the app.database import issue"""
        print("🗄️ Fixing database import issue...")
        try:
            # Check if app directory exists
            if not os.path.exists('app'):
                print("❌ app directory not found")
                self.issues_found.append("app directory missing")
                return
                
            # Check if database.py exists
            if not os.path.exists('app/database.py'):
                print("❌ app/database.py not found")
                self.issues_found.append("app/database.py missing")
                return
                
            # Test import with proper path
            result = subprocess.run([
                "python3", "-c", 
                "import sys; sys.path.append('.'); from app.database import engine; print('Database import OK')"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ Database import working")
            else:
                error_msg = result.stderr.strip()
                print(f"❌ Database import error: {error_msg}")
                self.issues_found.append(f"Database import error: {error_msg}")
                
        except Exception as e:
            print(f"❌ Error checking database import: {str(e)}")
            self.issues_found.append(f"Database import check error: {str(e)}")

    async def check_and_fix_routing(self):
        """Check and fix routing issues causing 404 errors"""
        print("🔗 Checking routing issues...")
        
        # Test main app startup
        try:
            result = subprocess.run([
                "python3", "-c", 
                "import sys; sys.path.append('.'); from app.main import app; print('App import OK')"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ App import successful")
            else:
                error_msg = result.stderr.strip()
                print(f"❌ App import error: {error_msg}")
                self.issues_found.append(f"App import error: {error_msg}")
                
        except Exception as e:
            print(f"❌ Error checking app import: {str(e)}")
            self.issues_found.append(f"App import check error: {str(e)}")

    async def test_critical_endpoints(self):
        """Test the most critical endpoints for frontend functionality"""
        print("🎯 Testing critical endpoints...")
        
        critical_endpoints = [
            "/api/proposals/",
            "/api/custody/",
            "/api/health"
        ]
        
        for endpoint in critical_endpoints:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.base_url}{endpoint}", timeout=10) as response:
                        if response.status == 200:
                            data = await response.json()
                            print(f"✅ {endpoint} - working")
                            if endpoint == "/api/proposals/":
                                proposal_count = len(data) if isinstance(data, list) else 0
                                print(f"   📋 Found {proposal_count} proposals")
                        else:
                            print(f"❌ {endpoint} - failed ({response.status})")
                            if endpoint == "/api/proposals/":
                                self.issues_found.append("Proposals endpoint not working - frontend won't show proposals")
            except Exception as e:
                print(f"❌ {endpoint} - error: {str(e)}")
                if endpoint == "/api/proposals/":
                    self.issues_found.append(f"Proposals endpoint error: {str(e)}")

    async def restart_backend_service(self):
        """Restart the backend service to apply fixes"""
        print("🔄 Restarting backend service...")
        try:
            subprocess.run(["sudo", "systemctl", "restart", "ultimate_start"], check=True)
            print("✅ Backend service restarted")
            
            # Wait for service to start
            print("⏳ Waiting for service to start...")
            time.sleep(15)
            
            # Check service status
            result = subprocess.run(["sudo", "systemctl", "status", "ultimate_start"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ Backend service is running")
            else:
                print("❌ Backend service may not be running properly")
                self.issues_found.append("Backend service not running properly")
                
        except Exception as e:
            print(f"❌ Error restarting service: {str(e)}")
            self.issues_found.append(f"Service restart error: {str(e)}")

    async def check_recent_logs(self):
        """Check recent logs for errors"""
        print("📋 Checking recent logs...")
        try:
            result = subprocess.run([
                "sudo", "journalctl", "-u", "ultimate_start", "--since", "2 minutes ago"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logs = result.stdout.strip()
                if "_static_cache_key" in logs:
                    print("❌ _static_cache_key errors still present in logs")
                    self.issues_found.append("_static_cache_key errors in logs")
                else:
                    print("✅ No _static_cache_key errors in recent logs")
                    
                # Check for other critical errors
                if "error" in logs.lower() or "exception" in logs.lower():
                    print("⚠️ Other errors found in logs")
                    error_lines = [line for line in logs.split('\n') if 'error' in line.lower() or 'exception' in line.lower()]
                    for line in error_lines[-5:]:  # Last 5 error lines
                        print(f"   {line}")
            else:
                print("❌ Could not check logs")
                
        except Exception as e:
            print(f"❌ Error checking logs: {str(e)}")

    def generate_fix_summary(self):
        """Generate summary of fixes applied"""
        print("\n" + "="*60)
        print("🔧 CRITICAL ISSUES FIX SUMMARY")
        print("="*60)
        
        print(f"✅ Fixes Applied: {len(self.fixes_applied)}")
        for fix in self.fixes_applied:
            print(f"   • {fix}")
            
        print(f"🚨 Issues Found: {len(self.issues_found)}")
        for issue in self.issues_found:
            print(f"   • {issue}")
            
        # Save detailed results
        results = {
            "timestamp": datetime.now().isoformat(),
            "fixes_applied": self.fixes_applied,
            "issues_found": self.issues_found,
            "overall_status": "fixed" if len(self.fixes_applied) > 0 else "failed"
        }
        
        with open('critical_issues_fix_report.json', 'w') as f:
            json.dump(results, f, indent=2)
            
        print(f"\n📄 Detailed report saved to: critical_issues_fix_report.json")
        
        if len(self.issues_found) == 0:
            print("✅ All critical issues resolved!")
        else:
            print("⚠️ Some issues remain - manual intervention may be needed")

    async def run_critical_fixes(self):
        """Run all critical fixes"""
        print("🚀 Starting critical issues fix...")
        print(f"⏰ Timestamp: {datetime.now().isoformat()}")
        
        # Apply fixes
        await self.fix_sqlalchemy_version()
        await self.fix_database_import_issue()
        await self.check_and_fix_routing()
        
        # Restart service to apply fixes
        await self.restart_backend_service()
        
        # Test critical endpoints
        await self.test_critical_endpoints()
        
        # Check logs
        await self.check_recent_logs()
        
        # Generate summary
        self.generate_fix_summary()

async def main():
    fixer = CriticalIssuesFixer()
    await fixer.run_critical_fixes()

if __name__ == "__main__":
    asyncio.run(main()) 