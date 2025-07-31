#!/usr/bin/env python3
"""
Force Custodes Tests Script
This script forces Custodes Protocol tests for all AIs to enable proposal creation.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.custody_protocol_service import CustodyProtocolService
from app.core.database import init_database
import structlog

logger = structlog.get_logger()

async def force_custodes_tests():
    """Force Custodes tests for all AIs"""
    try:
        logger.info("🛡️ Starting forced Custodes tests for all AIs...")
        
        # Initialize database
        await init_database()
        
        # Initialize Custody Protocol Service
        custody_service = CustodyProtocolService()
        
        # List of AI types to test
        ai_types = ['imperium', 'guardian', 'sandbox', 'conquest']
        
        for ai_type in ai_types:
            logger.info(f"🧪 Administering Custodes test for {ai_type} AI...")
            
            try:
                # Force administer a basic test for each AI
                result = await custody_service.administer_custody_test(ai_type)
                
                logger.info(f"✅ {ai_type} AI test completed: {result}")
                
            except Exception as e:
                logger.error(f"❌ Error testing {ai_type} AI: {e}")
                
        logger.info("🎉 All Custodes tests completed!")
        
    except Exception as e:
        logger.error(f"❌ Error in force_custodes_tests: {e}")

async def check_custody_status():
    """Check the current custody status of all AIs"""
    try:
        logger.info("📊 Checking current custody status...")
        
        # Initialize database
        await init_database()
        
        # Initialize Custody Protocol Service
        custody_service = CustodyProtocolService()
        
        # Get custody status for all AIs
        status = await custody_service.get_custody_analytics()
        
        logger.info("📈 Current Custody Status:")
        ai_metrics = status.get('ai_specific_metrics', {})
        for ai_type, data in ai_metrics.items():
            logger.info(f"  {ai_type}:")
            logger.info(f"    - Tests Given: {data.get('total_tests_given', 0)}")
            logger.info(f"    - Tests Passed: {data.get('total_tests_passed', 0)}")
            logger.info(f"    - Pass Rate: {data.get('pass_rate', 0)}%")
            logger.info(f"    - Custody Level: {data.get('custody_level', 1)}")
            logger.info(f"    - Custody XP: {data.get('custody_xp', 0)}")
            
    except Exception as e:
        logger.error(f"❌ Error checking custody status: {e}")

async def main():
    """Main function"""
    logger.info("🚀 Starting Custodes Protocol Management...")
    
    # First check current status
    await check_custody_status()
    
    # Then force tests
    await force_custodes_tests()
    
    # Check status again
    await check_custody_status()
    
    logger.info("✅ Custodes Protocol Management completed!")

if __name__ == "__main__":
    asyncio.run(main()) 