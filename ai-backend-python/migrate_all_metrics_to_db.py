#!/usr/bin/env python3
"""
Migration Script: Migrate All Metrics to Database
================================================

This script migrates all existing in-memory metrics to the database
using the new AgentMetricsService for the database-first approach.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import init_database, create_tables, get_session
from app.services.agent_metrics_service import AgentMetricsService
from app.models.sql_models import AgentMetrics
import structlog

logger = structlog.get_logger()


def parse_datetime(datetime_str):
    """Parse datetime string to datetime object"""
    if isinstance(datetime_str, str):
        try:
            return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        except ValueError:
            try:
                return datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%f')
            except ValueError:
                return datetime.utcnow()
    return datetime_str


async def migrate():
    """Migrate all metrics to database using AgentMetricsService"""
    logger.info("Starting migration to database-first approach...")
    
    # Initialize database
    await init_database()
    await create_tables()
    
    # Initialize AgentMetricsService
    agent_metrics_service = AgentMetricsService()
    
    # Get all existing metrics from database
    all_metrics = await agent_metrics_service.get_all_agent_metrics()
    
    logger.info(f"Found {len(all_metrics)} existing agent metrics in database")
    
    # Process each agent's metrics
    for ai_type, metrics in all_metrics.items():
        logger.info(f"Processing metrics for {ai_type}")
        
        try:
            # Update metrics using the new service
            success = await agent_metrics_service.update_specific_metrics(ai_type, {
                "learning_score": metrics.get("learning_score", 0.0),
                "success_rate": metrics.get("success_rate", 0.0),
                "failure_rate": metrics.get("failure_rate", 0.0),
                "pass_rate": metrics.get("pass_rate", 0.0),
                "total_learning_cycles": metrics.get("total_learning_cycles", 0),
                "xp": metrics.get("xp", 0),
                "level": metrics.get("level", 1),
                "prestige": metrics.get("prestige", 0),
                "current_difficulty": metrics.get("current_difficulty", "basic"),
                "total_tests_given": metrics.get("total_tests_given", 0),
                "total_tests_passed": metrics.get("total_tests_passed", 0),
                "total_tests_failed": metrics.get("total_tests_failed", 0),
                "consecutive_successes": metrics.get("consecutive_successes", 0),
                "consecutive_failures": metrics.get("consecutive_failures", 0),
                "custody_level": metrics.get("custody_level", 1),
                "custody_xp": metrics.get("custody_xp", 0),
                "adversarial_wins": metrics.get("adversarial_wins", 0),
                "learning_patterns": metrics.get("learning_patterns", []),
                "improvement_suggestions": metrics.get("improvement_suggestions", []),
                "test_history": metrics.get("test_history", []),
                "status": metrics.get("status", "idle"),
                "is_active": metrics.get("is_active", True),
                "priority": metrics.get("priority", "medium")
            })
            
            if success:
                logger.info(f"✅ Successfully updated metrics for {ai_type}")
            else:
                logger.error(f"❌ Failed to update metrics for {ai_type}")
                
        except Exception as e:
            logger.error(f"Error processing {ai_type}: {str(e)}")
    
    logger.info("Migration complete.")


if __name__ == "__main__":
    asyncio.run(migrate()) 