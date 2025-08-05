#!/usr/bin/env python3
"""
Diagnose pending proposals and fix testing issues
"""

import asyncio
import json
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Optional

# Add the backend path to sys.path
sys.path.append('ai-backend-python')

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.sql_models import Proposal
from app.services.testing_service import TestingService

async def check_system_dependencies():
    """Check if required testing tools are available"""
    print("🔍 Checking system dependencies...")
    
    dependencies = {
        'python': 'python --version',
        'dart': 'dart --version',
        'node': 'node --version',
        'flake8': 'flake8 --version',
    }
    
    available = {}
    for tool, command in dependencies.items():
        try:
            result = subprocess.run(command.split(), capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                available[tool] = True
                print(f"✅ {tool}: Available")
            else:
                available[tool] = False
                print(f"❌ {tool}: Not available")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            available[tool] = False
            print(f"❌ {tool}: Not available")
    
    return available

async def analyze_pending_proposals():
    """Analyze the current state of pending proposals"""
    print("\n📊 Analyzing pending proposals...")
    
    # Create database connection
    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Get all proposals with their status
        query = select(Proposal)
        result = await session.execute(query)
        all_proposals = result.scalars().all()
        
        # Count by status
        status_counts = {}
        for proposal in all_proposals:
            status = proposal.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"📈 Total proposals: {len(all_proposals)}")
        print("📊 Status breakdown:")
        for status, count in sorted(status_counts.items()):
            print(f"   {status}: {count}")
        
        # Analyze pending proposals
        pending_query = select(Proposal).where(Proposal.status == "pending")
        pending_result = await session.execute(pending_query)
        pending_proposals = pending_result.scalars().all()
        
        print(f"\n🔍 Analyzing {len(pending_proposals)} pending proposals...")
        
        # Check test status of pending proposals
        test_status_counts = {}
        ai_type_counts = {}
        recent_proposals = []
        
        for proposal in pending_proposals:
            # Test status
            test_status = proposal.test_status or "not_tested"
            test_status_counts[test_status] = test_status_counts.get(test_status, 0) + 1
            
            # AI type
            ai_type = proposal.ai_type or "unknown"
            ai_type_counts[ai_type] = ai_type_counts.get(ai_type, 0) + 1
            
            # Recent proposals (last 10)
            if len(recent_proposals) < 10:
                recent_proposals.append({
                    'id': str(proposal.id),
                    'ai_type': proposal.ai_type,
                    'file_path': proposal.file_path,
                    'test_status': proposal.test_status,
                    'test_output': proposal.test_output,
                    'created_at': proposal.created_at.isoformat() if proposal.created_at else None
                })
        
        print(f"\n📋 Test status of pending proposals:")
        for status, count in test_status_counts.items():
            print(f"   {status}: {count}")
        
        print(f"\n🤖 AI type breakdown:")
        for ai_type, count in ai_type_counts.items():
            print(f"   {ai_type}: {count}")
        
        print(f"\n🕒 Recent pending proposals:")
        for prop in recent_proposals:
            print(f"   ID: {prop['id'][:8]}... | AI: {prop['ai_type']} | File: {prop['file_path']} | Test: {prop['test_status']}")
            if prop['test_output']:
                print(f"      Test output: {prop['test_output'][:100]}...")
        
        return pending_proposals, status_counts

