#!/usr/bin/env python3
"""
Simple patch script to test AI agent fixes and force meaningful proposals.
Run this on the EC2 instance to test the fixes.
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.ai_agent_service import AIAgentService
from app.core.database import get_session
from app.models.sql_models import Proposal
from sqlalchemy import select

async def test_ai_agents():
    """Test the AI agents to see if they generate meaningful proposals"""
    print("🧪 Testing AI Agents for Meaningful Proposals")
    print("=" * 60)
    
    try:
        # Initialize the AI agent service
        agent_service = await AIAgentService.initialize()
        print("✅ AI Agent Service initialized")
        
        # Test each agent
        agents = [
            ("Imperium", agent_service.run_imperium_agent),
            ("Guardian", agent_service.run_guardian_agent),
            ("Sandbox", agent_service.run_sandbox_agent)
        ]
        
        for agent_name, agent_func in agents:
            print(f"\n🚀 Testing {agent_name} agent...")
            try:
                result = await agent_func()
                print(f"✅ {agent_name} result: {result}")
                
                if result.get("status") == "success":
                    proposals_created = result.get("proposals_created", 0)
                    print(f"📄 {agent_name} created {proposals_created} proposals")
                else:
                    print(f"⚠️ {agent_name} status: {result.get('status')}")
                    print(f"📝 {agent_name} message: {result.get('message', 'No message')}")
                    
            except Exception as e:
                print(f"❌ {agent_name} agent failed: {e}")
        
        # Check for recent proposals
        await check_recent_proposals()
        
        # Create a test proposal with real changes
        await create_test_proposal()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

async def check_recent_proposals():
    """Check recent proposals in the database"""
    print("\n🔍 Checking recent proposals...")
    
    try:
        async with get_session() as session:
            # Get recent proposals
            result = await session.execute(
                select(Proposal).order_by(Proposal.created_at.desc()).limit(5)
            )
            proposals = result.scalars().all()
            
            print(f"Found {len(proposals)} recent proposals:")
            
            for proposal in proposals:
                print(f"\n📄 Proposal ID: {proposal.id}")
                print(f"   AI Type: {proposal.ai_type}")
                print(f"   File: {proposal.file_path}")
                print(f"   Type: {proposal.improvement_type}")
                print(f"   Status: {proposal.status}")
                print(f"   Created: {proposal.created_at}")
                
                # Check if there are real code changes
                code_before = proposal.code_before or ""
                code_after = proposal.code_after or ""
                
                print(f"   Code Before Length: {len(code_before)}")
                print(f"   Code After Length: {len(code_after)}")
                print(f"   Has Real Changes: {code_before != code_after}")
                
                if code_before != code_after:
                    print("   ✅ This proposal has real code changes!")
                else:
                    print("   ⚠️ This proposal has no real code changes")
                
                # Show a snippet of the changes
                if code_before and code_after and code_before != code_after:
                    print("   📝 Change Preview:")
                    before_lines = code_before.split('\n')[:3]
                    after_lines = code_after.split('\n')[:3]
                    print("      Before:", ' | '.join(before_lines))
                    print("      After: ", ' | '.join(after_lines))
                
    except Exception as e:
        print(f"❌ Error checking proposals: {e}")

async def create_test_proposal():
    """Create a test proposal with real code changes"""
    print("\n🎯 Creating test proposal with real code changes...")
    
    try:
        # Create a proposal with actual code improvements
        proposal_data = {
            "ai_type": "imperium",
            "file_path": "lib/test_widget.dart",
            "code_before": '''
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
    
    return Container(
      child: Text(data),
    );
  }
}
''',
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
            "confidence": 0.9,
            "ai_reasoning": "Test proposal with real improvements: replaced print with logging, added null safety, improved setState usage",
            "status": "pending",
            "description": "Performance optimization for TestWidget - replaced print with logging and added null safety"
        }
        
        async with get_session() as session:
            import uuid
            proposal = Proposal(
                id=uuid.uuid4(),
                **proposal_data,
                created_at=datetime.utcnow()
            )
            session.add(proposal)
            await session.commit()
            await session.refresh(proposal)
            
            print(f"✅ Created test proposal: {proposal.id}")
            print(f"📄 Proposal has real changes: {proposal.code_before != proposal.code_after}")
            
            return proposal
            
    except Exception as e:
        print(f"❌ Error creating test proposal: {e}")
        return None

async def main():
    """Main function"""
    print("🚀 Starting AI Agent Patch Test")
    print(f"⏰ Started at: {datetime.now()}")
    
    await test_ai_agents()
    
    print("\n" + "=" * 60)
    print("✅ Patch test completed!")
    print(f"⏰ Finished at: {datetime.now()}")

if __name__ == "__main__":
    asyncio.run(main()) 