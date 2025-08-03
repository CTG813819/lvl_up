"""
Comprehensive Test Script for New AI Services
Tests Project Horus, Olympic AI, Collaborative AI, and Custodes AI services
"""

import asyncio
import json
import time
from datetime import datetime
import structlog

# Import new AI services
from app.services.project_horus_service import project_horus_service
from app.services.olympic_ai_service import olympic_ai_service, OlympicEvent
from app.services.collaborative_ai_service import collaborative_ai_service, CollaborationType
from app.services.custodes_ai_service import custodes_ai_service, CustodesTestType

# Import database initialization
from app.core.database import init_database

logger = structlog.get_logger()

class NewAIServicesTester:
    """Comprehensive tester for new AI services"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = time.time()
        
    async def run_all_tests(self):
        """Run all tests for new AI services"""
        logger.info("🧪 Starting comprehensive test of new AI services")
        
        # Initialize database
        await init_database()
        
        # Test Project Horus
        await self.test_project_horus()
        
        # Test Olympic AI
        await self.test_olympic_ai()
        
        # Test Collaborative AI
        await self.test_collaborative_ai()
        
        # Test Custodes AI
        await self.test_custodes_ai()
        
        # Generate final report
        await self.generate_final_report()
        
    async def test_project_horus(self):
        """Test Project Horus Chaos code generation"""
        logger.info("🌀 Testing Project Horus service")
        
        try:
            # Test 1: Generate Chaos code
            chaos_result = await project_horus_service.generate_chaos_code("test_context")
            self.test_results["project_horus_chaos_generation"] = {
                "passed": "chaos_id" in chaos_result and "code" in chaos_result,
                "chaos_id": chaos_result.get("chaos_id"),
                "complexity": chaos_result.get("metadata", {}).get("complexity", 0),
                "learning_progress": chaos_result.get("metadata", {}).get("learning_progress", 0)
            }
            
            # Test 2: Assimilate existing code
            assimilation_result = await project_horus_service.assimilate_existing_code("test_codebase")
            self.test_results["project_horus_assimilation"] = {
                "passed": "target_codebase" in assimilation_result,
                "patterns_learned": assimilation_result.get("new_patterns_learned", 0),
                "frameworks_identified": assimilation_result.get("frameworks_identified", 0)
            }
            
            # Test 3: Get repository
            repository_result = await project_horus_service.get_chaos_code_repository()
            self.test_results["project_horus_repository"] = {
                "passed": "total_codes" in repository_result,
                "total_codes": repository_result.get("total_codes", 0),
                "knowledge_base_size": repository_result.get("knowledge_base_size", 0)
            }
            
            logger.info("✅ Project Horus tests completed")
            
        except Exception as e:
            logger.error(f"❌ Project Horus test failed: {str(e)}")
            self.test_results["project_horus"] = {"passed": False, "error": str(e)}
    
    async def test_olympic_ai(self):
        """Test Olympic AI competitive system"""
        logger.info("🏅 Testing Olympic AI service")
        
        try:
            # Test 1: Register competitors
            competitor1 = await olympic_ai_service.register_ai_competitor("imperium", {"code_quality": 0.8, "performance": 0.7})
            competitor2 = await olympic_ai_service.register_ai_competitor("guardian", {"code_quality": 0.9, "performance": 0.8})
            
            self.test_results["olympic_ai_registration"] = {
                "passed": "competitor_id" in competitor1 and "competitor_id" in competitor2,
                "competitor1_id": competitor1.get("competitor_id"),
                "competitor2_id": competitor2.get("competitor_id")
            }
            
            # Test 2: Start competition
            competitors = [competitor1["competitor_id"], competitor2["competitor_id"]]
            competition_result = await olympic_ai_service.start_olympic_competition(
                OlympicEvent.CODE_QUALITY, competitors
            )
            
            self.test_results["olympic_ai_competition"] = {
                "passed": "competition_id" in competition_result,
                "competition_id": competition_result.get("competition_id"),
                "participants": competition_result.get("participants", 0),
                "medals_awarded": len(competition_result.get("medals", {}).get("gold", [])) + 
                                len(competition_result.get("medals", {}).get("silver", [])) +
                                len(competition_result.get("medals", {}).get("bronze", []))
            }
            
            # Test 3: Get leaderboard
            leaderboard_result = await olympic_ai_service.get_olympic_leaderboard()
            self.test_results["olympic_ai_leaderboard"] = {
                "passed": "leaderboard" in leaderboard_result,
                "total_competitors": leaderboard_result.get("total_competitors", 0),
                "total_events": leaderboard_result.get("total_events", 0)
            }
            
            logger.info("✅ Olympic AI tests completed")
            
        except Exception as e:
            logger.error(f"❌ Olympic AI test failed: {str(e)}")
            self.test_results["olympic_ai"] = {"passed": False, "error": str(e)}
    
    async def test_collaborative_ai(self):
        """Test Collaborative AI team coordination"""
        logger.info("🤝 Testing Collaborative AI service")
        
        try:
            # Test 1: Create collaboration team
            team_result = await collaborative_ai_service.create_collaboration_team(
                "Test Team", ["imperium", "guardian"], CollaborationType.TEAM_PROJECT
            )
            
            self.test_results["collaborative_ai_team_creation"] = {
                "passed": "team_id" in team_result,
                "team_id": team_result.get("team_id"),
                "participants": len(team_result.get("ai_participants", []))
            }
            
            # Test 2: Start collaboration session
            if "team_id" in team_result:
                session_result = await collaborative_ai_service.start_collaboration_session(
                    team_result["team_id"], "Test collaboration topic", 1800
                )
                
                self.test_results["collaborative_ai_session"] = {
                    "passed": "session_id" in session_result,
                    "session_id": session_result.get("session_id"),
                    "knowledge_shared": session_result.get("knowledge_shared", {}).get("total_knowledge", 0)
                }
            
            # Test 3: Get collaboration statistics
            stats_result = await collaborative_ai_service.get_collaboration_statistics()
            self.test_results["collaborative_ai_statistics"] = {
                "passed": "total_sessions" in stats_result,
                "total_sessions": stats_result.get("total_sessions", 0),
                "total_knowledge_shared": stats_result.get("total_knowledge_shared", 0)
            }
            
            logger.info("✅ Collaborative AI tests completed")
            
        except Exception as e:
            logger.error(f"❌ Collaborative AI test failed: {str(e)}")
            self.test_results["collaborative_ai"] = {"passed": False, "error": str(e)}
    
    async def test_custodes_ai(self):
        """Test Custodes AI security and monitoring"""
        logger.info("🛡️ Testing Custodes AI service")
        
        try:
            # Test 1: Initiate security audit
            test_result = await custodes_ai_service.initiate_custodes_test(
                "imperium", CustodesTestType.SECURITY_AUDIT, "medium"
            )
            
            self.test_results["custodes_ai_security_test"] = {
                "passed": "test_id" in test_result,
                "test_id": test_result.get("test_id"),
                "overall_score": test_result.get("test_results", {}).get("overall_score", 0),
                "vulnerabilities_found": test_result.get("test_results", {}).get("vulnerabilities_found", 0)
            }
            
            # Test 2: Initiate performance test
            perf_test_result = await custodes_ai_service.initiate_custodes_test(
                "guardian", CustodesTestType.PERFORMANCE_TEST, "high"
            )
            
            self.test_results["custodes_ai_performance_test"] = {
                "passed": "test_id" in perf_test_result,
                "test_id": perf_test_result.get("test_id"),
                "overall_score": perf_test_result.get("test_results", {}).get("overall_score", 0)
            }
            
            # Test 3: Get test history
            history_result = await custodes_ai_service.get_custodes_test_history()
            self.test_results["custodes_ai_history"] = {
                "passed": "total_tests" in history_result,
                "total_tests": history_result.get("total_tests", 0),
                "passed_tests": history_result.get("passed_tests", 0),
                "failed_tests": history_result.get("failed_tests", 0)
            }
            
            logger.info("✅ Custodes AI tests completed")
            
        except Exception as e:
            logger.error(f"❌ Custodes AI test failed: {str(e)}")
            self.test_results["custodes_ai"] = {"passed": False, "error": str(e)}
    
    async def generate_final_report(self):
        """Generate comprehensive test report"""
        end_time = time.time()
        duration = end_time - self.start_time
        
        # Calculate overall statistics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if isinstance(result, dict) and result.get("passed", False))
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Generate detailed report
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": f"{success_rate:.1f}%",
                "duration_seconds": f"{duration:.2f}",
                "timestamp": datetime.utcnow().isoformat()
            },
            "service_results": {
                "project_horus": {
                    "chaos_generation": self.test_results.get("project_horus_chaos_generation", {}),
                    "assimilation": self.test_results.get("project_horus_assimilation", {}),
                    "repository": self.test_results.get("project_horus_repository", {})
                },
                "olympic_ai": {
                    "registration": self.test_results.get("olympic_ai_registration", {}),
                    "competition": self.test_results.get("olympic_ai_competition", {}),
                    "leaderboard": self.test_results.get("olympic_ai_leaderboard", {})
                },
                "collaborative_ai": {
                    "team_creation": self.test_results.get("collaborative_ai_team_creation", {}),
                    "session": self.test_results.get("collaborative_ai_session", {}),
                    "statistics": self.test_results.get("collaborative_ai_statistics", {})
                },
                "custodes_ai": {
                    "security_test": self.test_results.get("custodes_ai_security_test", {}),
                    "performance_test": self.test_results.get("custodes_ai_performance_test", {}),
                    "history": self.test_results.get("custodes_ai_history", {})
                }
            },
            "overall_status": "PASSED" if success_rate >= 80 else "PARTIAL" if success_rate >= 50 else "FAILED"
        }
        
        # Print report
        logger.info("📊 NEW AI SERVICES TEST REPORT")
        logger.info("=" * 50)
        logger.info(f"⏱️  Test Duration: {duration:.2f} seconds")
        logger.info(f"📈 Total Tests: {total_tests}")
        logger.info(f"✅ Passed: {passed_tests}")
        logger.info(f"❌ Failed: {failed_tests}")
        logger.info(f"📊 Success Rate: {success_rate:.1f}%")
        logger.info("=" * 50)
        
        # Print service-specific results
        for service, results in report["service_results"].items():
            logger.info(f"\n🔍 {service.upper().replace('_', ' ')} RESULTS:")
            for test_name, result in results.items():
                status = "✅ PASSED" if result.get("passed", False) else "❌ FAILED"
                logger.info(f"   {test_name}: {status}")
        
        logger.info(f"\n🏁 OVERALL STATUS: {report['overall_status']}")
        
        # Save detailed report
        with open(f"new_ai_services_test_report_{int(time.time())}.json", "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"📄 Detailed report saved to: new_ai_services_test_report_{int(time.time())}.json")
        
        return report

async def main():
    """Main test execution"""
    tester = NewAIServicesTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 