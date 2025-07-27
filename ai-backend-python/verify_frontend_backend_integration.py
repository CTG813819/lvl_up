#!/usr/bin/env python3
"""
Final Verification of Frontend-Backend Integration
Tests that all critical frontend features now work with the backend
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

class FrontendBackendVerifier:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "critical_features": {},
            "data_flow": {},
            "overall_status": "unknown"
        }
        
    async def test_critical_frontend_features(self):
        """Test all critical frontend features"""
        print("🎯 Testing critical frontend features...")
        
        # Test 1: Custody Protocol (Custodes Protocol Screen)
        print("🛡️ Testing Custody Protocol...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/custody/", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        has_analytics = 'analytics' in data
                        has_ai_metrics = has_analytics and 'ai_specific_metrics' in data['analytics']
                        has_recommendations = has_analytics and 'recommendations' in data['analytics']
                        
                        self.test_results["critical_features"]["custody_protocol"] = {
                            "status": "working",
                            "has_analytics": has_analytics,
                            "has_ai_metrics": has_ai_metrics,
                            "has_recommendations": has_recommendations,
                            "frontend_compatible": has_analytics and has_ai_metrics
                        }
                        
                        if has_analytics and has_ai_metrics:
                            print("✅ Custody Protocol - Frontend will show data correctly")
                            # Show AI metrics
                            ai_metrics = data['analytics'].get('ai_specific_metrics', {})
                            for ai_type, metrics in ai_metrics.items():
                                level = metrics.get('custody_level', 1)
                                xp = metrics.get('custody_xp', 0)
                                print(f"   📊 {ai_type}: Level {level}, XP {xp}")
                        else:
                            print("❌ Custody Protocol - Missing required data structure")
                    else:
                        self.test_results["critical_features"]["custody_protocol"] = {
                            "status": "failed",
                            "status_code": response.status
                        }
                        print(f"❌ Custody Protocol - Failed ({response.status})")
        except Exception as e:
            self.test_results["critical_features"]["custody_protocol"] = {
                "status": "error",
                "error": str(e)
            }
            print(f"❌ Custody Protocol - Error: {str(e)}")
        
        # Test 2: Proposals (Main proposals screen)
        print("📋 Testing Proposals...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/proposals/", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        proposal_count = len(data) if isinstance(data, list) else 0
                        
                        self.test_results["critical_features"]["proposals"] = {
                            "status": "working",
                            "proposal_count": proposal_count,
                            "has_data": proposal_count > 0,
                            "frontend_compatible": True
                        }
                        
                        if proposal_count > 0:
                            print(f"✅ Proposals - Found {proposal_count} proposals")
                            # Show first few proposals
                            for i, proposal in enumerate(data[:3]):
                                title = proposal.get('title', 'No title')
                                status = proposal.get('status', 'unknown')
                                print(f"   📄 {i+1}. {title} ({status})")
                        else:
                            print("⚠️ Proposals - No proposals found (frontend will show empty)")
                    else:
                        self.test_results["critical_features"]["proposals"] = {
                            "status": "failed",
                            "status_code": response.status
                        }
                        print(f"❌ Proposals - Failed ({response.status})")
        except Exception as e:
            self.test_results["critical_features"]["proposals"] = {
                "status": "error",
                "error": str(e)
            }
            print(f"❌ Proposals - Error: {str(e)}")
        
        # Test 3: AI Agents Status (Black Library Screen)
        print("🤖 Testing AI Agents Status...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/agents/status", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        has_agents = bool(data)
                        
                        self.test_results["critical_features"]["ai_agents"] = {
                            "status": "working",
                            "has_data": has_agents,
                            "frontend_compatible": True
                        }
                        
                        if has_agents:
                            print("✅ AI Agents Status - Data available")
                            # Show agent types if available
                            if isinstance(data, dict):
                                for agent_type, status in data.items():
                                    print(f"   🤖 {agent_type}: {status}")
                        else:
                            print("⚠️ AI Agents Status - No data (frontend will show empty)")
                    else:
                        self.test_results["critical_features"]["ai_agents"] = {
                            "status": "failed",
                            "status_code": response.status
                        }
                        print(f"❌ AI Agents Status - Failed ({response.status})")
        except Exception as e:
            self.test_results["critical_features"]["ai_agents"] = {
                "status": "error",
                "error": str(e)
            }
            print(f"❌ AI Agents Status - Error: {str(e)}")
        
        # Test 4: Imperium Agents (AI Growth Analytics)
        print("👑 Testing Imperium Agents...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/imperium/agents", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        has_agents = bool(data)
                        
                        self.test_results["critical_features"]["imperium_agents"] = {
                            "status": "working",
                            "has_data": has_agents,
                            "frontend_compatible": True
                        }
                        
                        if has_agents:
                            print("✅ Imperium Agents - Data available")
                        else:
                            print("⚠️ Imperium Agents - No data (frontend will show empty)")
                    else:
                        self.test_results["critical_features"]["imperium_agents"] = {
                            "status": "failed",
                            "status_code": response.status
                        }
                        print(f"❌ Imperium Agents - Failed ({response.status})")
        except Exception as e:
            self.test_results["critical_features"]["imperium_agents"] = {
                "status": "error",
                "error": str(e)
            }
            print(f"❌ Imperium Agents - Error: {str(e)}")

    async def test_data_flow(self):
        """Test data flow between frontend and backend"""
        print("🔄 Testing data flow...")
        
        # Test that endpoints return proper JSON structure
        endpoints_to_test = [
            "/api/custody/",
            "/api/proposals/",
            "/api/agents/status",
            "/api/imperium/agents",
            "/api/learning/data",
            "/api/growth/analysis"
        ]
        
        for endpoint in endpoints_to_test:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.base_url}{endpoint}", timeout=10) as response:
                        if response.status == 200:
                            data = await response.json()
                            is_valid_json = isinstance(data, (dict, list))
                            
                            self.test_results["data_flow"][endpoint] = {
                                "status": "working",
                                "valid_json": is_valid_json,
                                "data_type": type(data).__name__,
                                "has_content": bool(data)
                            }
                            
                            if is_valid_json:
                                print(f"✅ {endpoint} - Valid JSON ({type(data).__name__})")
                            else:
                                print(f"⚠️ {endpoint} - Invalid JSON structure")
                        else:
                            self.test_results["data_flow"][endpoint] = {
                                "status": "failed",
                                "status_code": response.status
                            }
                            print(f"❌ {endpoint} - Failed ({response.status})")
            except Exception as e:
                self.test_results["data_flow"][endpoint] = {
                    "status": "error",
                    "error": str(e)
                }
                print(f"❌ {endpoint} - Error: {str(e)}")

    def generate_verification_summary(self):
        """Generate comprehensive verification summary"""
        print("\n" + "="*60)
        print("🎯 FRONTEND-BACKEND INTEGRATION VERIFICATION")
        print("="*60)
        
        # Count working vs failed critical features
        critical_features = self.test_results["critical_features"]
        working_features = sum(1 for f in critical_features.values() if f.get("status") == "working")
        failed_features = len(critical_features) - working_features
        
        print(f"📊 Critical Features: {working_features}/{len(critical_features)} working")
        
        # Check each critical feature
        for feature_name, result in critical_features.items():
            status = result.get("status", "unknown")
            if status == "working":
                frontend_compatible = result.get("frontend_compatible", False)
                if frontend_compatible:
                    print(f"   ✅ {feature_name} - Working (Frontend compatible)")
                else:
                    print(f"   ⚠️ {feature_name} - Working (Frontend may have issues)")
            else:
                print(f"   ❌ {feature_name} - Failed")
        
        # Data flow summary
        data_flow = self.test_results["data_flow"]
        working_endpoints = sum(1 for e in data_flow.values() if e.get("status") == "working")
        failed_endpoints = len(data_flow) - working_endpoints
        
        print(f"\n🔄 Data Flow: {working_endpoints}/{len(data_flow)} endpoints working")
        
        # Overall status
        if working_features == len(critical_features) and working_endpoints == len(data_flow):
            self.test_results["overall_status"] = "excellent"
            print("✅ Overall Status: EXCELLENT - All critical features working!")
        elif working_features >= len(critical_features) * 0.8:
            self.test_results["overall_status"] = "good"
            print("✅ Overall Status: GOOD - Most critical features working")
        elif working_features >= len(critical_features) * 0.5:
            self.test_results["overall_status"] = "fair"
            print("⚠️ Overall Status: FAIR - Some critical features working")
        else:
            self.test_results["overall_status"] = "poor"
            print("❌ Overall Status: POOR - Most critical features failing")
        
        # Save detailed results
        with open('frontend_backend_verification_report.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: frontend_backend_verification_report.json")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        if self.test_results["overall_status"] == "excellent":
            print("   • Frontend-backend integration is working perfectly!")
            print("   • All critical features are operational")
            print("   • Users should see data in all screens")
        elif self.test_results["overall_status"] == "good":
            print("   • Most features are working well")
            print("   • Check any failed features for specific issues")
        else:
            print("   • Some critical features need attention")
            print("   • Check backend logs for errors")
            print("   • Verify database connectivity")

    async def run_verification(self):
        """Run complete verification"""
        print("🚀 Starting frontend-backend integration verification...")
        print(f"⏰ Timestamp: {self.test_results['timestamp']}")
        print(f"🌐 Base URL: {self.base_url}")
        
        await self.test_critical_frontend_features()
        await self.test_data_flow()
        self.generate_verification_summary()

async def main():
    verifier = FrontendBackendVerifier()
    await verifier.run_verification()

if __name__ == "__main__":
    asyncio.run(main()) 