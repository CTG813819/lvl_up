#!/usr/bin/env python3
"""
Check Endpoint Mismatches Between Frontend and Backend
Identifies which endpoints the frontend calls vs what the backend provides
"""

import asyncio
import aiohttp
import json
import sys
import os
import subprocess
from datetime import datetime

class EndpointMismatchChecker:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.frontend_endpoints = set()
        self.backend_endpoints = set()
        self.working_endpoints = set()
        self.failed_endpoints = set()
        
    def extract_frontend_endpoints(self):
        """Extract endpoints from frontend code"""
        print("📱 Extracting frontend endpoints...")
        
        # Common frontend endpoints found in the grep search
        frontend_calls = [
            "/api/custody/",
            "/api/custody/test/{aiType}/force",
            "/api/agents/status", 
            "/api/proposals",
            "/api/proposals?status=pending",
            "/api/proposals/{id}/accept",
            "/api/proposals/{id}/apply",
            "/api/imperium/agents",
            "/api/imperium/status",
            "/api/guardian/health-check",
            "/api/guardian/",
            "/api/guardian/security-status",
            "/api/guardian/code-review",
            "/api/guardian/threat-detection",
            "/api/imperium/monitoring",
            "/api/imperium/improvements",
            "/api/imperium/issues",
            "/api/imperium/trigger-scan",
            "/api/imperium/learning/data",
            "/api/imperium/dashboard",
            "/api/learning/effectiveness",
            "/api/learning/test",
            "/api/learning/data",
            "/api/learning/insights/{aiType}",
            "/api/approval/pending",
            "/api/approval/stats/overview",
            "/api/imperium/trusted-sources",
            "/api/terra/extensions",
            "/api/terra/extensions/{extensionId}",
            "/api/ai/upload-training-data",
            "/api/ai/research-subject",
            "/api/notifications/ws",
            "/api/missions/sync",
            "/api/missions/statistics",
            "/api/missions/health-check",
            "/api/feedback",
            "/api/usage",
            "/api/error",
            "/api/performance",
            "/api/analytics",
            "/api/growth/analysis",
            "/api/growth/insights",
            "/api/oath-papers/enhanced-learning",
            "/api/oath-papers",
            "/api/proposals/quotas",
            "/api/codex/log",
            "/api/codex/",
            "/health",
            "/api/conquest/force-work",
            "/api/conquest/improve-app",
            "/api/conquest/deployments",
            "/api/ai/learning/cross-ai",
            "/api/notifications/send",
            "/api/imperium/agents/{agentId}/topics"
        ]
        
        self.frontend_endpoints = set(frontend_calls)
        print(f"📋 Found {len(self.frontend_endpoints)} frontend endpoint calls")
        
        # Show the most critical ones
        critical_endpoints = [
            "/api/custody/",
            "/api/proposals",
            "/api/agents/status",
            "/api/imperium/agents",
            "/api/health"
        ]
        
        print("🎯 Critical frontend endpoints:")
        for endpoint in critical_endpoints:
            print(f"   • {endpoint}")

    async def discover_backend_endpoints(self):
        """Discover what endpoints the backend actually provides"""
        print("🔍 Discovering backend endpoints...")
        
        # Try to get OpenAPI docs
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/docs", timeout=10) as response:
                    if response.status == 200:
                        content = await response.text()
                        # Extract endpoints from OpenAPI docs
                        import re
                        endpoints = re.findall(r'/api/[^"<>]*', content)
                        self.backend_endpoints = set(endpoints)
                        print(f"📊 Found {len(self.backend_endpoints)} endpoints in OpenAPI docs")
                    else:
                        print(f"❌ Could not access /docs (status: {response.status})")
                        await self.fallback_endpoint_discovery()
        except Exception as e:
            print(f"❌ Error accessing /docs: {str(e)}")
            await self.fallback_endpoint_discovery()

    async def fallback_endpoint_discovery(self):
        """Fallback method to discover endpoints"""
        print("🔄 Using fallback endpoint discovery...")
        
        # Common endpoints that should exist
        common_endpoints = [
            "/api/health",
            "/api/proposals/",
            "/api/custody/",
            "/api/ai/imperium/status",
            "/api/ai/guardian/status",
            "/api/ai/sandbox/status", 
            "/api/ai/conquest/status",
            "/api/ai/agents/status",
            "/api/learning/",
            "/api/analytics/",
            "/api/health/advanced",
            "/api/health/detailed"
        ]
        
        self.backend_endpoints = set(common_endpoints)
        print(f"📊 Using {len(self.backend_endpoints)} common endpoints")

    async def test_endpoints(self):
        """Test which endpoints actually work"""
        print("🧪 Testing endpoint availability...")
        
        all_endpoints = self.frontend_endpoints.union(self.backend_endpoints)
        
        for endpoint in sorted(all_endpoints):
            try:
                async with aiohttp.ClientSession() as session:
                    # Convert path parameters to test values
                    test_endpoint = endpoint.replace("{id}", "1").replace("{aiType}", "imperium").replace("{agentId}", "1")
                    
                    async with session.get(f"{self.base_url}{test_endpoint}", timeout=5) as response:
                        if response.status in [200, 201, 204]:
                            self.working_endpoints.add(endpoint)
                            print(f"✅ {endpoint} - working ({response.status})")
                        else:
                            self.failed_endpoints.add(endpoint)
                            print(f"❌ {endpoint} - failed ({response.status})")
            except Exception as e:
                self.failed_endpoints.add(endpoint)
                print(f"❌ {endpoint} - error: {str(e)}")

    def analyze_mismatches(self):
        """Analyze mismatches between frontend and backend"""
        print("\n" + "="*60)
        print("🔍 ENDPOINT MISMATCH ANALYSIS")
        print("="*60)
        
        # Frontend-only endpoints (backend doesn't provide)
        frontend_only = self.frontend_endpoints - self.backend_endpoints
        print(f"\n📱 Frontend-only endpoints ({len(frontend_only)}):")
        for endpoint in sorted(frontend_only):
            status = "✅ working" if endpoint in self.working_endpoints else "❌ failed"
            print(f"   • {endpoint} - {status}")
        
        # Backend-only endpoints (frontend doesn't use)
        backend_only = self.backend_endpoints - self.frontend_endpoints
        print(f"\n🔧 Backend-only endpoints ({len(backend_only)}):")
        for endpoint in sorted(backend_only):
            status = "✅ working" if endpoint in self.working_endpoints else "❌ failed"
            print(f"   • {endpoint} - {status}")
        
        # Common endpoints
        common = self.frontend_endpoints.intersection(self.backend_endpoints)
        print(f"\n🤝 Common endpoints ({len(common)}):")
        for endpoint in sorted(common):
            status = "✅ working" if endpoint in self.working_endpoints else "❌ failed"
            print(f"   • {endpoint} - {status}")
        
        # Critical mismatches
        critical_frontend = {
            "/api/custody/",
            "/api/proposals",
            "/api/agents/status",
            "/api/imperium/agents"
        }
        
        critical_missing = critical_frontend - self.working_endpoints
        if critical_missing:
            print(f"\n🚨 CRITICAL: Missing working endpoints ({len(critical_missing)}):")
            for endpoint in sorted(critical_missing):
                print(f"   • {endpoint} - Frontend expects this but it's not working")
        
        # Save detailed report
        report = {
            "timestamp": datetime.now().isoformat(),
            "frontend_endpoints": list(self.frontend_endpoints),
            "backend_endpoints": list(self.backend_endpoints),
            "working_endpoints": list(self.working_endpoints),
            "failed_endpoints": list(self.failed_endpoints),
            "frontend_only": list(frontend_only),
            "backend_only": list(backend_only),
            "common_endpoints": list(common),
            "critical_missing": list(critical_missing)
        }
        
        with open('endpoint_mismatch_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: endpoint_mismatch_report.json")
        
        # Summary
        total_endpoints = len(self.frontend_endpoints.union(self.backend_endpoints))
        working_percentage = (len(self.working_endpoints) / total_endpoints * 100) if total_endpoints > 0 else 0
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total endpoints tested: {total_endpoints}")
        print(f"   Working endpoints: {len(self.working_endpoints)} ({working_percentage:.1f}%)")
        print(f"   Failed endpoints: {len(self.failed_endpoints)}")
        print(f"   Critical missing: {len(critical_missing)}")
        
        if len(critical_missing) == 0:
            print("✅ All critical endpoints are working!")
        else:
            print("❌ Critical endpoints are missing - frontend will have issues")

    async def run_analysis(self):
        """Run complete endpoint analysis"""
        print("🚀 Starting endpoint mismatch analysis...")
        print(f"⏰ Timestamp: {datetime.now().isoformat()}")
        
        self.extract_frontend_endpoints()
        await self.discover_backend_endpoints()
        await self.test_endpoints()
        self.analyze_mismatches()

async def main():
    checker = EndpointMismatchChecker()
    await checker.run_analysis()

if __name__ == "__main__":
    asyncio.run(main()) 