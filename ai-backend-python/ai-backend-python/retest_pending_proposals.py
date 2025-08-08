#!/usr/bin/env python3
"""
Retest all pending proposals and fix testing issues
"""

import asyncio
import json
import sys
from datetime import datetime

# Add the backend path to sys.path
sys.path.append('ai-backend-python')

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.sql_models import Proposal
from app.services.testing_service import TestingService

async def retest_all_pending_proposals():
    """Retest all pending proposals and update their status"""
    print("🔄 Retesting all pending proposals...")
    
    # Create database connection
    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Get all pending proposals
        query = select(Proposal).where(Proposal.status == "pending")
        result = await session.execute(query)
        pending_proposals = result.scalars().all()
        
        print(f"📊 Found {len(pending_proposals)} pending proposals to retest")
        
        testing_service = TestingService()
        success_count = 0
        failed_count = 0
        error_count = 0
        
        for i, proposal in enumerate(pending_proposals, 1):
            if i % 100 == 0:
                print(f"   Progress: {i}/{len(pending_proposals)}")
            
            try:
                # Prepare proposal data for testing
                proposal_data = {
                    "id": str(proposal.id),
                    "ai_type": proposal.ai_type,
                    "file_path": proposal.file_path,
                    "code_before": proposal.code_before,
                    "code_after": proposal.code_after,
                    "improvement_type": proposal.improvement_type,
                    "confidence": proposal.confidence,
                }
                
                # Run tests
                overall_result, summary, detailed_results = await testing_service.test_proposal(proposal_data)
                
                # Update proposal status based on test results
                if overall_result.value == "passed":
                    proposal.status = "test-passed"
                    proposal.test_status = "passed"
                    success_count += 1
                elif overall_result.value == "failed":
                    proposal.status = "test-failed"
                    proposal.test_status = "failed"
                    failed_count += 1
                else:  # error or skipped
                    proposal.status = "test-failed"
                    proposal.test_status = "error"
                    error_count += 1
                
                proposal.test_output = summary
                proposal.result = json.dumps([result.to_dict() for result in detailed_results])
                
            except Exception as e:
                print(f"   ❌ Error testing proposal {str(proposal.id)[:8]}: {str(e)}")
                proposal.test_status = "error"
                proposal.test_output = f"Testing error: {str(e)}"
                error_count += 1
        
        # Commit all changes
        await session.commit()
        
        print(f"\n✅ Retesting completed:")
        print(f"   Success: {success_count}")
        print(f"   Failed: {failed_count}")
        print(f"   Errors: {error_count}")
        print(f"   Total: {len(pending_proposals)}")

async def install_missing_dependencies():
    """Install missing testing dependencies"""
    print("🔧 Installing missing dependencies...")
    
    try:
        import subprocess
        
        # Install flake8 for Python linting
        print("   Installing flake8...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "flake8"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ flake8 installed successfully")
        else:
            print(f"   ❌ Failed to install flake8: {result.stderr}")
            
    except Exception as e:
        print(f"   ❌ Error installing dependencies: {str(e)}")

async def main():
    """Main function"""
    print("🚀 Starting proposal retesting process...")
    print("=" * 50)
    
    # Install missing dependencies
    await install_missing_dependencies()
    
    # Retest all pending proposals
    await retest_all_pending_proposals()
    
    print("\n" + "=" * 50)
    print("🎯 Summary:")
    print("   - All pending proposals have been retested")
    print("   - Only proposals with status 'test-passed' will be shown to users")
    print("   - Failed proposals are marked as 'test-failed'")
    print("   - Error proposals are marked as 'test-failed' with error status")

if __name__ == "__main__":
    asyncio.run(main()) 