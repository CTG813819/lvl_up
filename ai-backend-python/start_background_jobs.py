#!/usr/bin/env python3
"""
Start Background Jobs Script
Starts the background services that run custody tests, Olympic events, and collaborative tests
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def start_background_jobs():
    """Start all background jobs"""
    print("🚀 Starting Background Jobs...")
    print("=" * 50)
    
    try:
        # Background jobs are now enabled by default
        
        # Initialize database
        from app.core.database import init_database, create_tables, create_indexes
        await init_database()
        await create_tables()
        await create_indexes()
        print("✅ Database initialized")
        
        # Initialize Custody Protocol Service
        from app.services.custody_protocol_service import CustodyProtocolService
        custody_service = await CustodyProtocolService.initialize()
        print("✅ Custody Protocol Service initialized")
        
        # Initialize Background Service
        from app.services.background_service import BackgroundService
        background_service = await BackgroundService.initialize()
        print("✅ Background Service initialized")
        
        # Start background services
        print("\n🔄 Starting background services...")
        
        # Start custody testing cycle
        print("🛡️ Starting custody testing cycle...")
        custody_task = asyncio.create_task(background_service._custody_testing_cycle())
        
        # Start learning cycle
        print("🧠 Starting learning cycle...")
        learning_task = asyncio.create_task(background_service._learning_cycle())
        
        # Start Olympic events and collaborative tests
        print("🏆 Starting Olympic events and collaborative tests...")
        
        # Run Olympic events every 45 minutes
        async def run_olympic_events():
            while True:
                try:
                    print("🏆 Running Olympic events...")
                    result = await custody_service.administer_olympic_event(
                        participants=["imperium", "guardian", "sandbox", "conquest"],
                        difficulty=custody_service.TestDifficulty.INTERMEDIATE,
                        event_type="olympics"
                    )
                    print(f"   ✅ Olympic event: {result.get('passed', False)}")
                except Exception as e:
                    print(f"   ❌ Olympic event: {str(e)}")
                
                # Wait 45 minutes
                await asyncio.sleep(2700)  # 45 minutes
        
        olympic_task = asyncio.create_task(run_olympic_events())
        
        # Run collaborative tests every 90 minutes
        async def run_collaborative_tests():
            while True:
                try:
                    print("🤝 Running collaborative tests...")
                    result = await custody_service._execute_collaborative_test(
                        participants=["imperium", "guardian"],
                        scenario="Design a secure authentication system",
                        context={"difficulty": "intermediate"}
                    )
                    print(f"   ✅ Collaborative test: {result.get('passed', False)}")
                except Exception as e:
                    print(f"   ❌ Collaborative test: {str(e)}")
                
                # Wait 90 minutes
                await asyncio.sleep(5400)  # 90 minutes
        
        collaborative_task = asyncio.create_task(run_collaborative_tests())
        
        print("\n✅ All background jobs started successfully!")
        print("📋 Running services:")
        print("   - Custody testing cycle (every 20 minutes)")
        print("   - Learning cycle (every 30 minutes)")
        print("   - Olympic events every 45 minutes")
        print("   - Collaborative tests every 90 minutes")
        
        # Keep the script running
        print("\n🔄 Background jobs are now running... Press Ctrl+C to stop")
        
        # Wait for all tasks
        await asyncio.gather(
            custody_task,
            learning_task,
            olympic_task,
            collaborative_task
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping background jobs...")
    except Exception as e:
        print(f"❌ Error starting background jobs: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(start_background_jobs()) 