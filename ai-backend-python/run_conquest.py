#!/usr/bin/env python3
"""
Conquest AI Deployment Service Runner
"""

import asyncio
import sys
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/ai-backend-python/logs/conquest.log'),
        logging.StreamHandler()
    ]
)

# Add app directory to path
sys.path.insert(0, '/home/ubuntu/ai-backend-python/app')

try:
    from app.services.ai_agent_service import AIAgentService
    from app.core.database import get_session

    async def run_conquest():
        """Main conquest service loop"""
        service = AIAgentService()
        logging.info('🚀 [CONQUEST] Conquest AI Deployment Service started')

        while True:
            try:
                logging.info('🚀 [CONQUEST] Starting Conquest deployment cycle')
                result = await service.run_conquest_agent()
                logging.info(f'✅ [CONQUEST] Conquest deployment cycle completed: {result}')
            except Exception as e:
                logging.error(f'❌ [CONQUEST] Conquest deployment error: {str(e)}')

            # Wait 1 hour before next cycle
            await asyncio.sleep(3600)  # 1 hour

    asyncio.run(run_conquest())
except Exception as e:
    logging.error(f'❌ [CONQUEST] Conquest service startup error: {str(e)}')
    sys.exit(1) 