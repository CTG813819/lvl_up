#!/usr/bin/env python3
"""
Script to ensure all learning cycles and AI learning activities are properly persisted to the Neon database
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.core.database import init_database, get_session
from app.services.token_usage_service import token_usage_service
from app.services.ai_learning_service import AILearningService
from app.services.imperium_learning_controller import ImperiumLearningController
from app.services.agent_metrics_service import AgentMetricsService
from app.core.config import settings
from app.models.sql_models import (
    AgentMetrics, LearningCycle, LearningLog, InternetLearningResult,
    AIAnswer, LearningRecord, ExplainabilityMetrics, CustodyTestResult
)
from sqlalchemy import select, and_, func
import structlog

logger = structlog.get_logger()

class LearningPersistenceManager:
    """Manager to ensure all learning activities are properly persisted to the database"""
    
    def __init__(self):
        self.learning_service = None
        self.learning_controller = None
        self.agent_metrics_service = None
    
    async def initialize(self):
        """Initialize all services"""
        try:
            # Initialize database
            await init_database()
            
            # Initialize services
            self.learning_service = await AILearningService.initialize()
            self.learning_controller = await ImperiumLearningController.initialize()
            self.agent_metrics_service = AgentMetricsService()
            
            logger.info("✅ Learning Persistence Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Error initializing Learning Persistence Manager: {str(e)}")
            raise
    
    async def ensure_agent_metrics_persistence(self):
        """Ensure all agent metrics are properly persisted"""
        try:
            logger.info("🔍 Checking agent metrics persistence...")
            
            async with get_session() as session:
                # Get all agent metrics from database
                stmt = select(AgentMetrics)
                result = await session.execute(stmt)
                db_metrics = result.scalars().all()
                
                logger.info(f"📊 Found {len(db_metrics)} agent metrics in database")
                
                # Check each AI type
                ai_types = ["imperium", "guardian", "sandbox", "conquest"]
                
                for ai_type in ai_types:
                    # Get metrics from learning controller
                    controller_metrics = self.learning_controller._agent_metrics.get(ai_type)
                    
                    if controller_metrics:
                        # Check if metrics exist in database
                        db_metric = next((m for m in db_metrics if m.agent_id == ai_type), None)
                        
                        if db_metric:
                            # Update database with latest controller data
                            db_metric.learning_score = controller_metrics.learning_score
                            db_metric.success_rate = controller_metrics.success_rate
                            db_metric.failure_rate = controller_metrics.failure_rate
                            db_metric.total_learning_cycles = controller_metrics.total_learning_cycles
                            db_metric.last_learning_cycle = controller_metrics.last_learning_cycle
                            db_metric.last_success = controller_metrics.last_success
                            db_metric.last_failure = controller_metrics.last_failure
                            db_metric.learning_patterns = controller_metrics.learning_patterns
                            db_metric.improvement_suggestions = controller_metrics.improvement_suggestions
                            db_metric.status = controller_metrics.status.value
                            db_metric.updated_at = datetime.utcnow()
                            
                            logger.info(f"✅ Updated agent metrics for {ai_type}")
                        else:
                            # Create new agent metrics record
                            new_metric = AgentMetrics(
                                agent_id=ai_type,
                                agent_type=ai_type,
                                learning_score=controller_metrics.learning_score,
                                success_rate=controller_metrics.success_rate,
                                failure_rate=controller_metrics.failure_rate,
                                total_learning_cycles=controller_metrics.total_learning_cycles,
                                last_learning_cycle=controller_metrics.last_learning_cycle,
                                last_success=controller_metrics.last_success,
                                last_failure=controller_metrics.last_failure,
                                learning_patterns=controller_metrics.learning_patterns,
                                improvement_suggestions=controller_metrics.improvement_suggestions,
                                status=controller_metrics.status.value,
                                is_active=controller_metrics.is_active
                            )
                            session.add(new_metric)
                            logger.info(f"✅ Created new agent metrics for {ai_type}")
                    else:
                        logger.warning(f"⚠️ No controller metrics found for {ai_type}")
                
                await session.commit()
                logger.info("✅ Agent metrics persistence check completed")
                
        except Exception as e:
            logger.error(f"❌ Error ensuring agent metrics persistence: {str(e)}")
    
    async def ensure_learning_cycles_persistence(self):
        """Ensure all learning cycles are properly persisted"""
        try:
            logger.info("🔍 Checking learning cycles persistence...")
            
            async with get_session() as session:
                # Get all learning cycles from database
                stmt = select(LearningCycle)
                result = await session.execute(stmt)
                db_cycles = result.scalars().all()
                
                logger.info(f"📊 Found {len(db_cycles)} learning cycles in database")
                
                # Get learning cycles from controller
                controller_cycles = self.learning_controller._learning_cycles
                logger.info(f"📊 Found {len(controller_cycles)} learning cycles in controller")
                
                # Persist any cycles that aren't in database
                for cycle in controller_cycles:
                    # Check if cycle exists in database
                    db_cycle = next((c for c in db_cycles if c.cycle_id == cycle.cycle_id), None)
                    
                    if not db_cycle:
                        # Create new learning cycle record
                        new_cycle = LearningCycle(
                            cycle_id=cycle.cycle_id,
                            start_time=cycle.start_time,
                            end_time=cycle.end_time,
                            participating_agents=cycle.participating_agents,
                            total_learning_value=cycle.total_learning_value,
                            success_count=cycle.success_count,
                            failure_count=cycle.failure_count,
                            insights_generated=cycle.insights_generated,
                            status=cycle.status.value,
                            cycle_metadata=cycle.metadata
                        )
                        session.add(new_cycle)
                        logger.info(f"✅ Created new learning cycle: {cycle.cycle_id}")
                
                await session.commit()
                logger.info("✅ Learning cycles persistence check completed")
                
        except Exception as e:
            logger.error(f"❌ Error ensuring learning cycles persistence: {str(e)}")
    
    async def ensure_learning_logs_persistence(self):
        """Ensure all learning logs are properly persisted"""
        try:
            logger.info("🔍 Checking learning logs persistence...")
            
            async with get_session() as session:
                # Get recent learning logs from database
                stmt = select(LearningLog).order_by(LearningLog.created_at.desc()).limit(100)
                result = await session.execute(stmt)
                db_logs = result.scalars().all()
                
                logger.info(f"📊 Found {len(db_logs)} recent learning logs in database")
                
                # Get internet learning log from controller
                internet_logs = self.learning_controller.get_internet_learning_log(limit=50)
                logger.info(f"📊 Found {len(internet_logs)} internet learning logs in controller")
                
                # Persist any recent internet learning events
                for log_entry in internet_logs:
                    # Check if this event is already logged
                    existing_log = next((l for l in db_logs if 
                                       l.event_type == "internet_learning" and
                                       l.agent_id == log_entry.get("agent_id") and
                                       l.topic == log_entry.get("topic")), None)
                    
                    if not existing_log:
                        # Create new learning log record
                        new_log = LearningLog(
                            event_type="internet_learning",
                            agent_id=log_entry.get("agent_id"),
                            agent_type=log_entry.get("agent_id"),
                            topic=log_entry.get("topic"),
                            results_count=log_entry.get("results_count", 0),
                            results_sample=log_entry.get("results_sample"),
                            insights=log_entry.get("insights"),
                            impact_score=log_entry.get("learning_value", 0.0),
                            event_data=log_entry
                        )
                        session.add(new_log)
                        logger.info(f"✅ Created new learning log for {log_entry.get('agent_id')} - {log_entry.get('topic')}")
                
                await session.commit()
                logger.info("✅ Learning logs persistence check completed")
                
        except Exception as e:
            logger.error(f"❌ Error ensuring learning logs persistence: {str(e)}")
    
    async def ensure_ai_answers_persistence(self):
        """Ensure all AI answers are properly persisted"""
        try:
            logger.info("🔍 Checking AI answers persistence...")
            
            async with get_session() as session:
                # Get recent AI answers from database
                stmt = select(AIAnswer).order_by(AIAnswer.created_at.desc()).limit(100)
                result = await session.execute(stmt)
                db_answers = result.scalars().all()
                
                logger.info(f"📊 Found {len(db_answers)} recent AI answers in database")
                
                # Get learning data from learning service
                learning_data = self.learning_service._learning_data
                logger.info(f"📊 Found {len(learning_data)} learning data entries in service")
                
                # Persist any recent learning data that isn't already in database
                for learning_entry in learning_data[-50:]:  # Last 50 entries
                    if learning_entry.get("source") == "ai_answer":
                        # Check if this answer is already in database
                        existing_answer = next((a for a in db_answers if 
                                             a.ai_type == learning_entry.get("ai_type") and
                                             a.prompt == learning_entry.get("prompt") and
                                             a.answer == learning_entry.get("answer")), None)
                        
                        if not existing_answer:
                            # Create new AI answer record
                            explainability_data = learning_entry.get("explainability_data", {})
                            new_answer = AIAnswer(
                                ai_type=learning_entry.get("ai_type"),
                                prompt=learning_entry.get("prompt"),
                                answer=learning_entry.get("answer"),
                                reasoning_trace=explainability_data.get("reasoning_trace"),
                                confidence_score=explainability_data.get("confidence_score", 50.0),
                                reasoning_quality=explainability_data.get("reasoning_quality"),
                                uncertainty_areas=explainability_data.get("uncertainty_areas", []),
                                knowledge_applied=explainability_data.get("knowledge_applied", []),
                                is_fallback=explainability_data.get("is_fallback", False),
                                self_assessment=explainability_data.get("self_assessment"),
                                learning_context_used=learning_entry.get("learning_context_used", False),
                                prompt_length=learning_entry.get("prompt_length", 0),
                                answer_length=learning_entry.get("answer_length", 0),
                                source="ai_answer"
                            )
                            session.add(new_answer)
                            logger.info(f"✅ Created new AI answer for {learning_entry.get('ai_type')}")
                
                await session.commit()
                logger.info("✅ AI answers persistence check completed")
                
        except Exception as e:
            logger.error(f"❌ Error ensuring AI answers persistence: {str(e)}")
    
    async def ensure_internet_learning_persistence(self):
        """Ensure all internet learning results are properly persisted"""
        try:
            logger.info("🔍 Checking internet learning persistence...")
            
            async with get_session() as session:
                # Get recent internet learning results from database
                stmt = select(InternetLearningResult).order_by(InternetLearningResult.created_at.desc()).limit(100)
                result = await session.execute(stmt)
                db_results = result.scalars().all()
                
                logger.info(f"📊 Found {len(db_results)} recent internet learning results in database")
                
                # Get internet learning results from controller
                internet_results = self.learning_controller._internet_learning_log
                logger.info(f"📊 Found {len(internet_results)} internet learning results in controller")
                
                # Persist any recent results that aren't already in database
                for result_entry in internet_results[-50:]:  # Last 50 entries
                    # Check if this result is already in database
                    existing_result = next((r for r in db_results if 
                                          r.agent_id == result_entry.get("agent_id") and
                                          r.topic == result_entry.get("topic") and
                                          r.source == result_entry.get("source")), None)
                    
                    if not existing_result:
                        # Create new internet learning result record
                        new_result = InternetLearningResult(
                            agent_id=result_entry.get("agent_id"),
                            topic=result_entry.get("topic"),
                            source=result_entry.get("source"),
                            title=result_entry.get("title"),
                            url=result_entry.get("url"),
                            summary=result_entry.get("summary"),
                            content=result_entry.get("content"),
                            relevance_score=result_entry.get("relevance_score", 0.0),
                            learning_value=result_entry.get("learning_value", 0.0),
                            insights_extracted=result_entry.get("insights_extracted", []),
                            applied_to_agent=result_entry.get("applied_to_agent", False)
                        )
                        session.add(new_result)
                        logger.info(f"✅ Created new internet learning result for {result_entry.get('agent_id')} - {result_entry.get('topic')}")
                
                await session.commit()
                logger.info("✅ Internet learning persistence check completed")
                
        except Exception as e:
            logger.error(f"❌ Error ensuring internet learning persistence: {str(e)}")
    
    async def run_comprehensive_persistence_check(self):
        """Run comprehensive persistence check for all learning data"""
        try:
            logger.info("🚀 Starting comprehensive learning persistence check...")
            
            # Check all persistence areas
            await self.ensure_agent_metrics_persistence()
            await self.ensure_learning_cycles_persistence()
            await self.ensure_learning_logs_persistence()
            await self.ensure_ai_answers_persistence()
            await self.ensure_internet_learning_persistence()
            
            logger.info("✅ Comprehensive learning persistence check completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Error in comprehensive persistence check: {str(e)}")
    
    async def get_persistence_summary(self):
        """Get a summary of all persisted learning data"""
        try:
            logger.info("📊 Generating persistence summary...")
            
            async with get_session() as session:
                # Count all learning-related records
                agent_metrics_count = await session.scalar(select(func.count(AgentMetrics.id)))
                learning_cycles_count = await session.scalar(select(func.count(LearningCycle.id)))
                learning_logs_count = await session.scalar(select(func.count(LearningLog.id)))
                ai_answers_count = await session.scalar(select(func.count(AIAnswer.id)))
                internet_results_count = await session.scalar(select(func.count(InternetLearningResult.id)))
                learning_records_count = await session.scalar(select(func.count(LearningRecord.id)))
                explainability_metrics_count = await session.scalar(select(func.count(ExplainabilityMetrics.id)))
                custody_test_results_count = await session.scalar(select(func.count(CustodyTestResult.id)))
                
                summary = {
                    "agent_metrics": agent_metrics_count,
                    "learning_cycles": learning_cycles_count,
                    "learning_logs": learning_logs_count,
                    "ai_answers": ai_answers_count,
                    "internet_learning_results": internet_results_count,
                    "learning_records": learning_records_count,
                    "explainability_metrics": explainability_metrics_count,
                    "custody_test_results": custody_test_results_count,
                    "total_learning_records": (
                        agent_metrics_count + learning_cycles_count + learning_logs_count +
                        ai_answers_count + internet_results_count + learning_records_count +
                        explainability_metrics_count + custody_test_results_count
                    )
                }
                
                logger.info("📊 Persistence Summary:", **summary)
                return summary
                
        except Exception as e:
            logger.error(f"❌ Error generating persistence summary: {str(e)}")
            return {}

async def main():
    """Main function to run the learning persistence check"""
    try:
        # Initialize the persistence manager
        manager = LearningPersistenceManager()
        await manager.initialize()
        
        # Run comprehensive persistence check
        await manager.run_comprehensive_persistence_check()
        
        # Get persistence summary
        summary = await manager.get_persistence_summary()
        
        logger.info("🎉 Learning persistence check completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error in main function: {str(e)}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main()) 