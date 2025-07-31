#!/usr/bin/env python3
"""
Test script to verify that AI agents can generate meaningful proposals with actual code changes.
This script creates test files with known issues and runs the AI agents to generate proposals.
"""

import asyncio
import os
import tempfile
import json
from datetime import datetime
from typing import Dict, Any

# Add the app directory to the Python path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.ai_agent_service import AIAgentService
from app.services.github_service import GitHubService
from app.core.database import get_session, init_database
from app.models.sql_models import Proposal
from sqlalchemy import select

class MeaningfulProposalTest:
    """Test class to verify meaningful proposal generation"""
    
    def __init__(self):
        self.test_files = {}
        self.agent_service = None
        self.github_service = None
    
    async def initialize(self):
        """Initialize the test"""
        await init_database()
        self.agent_service = AIAgentService()
        self.github_service = GitHubService()
        print("✅ Test initialized")
    
    def create_test_dart_file(self) -> str:
        """Create a test Dart file with known issues"""
        dart_code = '''
import 'package:flutter/material.dart';

class TestWidget extends StatefulWidget {
  @override
  _TestWidgetState createState() => _TestWidgetState();
}

class _TestWidgetState extends State<TestWidget> {
  String data = "test";
  String unusedVar = "never used";
  
  @override
  Widget build(BuildContext context) {
    print("Debug info");
    print("More debug info");
    
    setState(() {
      data = "updated";
    });
    
    setState(() {
      data = "updated again";
    });
    
    setState(() {
      data = "and again";
    });
    
    return Container(
      child: Text(data),
    );
  }
}
'''
        return dart_code
    
    def create_test_js_file(self) -> str:
        """Create a test JavaScript file with known issues"""
        js_code = '''
var oldVariable = "test";
var anotherVar = "something";

function testFunction() {
    console.log("Debug info");
    if (oldVariable == "test") {
        console.log("Found test");
    }
    
    var unusedVar = "never used";
    
    return oldVariable;
}

function longFunction() {
    var result = "";
    for (var i = 0; i < 100; i++) {
        result += i;
        if (i % 10 == 0) {
            console.log("Progress: " + i);
        }
    }
    return result;
}
'''
        return js_code
    
    def create_test_python_file(self) -> str:
        """Create a test Python file with known issues"""
        python_code = '''
import os
import sys
import unused_module

def test_function():
    print("Debug info")
    data = "test"
    result = data.format("value")
    return result

def long_function():
    result = []
    for i in range(100):
        result.append(i)
        if i % 10 == 0:
            print("Progress: {}".format(i))
    return result

def unused_function():
    pass
'''
        return python_code
    
    async def create_test_files_in_repo(self):
        """Create test files in the repository for analysis"""
        print("📝 Creating test files in repository...")
        
        # Create test files
        test_files = {
            "lib/test_widget.dart": self.create_test_dart_file(),
            "src/test_script.js": self.create_test_js_file(),
            "app/test_module.py": self.create_test_python_file()
        }
        
        # Mock the GitHub service methods
        async def mock_get_repo_content():
            return list(test_files.keys())
        
        async def mock_get_file_content(file_path):
            return test_files.get(file_path, "")
        
        # Replace the methods
        self.agent_service.github_service.get_repo_content = mock_get_repo_content
        self.agent_service.github_service.get_file_content = mock_get_file_content
        
        print(f"✅ Created {len(test_files)} test files")
        return test_files
    
    async def test_imperium_agent(self):
        """Test Imperium agent proposal generation"""
        print("\n🏆 Testing Imperium agent...")
        
        try:
            result = await self.agent_service.run_imperium_agent()
            print(f"Imperium result: {result}")
            
            if result.get("status") == "success":
                proposals_created = result.get("proposals_created", 0)
                print(f"✅ Imperium created {proposals_created} proposals")
                
                # Check if proposals have meaningful changes
                await self.verify_proposals_have_changes("Imperium")
            else:
                print(f"❌ Imperium failed: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Imperium test error: {str(e)}")
    
    async def test_guardian_agent(self):
        """Test Guardian agent proposal generation"""
        print("\n🛡️ Testing Guardian agent...")
        
        try:
            result = await self.agent_service.run_guardian_agent()
            print(f"Guardian result: {result}")
            
            if result.get("status") == "success":
                security_proposals = result.get("security_proposals", 0)
                quality_proposals = result.get("quality_proposals", 0)
                total_proposals = security_proposals + quality_proposals
                print(f"✅ Guardian created {total_proposals} proposals ({security_proposals} security, {quality_proposals} quality)")
                
                # Check if proposals have meaningful changes
                await self.verify_proposals_have_changes("Guardian")
            else:
                print(f"❌ Guardian failed: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Guardian test error: {str(e)}")
    
    async def test_sandbox_agent(self):
        """Test Sandbox agent proposal generation"""
        print("\n🧪 Testing Sandbox agent...")
        
        try:
            result = await self.agent_service.run_sandbox_agent()
            print(f"Sandbox result: {result}")
            
            if result.get("status") == "success":
                proposals_created = result.get("proposals_created", 0)
                print(f"✅ Sandbox created {proposals_created} proposals")
                
                # Check if proposals have meaningful changes
                await self.verify_proposals_have_changes("Sandbox")
            else:
                print(f"❌ Sandbox failed: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Sandbox test error: {str(e)}")
    
    async def verify_proposals_have_changes(self, ai_type: str):
        """Verify that proposals have meaningful code changes"""
        print(f"🔍 Verifying {ai_type} proposals have meaningful changes...")
        
        try:
            async with get_session() as session:
                # Get recent proposals for this AI type
                query = select(Proposal).where(
                    Proposal.ai_type == ai_type,
                    Proposal.status == "pending"
                ).order_by(Proposal.created_at.desc()).limit(5)
                
                result = await session.execute(query)
                proposals = result.scalars().all()
                
                if not proposals:
                    print(f"⚠️ No proposals found for {ai_type}")
                    return
                
                print(f"📊 Found {len(proposals)} proposals for {ai_type}")
                
                for i, proposal in enumerate(proposals):
                    print(f"\n  Proposal {i+1}: {proposal.id}")
                    print(f"    File: {proposal.file_path}")
                    print(f"    Code before length: {len(proposal.code_before or '')}")
                    print(f"    Code after length: {len(proposal.code_after or '')}")
                    
                    # Check for meaningful changes
                    if proposal.code_before and proposal.code_after:
                        lines_before = len(proposal.code_before.split('\n'))
                        lines_after = len(proposal.code_after.split('\n'))
                        chars_before = len(proposal.code_before)
                        chars_after = len(proposal.code_after)
                        
                        if lines_before == lines_after and chars_before == chars_after:
                            print(f"    ❌ No meaningful changes detected")
                        else:
                            print(f"    ✅ Meaningful changes detected:")
                            print(f"      Lines: {lines_before} → {lines_after}")
                            print(f"      Characters: {chars_before} → {chars_after}")
                    else:
                        print(f"    ❌ Empty code blocks")
                
        except Exception as e:
            print(f"❌ Error verifying proposals: {str(e)}")
    
    async def run_all_tests(self):
        """Run all agent tests"""
        print("🚀 Starting meaningful proposal tests...")
        
        await self.initialize()
        await self.create_test_files_in_repo()
        
        # Test each agent
        await self.test_imperium_agent()
        await self.test_guardian_agent()
        await self.test_sandbox_agent()
        
        print("\n🎯 Test summary:")
        print("✅ All agents tested for meaningful proposal generation")
        print("📊 Check the output above for proposal details")

async def main():
    """Main test function"""
    test = MeaningfulProposalTest()
    await test.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 