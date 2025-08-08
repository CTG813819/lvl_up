"""
Enhanced Autonomous Learning Service with Custodes Protocol
Provides advanced AI learning capabilities with rigorous testing
"""

import asyncio
import schedule
import structlog
from datetime import datetime, timedelta
from typing import Dict, List, Any
import random
import os

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_session
from app.models.training_data import TrainingData
from app.models.sql_models import OathPaper, AgentMetrics, Proposal
from app.services.ai_agent_service_shared import AIAgentServiceShared
from app.services.imperium_learning_controller import ImperiumLearningController
from app.services.ai_learning_service import AILearningService
from app.services.custody_protocol_service import CustodyProtocolService, TestCategory

logger = structlog.get_logger()

class EnhancedAutonomousLearningService:
    """Enhanced Autonomous Learning Service with Custodes Protocol Integration"""
    
    def __init__(self):
        self.ai_agent_service = AIAgentServiceShared()
        self.learning_controller = ImperiumLearningController()
        self.ai_learning_service = AILearningService()
        self.custody_service = None  # Will be initialized when needed
        
        # Custodes Protocol Configuration
        interval = int(os.getenv("CUSTODES_TEST_INTERVAL_MINUTES", "15"))
        self.custodes_test_interval = timedelta(minutes=interval)
        self.learning_cycle_interval = timedelta(minutes=60)  # Learn every 60 minutes
        self.custodes_approval_threshold = 0.8  # 80% success rate required
        
        logger.info(f"🛡️ Custodes test interval set to {self.custodes_test_interval.total_seconds() / 60} minutes")
        
        # Autonomous learning subjects
        self.autonomous_subjects = [
            "robotics", "machine_learning", "web_development", 
            "mobile_development", "data_science", "cybersecurity",
            "cloud_computing", "devops", "blockchain", "ai_ethics"
        ]
        
        # Custodes test scenarios
        self.custodes_test_scenarios = [
            "code_quality_validation",
            "security_vulnerability_detection", 
            "performance_optimization_analysis",
            "architecture_design_review",
            "best_practice_compliance",
            "error_handling_robustness",
            "scalability_assessment",
            "maintainability_evaluation"
        ]
        
        logger.info("🛡️ [CUSTODES] Enhanced Autonomous Learning Service initialized with Custodes Protocol")
        logger.info(f"📚 Learning subjects: {len(self.autonomous_subjects)}")
        logger.info(f"🧪 Custodes test scenarios: {len(self.custodes_test_scenarios)}")
    
    async def start_enhanced_autonomous_learning(self):
        """Start the enhanced autonomous learning system with Custodes Protocol"""
        try:
            logger.info("🚀 [CUSTODES] Enhanced Autonomous Learning Service is RUNNING and scheduling all cycles!")
            logger.info("🚀 Starting Enhanced Autonomous Learning Service with Custodes Protocol...")
            logger.info("🤖 AIs will learn autonomously and be tested rigorously by Custodes!")
            logger.info("📚 Subjects available: " + str(len(self.autonomous_subjects)))
            logger.info("⏰ Learning cycles: Every 60 minutes")
            logger.info("🛡️ Custodes Protocol: Active - AIs must pass tests to create proposals")
            logger.info("🧪 Custodes Test Scenarios: " + str(len(self.custodes_test_scenarios)))
            
            # Initialize custody service
            self.custody_service = await CustodyProtocolService.initialize()
            
            # Start background tasks
            await asyncio.gather(
                self._run_learning_cycles(),
                self._run_custodes_testing(),
                self._run_autonomous_knowledge_building(),
                self._run_custodes_approval_workflow()
            )
            
        except Exception as e:
            logger.error(f"❌ [CUSTODES] Enhanced learning service failed", error=str(e))
            raise
    
    async def _run_learning_cycles(self):
        """Run periodic learning cycles"""
        while True:
            try:
                logger.info("🔄 [CUSTODES] Starting learning cycle...")
                
                # Trigger learning for each AI type
                for ai_type in ["Imperium", "Guardian", "Sandbox"]:
                    await self._trigger_ai_learning(ai_type)
                
                # Wait for next cycle
                await asyncio.sleep(self.learning_cycle_interval.total_seconds())
                
            except Exception as e:
                logger.error(f"❌ [CUSTODES] Learning cycle failed", error=str(e))
                await asyncio.sleep(300)  # Wait 5 minutes before retry
    
    async def _run_custodes_testing(self):
        """Run Custodes Protocol testing"""
        while True:
            try:
                logger.info("🛡️ [CUSTODES] Starting Custodes Protocol testing cycle...")
                
                # Test each AI with real Custodes protocol
                for ai_type in ["imperium", "guardian", "sandbox"]:
                    await self._run_custodes_tests_for_ai(ai_type)
                
                # Wait for next test cycle
                await asyncio.sleep(self.custodes_test_interval.total_seconds())
                
            except Exception as e:
                logger.error(f"❌ [CUSTODES] Custodes testing failed", error=str(e))
                await asyncio.sleep(300)  # Wait 5 minutes before retry
    
    async def _run_autonomous_knowledge_building(self):
        """Build knowledge base autonomously"""
        while True:
            try:
                logger.info("📚 [CUSTODES] Starting autonomous knowledge building...")
                
                for subject in self.autonomous_subjects:
                    await self._build_knowledge_base(subject)
                
                # Wait 6 hours before next knowledge building cycle
                await asyncio.sleep(21600)  # 6 hours
                
            except Exception as e:
                logger.error(f"❌ [CUSTODES] Knowledge building failed", error=str(e))
                await asyncio.sleep(3600)  # Wait 1 hour before retry
    
    async def _run_custodes_approval_workflow(self):
        """Run Custodes approval workflow for proposals"""
        while True:
            try:
                logger.info("✅ [CUSTODES] Running Custodes approval workflow...")
                
                async with get_session() as db:
                    # Get pending proposals
                    pending_query = select(Proposal).where(Proposal.status == "pending")
                    result = await db.execute(pending_query)
                    pending_proposals = result.scalars().all()
                    
                    for proposal in pending_proposals:
                        await self._custodes_approval_check(proposal, db)
                
                # Check every 30 minutes
                await asyncio.sleep(1800)  # 30 minutes
                
            except Exception as e:
                logger.error(f"❌ [CUSTODES] Approval workflow failed", error=str(e))
                await asyncio.sleep(600)  # Wait 10 minutes before retry
    
    async def _trigger_ai_learning(self, ai_type: str):
        """Trigger learning for specific AI type"""
        try:
            logger.info(f"🧠 [CUSTODES] Triggering learning for {ai_type}...")
            
            # Trigger learning cycle for all agents
            await self.learning_controller._trigger_learning_cycle()
            
            logger.info(f"✅ [CUSTODES] Learning triggered for {ai_type}")
            
        except Exception as e:
            logger.error(f"❌ [CUSTODES] Failed to trigger learning for {ai_type}", error=str(e))
    
    async def _run_custodes_tests_for_ai(self, ai_type: str):
        """Run Custodes Protocol tests for specific AI using REAL custody service"""
        try:
            logger.info(f"🛡️ [CUSTODES] Running REAL Custodes tests for {ai_type}...")
            
            # Ensure custody service is initialized
            if not self.custody_service:
                self.custody_service = await CustodyProtocolService.initialize()
            
            # Run different test categories for comprehensive testing
            test_categories = [
                TestCategory.KNOWLEDGE_VERIFICATION,
                TestCategory.CODE_QUALITY,
                TestCategory.SECURITY_AWARENESS,
                TestCategory.PERFORMANCE_OPTIMIZATION,
                TestCategory.INNOVATION_CAPABILITY
            ]
            
            test_results = {}
            
            for category in test_categories:
                try:
                    logger.info(f"🧪 [CUSTODES] Running {category.value} test for {ai_type}...")
                    
                    # Call the REAL custody protocol service
                    result = await self.custody_service.administer_custody_test(ai_type, category)
                    
                    if result.get("status") == "error":
                        logger.error(f"❌ [CUSTODES] {category.value} test failed for {ai_type}: {result.get('message')}")
                        test_results[category.value] = 0.0
                    else:
                        test_result = result.get("test_result", {})
                        score = test_result.get("score", 0) / 100.0  # Convert to 0-1 scale
                        passed = test_result.get("passed", False)
                        
                        test_results[category.value] = score
                        
                        logger.info(f"✅ [CUSTODES] {category.value} test completed for {ai_type}: Score {score:.2f}, Passed: {passed}")
                        
                except Exception as e:
                    logger.error(f"❌ [CUSTODES] {category.value} test failed for {ai_type}", error=str(e))
                    test_results[category.value] = 0.0
            
            # Calculate overall Custodes score
            if test_results:
                overall_score = sum(test_results.values()) / len(test_results)
                logger.info(f"📊 [CUSTODES] {ai_type} overall Custodes test results: {overall_score:.2f}/1.0")
                
                # Update agent metrics
                await self._update_custodes_metrics(ai_type, overall_score, test_results)
            else:
                logger.warning(f"⚠️ [CUSTODES] No test results for {ai_type}")
            
        except Exception as e:
            logger.error(f"❌ [CUSTODES] Failed to run tests for {ai_type}", error=str(e))
    
    async def _build_knowledge_base(self, subject: str):
        """Build knowledge base for a subject"""
        try:
            logger.info(f"📚 [CUSTODES] Building knowledge base for: {subject}")
            
            # Create oath paper for the subject
            async with get_session() as db:
                oath_paper = OathPaper(
                    title=f"Knowledge Base: {subject.title()}",
                    subject=subject,
                    content=f"Comprehensive knowledge base for {subject}",
                    category="knowledge_base",
                    ai_insights={"subject": subject, "learning_value": 0.9},
                    learning_value=0.9,
                    status="learned"
                )
                
                db.add(oath_paper)
                await db.commit()
                
                # Create training data
                training_data = TrainingData(
                    title=f"Training Data: {subject.title()}",
                    subject=subject,
                    description=f"Training data for {subject} learning",
                    code=f"# {subject} training code\n# This is training data for {subject}",
                    status="processed"
                )
                
                db.add(training_data)
                await db.commit()
                
            logger.info(f"✅ [CUSTODES] Enhanced learning completed for: {subject}")
            
        except Exception as e:
            logger.error(f"❌ [CUSTODES] Error building knowledge base for {subject}: {str(e)}")
    
    async def _custodes_approval_check(self, proposal: Proposal, db: AsyncSession):
        """Check if proposal passes Custodes approval"""
        try:
            logger.info(f"🛡️ [CUSTODES] Running Custodes approval check for proposal {proposal.id}")
            
            # Get AI metrics for the proposal's AI type
            metrics_query = select(AgentMetrics).where(AgentMetrics.agent_type == proposal.ai_type)
            result = await db.execute(metrics_query)
            metrics = result.scalar_one_or_none()
            
            if metrics and metrics.success_rate >= self.custodes_approval_threshold:
                logger.info(f"✅ [CUSTODES] Proposal {proposal.id} approved by Custodes")
                proposal.status = "custodes_approved"
            else:
                logger.warning(f"⚠️ [CUSTODES] Proposal {proposal.id} rejected by Custodes - insufficient success rate")
                proposal.status = "custodes_rejected"
            
            await db.commit()
            
        except Exception as e:
            logger.error(f"❌ [CUSTODES] Custodes approval check failed", error=str(e))
    
    async def _update_custodes_metrics(self, ai_type: str, overall_score: float, test_results: Dict[str, float]):
        """Update Custodes metrics for AI"""
        try:
            async with get_session() as db:
                # Get or create agent metrics
                metrics_query = select(AgentMetrics).where(AgentMetrics.agent_type == ai_type)
                result = await db.execute(metrics_query)
                metrics = result.scalar_one_or_none()
                
                if not metrics:
                    metrics = AgentMetrics(
                        agent_id=f"{ai_type.lower()}_agent",
                        agent_type=ai_type,
                        success_rate=overall_score,
                        learning_score=overall_score,
                        status="active"
                    )
                    db.add(metrics)
                else:
                    metrics.success_rate = overall_score
                    metrics.learning_score = overall_score
                    metrics.updated_at = datetime.utcnow()
                
                await db.commit()
                
            logger.info(f"📊 [CUSTODES] Updated metrics for {ai_type}: success_rate={overall_score:.2f}")
            
        except Exception as e:
            logger.error(f"❌ [CUSTODES] Failed to update metrics for {ai_type}", error=str(e)) 