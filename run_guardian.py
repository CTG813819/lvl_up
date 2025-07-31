#!/usr/bin/env python3
"""
Guardian AI Security Service Runner
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
        logging.FileHandler('/home/ubuntu/ai-backend-python/logs/guardian.log'),
        logging.StreamHandler()
    ]
)

# Add app directory to path
sys.path.insert(0, '/home/ubuntu/ai-backend-python/app')

try:
    from app.services.ai_agent_service import AIAgentService
    from app.core.database import get_session

    async def run_guardian():
        """Main guardian service loop"""
        service = AIAgentService()
        logging.info('🛡️ [GUARDIAN] Guardian AI Security Service started')

        while True:
            try:
                logging.info('🛡️ [GUARDIAN] Starting Guardian security analysis cycle')
                result = await service.run_guardian_agent()
                logging.info(f'✅ [GUARDIAN] Guardian security analysis cycle completed: {result}')
            except Exception as e:
                logging.error(f'❌ [GUARDIAN] Guardian security analysis error: {str(e)}')

            # Wait 30 minutes before next cycle
            await asyncio.sleep(1800)  # 30 minutes

    asyncio.run(run_guardian())
except Exception as e:
    logging.error(f'❌ [GUARDIAN] Guardian service startup error: {str(e)}')
    sys.exit(1) 