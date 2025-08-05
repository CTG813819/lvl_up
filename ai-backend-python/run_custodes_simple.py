#!/usr/bin/env python3
"""
Simplified Custodes AI Testing Service Runner
"""

import asyncio
import sys
import os
import logging
from datetime import datetime

# Configure logging FIRST
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/ai-backend-python/logs/custodes.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info(f"Python executable: {sys.executable}")
logger.info(f"Python version: {sys.version}")
logger.info(f"DATABASE_URL: {os.environ.get('DATABASE_URL')}")

# Add app directory to path
sys.path.insert(0, '/home/ubuntu/ai-backend-python/app')

async def run_custodes_tests():
    # Import and initialize database FIRST
    from app.core.database import init_database
    await init_database()

    # Now import DB-using services
    from app.services.custody_protocol_service import CustodyProtocolService, TestCategory
    from app.services.ai_agent_service import AIAgentService
    from app.core.database import get_session
    from app.models.sql_models import AgentMetrics
    from sqlalchemy import select

    try:
        logging.info("🛡️ [CUSTODES] Running dynamic, learning-based custodes tests...")
        # AI types to test
        ai_types = ["imperium", "guardian", "sandbox"]
        # Test categories
        test_categories = [
            TestCategory.KNOWLEDGE_VERIFICATION,
            TestCategory.CODE_QUALITY,
            TestCategory.SECURITY_AWARENESS,
            TestCategory.PERFORMANCE_OPTIMIZATION,
            TestCategory.INNOVATION_CAPABILITY
        ]
        custody_service = await CustodyProtocolService.initialize()
        for ai_type in ai_types:
            logging.info(f"🧪 [CUSTODES] Testing {ai_type}...")
            test_results = {}
            for category in test_categories:
                try:
                    result = await custody_service.administer_custody_test(ai_type, category)
                    if result.get("status") == "error":
                        logging.error(f"❌ [CUSTODES] {category.value} test failed for {ai_type}: {result.get('message')}")
                        test_results[category.value] = 0.0
                    else:
                        test_result = result.get("test_result", {})
                        score = test_result.get("score", 0) / 100.0  # Convert to 0-1 scale
                        test_results[category.value] = score
                        logging.info(f"✅ [CUSTODES] {category.value} test for {ai_type}: {score:.2f}")
                except Exception as e:
                    test_results[category.value] = 0.0
                    logging.error(f"❌ [CUSTODES] {category.value} test for {ai_type} failed: {str(e)}")
            # Calculate overall score
            overall_score = sum(test_results.values()) / len(test_results)
            logging.info(f"📊 [CUSTODES] {ai_type} overall score: {overall_score:.2f}/1.0")
            # Update metrics in database (optional, if you want to keep this logic)
            await update_custodes_metrics(ai_type, overall_score, test_results)
        logging.info("✅ [CUSTODES] All custodes tests completed")
    except Exception as e:
        logging.error(f"❌ [CUSTODES] Custodes testing error: {str(e)}")

async def update_custodes_metrics(ai_type, overall_score, test_results):
    """Update custodes metrics in database"""
    try:
        async with get_session() as db:
            # Get or create agent metrics
            metrics_query = select(AgentMetrics).where(AgentMetrics.agent_type == ai_type)
            result = await db.execute(metrics_query)
            metrics = result.scalar_one_or_none()
            
            if not metrics:
                metrics = AgentMetrics(
                    agent_id=f"{ai_type}_agent",
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
            logging.info(f"📊 [CUSTODES] Updated metrics for {ai_type}")
            
    except Exception as e:
        logging.error(f"❌ [CUSTODES] Failed to update metrics for {ai_type}: {str(e)}")

if __name__ == "__main__":
    asyncio.run(run_custodes_tests()) 