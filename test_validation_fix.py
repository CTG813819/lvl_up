#!/usr/bin/env python3
"""
Test script to verify that the validation changes allow proposals to be generated
without requiring user feedback first.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.enhanced_proposal_validation_service import EnhancedProposalValidationService
from app.core.database import init_database, get_db
from app.models.sql_models import Proposal
from sqlalchemy.ext.asyncio import AsyncSession


async def test_validation_changes():
    """Test that validation allows proposals without requiring user feedback first"""
    print("🧪 Testing validation changes...")
    
    # Initialize database
    await init_database()
    
    # Create validation service
    validation_service = EnhancedProposalValidationService()
    
    # Test proposal data
    test_proposal = {
        "ai_type": "Imperium",
        "file_path": "test_file.py",
        "code_before": "print('hello')",
        "code_after": "print('hello world')",
        "description": "Test proposal",
        "improvement_type": "performance",
        "confidence": 0.8
    }
    
    # Test validation
    db_gen = get_db()
    db = await db_gen.__anext__()
    
    try:
        print("📋 Testing proposal validation...")
        
        is_valid, reason, details = await validation_service.validate_proposal(test_proposal, db)
        
        print(f"✅ Validation result: {is_valid}")
        print(f"📝 Reason: {reason}")
        print(f"🔍 Details: {details}")
        
        if is_valid:
            print("🎉 SUCCESS: Proposal validation passed - no user feedback required!")
        else:
            print("❌ FAILED: Proposal validation failed - user feedback still required")
            print(f"   Error: {reason}")
        
        # Test with existing proposals (no user feedback)
        print("\n📋 Testing with existing proposals without user feedback...")
        
        # Create a test proposal in the database
        test_proposal_db = Proposal(
            ai_type="Imperium",
            file_path="existing_file.py",
            code_before="old code",
            code_after="new code",
            status="pending",
            test_status="not-run",
            created_at=datetime.utcnow() - timedelta(hours=3)  # Changed from 1 hour to 3 hours
        )
        
        db.add(test_proposal_db)
        await db.commit()
        
        # Test validation again
        is_valid2, reason2, details2 = await validation_service.validate_proposal(test_proposal, db)
        
        print(f"✅ Second validation result: {is_valid2}")
        print(f"📝 Second reason: {reason2}")
        
        if is_valid2:
            print("🎉 SUCCESS: Proposal validation passed even with existing proposals!")
        else:
            print("❌ FAILED: Proposal validation failed with existing proposals")
            print(f"   Error: {reason2}")
        
        # Clean up
        await db.delete(test_proposal_db)
        await db.commit()
        
    finally:
        await db.close()
        try:
            await db_gen.__anext__()  # Close the generator
        except StopAsyncIteration:
            pass
    
    print("\n🏁 Test completed!")


if __name__ == "__main__":
    asyncio.run(test_validation_changes()) 