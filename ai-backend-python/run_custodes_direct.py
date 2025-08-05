#!/usr/bin/env python3
"""
Direct Custodes test runner that imports from the backend code
"""

import sys
import os
sys.path.append('/home/ubuntu/ai-backend-python')

try:
    from app.services.custody_protocol_service import CustodyProtocolService
    from app.core.database import get_db
    
    print("🛡️ Running Custodes tests directly...")
    
    # Create service instance
    service = CustodyProtocolService()
    
    # Run batch test
    print("🧪 Running batch test for all AIs...")
    result = service.batch_test_all_ais()
    print(f"✅ Batch test result: {result}")
    
    # Get custody status
    print("\n📊 Getting custody status...")
    status = service.get_custody_protocol_overview()
    print(f"Status: {status}")
    
    print("\n🎉 Custodes tests completed!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the ai-backend-python directory")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 