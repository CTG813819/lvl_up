#!/usr/bin/env python3
"""
Custodes AI Testing Service Runner
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
        logging.FileHandler('/home/ubuntu/ai-backend-python/logs/custodes.log'),
        logging.StreamHandler()
    ]
)

# Add app directory to path
sys.path.insert(0, '/home/ubuntu/ai-backend-python/app')

try:
    from app.services.enhanced_autonomous_learning_service import EnhancedAutonomousLearningService
    from app.core.database import get_session

    async def run_custodes():
        service = EnhancedAutonomousLearningService()
        logging.info('Custodes AI Service started - Using EnhancedAutonomousLearningService')
        counter = 0

        while True:
            try:
                if counter % 2 == 0:
                    logging.info('Starting comprehensive Custodes testing cycle')
                    # Run comprehensive custodes testing
                    await service._run_custodes_testing()
                else:
                    logging.info('Starting regular Custodes testing cycle')
                    # Run regular custodes testing
                    await service._run_custodes_testing()

                counter += 1
                logging.info('Custodes testing cycle completed')
            except Exception as e:
                logging.error(f'Custodes testing error: {str(e)}')

            await asyncio.sleep(2700)  # 45 minutes

    asyncio.run(run_custodes())
except Exception as e:
    logging.error(f'Custodes service startup error: {str(e)}')
    sys.exit(1) 