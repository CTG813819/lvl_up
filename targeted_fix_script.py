#!/usr/bin/env python3
"""
Targeted Fix Script for LVL_UP AI Backend
Addresses specific issues found in the comprehensive fix report.
"""

import os
import sys
import psycopg2
import subprocess
import requests
import json
from datetime import datetime

class TargetedFixer:
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
            'warnings': [],
            'backend_analysis': {}
        }

    def run_targeted_fixes(self):
        """Run targeted fixes for specific issues"""
        print("🎯 Starting targeted system fixes...")
        print("=" * 60)
        
        try:
            # Fix database schema issues
            self.fix_database_schema_safely()
            
            # Analyze backend routing
            self.analyze_backend_routing()
            
            # Check for missing routes
            self.check_missing_routes()
            
            # Generate targeted report
            self.generate_targeted_report()
            
        except Exception as e:
            print(f"❌ Critical error during targeted fixes: {str(e)}")
            self.fix_results['errors'].append(f"Critical fix error: {str(e)}")

    def fix_database_schema_safely(self):
        """Safely fix database schema without conflicts"""
        print("📊 Safely fixing database schema...")
        
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Check proposals table structure
            cursor.execute("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'proposals' 
                ORDER BY ordinal_position
            """)
            proposals_columns = cursor.fetchall()
            print(f"Proposals table columns: {[col[0] for col in proposals_columns]}")
            
            # Check if agents table exists
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'agents'
            """)
            agents_exists = cursor.fetchone()
            
            if not agents_exists:
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
            else:
                print("✅ Agents table already exists")
            
            # Check if ai_learning_summaries table exists
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'ai_learning_summaries'
            """)
            learning_exists = cursor.fetchone()
            
            if not learning_exists:
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
            else:
                print("✅ ai_learning_summaries table already exists")
            
            # Check token_usage table structure
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'token_usage'
            """)
            token_columns = [row[0] for row in cursor.fetchall()]
            
            if 'tokens_used' not in token_columns:
                cursor.execute("ALTER TABLE token_usage ADD COLUMN tokens_used INTEGER DEFAULT 0")
                print("✅ Added tokens_used column to token_usage table")
                self.fix_results['fixes_applied'].append("Added tokens_used column to token_usage table")
            else:
                print("✅ tokens_used column already exists in token_usage table")
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print("✅ Database schema fixes completed safely")
            
        except Exception as e:
            print(f"❌ Database schema fix failed: {str(e)}")
            self.fix_results['errors'].append(f"Database schema fix failed: {str(e)}")

    def analyze_backend_routing(self):
        """Analyze backend routing and available endpoints"""
        print("🔍 Analyzing backend routing...")
        
        try:
            # Check what's actually running on port 8000
            result = subprocess.run(['netstat', '-tlnp'], capture_output=True, text=True)
            if result.returncode == 0:
                port_8000_info = [line for line in result.stdout.split('\n') if ':8000' in line]
                print(f"Port 8000 info: {port_8000_info}")
            
            # Check backend process details
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            if result.returncode == 0:
                uvicorn_processes = [line for line in result.stdout.split('\n') if 'uvicorn' in line]
                print(f"Uvicorn processes: {uvicorn_processes}")
            
            # Test the working endpoint to understand the API structure
            try:
                response = requests.get(f"{self.base_url}/api/health", timeout=5)
                if response.status_code == 200:
                    print(f"✅ /api/health response: {response.text[:200]}...")
                    self.fix_results['backend_analysis']['working_endpoint'] = {
                        'url': '/api/health',
                        'status': response.status_code,
                        'response': response.text[:200]
                    }
            except Exception as e:
                print(f"❌ Error testing /api/health: {str(e)}")
            
            # Try to find the actual API structure
            possible_endpoints = [
                "/api/v1/health",
                "/api/v1/status",
                "/api/status",
                "/health",
                "/",
                "/docs",
                "/openapi.json"
            ]
            
            working_endpoints = []
            for endpoint in possible_endpoints:
                try:
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                    if response.status_code in [200, 401, 403]:
                        working_endpoints.append(endpoint)
                        print(f"✅ Found working endpoint: {endpoint} (status: {response.status_code})")
                except Exception as e:
                    print(f"❌ Endpoint {endpoint} failed: {str(e)}")
            
            self.fix_results['backend_analysis']['working_endpoints'] = working_endpoints
            
        except Exception as e:
            print(f"❌ Backend routing analysis failed: {str(e)}")
            self.fix_results['errors'].append(f"Backend routing analysis failed: {str(e)}")

    def check_missing_routes(self):
        """Check for missing AI and Guardian routes"""
        print("🔍 Checking for missing routes...")
        
        try:
            # Check if there are any route files in the backend
            result = subprocess.run(['find', '/home/ubuntu', '-name', '*.py', '-path', '*/routers/*'], capture_output=True, text=True)
            if result.returncode == 0:
                router_files = result.stdout.strip().split('\n')
                print(f"Found router files: {router_files}")
                
                # Look for AI and Guardian related files
                ai_files = [f for f in router_files if 'ai' in f.lower()]
                guardian_files = [f for f in router_files if 'guardian' in f.lower()]
                
                print(f"AI-related router files: {ai_files}")
                print(f"Guardian-related router files: {guardian_files}")
                
                self.fix_results['backend_analysis']['router_files'] = {
                    'all': router_files,
                    'ai': ai_files,
                    'guardian': guardian_files
                }
            
            # Check the main backend directory structure
            result = subprocess.run(['ls', '-la', '/home/ubuntu'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Home directory contents: {result.stdout}")
            
            # Look for the actual backend application
            result = subprocess.run(['find', '/home/ubuntu', '-name', 'main.py'], capture_output=True, text=True)
            if result.returncode == 0:
                main_files = result.stdout.strip().split('\n')
                print(f"Main.py files found: {main_files}")
                
                if main_files:
                    # Check the content of the first main.py
                    try:
                        with open(main_files[0], 'r') as f:
                            main_content = f.read()
                            print(f"Main.py content (first 500 chars): {main_content[:500]}...")
                    except Exception as e:
                        print(f"Could not read main.py: {str(e)}")
            
        except Exception as e:
            print(f"❌ Route checking failed: {str(e)}")
            self.fix_results['errors'].append(f"Route checking failed: {str(e)}")

    def generate_targeted_report(self):
        """Generate targeted fix report"""
        print("\n" + "=" * 60)
        print("🎯 TARGETED SYSTEM FIX REPORT")
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
        
        if self.fix_results['backend_analysis']:
            print("\n🔍 BACKEND ANALYSIS:")
            print("-" * 40)
            if 'working_endpoints' in self.fix_results['backend_analysis']:
                print(f"  • Working endpoints: {self.fix_results['backend_analysis']['working_endpoints']}")
            if 'router_files' in self.fix_results['backend_analysis']:
                print(f"  • AI router files: {self.fix_results['backend_analysis']['router_files']['ai']}")
                print(f"  • Guardian router files: {self.fix_results['backend_analysis']['router_files']['guardian']}")
        
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
        with open('targeted_fix_report.json', 'w') as f:
            json.dump(self.fix_results, f, indent=2, default=str)
        
        print("\n" + "=" * 60)
        print("📋 NEXT STEPS:")
        print("-" * 40)
        
        if self.fix_results['backend_analysis'].get('router_files', {}).get('ai'):
            print("• AI router files found - check if they're properly registered")
        else:
            print("• No AI router files found - may need to create them")
        
        if self.fix_results['backend_analysis'].get('router_files', {}).get('guardian'):
            print("• Guardian router files found - check if they're properly registered")
        else:
            print("• No Guardian router files found - may need to create them")
        
        print("\n• Run: python comprehensive_system_audit_fixed.py")
        print("• Check: targeted_fix_report.json for detailed analysis")
        print("=" * 60)

def main():
    """Main function to run targeted fixes"""
    print("🎯 LVL_UP AI Backend Targeted Fixer")
    print("This will analyze and fix specific issues...")
    
    fixer = TargetedFixer()
    fixer.run_targeted_fixes()
    
    print("\n✅ Targeted fix process completed!")
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