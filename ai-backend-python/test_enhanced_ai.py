#!/usr/bin/env python3
"""
Test script for Enhanced AI Coordinator
Demonstrates proactive and creative AI behavior
"""

import asyncio
import httpx
import json
from datetime import datetime
import pytest

# API base URL
BASE_URL = "http://localhost:8000/api"

@pytest.mark.asyncio
async def test_enhanced_ai_status():
    """Test getting enhanced AI status"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/enhanced-ai/status")
        print("🔍 Enhanced AI Status:")
        print(json.dumps(response.json(), indent=2))
        print()

@pytest.mark.asyncio
async def test_generate_creative_code():
    """Test generating creative code for each AI type"""
    ai_types = ["imperium", "guardian", "sandbox", "conquest"]
    
    async with httpx.AsyncClient() as client:
        for ai_type in ai_types:
            print(f"✨ Testing creative code generation for {ai_type}...")
            response = await client.post(f"{BASE_URL}/enhanced-ai/generate-creative-code/{ai_type}")
            result = response.json()
            print(f"   {ai_type}: {result.get('new_code_generated', 0)} new files generated")
            print()

@pytest.mark.asyncio
async def test_run_enhanced_ai_agent():
    """Test running enhanced AI agents"""
    ai_types = ["imperium", "guardian", "sandbox", "conquest"]
    
    async with httpx.AsyncClient() as client:
        for ai_type in ai_types:
            print(f"🤖 Testing enhanced {ai_type} AI agent...")
            response = await client.post(f"{BASE_URL}/enhanced-ai/run-ai/{ai_type}")
            result = response.json()
            
            if result.get("status") == "success":
                ai_result = result.get("result", {})
                print(f"   ✅ {ai_type} completed successfully")
                print(f"   📊 Proposals created: {ai_result.get('proposals_created', 0)}")
                print(f"   📄 New code generated: {ai_result.get('new_code_generated', 0)}")
                print(f"   🧪 Proposals tested: {ai_result.get('proposals_tested', 0)}")
                print(f"   🚀 Proposals applied: {ai_result.get('proposals_applied', 0)}")
            else:
                print(f"   ❌ {ai_type} failed: {result.get('message', 'Unknown error')}")
            print()

@pytest.mark.asyncio
async def test_run_full_enhanced_cycle():
    """Test running the full enhanced AI cycle"""
    print("🚀 Testing full Enhanced AI Cycle...")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/enhanced-ai/run-cycle")
        result = response.json()
        
        if result.get("status") == "success":
            cycle_result = result.get("result", {})
            print("   ✅ Enhanced AI cycle completed successfully")
            print(f"   📊 Total proposals created: {cycle_result.get('total_proposals_created', 0)}")
            print(f"   📄 Total new code generated: {cycle_result.get('total_new_code_generated', 0)}")
            print(f"   🤖 AIs run: {len(cycle_result.get('ai_results', {}))}")
            
            # Show individual AI results
            for ai_type, ai_result in cycle_result.get('ai_results', {}).items():
                if ai_result.get('status') == 'success':
                    print(f"      {ai_type}: {ai_result.get('proposals_created', 0)} proposals, {ai_result.get('new_code_generated', 0)} new code")
        else:
            print(f"   ❌ Enhanced AI cycle failed: {result.get('message', 'Unknown error')}")
        print()

@pytest.mark.asyncio
async def test_apply_proposal():
    """Test applying a specific proposal"""
    print("🚀 Testing proposal application...")
    
    # First, get a list of proposals
    async with httpx.AsyncClient() as client:
        # Get proposals that have passed testing
        response = await client.get(f"{BASE_URL}/proposals/")
        proposals = response.json()
        
        # Find a proposal that has passed testing
        test_passed_proposal = None
        for proposal in proposals:
            if proposal.get('test_status') == 'passed' and proposal.get('status') == 'test-passed':
                test_passed_proposal = proposal
                break
        
        if test_passed_proposal:
            proposal_id = test_passed_proposal['id']
            print(f"   📝 Found proposal {proposal_id} that passed testing")
            
            # Apply the proposal
            response = await client.post(f"{BASE_URL}/enhanced-ai/apply-proposal/{proposal_id}")
            result = response.json()
            
            if result.get("status") == "success":
                print(f"   ✅ Proposal {proposal_id} applied successfully")
            else:
                print(f"   ❌ Failed to apply proposal {proposal_id}: {result.get('message', 'Unknown error')}")
        else:
            print("   ⚠️ No proposals found that have passed testing")
        print()

async def main():
    """Run all tests"""
    print("🧪 Enhanced AI Coordinator Test Suite")
    print("=" * 50)
    print(f"Started at: {datetime.now()}")
    print()
    
    try:
        # Test 1: Get enhanced AI status
        await test_enhanced_ai_status()
        
        # Test 2: Generate creative code
        await test_generate_creative_code()
        
        # Test 3: Run individual enhanced AI agents
        await test_run_enhanced_ai_agent()
        
        # Test 4: Run full enhanced AI cycle
        await test_run_full_enhanced_cycle()
        
        # Test 5: Apply a proposal
        await test_apply_proposal()
        
        print("✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 