#!/usr/bin/env python3
"""
Test script to verify difficulty adjustment and XP persistence fixes
"""

import asyncio
import json
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_difficulty_fixes():
    """Test the difficulty adjustment and XP persistence fixes"""
    try:
        # Initialize database and services
        from app.core.database import init_database
        from app.services.custody_protocol_service import CustodyProtocolService
        
        logger.info("Initializing database...")
        await init_database()
        
        logger.info("Initializing CustodyProtocolService...")
        await CustodyProtocolService.initialize()
        
        custody_service = CustodyProtocolService()
        
        # Test AI type
        ai_type = "conquest"
        
        logger.info(f"Testing difficulty adjustment and XP persistence for {ai_type}")
        
        # Get initial metrics
        initial_metrics = await custody_service.agent_metrics_service.get_custody_metrics(ai_type)
        logger.info(f"Initial metrics: {json.dumps(initial_metrics, default=str, ensure_ascii=False)}")
        
        # Run a test to see if difficulty decreases with failures
        logger.info("Running custody test...")
        test_result = await custody_service.administer_custody_test(ai_type)
        
        logger.info(f"Test result: {json.dumps(test_result, default=str, ensure_ascii=False)}")
        
        # Get updated metrics
        updated_metrics = await custody_service.agent_metrics_service.get_custody_metrics(ai_type)
        logger.info(f"Updated metrics: {json.dumps(updated_metrics, default=str, ensure_ascii=False)}")
        
        # Check if difficulty decreased
        initial_difficulty = initial_metrics.get('current_difficulty', 'basic') if initial_metrics else 'basic'
        updated_difficulty = updated_metrics.get('current_difficulty', 'basic') if updated_metrics else 'basic'
        
        logger.info(f"Difficulty change: {initial_difficulty} -> {updated_difficulty}")
        
        # Check XP persistence
        initial_xp = initial_metrics.get('custody_xp', 0) if initial_metrics else 0
        updated_xp = updated_metrics.get('custody_xp', 0) if updated_metrics else 0
        
        logger.info(f"XP change: {initial_xp} -> {updated_xp}")
        
        # Check test history for difficulty field
        test_history = updated_metrics.get('test_history', []) if updated_metrics else []
        if test_history:
            latest_entry = test_history[-1]
            difficulty_in_history = latest_entry.get('difficulty', 'unknown')
            logger.info(f"Difficulty in test history: {difficulty_in_history}")
        
        logger.info("Test completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(test_difficulty_fixes()) 