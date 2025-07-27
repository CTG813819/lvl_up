#!/usr/bin/env python3
"""
Comprehensive Frontend-Backend Integration Check
Checks all elements needed for frontend to backend communication
"""

import asyncio
import aiohttp
import json
import sys
import os
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Any

class FrontendBackendChecker:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "unknown",
            "database_status": "unknown",
            "endpoints": {},
            "frontend_requirements": {},
            "issues": [],
            "recommendations": []
        }
        
    async def check_database_connection(self):
        """Check database connection and identify the _static_cache_key error"""
        print("🔍 Checking database connection...")
        try:
            # Test database connection through API
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/health", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.results["database_status"] = "connected"
                        print("✅ Database connection working")
                    else:
                        self.results["database_status"] = "error"
                        self.results["issues"].append(f"Database health check failed: {response.status}")
                        print(f"❌ Database health check failed: {response.status}")
        except Exception as e:
            self.results["database_status"] = "error"
            self.results["issues"].append(f"Database connection error: {str(e)}")
            print(f"❌ Database connection error: {str(e)}")
            
        # Check for SQLAlchemy version compatibility issues
        try:
            result = subprocess.run([
                "python3", "-c", 
                "import sqlalchemy; print(f'SQLAlchemy version: {sqlalchemy.__version__}')"
            ], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"📊 {version}")
                if "1.4" in version or "2.0" in version:
                    self.results["issues"].append("SQLAlchemy version may be causing _static_cache_key errors")
                    self.results["recommendations"].append("Consider downgrading SQLAlchemy to 1.3.x or upgrading to 2.0+")
            else:
                print("❌ Could not check SQLAlchemy version")
        except Exception as e:
            print(f"❌ Error checking SQLAlchemy version: {str(e)}")

    async def check_ai_agents_endpoints(self):
        """Check all AI agent endpoints"""
        print("🤖 Checking AI agent endpoints...")
        endpoints = [
            "/api/ai/imperium/status",
            "/api/ai/guardian/status", 
            "/api/ai/sandbox/status",
            "/api/ai/conquest/status",
            "/api/ai/agents/status"
        ]
        
        for endpoint in endpoints:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.base_url}{endpoint}", timeout=10) as response:
                        if response.status == 200:
                            data = await response.json()
                            self.results["endpoints"][endpoint] = {
                                "status": "working",
                                "response_time": response.headers.get("X-Response-Time", "unknown"),
                                "has_data": bool(data)
                            }
                            print(f"✅ {endpoint} - working")
                        else:
                            self.results["endpoints"][endpoint] = {
                                "status": "failed",
                                "status_code": response.status
                            }
                            print(f"❌ {endpoint} - failed ({response.status})")
            except Exception as e:
                self.results["endpoints"][endpoint] = {
                    "status": "error",
                    "error": str(e)
                }
                print(f"❌ {endpoint} - error: {str(e)}")

    async def check_proposals_endpoints(self):
        """Check proposal endpoints - critical for frontend display"""
        print("📋 Checking proposal endpoints...")
        endpoints = [
            "/api/proposals/",
            "/api/proposals/validation/stats",
            "/api/proposals/active",
            "/api/proposals/recent"
        ]
        
        for endpoint in endpoints:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.base_url}{endpoint}", timeout=15) as response:
                        if response.status == 200:
                            data = await response.json()
                            proposal_count = len(data) if isinstance(data, list) else 0
                            self.results["endpoints"][endpoint] = {
                                "status": "working",
                                "proposal_count": proposal_count,
                                "has_data": bool(data)
                            }
                            print(f"✅ {endpoint} - working ({proposal_count} proposals)")
                        else:
                            self.results["endpoints"][endpoint] = {
                                "status": "failed",
                                "status_code": response.status
                            }
                            print(f"❌ {endpoint} - failed ({response.status})")
                            if endpoint == "/api/proposals/":
                                self.results["issues"].append("Main proposals endpoint not working - frontend won't show proposals")
            except Exception as e:
                self.results["endpoints"][endpoint] = {
                    "status": "error",
                    "error": str(e)
                }
                print(f"❌ {endpoint} - error: {str(e)}")
                if endpoint == "/api/proposals/":
                    self.results["issues"].append(f"Proposals endpoint error: {str(e)}")

    async def check_custody_endpoints(self):
        """Check custody protocol endpoints"""
        print("🛡️ Checking custody endpoints...")
        endpoints = [
            "/api/custody/",
            "/api/custody/eligibility",
            "/api/custody/analytics"
        ]
        
        for endpoint in endpoints:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.base_url}{endpoint}", timeout=10) as response:
                        if response.status == 200:
                            data = await response.json()
                            has_analytics = 'analytics' in data if isinstance(data, dict) else False
                            self.results["endpoints"][endpoint] = {
                                "status": "working",
                                "has_analytics": has_analytics,
                                "has_data": bool(data)
                            }
                            print(f"✅ {endpoint} - working")
                        else:
                            self.results["endpoints"][endpoint] = {
                                "status": "failed",
                                "status_code": response.status
                            }
                            print(f"❌ {endpoint} - failed ({response.status})")
            except Exception as e:
                self.results["endpoints"][endpoint] = {
                    "status": "error",
                    "error": str(e)
                }
                print(f"❌ {endpoint} - error: {str(e)}")

    async def check_learning_endpoints(self):
        """Check AI learning endpoints"""
        print("🧠 Checking learning endpoints...")
        endpoints = [
            "/api/learning/",
            "/api/learning/agents",
            "/api/learning/summary"
        ]
        
        for endpoint in endpoints:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.base_url}{endpoint}", timeout=10) as response:
                        if response.status == 200:
                            data = await response.json()
                            self.results["endpoints"][endpoint] = {
                                "status": "working",
                                "has_data": bool(data)
                            }
                            print(f"✅ {endpoint} - working")
                        else:
                            self.results["endpoints"][endpoint] = {
                                "status": "failed",
                                "status_code": response.status
                            }
                            print(f"❌ {endpoint} - failed ({response.status})")
            except Exception as e:
                self.results["endpoints"][endpoint] = {
                    "status": "error",
                    "error": str(e)
                }
                print(f"❌ {endpoint} - error: {str(e)}")

    async def check_analytics_endpoints(self):
        """Check analytics dashboard endpoints"""
        print("📊 Checking analytics endpoints...")
        endpoints = [
            "/api/analytics/",
            "/api/analytics/performance",
            "/api/analytics/leveling"
        ]
        
        for endpoint in endpoints:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.base_url}{endpoint}", timeout=10) as response:
                        if response.status == 200:
                            data = await response.json()
                            self.results["endpoints"][endpoint] = {
                                "status": "working",
                                "has_data": bool(data)
                            }
                            print(f"✅ {endpoint} - working")
                        else:
                            self.results["endpoints"][endpoint] = {
                                "status": "failed",
                                "status_code": response.status
                            }
                            print(f"❌ {endpoint} - failed ({response.status})")
            except Exception as e:
                self.results["endpoints"][endpoint] = {
                    "status": "error",
                    "error": str(e)
                }
                print(f"❌ {endpoint} - error: {str(e)}")

    async def check_health_endpoints(self):
        """Check health and monitoring endpoints"""
        print("🏥 Checking health endpoints...")
        endpoints = [
            "/api/health",
            "/api/health/advanced",
            "/api/health/detailed"
        ]
        
        for endpoint in endpoints:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.base_url}{endpoint}", timeout=10) as response:
                        if response.status == 200:
                            data = await response.json()
                            self.results["endpoints"][endpoint] = {
                                "status": "working",
                                "has_data": bool(data)
                            }
                            print(f"✅ {endpoint} - working")
                        else:
                            self.results["endpoints"][endpoint] = {
                                "status": "failed",
                                "status_code": response.status
                            }
                            print(f"❌ {endpoint} - failed ({response.status})")
            except Exception as e:
                self.results["endpoints"][endpoint] = {
                    "status": "error",
                    "error": str(e)
                }
                print(f"❌ {endpoint} - error: {str(e)}")

    def analyze_frontend_requirements(self):
        """Analyze what the frontend needs from backend"""
        print("📱 Analyzing frontend requirements...")
        
        # Check what endpoints frontend actually calls
        frontend_files = [
            "../lib/screens/custodes_protocol_screen.dart",
            "../lib/screens/black_library_screen.dart",
            "../lib/screens/ai_guardian_analytics_screen.dart",
            "../lib/main.dart",
            "../lib/home_page.dart"
        ]
        
        required_endpoints = set()
        
        for file_path in frontend_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Look for API calls
                        if '/api/' in content:
                            lines = content.split('\n')
                            for line in lines:
                                if '/api/' in line and 'Uri.parse' in line:
                                    # Extract endpoint from Uri.parse
                                    if 'Uri.parse' in line:
                                        start = line.find('Uri.parse(') + 10
                                        end = line.find(')', start)
                                        if start > 9 and end > start:
                                            uri = line[start:end]
                                            if '/api/' in uri:
                                                # Extract just the endpoint part
                                                api_start = uri.find('/api/')
                                                if api_start >= 0:
                                                    endpoint = uri[api_start:]
                                                    if '"' in endpoint:
                                                        endpoint = endpoint.split('"')[0]
                                                    required_endpoints.add(endpoint)
                except Exception as e:
                    print(f"⚠️ Could not analyze {file_path}: {str(e)}")
        
        self.results["frontend_requirements"]["required_endpoints"] = list(required_endpoints)
        print(f"📋 Frontend requires these endpoints: {list(required_endpoints)}")
        
        # Check if all required endpoints are working
        missing_endpoints = []
        for endpoint in required_endpoints:
            if endpoint not in self.results["endpoints"]:
                missing_endpoints.append(endpoint)
            elif self.results["endpoints"][endpoint]["status"] != "working":
                missing_endpoints.append(endpoint)
        
        if missing_endpoints:
            self.results["issues"].append(f"Frontend missing endpoints: {missing_endpoints}")
            print(f"❌ Frontend missing endpoints: {missing_endpoints}")
        else:
            print("✅ All frontend-required endpoints are working")

    def check_database_schema_issues(self):
        """Check for database schema issues that might cause _static_cache_key errors"""
        print("🗄️ Checking database schema issues...")
        
        # Check if there are any SQLAlchemy model issues
        try:
            result = subprocess.run([
                "python3", "-c", 
                "import sys; sys.path.append('.'); from app.database import engine; print('Database engine OK')"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                error_msg = result.stderr.strip()
                if "_static_cache_key" in error_msg:
                    self.results["issues"].append("SQLAlchemy _static_cache_key error detected")
                    self.results["recommendations"].append("Check SQLAlchemy version compatibility")
                    print("❌ SQLAlchemy _static_cache_key error detected")
                else:
                    print(f"⚠️ Database import error: {error_msg}")
            else:
                print("✅ Database engine import successful")
        except Exception as e:
            print(f"❌ Error checking database schema: {str(e)}")

    def generate_summary(self):
        """Generate comprehensive summary"""
        print("\n" + "="*60)
        print("🎯 FRONTEND-BACKEND INTEGRATION CHECK SUMMARY")
        print("="*60)
        
        # Count working vs failed endpoints
        working = sum(1 for ep in self.results["endpoints"].values() if ep["status"] == "working")
        failed = sum(1 for ep in self.results["endpoints"].values() if ep["status"] != "working")
        total = len(self.results["endpoints"])
        
        print(f"📊 Endpoint Health: {working}/{total} working ({working/total*100:.1f}%)")
        print(f"🗄️ Database Status: {self.results['database_status']}")
        print(f"🚨 Issues Found: {len(self.results['issues'])}")
        
        if self.results["issues"]:
            print("\n🚨 CRITICAL ISSUES:")
            for issue in self.results["issues"]:
                print(f"   • {issue}")
        
        if self.results["recommendations"]:
            print("\n💡 RECOMMENDATIONS:")
            for rec in self.results["recommendations"]:
                print(f"   • {rec}")
        
        # Check specific frontend requirements
        print(f"\n📱 Frontend Requirements:")
        print(f"   Required endpoints: {len(self.results['frontend_requirements'].get('required_endpoints', []))}")
        
        # Save detailed results
        with open('frontend_backend_integration_report.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: frontend_backend_integration_report.json")
        
        # Overall status
        if failed == 0 and self.results["database_status"] == "connected":
            self.results["overall_status"] = "healthy"
            print("✅ Overall Status: HEALTHY - All systems operational")
        elif failed <= 2:
            self.results["overall_status"] = "warning"
            print("⚠️ Overall Status: WARNING - Minor issues detected")
        else:
            self.results["overall_status"] = "critical"
            print("❌ Overall Status: CRITICAL - Multiple issues detected")

    async def run_comprehensive_check(self):
        """Run all checks"""
        print("🚀 Starting comprehensive frontend-backend integration check...")
        print(f"⏰ Timestamp: {self.results['timestamp']}")
        print(f"🌐 Base URL: {self.base_url}")
        
        # Run all checks
        await self.check_database_connection()
        await self.check_ai_agents_endpoints()
        await self.check_proposals_endpoints()
        await self.check_custody_endpoints()
        await self.check_learning_endpoints()
        await self.check_analytics_endpoints()
        await self.check_health_endpoints()
        
        # Analyze frontend requirements
        self.analyze_frontend_requirements()
        
        # Check database schema issues
        self.check_database_schema_issues()
        
        # Generate summary
        self.generate_summary()

async def main():
    checker = FrontendBackendChecker()
    await checker.run_comprehensive_check()

if __name__ == "__main__":
    asyncio.run(main()) 