async def test_sample_proposals():
    """Test a few sample proposals to see what's happening"""
    print("\n🧪 Testing sample proposals...")
    
    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Get a few pending proposals
        query = select(Proposal).where(Proposal.status == "pending").limit(3)
        result = await session.execute(query)
        sample_proposals = result.scalars().all()
        
        testing_service = TestingService()
        
        for i, proposal in enumerate(sample_proposals, 1):
            print(f"\n🧪 Testing proposal {i}: {str(proposal.id)[:8]}...")
            
            # Prepare proposal data
            proposal_data = {
                "id": str(proposal.id),
                "ai_type": proposal.ai_type,
                "file_path": proposal.file_path,
                "code_before": proposal.code_before,
                "code_after": proposal.code_after,
                "improvement_type": proposal.improvement_type,
                "confidence": proposal.confidence,
            }
            
            try:
                # Run tests
                overall_result, summary, detailed_results = await testing_service.test_proposal(proposal_data)
                
                print(f"   Overall result: {overall_result.value}")
                print(f"   Summary: {summary}")
                print(f"   Detailed results: {len(detailed_results)} tests")
                
                for test_result in detailed_results:
                    print(f"     {test_result.test_type.value}: {test_result.result.value} ({test_result.duration:.2f}s)")
                    if test_result.result.value in ['failed', 'error']:
                        print(f"       Output: {test_result.output[:200]}...")
                
            except Exception as e:
                print(f"   ❌ Testing failed: {str(e)}")

async def fix_testing_issues():
    """Fix common testing issues"""
    print("\n🔧 Fixing testing issues...")
    
    # Check if we need to install missing dependencies
    dependencies = await check_system_dependencies()
    
    missing_tools = [tool for tool, available in dependencies.items() if not available]
    
    if missing_tools:
        print(f"\n⚠️  Missing tools: {', '.join(missing_tools)}")
        print("💡 Recommendations:")
        
        if 'flake8' in missing_tools:
            print("   - Install flake8: pip install flake8")
        
        if 'dart' in missing_tools:
            print("   - Install Dart SDK: https://dart.dev/get-dart")
        
        if 'node' in missing_tools:
            print("   - Install Node.js: https://nodejs.org/")
    
    # Update testing service timeout
    print("\n⏱️  Updating testing service configuration...")
    
    # Create an improved testing service configuration
    improved_config = '''
# Improved testing service configuration
TEST_TIMEOUT = 60  # Increase timeout to 60 seconds
MAX_OUTPUT_LENGTH = 20000  # Increase output length limit
ENABLE_GRACEFUL_FAILURE = True  # Continue testing even if some tests fail
'''
    
    print("✅ Configuration recommendations:")
    print(improved_config)

async def retest_pending_proposals():
    """Retest all pending proposals"""
    print("\n🔄 Retesting pending proposals...")
    
    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Get all pending proposals
        query = select(Proposal).where(Proposal.status == "pending")
        result = await session.execute(query)
        pending_proposals = result.scalars().all()
        
        print(f"🔄 Retesting {len(pending_proposals)} pending proposals...")
        
        testing_service = TestingService()
        success_count = 0
        error_count = 0
        
        for i, proposal in enumerate(pending_proposals, 1):
            if i % 10 == 0:
                print(f"   Progress: {i}/{len(pending_proposals)}")
            
            try:
                # Prepare proposal data
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
                    error_count += 1
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
        print(f"   Errors: {error_count}")
        print(f"   Total: {len(pending_proposals)}")

async def main():
    """Main diagnostic function"""
    print("🔍 Diagnosing pending proposals issue...")
    print("=" * 50)
    
    # Check system dependencies
    dependencies = await check_system_dependencies()
    
    # Analyze current state
    pending_proposals, status_counts = await analyze_pending_proposals()
    
    # Test sample proposals
    await test_sample_proposals()
    
    # Fix testing issues
    await fix_testing_issues()
    
    # Ask user if they want to retest all pending proposals
    print("\n" + "=" * 50)
    print("🎯 Summary:")
    print(f"   - Total proposals: {sum(status_counts.values())}")
    print(f"   - Pending proposals: {len(pending_proposals)}")
    print(f"   - Missing tools: {len([t for t, a in dependencies.items() if not a])}")
    
    print("\n💡 Recommendations:")
    print("   1. Install missing testing tools")
    print("   2. Increase testing timeout")
    print("   3. Retest all pending proposals")
    
    response = input("\n❓ Do you want to retest all pending proposals? (y/n): ")
    if response.lower() == 'y':
        await retest_pending_proposals()
    else:
        print("⏭️  Skipping retest. You can run this script again later.")

if __name__ == "__main__":
    asyncio.run(main()) 