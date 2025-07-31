#!/usr/bin/env python3
"""
Script to enhance learning services to ensure automatic persistence of all learning activities
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.core.database import init_database, get_session
from app.services.ai_learning_service import AILearningService
from app.services.imperium_learning_controller import ImperiumLearningController
from app.services.background_service import BackgroundService
from app.models.sql_models import (
    LearningLog, InternetLearningResult, AIAnswer, LearningRecord
)
from sqlalchemy import select
import structlog

logger = structlog.get_logger()

class LearningPersistenceEnhancer:
    """Enhancer to add automatic persistence to learning services"""
    
    def __init__(self):
        self.learning_service = None
        self.learning_controller = None
        self.background_service = None
    
    async def initialize(self):
        """Initialize all services"""
        try:
            # Initialize database
            await init_database()
            
            # Initialize services
            self.learning_service = await AILearningService.initialize()
            self.learning_controller = await ImperiumLearningController.initialize()
            self.background_service = await BackgroundService.initialize()
            
            logger.info("✅ Learning Persistence Enhancer initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Error initializing Learning Persistence Enhancer: {str(e)}")
            raise
    
    async def enhance_learning_service_persistence(self):
        """Enhance AI Learning Service with automatic persistence"""
        try:
            logger.info("🔧 Enhancing AI Learning Service persistence...")
            
            # Store original methods
            original_log_answer = self.learning_service.log_answer
            original_save_internet_learning_result = self.learning_service.save_internet_learning_result
            
            async def enhanced_log_answer(ai_type: str, prompt: str, answer: str, structured_response: Dict[str, Any] = None):
                """Enhanced log_answer with automatic database persistence"""
                try:
                    # Call original method
                    await original_log_answer(ai_type, prompt, answer, structured_response)
                    
                    # Additional automatic persistence
                    await self._persist_learning_log(ai_type, "ai_answer", {
                        "prompt": prompt,
                        "answer": answer,
                        "structured_response": structured_response
                    })
                    
                    logger.info(f"✅ Enhanced persistence for AI answer from {ai_type}")
                    
                except Exception as e:
                    logger.error(f"❌ Error in enhanced log_answer: {str(e)}")
            
            async def enhanced_save_internet_learning_result(agent_id: str, topic: str, result: Dict[str, Any]) -> bool:
                """Enhanced save_internet_learning_result with automatic database persistence"""
                try:
                    # Call original method
                    success = await original_save_internet_learning_result(agent_id, topic, result)
                    
                    if success:
                        # Additional automatic persistence
                        await self._persist_internet_learning_result(agent_id, topic, result)
                        logger.info(f"✅ Enhanced persistence for internet learning result for {agent_id} - {topic}")
                    
                    return success
                    
                except Exception as e:
                    logger.error(f"❌ Error in enhanced save_internet_learning_result: {str(e)}")
                    return False
            
            # Replace methods with enhanced versions
            self.learning_service.log_answer = enhanced_log_answer
            self.learning_service.save_internet_learning_result = enhanced_save_internet_learning_result
            
            logger.info("✅ AI Learning Service persistence enhanced")
            
        except Exception as e:
            logger.error(f"❌ Error enhancing learning service persistence: {str(e)}")
    
    async def enhance_learning_controller_persistence(self):
        """Enhance Imperium Learning Controller with automatic persistence"""
        try:
            logger.info("🔧 Enhancing Imperium Learning Controller persistence...")
            
            # Store original methods
            original_persist_agent_metrics = self.learning_controller.persist_agent_metrics
            original_log_learning_event = self.learning_controller.log_learning_event
            
            async def enhanced_persist_agent_metrics(agent_id: str) -> bool:
                """Enhanced persist_agent_metrics with additional logging"""
                try:
                    # Call original method
                    success = await original_persist_agent_metrics(agent_id)
                    
                    if success:
                        # Log the persistence event
                        await self._persist_learning_log(agent_id, "metrics_persisted", {
                            "agent_id": agent_id,
                            "timestamp": datetime.utcnow().isoformat()
                        })
                        logger.info(f"✅ Enhanced persistence for agent metrics: {agent_id}")
                    
                    return success
                    
                except Exception as e:
                    logger.error(f"❌ Error in enhanced persist_agent_metrics: {str(e)}")
                    return False
            
            async def enhanced_log_learning_event(event_type: str, agent_id: Optional[str] = None, 
                                                agent_type: Optional[str] = None, topic: Optional[str] = None, 
                                                results_count: int = 0, results_sample: Optional[list] = None,
                                                insights: Optional[list] = None, error_message: Optional[str] = None,
                                                processing_time: Optional[float] = None, impact_score: float = 0.0,
                                                event_data: Optional[dict] = None) -> bool:
                """Enhanced log_learning_event with automatic database persistence"""
                try:
                    # Call original method
                    success = await original_log_learning_event(
                        event_type, agent_id, agent_type, topic, results_count, results_sample,
                        insights, error_message, processing_time, impact_score, event_data
                    )
                    
                    if success:
                        # Additional automatic persistence
                        await self._persist_learning_log(agent_id or "system", event_type, {
                            "agent_type": agent_type,
                            "topic": topic,
                            "results_count": results_count,
                            "insights": insights,
                            "impact_score": impact_score,
                            "event_data": event_data
                        })
                        logger.info(f"✅ Enhanced persistence for learning event: {event_type}")
                    
                    return success
                    
                except Exception as e:
                    logger.error(f"❌ Error in enhanced log_learning_event: {str(e)}")
                    return False
            
            # Replace methods with enhanced versions
            self.learning_controller.persist_agent_metrics = enhanced_persist_agent_metrics
            self.learning_controller.log_learning_event = enhanced_log_learning_event
            
            logger.info("✅ Imperium Learning Controller persistence enhanced")
            
        except Exception as e:
            logger.error(f"❌ Error enhancing learning controller persistence: {str(e)}")
    
    async def enhance_background_service_persistence(self):
        """Enhance Background Service with automatic persistence"""
        try:
            logger.info("🔧 Enhancing Background Service persistence...")
            
            # Store original methods
            original_learning_cycle = self.background_service._learning_cycle
            original_custody_testing_cycle = self.background_service._custody_testing_cycle
            
            async def enhanced_learning_cycle():
                """Enhanced learning cycle with automatic persistence"""
                try:
                    logger.info("🧠 Enhanced learning cycle starting...")
                    
                    # Call original method
                    await original_learning_cycle()
                    
                    # Log the learning cycle completion
                    await self._persist_learning_log("system", "learning_cycle_completed", {
                        "timestamp": datetime.utcnow().isoformat(),
                        "cycle_type": "background_learning"
                    })
                    
                    logger.info("✅ Enhanced learning cycle completed with persistence")
                    
                except Exception as e:
                    logger.error(f"❌ Error in enhanced learning cycle: {str(e)}")
            
            async def enhanced_custody_testing_cycle():
                """Enhanced custody testing cycle with automatic persistence"""
                try:
                    logger.info("🛡️ Enhanced custody testing cycle starting...")
                    
                    # Call original method
                    await original_custody_testing_cycle()
                    
                    # Log the custody testing cycle completion
                    await self._persist_learning_log("system", "custody_testing_cycle_completed", {
                        "timestamp": datetime.utcnow().isoformat(),
                        "cycle_type": "custody_testing"
                    })
                    
                    logger.info("✅ Enhanced custody testing cycle completed with persistence")
                    
                except Exception as e:
                    logger.error(f"❌ Error in enhanced custody testing cycle: {str(e)}")
            
            # Replace methods with enhanced versions
            self.background_service._learning_cycle = enhanced_learning_cycle
            self.background_service._custody_testing_cycle = enhanced_custody_testing_cycle
            
            logger.info("✅ Background Service persistence enhanced")
            
        except Exception as e:
            logger.error(f"❌ Error enhancing background service persistence: {str(e)}")
    
    async def _persist_learning_log(self, agent_id: str, event_type: str, event_data: Dict[str, Any]):
        """Persist learning log to database"""
        try:
            async with get_session() as session:
                learning_log = LearningLog(
                    event_type=event_type,
                    agent_id=agent_id,
                    agent_type=agent_id,
                    topic=event_data.get("topic"),
                    results_count=event_data.get("results_count", 0),
                    results_sample=event_data.get("results_sample"),
                    insights=event_data.get("insights"),
                    impact_score=event_data.get("impact_score", 0.0),
                    event_data=event_data
                )
                session.add(learning_log)
                await session.commit()
                
        except Exception as e:
            logger.error(f"❌ Error persisting learning log: {str(e)}")
    
    async def _persist_internet_learning_result(self, agent_id: str, topic: str, result: Dict[str, Any]):
        """Persist internet learning result to database"""
        try:
            async with get_session() as session:
                internet_result = InternetLearningResult(
                    agent_id=agent_id,
                    topic=topic,
                    source=result.get("source", "unknown"),
                    title=result.get("title"),
                    url=result.get("url"),
                    summary=result.get("summary"),
                    content=result.get("content"),
                    relevance_score=result.get("relevance_score", 0.0),
                    learning_value=result.get("learning_value", 0.0),
                    insights_extracted=result.get("insights_extracted", []),
                    applied_to_agent=result.get("applied_to_agent", False)
                )
                session.add(internet_result)
                await session.commit()
                
        except Exception as e:
            logger.error(f"❌ Error persisting internet learning result: {str(e)}")
    
    async def run_enhancement(self):
        """Run all persistence enhancements"""
        try:
            logger.info("🚀 Starting learning persistence enhancement...")
            
            # Enhance all services
            await self.enhance_learning_service_persistence()
            await self.enhance_learning_controller_persistence()
            await self.enhance_background_service_persistence()
            
            logger.info("✅ All learning persistence enhancements completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Error in persistence enhancement: {str(e)}")

async def main():
    """Main function to run the learning persistence enhancement"""
    try:
        # Initialize the enhancer
        enhancer = LearningPersistenceEnhancer()
        await enhancer.initialize()
        
        # Run enhancement
        await enhancer.run_enhancement()
        
        logger.info("🎉 Learning persistence enhancement completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error in main function: {str(e)}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main()) 