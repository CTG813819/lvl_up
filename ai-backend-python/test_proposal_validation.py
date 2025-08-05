#!/usr/bin/env python3
"""
Test script for proposal validation service
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.proposal_validation_service import ProposalValidationService
from app.core.database import get_session, init_database
from sqlalchemy.ext.asyncio import AsyncSession


async def test_proposal_validation():
    """Test the proposal validation service"""
    print("🧪 Testing Proposal Validation Service")
    
    # Initialize database
    print("🔧 Initializing database...")
    await init_database()
    print("✅ Database initialized")
    
    validation_service = ProposalValidationService()
    
    # Test proposal data
    test_proposal = {
        "ai_type": "Imperium",
        "file_path": "lib/screens/test_screen.dart",
        "code_before": "class TestWidget extends StatelessWidget { }",
        "code_after": "class TestWidget extends StatelessWidget { \n  @override\n  Widget build(BuildContext context) {\n    return Container();\n  }\n}",
        "improvement_type": "feature",
        "confidence": 0.8
    }
    
    try:
        async with get_session() as db:
            print("✅ Database connection successful")
            
            # Test validation
            is_valid, reason, details = await validation_service.validate_proposal(test_proposal, db)
            
            print(f"📋 Validation Result: {is_valid}")
            print(f"📝 Reason: {reason}")
            print(f"🔍 Details: {details}")
            
            # Test validation stats
            stats = await validation_service.get_validation_stats(db)
            print(f"📊 Validation Stats: {stats}")
            
            print("✅ Proposal validation service test completed successfully")
            
    except Exception as e:
        print(f"❌ Error testing proposal validation: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_proposal_validation()) 