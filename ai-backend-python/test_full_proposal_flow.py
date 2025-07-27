#!/usr/bin/env python3
"""
Test the full proposal generation and validation flow.
This script tests that AI agents can generate proposals that pass validation.
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.ai_agent_service import AIAgentService
from app.core.database import get_session, init_database
from app.models.sql_models import Proposal
from app.services.proposal_validation_service import ProposalValidationService
from sqlalchemy import select

class FullProposalFlowTest:
    """Test class to verify the full proposal generation and validation flow"""
    
    def __init__(self):
        self.agent_service = None
        self.validation_service = None
    
    async def initialize(self):
        """Initialize the test"""
        await init_database()
        self.agent_service = AIAgentService()
        self.validation_service = ProposalValidationService()
        print("✅ Test initialized")
    
    def create_test_file_content(self) -> str:
        """Create test file content with known issues"""
        return '''
import 'package:flutter/material.dart';

class TestWidget extends StatefulWidget {
  @override
  _TestWidgetState createState() => _TestWidgetState();
}

class _TestWidgetState extends State<TestWidget> {
  String data = "test";
  
  @override
  Widget build(BuildContext context) {
    print("Debug info");
    
    setState(() {
      data = "updated";
    });
    
    setState(() {
      data = "updated again";
    });
    
    return Container(
      child: Text(data),
    );
  }
}
'''
    
    async def test_proposal_creation_and_validation(self):
        """Test that proposals are created and pass validation"""
        print("\n🔍 Testing proposal creation and validation...")
        
        # Create a test proposal with meaningful changes
        proposal_data = {
            "ai_type": "Imperium",
            "file_path": "lib/test_widget.dart",
            "code_before": self.create_test_file_content(),
            "code_after": '''
import 'package:flutter/material.dart';
import 'dart:developer';

class TestWidget extends StatefulWidget {
  @override
  _TestWidgetState createState() => _TestWidgetState();
}

class _TestWidgetState extends State<TestWidget> {
  String? data = "test";
  
  @override
  Widget build(BuildContext context) {
    log("Debug info");
    
    // Batched updates for better performance
    setState(() {
      data = "updated";
    });
    
    return Container(
      child: Text(data ?? "default"),
    );
  }
}
''',
            "improvement_type": "performance",
            "confidence": 0.8,
            "ai_reasoning": "Test proposal with real improvements: replaced print with logging, added null safety, improved setState usage",
            "status": "pending"
        }
        
        try:
            # Test validation
            async with get_session() as db:
                is_valid, validation_reason, validation_details = await self.validation_service.validate_proposal(proposal_data, db)
                
                print(f"Validation result: {is_valid}")
                print(f"Validation reason: {validation_reason}")
                print(f"Validation details: {validation_details}")
                
                if is_valid:
                    print("✅ Proposal passed validation")
                    
                    # Check if proposal would be created successfully
                    from app.models.proposal import ProposalCreate
                    from app.routers.proposals import create_proposal_internal
                    
                    try:
                        proposal_create = ProposalCreate(**proposal_data)
                        proposal = await create_proposal_internal(proposal_create, db)
                        print(f"✅ Proposal created successfully: {proposal.id}")
                        
                        # Verify the proposal has meaningful changes
                        lines_before = len(proposal.code_before.split('\n'))
                        lines_after = len(proposal.code_after.split('\n'))
                        chars_before = len(proposal.code_before)
                        chars_after = len(proposal.code_after)
                        
                        print(f"  Code changes: {lines_before}→{lines_after} lines, {chars_before}→{chars_after} characters")
                        
                        if lines_before != lines_after or chars_before != chars_after:
                            print("✅ Meaningful changes confirmed")
                        else:
                            print("❌ No meaningful changes detected")
                            
                    except Exception as e:
                        print(f"❌ Proposal creation failed: {str(e)}")
                else:
                    print(f"❌ Proposal failed validation: {validation_reason}")
                    
        except Exception as e:
            print(f"❌ Validation test error: {str(e)}")
    
    async def test_ai_agent_proposal_generation(self):
        """Test that AI agents can generate valid proposals"""
        print("\n🤖 Testing AI agent proposal generation...")
        
        # Mock the GitHub service to return our test file
        test_files = {
            "lib/test_widget.dart": self.create_test_file_content()
        }
        
        async def mock_get_repo_content():
            return list(test_files.keys())
        
        async def mock_get_file_content(file_path):
            return test_files.get(file_path, "")
        
        # Replace the methods
        self.agent_service.github_service.get_repo_content = mock_get_repo_content
        self.agent_service.github_service.get_file_content = mock_get_file_content
        
        try:
            # Run Imperium agent
            result = await self.agent_service.run_imperium_agent()
            print(f"Imperium agent result: {result}")
            
            if result.get("status") == "success":
                proposals_created = result.get("proposals_created", 0)
                print(f"✅ Imperium created {proposals_created} proposals")
                
                # Check if proposals were actually created in the database
                async with get_session() as session:
                    query = select(Proposal).where(
                        Proposal.ai_type == "Imperium",
                        Proposal.status == "pending"
                    ).order_by(Proposal.created_at.desc()).limit(5)
                    
                    result = await session.execute(query)
                    proposals = result.scalars().all()
                    
                    if proposals:
                        print(f"✅ Found {len(proposals)} proposals in database")
                        
                        for i, proposal in enumerate(proposals):
                            print(f"  Proposal {i+1}: {proposal.id}")
                            print(f"    File: {proposal.file_path}")
                            print(f"    Confidence: {proposal.confidence}")
                            
                            # Check for meaningful changes
                            if proposal.code_before and proposal.code_after:
                                lines_before = len(proposal.code_before.split('\n'))
                                lines_after = len(proposal.code_after.split('\n'))
                                chars_before = len(proposal.code_before)
                                chars_after = len(proposal.code_after)
                                
                                if lines_before != lines_after or chars_before != chars_after:
                                    print(f"    ✅ Meaningful changes: {lines_before}→{lines_after} lines")
                                else:
                                    print(f"    ❌ No meaningful changes")
                            else:
                                print(f"    ❌ Empty code blocks")
                    else:
                        print("❌ No proposals found in database")
            else:
                print(f"❌ Imperium agent failed: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ AI agent test error: {str(e)}")
    
    async def test_validation_service_directly(self):
        """Test the validation service directly with various scenarios"""
        print("\n🔧 Testing validation service directly...")
        
        async with get_session() as db:
            # Test 1: Valid proposal
            valid_proposal = {
                "ai_type": "Imperium",
                "file_path": "lib/test.dart",
                "code_before": "print('hello')",
                "code_after": "log('hello')",
                "improvement_type": "performance",
                "confidence": 0.8
            }
            
            is_valid, reason, details = await self.validation_service.validate_proposal(valid_proposal, db)
            print(f"Valid proposal test: {is_valid} - {reason}")
            
            # Test 2: Empty code blocks
            empty_proposal = {
                "ai_type": "Imperium",
                "file_path": "lib/test.dart",
                "code_before": "",
                "code_after": "",
                "improvement_type": "performance",
                "confidence": 0.8
            }
            
            is_valid, reason, details = await self.validation_service.validate_proposal(empty_proposal, db)
            print(f"Empty proposal test: {is_valid} - {reason}")
            
            # Test 3: No changes
            no_change_proposal = {
                "ai_type": "Imperium",
                "file_path": "lib/test.dart",
                "code_before": "print('hello')",
                "code_after": "print('hello')",
                "improvement_type": "performance",
                "confidence": 0.8
            }
            
            is_valid, reason, details = await self.validation_service.validate_proposal(no_change_proposal, db)
            print(f"No change proposal test: {is_valid} - {reason}")
            
            # Test 4: Low confidence
            low_confidence_proposal = {
                "ai_type": "Imperium",
                "file_path": "lib/test.dart",
                "code_before": "print('hello')",
                "code_after": "log('hello')",
                "improvement_type": "performance",
                "confidence": 0.3
            }
            
            is_valid, reason, details = await self.validation_service.validate_proposal(low_confidence_proposal, db)
            print(f"Low confidence proposal test: {is_valid} - {reason}")
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting full proposal flow tests...")
        
        await self.initialize()
        
        # Test validation service directly
        await self.test_validation_service_directly()
        
        # Test proposal creation and validation
        await self.test_proposal_creation_and_validation()
        
        # Test AI agent proposal generation
        await self.test_ai_agent_proposal_generation()
        
        print("\n🎯 Test summary:")
        print("✅ Full proposal flow tested")
        print("📊 Check the output above for validation results")

async def main():
    """Main test function"""
    test = FullProposalFlowTest()
    await test.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 