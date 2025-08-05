#!/usr/bin/env python3
"""
Olympus Treaty Test
==================

This script manually triggers and tests the Olympus Treaty scenario for a given AI type.
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

try:
    from app.services.custody_protocol_service import CustodyProtocolService
    from app.core.database import init_database
    print("✅ CustodyProtocolService and init_database imported successfully")
except Exception as e:
    print(f"❌ Error importing modules: {str(e)}")
    sys.exit(1)

def print_olympus_result(result):
    print("\n===== Olympus Treaty Result =====")
    print(f"AI Type: {result.get('ai_type')}")
    print(f"Passed: {result.get('passed')}")
    print(f"Score: {result.get('score')}")
    print(f"Scenario: {result.get('scenario')}")
    print(f"AI Response: {result.get('ai_response')}")
    print(f"Evaluation: {result.get('evaluation')}")
    print(f"Timestamp: {result.get('timestamp')}")
    print("================================\n")

async def test_olympus_treaty(ai_type: str):
    try:
        print(f"🛡️ Testing Olympus Treaty for AI: {ai_type} ...")
        await init_database()
        custody_service = await CustodyProtocolService.initialize()
        print("✅ Custody service initialized")
        result = await custody_service.administer_olympus_treaty(ai_type)
        print_olympus_result(result)
        return result.get('passed', False)
    except Exception as e:
        print(f"❌ Error testing Olympus Treaty: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Olympus Treaty Test")
    print("=" * 30)
    ai_type = sys.argv[1] if len(sys.argv) > 1 else "conquest"
    print(f"AI Type: {ai_type}")
    success = asyncio.run(test_olympus_treaty(ai_type))
    if success:
        print("\n✅ Olympus Treaty test completed successfully!")
    else:
        print("\n❌ Olympus Treaty test failed!")
        sys.exit(1) 