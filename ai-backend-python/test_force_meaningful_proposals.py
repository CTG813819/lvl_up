#!/usr/bin/env python3
"""
Test script to force meaningful proposals with real code diffs.
This script creates test files with known issues and runs the AI agents
to generate proposals with actual code improvements.
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
from app.core.database import get_session
from app.models.sql_models import Proposal
from sqlalchemy import select

class ProposalTestGenerator:
    """Test class to generate meaningful proposals for testing"""
    
    def __init__(self):
        self.test_files = {}
        self.agent_service = None
    
    async def initialize(self):
        """Initialize the test generator"""
        self.agent_service = await AIAgentService.initialize()
        print("✅ Test generator initialized")
    
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
function processData(data) {
    var result = [];
    var temp = "unused";
    
    for (var i = 0; i < data.length; i++) {
        console.log("Processing item:", data[i]);
        if (data[i] == "test") {
            result.push(data[i]);
        }
    }
    
    return result;
}

function anotherFunction() {
    var x = 10;
    var y = 20;
    if (x == y) {
        console.log("Values are equal");
    }
    
    // This is a very long function that should be refactored
    // Adding many lines to make it long enough for the analysis
    var longVariableName = "This is a very long variable name that exceeds the recommended line length and should be shortened or split across multiple lines for better readability and maintainability";
    
    for (var j = 0; j < 100; j++) {
        console.log("Processing iteration:", j);
        if (j % 2 == 0) {
            console.log("Even number:", j);
        } else {
            console.log("Odd number:", j);
        }
    }
    
    return "function completed";
}
'''
        return js_code
    
    def create_test_python_file(self) -> str:
        """Create a test Python file with known issues"""
        python_code = '''
import os
import sys
import unused_module

def process_data(data_list):
    result = []
    for item in data_list:
        print("Processing item: {}".format(item))
        if item == "test":
            result.append(item)
    return result

def long_function_that_needs_refactoring():
    """This function is too long and should be split into smaller functions"""
    print("Starting long function")
    
    # Many lines of code to make this function long
    data = []
    for i in range(100):
        print("Processing iteration: {}".format(i))
        if i % 2 == 0:
            print("Even number: {}".format(i))
            data.append(i)
        else:
            print("Odd number: {}".format(i))
            data.append(i * 2)
    
    # More processing
    processed_data = []
    for item in data:
        if item > 50:
            processed_data.append(item * 2)
        else:
            processed_data.append(item)
    
    # Even more processing
    final_result = []
    for item in processed_data:
        if item % 3 == 0:
            final_result.append(item)
        elif item % 5 == 0:
            final_result.append(item * 2)
        else:
            final_result.append(item)
    
    print("Long function completed")
    return final_result

def another_function():
    x = 10
    y = 20
    if x == y:
        print("Values are equal")
    return "completed"
'''
        return python_code
    
    async def create_test_repository(self) -> str:
        """Create a temporary test repository with files containing known issues"""
        temp_dir = tempfile.mkdtemp()
        
        # Create test files
        test_files = {
            'lib/test_widget.dart': self.create_test_dart_file(),
            'src/test_processor.js': self.create_test_js_file(),
            'app/test_processor.py': self.create_test_python_file()
        }
        
        for file_path, content in test_files.items():
            full_path = os.path.join(temp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)
        
        print(f"✅ Created test repository at: {temp_dir}")
        return temp_dir
    
    async def mock_github_service(self, temp_dir: str):
        """Mock the GitHub service to return our test files"""
        class MockGitHubService:
            def __init__(self, test_dir):
                self.test_dir = test_dir
                self.repo = "test-repo"
                self.token = None
            
            async def get_repo_content(self):
                """Return test repository content"""
                return [
                    {"path": "lib/test_widget.dart", "type": "file"},
                    {"path": "src/test_processor.js", "type": "file"},
                    {"path": "app/test_processor.py", "type": "file"}
                ]
            
            async def get_file_content(self, file_path: str):
                """Return content of test files"""
                full_path = os.path.join(self.test_dir, file_path)
                if os.path.exists(full_path):
                    with open(full_path, 'r') as f:
                        return f.read()
                return None
        
        # Replace the GitHub service with our mock
        self.agent_service.github_service = MockGitHubService(temp_dir)
    
    async def run_agents_and_generate_proposals(self):
        """Run all AI agents to generate proposals"""
        print("🚀 Running AI agents to generate proposals...")
        
        # Run Imperium agent (code optimization)
        print("📊 Running Imperium agent...")
        imperium_result = await self.agent_service.run_imperium_agent()
        print(f"Imperium result: {imperium_result}")
        
        # Run Guardian agent (security analysis)
        print("🛡️ Running Guardian agent...")
        guardian_result = await self.agent_service.run_guardian_agent()
        print(f"Guardian result: {guardian_result}")
        
        # Run Sandbox agent (experiments)
        print("🧪 Running Sandbox agent...")
        sandbox_result = await self.agent_service.run_sandbox_agent()
        print(f"Sandbox result: {sandbox_result}")
        
        return {
            "imperium": imperium_result,
            "guardian": guardian_result,
            "sandbox": sandbox_result
        }
    
    async def check_generated_proposals(self):
        """Check what proposals were generated"""
        print("🔍 Checking generated proposals...")
        
        async with get_session() as session:
            # Get recent proposals
            result = await session.execute(
                select(Proposal).order_by(Proposal.created_at.desc()).limit(10)
            )
            proposals = result.scalars().all()
            
            print(f"Found {len(proposals)} recent proposals:")
            for proposal in proposals:
                print(f"  - ID: {proposal.id}")
                print(f"    AI Type: {proposal.ai_type}")
                print(f"    File: {proposal.file_path}")
                print(f"    Type: {proposal.improvement_type}")
                print(f"    Status: {proposal.status}")
                print(f"    Code Before Length: {len(proposal.code_before or '')}")
                print(f"    Code After Length: {len(proposal.code_after or '')}")
                print(f"    Has Changes: {proposal.code_before != proposal.code_after}")
                print("    ---")
    
    async def create_forced_proposal(self):
        """Create a forced proposal with real code changes"""
        print("🎯 Creating forced proposal with real code changes...")
        
        # Create a proposal with actual code improvements
        proposal_data = {
            "ai_type": "imperium",
            "file_path": "lib/test_widget.dart",
            "code_before": self.create_test_dart_file(),
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
    log("More debug info");
    
    // Batched updates for better performance
    setState(() {
      data = "updated";
      // TODO: Consider splitting this large class into smaller, focused classes
    });
    
    return Container(
      child: Text(data ?? "default"),
    );
  }
}
''',
            "improvement_type": "performance",
            "confidence": 0.9,
            "ai_reasoning": "Forced test proposal with real code improvements: replaced print with logging, added null safety, batched setState calls",
            "status": "pending"
        }
        
        async with get_session() as session:
            proposal = Proposal(
                id=await self._generate_uuid(),
                **proposal_data,
                created_at=datetime.utcnow()
            )
            session.add(proposal)
            await session.commit()
            await session.refresh(proposal)
            
            print(f"✅ Created forced proposal: {proposal.id}")
            return proposal
    
    async def _generate_uuid(self):
        """Generate a UUID for the proposal"""
        import uuid
        return uuid.uuid4()

async def main():
    """Main test function"""
    print("🧪 Starting AI Agent Proposal Test")
    print("=" * 50)
    
    test_generator = ProposalTestGenerator()
    await test_generator.initialize()
    
    # Create test repository
    temp_dir = await test_generator.create_test_repository()
    
    try:
        # Mock GitHub service
        await test_generator.mock_github_service(temp_dir)
        
        # Run agents to generate proposals
        results = await test_generator.run_agents_and_generate_proposals()
        
        # Check what proposals were generated
        await test_generator.check_generated_proposals()
        
        # Create a forced proposal with real changes
        forced_proposal = await test_generator.create_forced_proposal()
        
        print("\n" + "=" * 50)
        print("✅ Test completed successfully!")
        print(f"📄 Created forced proposal: {forced_proposal.id}")
        print("🔍 Check the database for generated proposals")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"🧹 Cleaned up test directory: {temp_dir}")

if __name__ == "__main__":
    asyncio.run(main()) 