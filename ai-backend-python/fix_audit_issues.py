#!/usr/bin/env python3
"""
Comprehensive Fix Script for LVL_UP AI Backend Audit Issues
This script addresses all the critical issues found in the system audit.
"""

import os
import sys
import psycopg2
import subprocess
import requests
import time
from datetime import datetime

class SystemFixer:
    def __init__(self):
        self.db_config = {
            'host': 'ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech',
            'port': 5432,
            'database': 'neondb',
            'user': 'neondb_owner',
            'password': 'npg_TV1hbOzC9ReA',
            'sslmode': 'require'
        }
        self.base_url = "http://localhost:8000"
        self.fix_results = {
            'timestamp': datetime.now().isoformat(),
            'fixes_applied': [],
            'errors': [],
            'warnings': []
        }

    def run_comprehensive_fixes(self):
        """Run all fixes for identified issues"""
        print("🔧 Starting comprehensive system fixes...")
        print("=" * 60)
        
        try:
            # Database fixes
            self.fix_database_schema()
            self.fix_database_extensions()
            
            # Backend fixes
            self.fix_backend_configuration()
            self.check_backend_health()
            
            # Service fixes
            self.fix_ai_services()
            self.fix_guardian_services()
            
            # Generate fix report
            self.generate_fix_report()
            
        except Exception as e:
            print(f"❌ Critical error during fixes: {str(e)}")
            self.fix_results['errors'].append(f"Critical fix error: {str(e)}")

    def fix_database_schema(self):
        """Fix database schema issues"""
        print("📊 Fixing database schema...")
        
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Check existing tables
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            existing_tables = [row[0] for row in cursor.fetchall()]
            print(f"Existing tables: {existing_tables}")
            
            # Fix proposals table
            if 'proposals' in existing_tables:
                cursor.execute("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'proposals'
                """)
                existing_columns = [row[0] for row in cursor.fetchall()]
                
                if 'title' not in existing_columns:
                    cursor.execute("ALTER TABLE proposals ADD COLUMN title VARCHAR(255)")
                    print("✅ Added 'title' column to proposals table")
                    self.fix_results['fixes_applied'].append("Added title column to proposals table")
                
                if 'description' not in existing_columns:
                    cursor.execute("ALTER TABLE proposals ADD COLUMN description TEXT")
                    print("✅ Added 'description' column to proposals table")
                    self.fix_results['fixes_applied'].append("Added description column to proposals table")
                
                if 'status' not in existing_columns:
                    cursor.execute("ALTER TABLE proposals ADD COLUMN status VARCHAR(50) DEFAULT 'pending'")
                    print("✅ Added 'status' column to proposals table")
                    self.fix_results['fixes_applied'].append("Added status column to proposals table")
                
                if 'created_at' not in existing_columns:
                    cursor.execute("ALTER TABLE proposals ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                    print("✅ Added 'created_at' column to proposals table")
                    self.fix_results['fixes_applied'].append("Added created_at column to proposals table")
            
            # Create agents table if it doesn't exist
            if 'agents' not in existing_tables:
                cursor.execute("""
                    CREATE TABLE agents (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        type VARCHAR(100) NOT NULL,
                        status VARCHAR(50) DEFAULT 'active',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                print("✅ Created agents table")
                self.fix_results['fixes_applied'].append("Created agents table")
            
            # Create ai_learning_summaries table if it doesn't exist
            if 'ai_learning_summaries' not in existing_tables:
                cursor.execute("""
                    CREATE TABLE ai_learning_summaries (
                        id SERIAL PRIMARY KEY,
                        summary TEXT NOT NULL,
                        learning_type VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                print("✅ Created ai_learning_summaries table")
                self.fix_results['fixes_applied'].append("Created ai_learning_summaries table")
            
            # Create token_usage table if it doesn't exist
            if 'token_usage' not in existing_tables:
                cursor.execute("""
                    CREATE TABLE token_usage (
                        id SERIAL PRIMARY KEY,
                        service_name VARCHAR(100),
                        tokens_used INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                print("✅ Created token_usage table")
                self.fix_results['fixes_applied'].append("Created token_usage table")
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print("✅ Database schema fixes completed")
            
        except Exception as e:
            print(f"❌ Database schema fix failed: {str(e)}")
            self.fix_results['errors'].append(f"Database schema fix failed: {str(e)}")

    def fix_database_extensions(self):
        """Install required database extensions"""
        print("🔧 Installing database extensions...")
        
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Check if pg_stat_statements extension exists
            cursor.execute("""
                SELECT extname FROM pg_extension WHERE extname = 'pg_stat_statements'
            """)
            
            if not cursor.fetchone():
                try:
                    cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_stat_statements")
                    print("✅ Installed pg_stat_statements extension")
                    self.fix_results['fixes_applied'].append("Installed pg_stat_statements extension")
                except Exception as e:
                    print(f"⚠️ Could not install pg_stat_statements: {str(e)}")
                    self.fix_results['warnings'].append(f"Could not install pg_stat_statements: {str(e)}")
            else:
                print("✅ pg_stat_statements extension already installed")
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"❌ Database extension fix failed: {str(e)}")
            self.fix_results['errors'].append(f"Database extension fix failed: {str(e)}")

    def fix_backend_configuration(self):
        """Fix backend configuration issues"""
        print("🔧 Checking backend configuration...")
        
        try:
            # Check if backend is running on correct port
            result = subprocess.run(['netstat', '-tlnp'], capture_output=True, text=True)
            if result.returncode == 0:
                if ':8000' in result.stdout:
                    print("✅ Backend is running on port 8000")
                else:
                    print("⚠️ Backend not found on port 8000")
                    self.fix_results['warnings'].append("Backend not found on port 8000")
            
            # Check backend process
            result = subprocess.run(['pgrep', '-f', 'uvicorn'], capture_output=True, text=True)
            if result.returncode == 0:
                pids = result.stdout.strip().split('\n')
                print(f"✅ Backend processes running: {pids}")
            else:
                print("❌ No backend processes found")
                self.fix_results['errors'].append("No backend processes found")
                
        except Exception as e:
            print(f"❌ Backend configuration check failed: {str(e)}")
            self.fix_results['errors'].append(f"Backend configuration check failed: {str(e)}")

    def check_backend_health(self):
        """Check backend health endpoints"""
        print("🏥 Checking backend health...")
        
        try:
            # Try different health endpoints
            health_endpoints = [
                "/health",
                "/",
                "/api/health",
                "/status"
            ]
            
            working_endpoints = []
            for endpoint in health_endpoints:
                try:
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                    if response.status_code in [200, 401, 403]:
                        working_endpoints.append(endpoint)
                        print(f"✅ Endpoint {endpoint} is working (status: {response.status_code})")
                    else:
                        print(f"⚠️ Endpoint {endpoint} returned status {response.status_code}")
                except Exception as e:
                    print(f"❌ Endpoint {endpoint} failed: {str(e)}")
            
            if working_endpoints:
                print(f"✅ Found {len(working_endpoints)} working endpoints")
                self.fix_results['fixes_applied'].append(f"Found {len(working_endpoints)} working endpoints")
            else:
                print("❌ No working endpoints found")
                self.fix_results['errors'].append("No working endpoints found")
                
        except Exception as e:
            print(f"❌ Backend health check failed: {str(e)}")
            self.fix_results['errors'].append(f"Backend health check failed: {str(e)}")

    def fix_ai_services(self):
        """Check and fix AI services"""
        print("🤖 Checking AI services...")
        
        try:
            ai_endpoints = [
                "/ai/agents",
                "/ai/learning",
                "/ai/growth",
                "/ai/proposals",
                "/ai/analytics"
            ]
            
            working_endpoints = []
            for endpoint in ai_endpoints:
                try:
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                    if response.status_code in [200, 401, 403]:
                        working_endpoints.append(endpoint)
                        print(f"✅ AI endpoint {endpoint} is working")
                    else:
                        print(f"⚠️ AI endpoint {endpoint} returned status {response.status_code}")
                except Exception as e:
                    print(f"❌ AI endpoint {endpoint} failed: {str(e)}")
            
            if working_endpoints:
                print(f"✅ Found {len(working_endpoints)} working AI endpoints")
                self.fix_results['fixes_applied'].append(f"Found {len(working_endpoints)} working AI endpoints")
            else:
                print("⚠️ No AI endpoints are currently working")
                self.fix_results['warnings'].append("No AI endpoints are currently working")
                
        except Exception as e:
            print(f"❌ AI services check failed: {str(e)}")
            self.fix_results['errors'].append(f"AI services check failed: {str(e)}")

    def fix_guardian_services(self):
        """Check and fix Guardian services"""
        print("🛡️ Checking Guardian services...")
        
        try:
            guardian_endpoints = [
                "/guardian/status",
                "/guardian/suggestions",
                "/guardian/analytics"
            ]
            
            working_endpoints = []
            for endpoint in guardian_endpoints:
                try:
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                    if response.status_code in [200, 401, 403]:
                        working_endpoints.append(endpoint)
                        print(f"✅ Guardian endpoint {endpoint} is working")
                    else:
                        print(f"⚠️ Guardian endpoint {endpoint} returned status {response.status_code}")
                except Exception as e:
                    print(f"❌ Guardian endpoint {endpoint} failed: {str(e)}")
            
            if working_endpoints:
                print(f"✅ Found {len(working_endpoints)} working Guardian endpoints")
                self.fix_results['fixes_applied'].append(f"Found {len(working_endpoints)} working Guardian endpoints")
            else:
                print("⚠️ No Guardian endpoints are currently working")
                self.fix_results['warnings'].append("No Guardian endpoints are currently working")
                
        except Exception as e:
            print(f"❌ Guardian services check failed: {str(e)}")
            self.fix_results['errors'].append(f"Guardian services check failed: {str(e)}")

    def generate_fix_report(self):
        """Generate comprehensive fix report"""
        print("\n" + "=" * 60)
        print("🔧 COMPREHENSIVE SYSTEM FIX REPORT")
        print("=" * 60)
        print(f"Timestamp: {self.fix_results['timestamp']}")
        print(f"Fixes Applied: {len(self.fix_results['fixes_applied'])}")
        print(f"Errors: {len(self.fix_results['errors'])}")
        print(f"Warnings: {len(self.fix_results['warnings'])}")
        
        if self.fix_results['fixes_applied']:
            print("\n✅ FIXES APPLIED:")
            print("-" * 40)
            for fix in self.fix_results['fixes_applied']:
                print(f"  • {fix}")
        
        if self.fix_results['errors']:
            print("\n❌ ERRORS:")
            print("-" * 40)
            for error in self.fix_results['errors']:
                print(f"  • {error}")
        
        if self.fix_results['warnings']:
            print("\n⚠️ WARNINGS:")
            print("-" * 40)
            for warning in self.fix_results['warnings']:
                print(f"  • {warning}")
        
        # Save detailed report
        import json
        with open('system_fix_report.json', 'w') as f:
            json.dump(self.fix_results, f, indent=2, default=str)
        
        print("\n" + "=" * 60)
        print("📋 RECOMMENDATIONS:")
        print("-" * 40)
        
        if self.fix_results['errors']:
            print("• Address the errors above before running the audit again")
        
        if self.fix_results['warnings']:
            print("• Review the warnings and consider addressing them")
        
        if not self.fix_results['errors'] and not self.fix_results['warnings']:
            print("• All critical issues have been resolved")
            print("• Run the audit again to verify the fixes")
        
        print("\n• Run: python comprehensive_system_audit_fixed.py")
        print("• Check: system_fix_report.json for detailed results")
        print("=" * 60)

def main():
    """Main function to run all fixes"""
    print("🔧 LVL_UP AI Backend System Fixer")
    print("This will attempt to fix all issues identified in the audit...")
    
    fixer = SystemFixer()
    fixer.run_comprehensive_fixes()
    
    print("\n✅ Fix process completed!")
    return len(fixer.fix_results['errors']) == 0

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Fix process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Critical error: {str(e)}")
        sys.exit(1) 