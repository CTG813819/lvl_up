#!/usr/bin/env python3
"""
Comprehensive AI Functionality Test
Tests that AIs are conducting proper work and generating real proposals
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
from typing import Dict, List, Any

# Test configuration
BASE_URL = "http://34.202.215.209:8000"
TEST_TIMEOUT = 30

class AITestSuite:
    def __init__(self):
        self.results = []
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=TEST_TIMEOUT))
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_result(self, test_name: str, success: bool, details: str = "", data: Any = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
    async def test_backend_health(self) -> bool:
        """Test if backend is running and healthy"""
        try:
            async with self.session.get(f"{BASE_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_result("Backend Health", True, f"Status: {data.get('status', 'unknown')}")
                    return True
                else:
                    self.log_result("Backend Health", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_result("Backend Health", False, f"Connection error: {str(e)}")
            return False
    
    async def test_ai_status(self) -> bool:
        """Test AI status endpoint"""
        try:
            async with self.session.get(f"{BASE_URL}/api/proposals/ai-status") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_result("AI Status", True, f"Found {len(data.get('ai_types', []))} AI types")
                    return True
                else:
                    self.log_result("AI Status", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_result("AI Status", False, f"Error: {str(e)}")
            return False
    
    async def test_proposal_validation(self) -> bool:
        """Test proposal validation service"""
        try:
            async with self.session.get(f"{BASE_URL}/api/proposals/validation/stats") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_result("Proposal Validation", True, f"Validation service active")
                    return True
                else:
                    self.log_result("Proposal Validation", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_result("Proposal Validation", False, f"Error: {str(e)}")
            return False
    
    async def test_ai_agent_generation(self) -> bool:
        """Test if AI agents can generate proposals"""
        try:
            # Trigger manual cycle to generate proposals
            async with self.session.post(f"{BASE_URL}/api/background/manual-cycle") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_result("AI Agent Generation", True, f"Manual cycle triggered: {data.get('status', 'unknown')}")
                    return True
                else:
                    self.log_result("AI Agent Generation", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_result("AI Agent Generation", False, f"Error: {str(e)}")
            return False
    
    async def test_recent_proposals(self) -> bool:
        """Test if there are recent proposals with real content"""
        try:
            async with self.session.get(f"{BASE_URL}/api/proposals/?limit=5") as response:
                if response.status == 200:
                    proposals = await response.json()
                    
                    if not proposals:
                        self.log_result("Recent Proposals", False, "No proposals found")
                        return False
                    
                    # Check if proposals have real content (not placeholder)
                    real_proposals = 0
                    for proposal in proposals:
                        code_before = proposal.get('code_before', '')
                        code_after = proposal.get('code_after', '')
                        
                        # Check if it's not a placeholder
                        if (code_before and code_before != "# before code" and 
                            code_after and code_after != "# after code" and
                            len(code_before) > 10 and len(code_after) > 10):
                            real_proposals += 1
                    
                    if real_proposals > 0:
                        self.log_result("Recent Proposals", True, f"Found {real_proposals}/{len(proposals)} real proposals")
                        return True
                    else:
                        self.log_result("Recent Proposals", False, "All proposals appear to be placeholders")
                        return False
                else:
                    self.log_result("Recent Proposals", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_result("Recent Proposals", False, f"Error: {str(e)}")
            return False
    
    async def test_ml_service(self) -> bool:
        """Test ML service functionality"""
        try:
            async with self.session.get(f"{BASE_URL}/api/enhanced-learning/status") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_result("ML Service", True, f"ML service active: {data.get('status', 'unknown')}")
                    return True
                else:
                    self.log_result("ML Service", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_result("ML Service", False, f"Error: {str(e)}")
            return False
    
    async def test_database_connection(self) -> bool:
        """Test database connection"""
        try:
            async with self.session.get(f"{BASE_URL}/api/proposals/stats/summary") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_result("Database Connection", True, f"Database accessible, {data.get('total_proposals', 0)} proposals")
                    return True
                else:
                    self.log_result("Database Connection", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_result("Database Connection", False, f"Error: {str(e)}")
            return False
    
    async def test_ai_learning(self) -> bool:
        """Test AI learning functionality"""
        try:
            # Test learning insights endpoint
            async with self.session.get(f"{BASE_URL}/api/learning/insights") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_result("AI Learning", True, f"Learning service active")
                    return True
                else:
                    self.log_result("AI Learning", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_result("AI Learning", False, f"Error: {str(e)}")
            return False
    
    async def test_background_service(self) -> bool:
        """Test background service functionality"""
        try:
            async with self.session.get(f"{BASE_URL}/api/background/status") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_result("Background Service", True, f"Background service active: {data.get('autonomous_cycle_running', False)}")
                    return True
                else:
                    self.log_result("Background Service", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_result("Background Service", False, f"Error: {str(e)}")
            return False
    
    async def test_imperium_agent(self) -> bool:
        """Test Imperium agent specifically"""
        try:
            async with self.session.get(f"{BASE_URL}/api/imperium/status") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_result("Imperium Agent", True, f"Imperium agent active: {data.get('status', 'unknown')}")
                    return True
                else:
                    self.log_result("Imperium Agent", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_result("Imperium Agent", False, f"Error: {str(e)}")
            return False
    
    async def test_guardian_agent(self) -> bool:
        """Test Guardian agent specifically"""
        try:
            async with self.session.get(f"{BASE_URL}/api/guardian/status") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_result("Guardian Agent", True, f"Guardian agent active: {data.get('status', 'unknown')}")
                    return True
                else:
                    self.log_result("Guardian Agent", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_result("Guardian Agent", False, f"Error: {str(e)}")
            return False
    
    async def test_sandbox_agent(self) -> bool:
        """Test Sandbox agent specifically"""
        try:
            async with self.session.get(f"{BASE_URL}/api/sandbox/") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_result("Sandbox Agent", True, f"Sandbox agent active: {data.get('status', 'unknown')}")
                    return True
                else:
                    self.log_result("Sandbox Agent", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_result("Sandbox Agent", False, f"Error: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🧪 Running Comprehensive AI Functionality Tests")
        print("=" * 60)
        
        tests = [
            self.test_backend_health,
            self.test_ai_status,
            self.test_proposal_validation,
            self.test_database_connection,
            self.test_ml_service,
            self.test_ai_learning,
            self.test_background_service,
            self.test_imperium_agent,
            self.test_guardian_agent,
            self.test_sandbox_agent,
            self.test_ai_agent_generation,
            self.test_recent_proposals,
        ]
        
        for test in tests:
            try:
                await test()
                await asyncio.sleep(1)  # Small delay between tests
            except Exception as e:
                self.log_result(test.__name__, False, f"Test failed with exception: {str(e)}")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in self.results if r['success'])
        total = len(self.results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! AIs are working properly.")
        else:
            print(f"\n⚠️  {total - passed} tests failed. Some AI functionality may need attention.")
        
        # Save results
        with open(f"ai_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
            json.dump(self.results, f, indent=2)
        
        return passed == total

async def main():
    """Main test function"""
    async with AITestSuite() as test_suite:
        success = await test_suite.run_all_tests()
        return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 