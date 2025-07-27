#!/usr/bin/env python3
"""
Sandbox AI Experimentation Service Runner
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
        logging.FileHandler('/home/ubuntu/ai-backend-python/logs/sandbox.log'),
        logging.StreamHandler()
    ]
)

# Add app directory to path
sys.path.insert(0, '/home/ubuntu/ai-backend-python/app')

try:
    from app.services.ai_agent_service import AIAgentService
    from app.core.database import get_session

    async def run_sandbox():
        """Main sandbox service loop"""
        service = AIAgentService()
        logging.info('🧪 [SANDBOX] Sandbox AI Experimentation Service started')

        while True:
            try:
                logging.info('🧪 [SANDBOX] Starting Sandbox experimentation cycle')
                result = await service.run_sandbox_agent()
                logging.info(f'✅ [SANDBOX] Sandbox experimentation cycle completed: {result}')
            except Exception as e:
                logging.error(f'❌ [SANDBOX] Sandbox experimentation error: {str(e)}')

            # Wait 45 minutes before next cycle
            await asyncio.sleep(2700)  # 45 minutes

    asyncio.run(run_sandbox())
except Exception as e:
    logging.error(f'❌ [SANDBOX] Sandbox service startup error: {str(e)}')
    sys.exit(1) 