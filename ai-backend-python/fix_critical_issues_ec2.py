#!/usr/bin/env python3
"""
Critical Frontend-Backend Integration Issues Fix for EC2
Handles externally managed Python environment
"""

import asyncio
import aiohttp
import json
import sys
import os
import subprocess
import time
from datetime import datetime

class CriticalIssuesFixerEC2:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.fixes_applied = []
        self.issues_found = []
        
    async def check_sqlalchemy_version(self):
        """Check SQLAlchemy version without trying to upgrade"""
        print("🔧 Checking SQLAlchemy version...")
        try:
            result = subprocess.run([
                "python3", "-c", 
                "import sqlalchemy; print(f'Current: {sqlalchemy.__version__}')"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                current_version = result.stdout.strip()
                print(f"📊 {current_version}")
                
                if "1.4" in current_version:
                    print("⚠️ SQLAlchemy 1.4.x detected - may cause _static_cache_key errors")
                    self.issues_found.append("SQLAlchemy 1.4.x may cause compatibility issues")
                    print("💡 Recommendation: Consider using a virtual environment for package management")
                else:
                    print("✅ SQLAlchemy version appears compatible")
            else:
                print("❌ Could not check SQLAlchemy version")
                
        except Exception as e:
            print(f"❌ Error checking SQLAlchemy: {str(e)}")
            self.issues_found.append(f"SQLAlchemy check error: {str(e)}")

    async def check_database_import_issue(self):
        """Check the app.database import issue"""
        print("🗄️ Checking database import issue...")
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

    async def check_routing_issues(self):
        """Check routing issues causing 404 errors"""
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
                                if proposal_count == 0:
                                    print("   ⚠️ No proposals found - this may be why frontend shows blank")
                        else:
                            print(f"❌ {endpoint} - failed ({response.status})")
                            if endpoint == "/api/proposals/":
                                self.issues_found.append("Proposals endpoint not working - frontend won't show proposals")
            except Exception as e:
                print(f"❌ {endpoint} - error: {str(e)}")
                if endpoint == "/api/proposals/":
                    self.issues_found.append(f"Proposals endpoint error: {str(e)}")

    async def check_service_status(self):
        """Check backend service status"""
        print("🔍 Checking backend service status...")
        try:
            result = subprocess.run(["sudo", "systemctl", "status", "ultimate_start"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ Backend service is running")
                # Check if service is active
                if "active (running)" in result.stdout:
                    print("✅ Service is active and running")
                else:
                    print("⚠️ Service may not be fully active")
                    self.issues_found.append("Backend service not fully active")
            else:
                print("❌ Backend service may not be running properly")
                self.issues_found.append("Backend service not running properly")
                
        except Exception as e:
            print(f"❌ Error checking service status: {str(e)}")
            self.issues_found.append(f"Service status check error: {str(e)}")

    async def check_recent_logs(self):
        """Check recent logs for errors"""
        print("📋 Checking recent logs...")
        try:
            result = subprocess.run([
                "sudo", "journalctl", "-u", "ultimate_start", "--since", "5 minutes ago"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logs = result.stdout.strip()
                if "_static_cache_key" in logs:
                    print("❌ _static_cache_key errors found in logs")
                    self.issues_found.append("_static_cache_key errors in logs")
                    # Show the specific error lines
                    error_lines = [line for line in logs.split('\n') if '_static_cache_key' in line]
                    for line in error_lines[-3:]:  # Last 3 error lines
                        print(f"   {line}")
                else:
                    print("✅ No _static_cache_key errors in recent logs")
                    
                # Check for other critical errors
                if "error" in logs.lower() or "exception" in logs.lower():
                    print("⚠️ Other errors found in logs")
                    error_lines = [line for line in logs.split('\n') if 'error' in line.lower() or 'exception' in line.lower()]
                    for line in error_lines[-5:]:  # Last 5 error lines
                        print(f"   {line}")
                        
                # Check for proposal-related errors
                if "proposal" in logs.lower():
                    proposal_lines = [line for line in logs.split('\n') if 'proposal' in line.lower()]
                    print("📋 Recent proposal-related log entries:")
                    for line in proposal_lines[-3:]:
                        print(f"   {line}")
            else:
                print("❌ Could not check logs")
                
        except Exception as e:
            print(f"❌ Error checking logs: {str(e)}")

    async def check_database_connection(self):
        """Check database connection directly"""
        print("🗄️ Checking database connection...")
        try:
            result = subprocess.run([
                "python3", "-c", 
                """
import sys
sys.path.append('.')
try:
    from app.database import engine
    with engine.connect() as conn:
        result = conn.execute('SELECT 1')
        print('Database connection OK')
except Exception as e:
    print(f'Database connection error: {e}')
"""
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and "Database connection OK" in result.stdout:
                print("✅ Database connection working")
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                print(f"❌ Database connection error: {error_msg}")
                self.issues_found.append(f"Database connection error: {error_msg}")
                
        except Exception as e:
            print(f"❌ Error checking database connection: {str(e)}")
            self.issues_found.append(f"Database connection check error: {str(e)}")

    def generate_diagnostic_summary(self):
        """Generate diagnostic summary"""
        print("\n" + "="*60)
        print("🔍 CRITICAL ISSUES DIAGNOSTIC SUMMARY")
        print("="*60)
        
        print(f"🚨 Issues Found: {len(self.issues_found)}")
        for issue in self.issues_found:
            print(f"   • {issue}")
            
        # Save detailed results
        results = {
            "timestamp": datetime.now().isoformat(),
            "issues_found": self.issues_found,
            "overall_status": "critical" if len(self.issues_found) > 0 else "healthy"
        }
        
        with open('critical_issues_diagnostic_report.json', 'w') as f:
            json.dump(results, f, indent=2)
            
        print(f"\n📄 Detailed report saved to: critical_issues_diagnostic_report.json")
        
        # Provide specific recommendations
        print("\n💡 RECOMMENDATIONS:")
        if any("_static_cache_key" in issue for issue in self.issues_found):
            print("   • SQLAlchemy version issue: Consider using virtual environment")
            print("   • Alternative: Use system package manager (apt) for SQLAlchemy")
        if any("proposal" in issue.lower() for issue in self.issues_found):
            print("   • Proposals not showing: Check database for proposal data")
            print("   • Verify proposal creation process is working")
        if any("database" in issue.lower() for issue in self.issues_found):
            print("   • Database issues: Check PostgreSQL service and connection")
            print("   • Verify database schema and migrations")
        
        if len(self.issues_found) == 0:
            print("✅ No critical issues detected!")
        else:
            print("⚠️ Critical issues detected - manual intervention needed")

    async def run_diagnostic(self):
        """Run comprehensive diagnostic"""
        print("🚀 Starting critical issues diagnostic...")
        print(f"⏰ Timestamp: {datetime.now().isoformat()}")
        
        # Run all checks
        await self.check_sqlalchemy_version()
        await self.check_database_import_issue()
        await self.check_routing_issues()
        await self.check_database_connection()
        await self.check_service_status()
        await self.test_critical_endpoints()
        await self.check_recent_logs()
        
        # Generate summary
        self.generate_diagnostic_summary()

async def main():
    fixer = CriticalIssuesFixerEC2()
    await fixer.run_diagnostic()

if __name__ == "__main__":
    asyncio.run(main()) 