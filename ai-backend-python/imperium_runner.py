#!/usr/bin/env python3
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def run_imperium():
    try:
        from app.services.ai_agent_service import AIAgentService
        service = AIAgentService()
        while True:
            print("Running Imperium AI testing...")
            await service.run_imperium_testing(threshold=0.92)
            await asyncio.sleep(2700)  # 45 minutes
    except Exception as e:
        print(f"Imperium error: {e}")
        await asyncio.sleep(60)  # Wait before retry

if __name__ == "__main__":
    asyncio.run(run_imperium())
