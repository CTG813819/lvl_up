#!/usr/bin/env python3
"""
Script to reset usage data and test provider availability
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.core.database import init_database
from app.services.token_usage_service import token_usage_service
from app.core.config import settings
import structlog

logger = structlog.get_logger()

async def main():
    """Reset usage and test providers"""
    try:
        # Initialize database
        await init_database()
        await token_usage_service.initialize()
        
        # Reset all usage data
        logger.info("Resetting all usage data...")
        success = await token_usage_service.reset_all_usage_for_testing()
        if success:
            logger.info("✅ Successfully reset all usage data")
        else:
            logger.error("❌ Failed to reset usage data")
            return
        
        # Test provider recommendations for each AI
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        for ai_type in ai_types:
            logger.info(f"Testing provider recommendation for {ai_type}...")
            
            # Get provider recommendation
            recommendation = await token_usage_service.get_provider_recommendation(ai_type)
            
            logger.info(f"Provider recommendation for {ai_type}:", 
                       recommendation=recommendation.get("recommendation"),
                       reason=recommendation.get("reason"),
                       anthropic_available=recommendation.get("anthropic", {}).get("available"),
                       openai_available=recommendation.get("openai", {}).get("available"))
            
            # Test individual provider availability
            anthropic_available, anthropic_details = await token_usage_service.check_provider_availability(ai_type, "anthropic")
            openai_available, openai_details = await token_usage_service.check_provider_availability(ai_type, "openai")
            
            logger.info(f"Individual provider availability for {ai_type}:",
                       anthropic_available=anthropic_available,
                       openai_available=openai_available,
                       anthropic_details=anthropic_details,
                       openai_details=openai_details)
        
        # Show current limits
        logger.info("Current limits:",
                   anthropic_monthly_limit=settings.anthropic_monthly_limit,
                   openai_monthly_limit=settings.openai_monthly_limit,
                   openai_fallback_threshold=settings.openai_fallback_threshold)
        
        logger.info("✅ Provider testing completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error during testing: {str(e)}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main()) 