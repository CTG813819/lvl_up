#!/usr/bin/env python3
"""
Enhanced Autonomous Learning Service Runner
Runs the enhanced autonomous learning system with Custody Protocol integration
"""

import asyncio
import sys
import os
import signal
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.enhanced_autonomous_learning_service import EnhancedAutonomousLearningService
import structlog

logger = structlog.get_logger()

class EnhancedAutonomousLearningRunner:
    """Runner for the enhanced autonomous learning service"""
    
    def __init__(self):
        self.service = None
        self.running = False
        
    async def start(self):
        """Start the enhanced autonomous learning service"""
        try:
            logger.info("🚀 Starting Enhanced Autonomous Learning Service...")
            logger.info("🛡️ Custody Protocol Integration: ACTIVE")
            logger.info("🤖 AIs will be tested before creating proposals or leveling up")
            logger.info("=" * 60)
            
            # Initialize the service
            self.service = await EnhancedAutonomousLearningService.initialize()
            
            # Set up signal handlers for graceful shutdown
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            self.running = True
            
            # Start the enhanced autonomous learning
            await self.service.start_enhanced_autonomous_learning()
            
        except Exception as e:
            logger.error(f"❌ Error starting enhanced autonomous learning: {str(e)}")
            raise
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"🛑 Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    async def stop(self):
        """Stop the enhanced autonomous learning service"""
        try:
            logger.info("🛑 Stopping Enhanced Autonomous Learning Service...")
            self.running = False
            
            if self.service:
                # Cleanup if needed
                logger.info("🧹 Cleaning up resources...")
            
            logger.info("✅ Enhanced Autonomous Learning Service stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping service: {str(e)}")

async def main():
    """Main function to run the enhanced autonomous learning service"""
    runner = EnhancedAutonomousLearningRunner()
    
    try:
        await runner.start()
    except KeyboardInterrupt:
        logger.info("🛑 Keyboard interrupt received")
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}")
        return 1
    finally:
        await runner.stop()
    
    return 0

if __name__ == "__main__":
    print("🚀 Enhanced Autonomous Learning Service with Custody Protocol")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🛡️ Custody Protocol: ACTIVE")
    print("🤖 AI Testing: RIGOROUS")
    print("📚 Learning: AUTONOMOUS")
    print("=" * 60)
    
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        sys.exit(1) 