import asyncio
import sys

from app.services.custody_protocol_service import CustodyProtocolService
# Import any other dependencies or test helpers as needed

async def test_custody_persistence():
    print("Running test_custody_persistence...")
    # Place the original test logic here
    # Example: (replace with your actual test code)
    service = CustodyProtocolService()
    # ... setup test data ...
    # result = await service.administer_custody_test(...)
    # assert ...
    print("test_custody_persistence completed.")

async def test_custody_analytics():
    print("Running test_custody_analytics...")
    # Place the original test logic here
    # Example: (replace with your actual test code)
    service = CustodyProtocolService()
    # ... setup test data ...
    # result = await service.administer_custody_test(...)
    # assert ...
    print("test_custody_analytics completed.")

async def main():
    try:
        await test_custody_persistence()
    except Exception as e:
        print(f"test_custody_persistence FAILED: {e}", file=sys.stderr)
    try:
        await test_custody_analytics()
    except Exception as e:
        print(f"test_custody_analytics FAILED: {e}", file=sys.stderr)

if __name__ == "__main__":
    asyncio.run(main()) 