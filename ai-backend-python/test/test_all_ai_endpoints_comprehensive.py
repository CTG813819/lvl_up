#!/usr/bin/env python3
"""
Comprehensive AI Endpoints Test Suite
=====================================

This script tests all AI endpoints for the Imperium Learning Controller,
including validation, error handling, and performance metrics.

Test Coverage:
- Agent Registration & Management
- Learning Cycles & Analytics
- Internet Learning & Impact Analysis
- Persistence & Logging
- WebSocket Connections
- Trusted Sources Management
- Error Handling & Edge Cases

Author: Imperium AI System
Version: 2.0.0
"""

import requests
import time
import json
import asyncio
import websockets
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import sys

# Configuration
BASE_URL = "http://34.202.215.209:8000/api/imperium"
WS_URL = "ws://34.202.215.209:8000/api/imperium/ws/learning-analytics"

class TestStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    ERROR = "ERROR"

@dataclass
class TestResult:
    endpoint: str
    method: str
    status: TestStatus
    status_code: Optional[int]
    response_time: float
    error_message: Optional[str]
    response_data: Optional[Dict[str, Any]]
    agent_type: Optional[str] = None

class AITestSuite:
    def __init__(self):
        self.results: List[TestResult] = []
        self.session = requests.Session()
        self.test_agents = {}
        self.start_time = datetime.now()
        
    def log_test(self, endpoint: str, method: str, status: TestStatus, 
                 status_code: Optional[int], response_time: float, 
                 error_message: Optional[str] = None, 
                 response_data: Optional[Dict[str, Any]] = None,
                 agent_type: Optional[str] = None):
        """Log a test result"""
        result = TestResult(
            endpoint=endpoint,
            method=method,
            status=status,
            status_code=status_code,
            response_time=response_time,
            error_message=error_message,
            response_data=response_data,
            agent_type=agent_type
        )
        self.results.append(result)
        
        # Print result
        status_emoji = {
            TestStatus.PASS: "✅",
            TestStatus.FAIL: "❌",
            TestStatus.SKIP: "⏭️",
            TestStatus.ERROR: "💥"
        }
        
        print(f"{status_emoji[status]} {method} {endpoint} - {status_code or 'N/A'} ({response_time:.3f}s)")
        if error_message:
            print(f"   Error: {error_message}")
    
    def test_endpoint(self, method: str, endpoint: str, **kwargs) -> TestResult:
        """Test a single endpoint"""
        url = f"{BASE_URL}{endpoint}"
        start_time = time.time()
        
        try:
            if method == "GET":
                response = self.session.get(url, **kwargs)
            elif method == "POST":
                response = self.session.post(url, **kwargs)
            elif method == "DELETE":
                response = self.session.delete(url, **kwargs)
            else:
                return TestResult(
                    endpoint=endpoint,
                    method=method,
                    status=TestStatus.SKIP,
                    status_code=None,
                    response_time=time.time() - start_time,
                    error_message="Unsupported method"
                )
            
            response_time = time.time() - start_time
            
            # Determine test status
            if response.status_code < 400:
                status = TestStatus.PASS
            elif response.status_code < 500:
                status = TestStatus.FAIL
            else:
                status = TestStatus.ERROR
            
            # Parse response
            try:
                response_data = response.json() if response.content else None
            except:
                response_data = {"raw_response": response.text}
            
            result = TestResult(
                endpoint=endpoint,
                method=method,
                status=status,
                status_code=response.status_code,
                response_time=response_time,
                error_message=None if status == TestStatus.PASS else response.text,
                response_data=response_data
            )
            
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                endpoint=endpoint,
                method=method,
                status=TestStatus.ERROR,
                status_code=None,
                response_time=response_time,
                error_message=str(e)
            )
    
    def test_agent_registration(self, agent_type: str):
        """Test agent registration for a specific type"""
        print(f"\n🔧 Testing {agent_type.upper()} Agent Registration")
        
        agent_id = f"test_{agent_type}_agent_{int(time.time())}"
        
        # Test registration
        result = self.test_endpoint(
            "POST", "/agents/register",
            json={
                "agent_id": agent_id,
                "agent_type": agent_type,
                "priority": "high",
                "capabilities": ["learning", "analysis", "optimization"],
                "metadata": {"test_agent": True, "created_by": "test_suite"}
            }
        )
        result.agent_type = agent_type
        self.log_test(**result.__dict__)
        
        if result.status == TestStatus.PASS:
            self.test_agents[agent_id] = agent_type
            
            # Test get agent
            result = self.test_endpoint("GET", f"/agents/{agent_id}")
            result.agent_type = agent_type
            self.log_test(**result.__dict__)
            
            # Test pause
            result = self.test_endpoint("POST", f"/agents/{agent_id}/pause")
            result.agent_type = agent_type
            self.log_test(**result.__dict__)
            
            # Test resume
            result = self.test_endpoint("POST", f"/agents/{agent_id}/resume")
            result.agent_type = agent_type
            self.log_test(**result.__dict__)
            
            # Test add topic
            result = self.test_endpoint(
                "POST", f"/agents/{agent_id}/topics",
                json={"topic": f"Advanced {agent_type} Learning"}
            )
            result.agent_type = agent_type
            self.log_test(**result.__dict__)
            
            # Test unregister
            result = self.test_endpoint("DELETE", f"/agents/{agent_id}")
            result.agent_type = agent_type
            self.log_test(**result.__dict__)
            
            if result.status == TestStatus.PASS:
                del self.test_agents[agent_id]
    
    def test_learning_cycles(self):
        """Test learning cycle endpoints"""
        print(f"\n🔄 Testing Learning Cycles")
        
        # Test get cycles
        result = self.test_endpoint("GET", "/cycles")
        self.log_test(**result.__dict__)
        
        # Test trigger cycle
        result = self.test_endpoint("POST", "/cycles/trigger", json={})
        self.log_test(**result.__dict__)
        
        # Test get cycles again to see new cycle
        result = self.test_endpoint("GET", "/cycles")
        self.log_test(**result.__dict__)
    
    def test_internet_learning(self):
        """Test internet learning endpoints"""
        print(f"\n🌐 Testing Internet Learning")
        
        # Test trigger internet learning
        result = self.test_endpoint("POST", "/internet-learning/trigger", json={})
        self.log_test(**result.__dict__)
        
        # Test get log
        result = self.test_endpoint("GET", "/internet-learning/log")
        self.log_test(**result.__dict__)
        
        # Test get impact
        result = self.test_endpoint("GET", "/internet-learning/impact")
        self.log_test(**result.__dict__)
        
        # Test get interval
        result = self.test_endpoint("GET", "/internet-learning/interval")
        self.log_test(**result.__dict__)
        
        # Test set interval
        result = self.test_endpoint("POST", "/internet-learning/interval", json={"interval": 300})
        self.log_test(**result.__dict__)
        
        # Test get topics
        result = self.test_endpoint("GET", "/internet-learning/topics")
        self.log_test(**result.__dict__)
        
        # Test set topics
        result = self.test_endpoint("POST", "/internet-learning/topics", json={"topics": {"imperium": ["AI", "Machine Learning"], "guardian": ["Security", "Monitoring"], "sandbox": ["Testing", "Development"], "conquest": ["Optimization", "Performance"]}})
        self.log_test(**result.__dict__)
    
    def test_trusted_sources(self):
        """Test trusted sources management"""
        print(f"\n🔒 Testing Trusted Sources")
        
        # Test get sources
        result = self.test_endpoint("GET", "/trusted-sources")
        self.log_test(**result.__dict__)
        
        # Test add source
        test_url = "https://test-ai-source.example.com"
        result = self.test_endpoint("POST", "/trusted-sources", json={"url": test_url})
        self.log_test(**result.__dict__)
        
        # Test remove source
        result = self.test_endpoint("DELETE", "/trusted-sources", json={"url": test_url})
        self.log_test(**result.__dict__)
    
    def test_persistence(self):
        """Test persistence endpoints"""
        print(f"\n💾 Testing Persistence")
        
        # Test get agent metrics
        result = self.test_endpoint("GET", "/persistence/agent-metrics")
        self.log_test(**result.__dict__)
        
        # Test persist agent metrics (this might fail due to validation)
        result = self.test_endpoint("POST", "/persistence/agent-metrics", data='"test_agent"', headers={"Content-Type": "application/json"})
        self.log_test(**result.__dict__)
        
        # Test get learning cycles
        result = self.test_endpoint("GET", "/persistence/learning-cycles")
        self.log_test(**result.__dict__)
        
        # Test get learning analytics
        result = self.test_endpoint("GET", "/persistence/learning-analytics")
        self.log_test(**result.__dict__)
        
        # Test log learning event
        result = self.test_endpoint(
            "POST", "/persistence/log-learning-event",
            json={
                "event_type": "test_event",
                "agent_id": "test_agent",
                "agent_type": "imperium",
                "topic": "Test Learning",
                "impact_score": 5.0,
                "event_data": {"test": True}
            }
        )
        self.log_test(**result.__dict__)
        
        # Test persist internet learning result
        result = self.test_endpoint(
            "POST", "/persistence/internet-learning-result",
            json={
                "agent_id": "test_agent",
                "topic": "Test Topic",
                "source": "test_source",
                "result": {"summary": "Test result", "score": 8.5}
            }
        )
        self.log_test(**result.__dict__)
    
    def test_system_endpoints(self):
        """Test system-level endpoints"""
        print(f"\n⚙️ Testing System Endpoints")
        
        # Test initialize
        result = self.test_endpoint("POST", "/initialize")
        self.log_test(**result.__dict__)
        
        # Test status
        result = self.test_endpoint("GET", "/status")
        self.log_test(**result.__dict__)
        
        # Test get all agents
        result = self.test_endpoint("GET", "/agents")
        self.log_test(**result.__dict__)
        
        # Test dashboard
        result = self.test_endpoint("GET", "/dashboard")
        self.log_test(**result.__dict__)
    
    def test_error_handling(self):
        """Test error handling and edge cases"""
        print(f"\n🚨 Testing Error Handling")
        
        # Test invalid agent registration
        result = self.test_endpoint("POST", "/agents/register", json={})
        self.log_test(**result.__dict__)
        
        # Test invalid agent type
        result = self.test_endpoint("POST", "/agents/register", json={"agent_id": "test", "agent_type": "invalid"})
        self.log_test(**result.__dict__)
        
        # Test get non-existent agent
        result = self.test_endpoint("GET", "/agents/non_existent_agent")
        self.log_test(**result.__dict__)
        
        # Test pause non-existent agent
        result = self.test_endpoint("POST", "/agents/non_existent_agent/pause")
        self.log_test(**result.__dict__)
        
        # Test invalid internet learning trigger
        result = self.test_endpoint("POST", "/internet-learning/agent/non_existent_agent", params={"topic": "test"})
        self.log_test(**result.__dict__)
    
    async def test_websocket(self):
        """Test WebSocket connection"""
        print(f"\n🔌 Testing WebSocket Connection")
        
        try:
            async with websockets.connect(WS_URL) as websocket:
                # Wait for welcome message
                try:
                    welcome_response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                    welcome_data = json.loads(welcome_response)
                    
                    if welcome_data.get("type") == "welcome":
                        result = TestResult(
                            endpoint="/ws/learning-analytics",
                            method="WEBSOCKET",
                            status=TestStatus.PASS,
                            status_code=200,
                            response_time=0.0,
                            error_message=None,
                            response_data=welcome_data
                        )
                        self.log_test(**result.__dict__)
                    else:
                        result = TestResult(
                            endpoint="/ws/learning-analytics",
                            method="WEBSOCKET",
                            status=TestStatus.FAIL,
                            status_code=None,
                            response_time=3.0,
                            error_message="Unexpected response type",
                            response_data=welcome_data
                        )
                        self.log_test(**result.__dict__)
                        
                    # Test ping/pong
                    await websocket.send(json.dumps({"type": "ping", "timestamp": datetime.now().isoformat()}))
                    
                    try:
                        pong_response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                        pong_data = json.loads(pong_response)
                        
                        if pong_data.get("type") == "pong":
                            result = TestResult(
                                endpoint="/ws/learning-analytics",
                                method="WEBSOCKET_PING",
                                status=TestStatus.PASS,
                                status_code=200,
                                response_time=0.0,
                                error_message=None,
                                response_data=pong_data
                            )
                            self.log_test(**result.__dict__)
                        else:
                            result = TestResult(
                                endpoint="/ws/learning-analytics",
                                method="WEBSOCKET_PING",
                                status=TestStatus.FAIL,
                                status_code=None,
                                response_time=2.0,
                                error_message="Unexpected pong response",
                                response_data=pong_data
                            )
                            self.log_test(**result.__dict__)
                            
                    except asyncio.TimeoutError:
                        result = TestResult(
                            endpoint="/ws/learning-analytics",
                            method="WEBSOCKET_PING",
                            status=TestStatus.FAIL,
                            status_code=None,
                            response_time=2.0,
                            error_message="Timeout waiting for pong response",
                            response_data=None
                        )
                        self.log_test(**result.__dict__)
                        
                except asyncio.TimeoutError:
                    result = TestResult(
                        endpoint="/ws/learning-analytics",
                        method="WEBSOCKET",
                        status=TestStatus.FAIL,
                        status_code=None,
                        response_time=3.0,
                        error_message="Timeout waiting for welcome message",
                        response_data=None
                    )
                    self.log_test(**result.__dict__)
                    
        except Exception as e:
            result = TestResult(
                endpoint="/ws/learning-analytics",
                method="WEBSOCKET",
                status=TestStatus.ERROR,
                status_code=None,
                response_time=0.0,
                error_message=f"WebSocket connection failed: {str(e)}",
                response_data=None
            )
            self.log_test(**result.__dict__)
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print(f"\n📊 Test Report")
        print("=" * 50)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.status == TestStatus.PASS)
        failed_tests = sum(1 for r in self.results if r.status == TestStatus.FAIL)
        error_tests = sum(1 for r in self.results if r.status == TestStatus.ERROR)
        skipped_tests = sum(1 for r in self.results if r.status == TestStatus.SKIP)
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Errors: {error_tests} 💥")
        print(f"Skipped: {skipped_tests} ⏭️")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        # Average response time
        avg_response_time = sum(r.response_time for r in self.results) / total_tests
        print(f"Average Response Time: {avg_response_time:.3f}s")
        
        # Tests by agent type
        agent_results = {}
        for result in self.results:
            if result.agent_type:
                if result.agent_type not in agent_results:
                    agent_results[result.agent_type] = []
                agent_results[result.agent_type].append(result)
        
        if agent_results:
            print(f"\nResults by Agent Type:")
            for agent_type, results in agent_results.items():
                passed = sum(1 for r in results if r.status == TestStatus.PASS)
                total = len(results)
                print(f"  {agent_type}: {passed}/{total} ({passed/total*100:.1f}%)")
        
        # Failed tests summary
        failed_results = [r for r in self.results if r.status in [TestStatus.FAIL, TestStatus.ERROR]]
        if failed_results:
            print(f"\nFailed Tests:")
            for result in failed_results:
                print(f"  {result.method} {result.endpoint} - {result.status_code or 'N/A'}")
                if result.error_message:
                    print(f"    Error: {result.error_message[:100]}...")
        
        # Save detailed report
        report_data = {
            "test_suite": "Imperium AI Endpoints Comprehensive Test",
            "version": "2.0.0",
            "timestamp": datetime.now().isoformat(),
            "duration": (datetime.now() - self.start_time).total_seconds(),
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "errors": error_tests,
                "skipped": skipped_tests,
                "success_rate": passed_tests/total_tests*100,
                "avg_response_time": avg_response_time
            },
            "results": [result.__dict__ for result in self.results]
        }
        
        report_filename = f"test_report_{int(time.time())}.json"
        with open(report_filename, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"\nDetailed report saved to: {report_filename}")
        
        return passed_tests == total_tests
    
    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Comprehensive AI Endpoints Test Suite")
        print("=" * 60)
        try:
            # Test system endpoints first
            self.test_system_endpoints()
            # Test agent registration for each type
            agent_types = ["imperium", "guardian", "sandbox", "conquest"]
            for agent_type in agent_types:
                self.test_agent_registration(agent_type)
            # Test learning cycles
            self.test_learning_cycles()
            # Test internet learning
            self.test_internet_learning()
            # Test trusted sources
            self.test_trusted_sources()
            # Test persistence
            self.test_persistence()
            # Test error handling
            self.test_error_handling()
            # Test WebSocket
            asyncio.run(self.test_websocket())
        finally:
            # Generate report even if there was an error
            success = self.generate_report()
        return success

def main():
    """Main test runner"""
    test_suite = AITestSuite()
    
    try:
        success = test_suite.run_all_tests()
        
        if success:
            print("\n🎉 All tests passed!")
            sys.exit(0)
        else:
            print("\n⚠️ Some tests failed. Check the report for details.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 