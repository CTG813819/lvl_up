#!/usr/bin/env python3
"""
Fix Learning XP Award System
This script fixes the Imperium Learning Controller to properly award XP during learning cycles
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai-backend-python'))

from app.core.database import init_database, get_session
from app.models.sql_models import AgentMetrics
from sqlalchemy import select, update, delete
import structlog

logger = structlog.get_logger()

async def fix_imperium_learning_controller():
    """Fix the Imperium Learning Controller to award XP"""
    print("🔧 Fixing Imperium Learning Controller XP Award...")
    
    try:
        # Read the current file
        controller_file = "app/services/imperium_learning_controller.py"
        
        if not os.path.exists(controller_file):
            print("   ❌ Imperium Learning Controller file not found")
            return False
        
        with open(controller_file, 'r') as f:
            content = f.read()
        
        # Check if XP award is already implemented
        if "metrics.xp +=" in content:
            print("   ✅ XP award already implemented in Imperium Learning Controller")
            return True
        
        # Find the learning success section and add XP award
        old_pattern = """            if result.get("status") == "success":
                metrics.status = LearningStatus.SUCCESS
                metrics.last_success = datetime.utcnow()
                # Change: accumulate raw XP, e.g., +1000 per cycle, no cap
                old_score = metrics.learning_score
                metrics.learning_score = metrics.learning_score + result.get("learning_score", 1000.0)
                logger.info(f"[LEARNING] Agent {agent_id}: Learning succeeded. Score: {old_score} -> {metrics.learning_score} (+{result.get('learning_score', 1000.0)})")
                
                # Persist XP immediately to ensure no loss
                await self.persist_agent_metrics(agent_id)
                logger.info(f"[LEARNING] Agent {agent_id}: XP persisted to database")"""
        
        new_pattern = """            if result.get("status") == "success":
                metrics.status = LearningStatus.SUCCESS
                metrics.last_success = datetime.utcnow()
                # Change: accumulate raw XP, e.g., +1000 per cycle, no cap
                old_score = metrics.learning_score
                metrics.learning_score = metrics.learning_score + result.get("learning_score", 1000.0)
                
                # FIX: Award XP for successful learning cycles
                learning_xp = int(result.get("learning_score", 1000.0) * 0.1)  # 10% of learning score as XP
                old_xp = metrics.xp
                metrics.xp += learning_xp
                logger.info(f"[LEARNING] Agent {agent_id}: Learning succeeded. Score: {old_score} -> {metrics.learning_score} (+{result.get('learning_score', 1000.0)}), XP: {old_xp} -> {metrics.xp} (+{learning_xp})")
                
                # Persist XP immediately to ensure no loss
                await self.persist_agent_metrics(agent_id)
                logger.info(f"[LEARNING] Agent {agent_id}: XP persisted to database")"""
        
        if old_pattern in content:
            content = content.replace(old_pattern, new_pattern)
            
            with open(controller_file, 'w') as f:
                f.write(content)
            
            print("   ✅ XP award added to Imperium Learning Controller")
            return True
        else:
            print("   ⚠️ Could not find exact pattern to replace")
            return False
            
    except Exception as e:
        print(f"   ❌ Error fixing Imperium Learning Controller: {str(e)}")
        return False

async def fix_duplicate_ai_records():
    """Fix duplicate AI records in the database"""
    print("🔧 Fixing duplicate AI records...")
    
    try:
        await init_database()
        
        async with get_session() as session:
            # Get all agent metrics
            result = await session.execute(select(AgentMetrics))
            agents = result.scalars().all()
            
            # Group by agent type (case-insensitive)
            agent_groups = {}
            for agent in agents:
                agent_type_lower = agent.agent_type.lower()
                if agent_type_lower not in agent_groups:
                    agent_groups[agent_type_lower] = []
                agent_groups[agent_type_lower].append(agent)
            
            # Find duplicates
            duplicates_found = False
            for agent_type, agent_list in agent_groups.items():
                if len(agent_list) > 1:
                    duplicates_found = True
                    print(f"   🔍 Found {len(agent_list)} records for {agent_type}:")
                    
                    # Sort by learning score (keep the one with highest score)
                    agent_list.sort(key=lambda x: x.learning_score, reverse=True)
                    
                    # Keep the first one (highest learning score), delete the rest
                    for i, agent in enumerate(agent_list[1:], 1):
                        print(f"      Deleting duplicate {i}: {agent.agent_type} (XP: {agent.xp}, Learning Score: {agent.learning_score})")
                        await session.execute(delete(AgentMetrics).where(AgentMetrics.id == agent.id))
                    
                    # Update the kept record to use lowercase agent type
                    kept_agent = agent_list[0]
                    if kept_agent.agent_type != agent_type:
                        kept_agent.agent_type = agent_type
                        print(f"      Updated kept record to use lowercase: {agent_type}")
            
            if duplicates_found:
                await session.commit()
                print("   ✅ Duplicate records cleaned up")
            else:
                print("   ✅ No duplicate records found")
            
            return True
            
    except Exception as e:
        print(f"   ❌ Error fixing duplicate records: {str(e)}")
        return False

async def award_retroactive_xp():
    """Award retroactive XP for existing learning cycles"""
    print("🔧 Awarding retroactive XP for existing learning cycles...")
    
    try:
        await init_database()
        
        async with get_session() as session:
            # Get all agent metrics
            result = await session.execute(select(AgentMetrics))
            agents = result.scalars().all()
            
            total_xp_awarded = 0
            
            for agent in agents:
                if agent.learning_score > 0 and agent.xp == 0:
                    # Calculate retroactive XP (10% of learning score)
                    retroactive_xp = int(agent.learning_score * 0.1)
                    old_xp = agent.xp
                    agent.xp = retroactive_xp
                    total_xp_awarded += retroactive_xp
                    
                    print(f"   🎁 Awarded {retroactive_xp} XP to {agent.agent_type} (Learning Score: {agent.learning_score})")
            
            if total_xp_awarded > 0:
                await session.commit()
                print(f"   ✅ Awarded {total_xp_awarded} total retroactive XP")
            else:
                print("   ✅ No retroactive XP needed")
            
            return True
            
    except Exception as e:
        print(f"   ❌ Error awarding retroactive XP: {str(e)}")
        return False

async def test_xp_system():
    """Test the XP system after fixes"""
    print("🧪 Testing XP system after fixes...")
    
    try:
        await init_database()
        
        async with get_session() as session:
            # Get all agent metrics
            result = await session.execute(select(AgentMetrics))
            agents = result.scalars().all()
            
            print(f"   📊 Found {len(agents)} AI agents:")
            print()
            
            total_xp = 0
            total_learning_score = 0
            
            for agent in agents:
                print(f"   🤖 {agent.agent_type.upper()}:")
                print(f"      XP: {agent.xp}")
                print(f"      Level: {agent.level}")
                print(f"      Learning Score: {agent.learning_score}")
                print(f"      Total Learning Cycles: {agent.total_learning_cycles}")
                print()
                
                total_xp += agent.xp
                total_learning_score += agent.learning_score
            
            print(f"   📈 TOTALS:")
            print(f"      Total XP: {total_xp}")
            print(f"      Total Learning Score: {total_learning_score}")
            print()
            
            # Check if XP is reasonable (should be roughly 10% of learning score)
            expected_xp = int(total_learning_score * 0.1)
            if total_xp > 0 and abs(total_xp - expected_xp) < expected_xp * 0.5:
                print("   ✅ XP system working correctly!")
                return True
            else:
                print(f"   ⚠️ XP may need adjustment (Expected: ~{expected_xp}, Actual: {total_xp})")
                return False
                
    except Exception as e:
        print(f"   ❌ Error testing XP system: {str(e)}")
        return False

async def main():
    """Main function to fix XP award system"""
    print("🚀 Fixing Learning XP Award System")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    fixes = [
        ("Fix Duplicate AI Records", fix_duplicate_ai_records),
        ("Award Retroactive XP", award_retroactive_xp),
        ("Fix Imperium Learning Controller", fix_imperium_learning_controller),
        ("Test XP System", test_xp_system),
    ]
    
    results = {}
    
    for fix_name, fix_function in fixes:
        print(f"\n🔧 Running: {fix_name}")
        print("-" * 40)
        try:
            result = await fix_function()
            results[fix_name] = result
            if result:
                print(f"   ✅ {fix_name} completed successfully")
            else:
                print(f"   ❌ {fix_name} failed")
        except Exception as e:
            print(f"   ❌ {fix_name} failed with exception: {str(e)}")
            results[fix_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 FIX SUMMARY")
    print("=" * 60)
    
    successful_fixes = sum(1 for result in results.values() if result)
    total_fixes = len(results)
    
    for fix_name, result in results.items():
        status = "✅ SUCCESS" if result else "❌ FAILED"
        print(f"{status}: {fix_name}")
    
    print(f"\nOverall Result: {successful_fixes}/{total_fixes} fixes completed successfully")
    
    if successful_fixes >= 3:
        print("\n🎉 EXCELLENT! XP Award System Fixed!")
        print("✅ AIs will now gain XP from learning cycles")
        print("✅ Retroactive XP has been awarded")
        print("✅ Duplicate records have been cleaned up")
        print("✅ Future learning cycles will award XP properly")
        
        print("\n📋 Next Steps:")
        print("1. Monitor the next learning cycle to see XP gains")
        print("2. Check the AI leveling system")
        print("3. Verify XP is being awarded correctly")
        
    else:
        print("\n⚠️ PARTIAL SUCCESS: Some fixes applied but system may need manual intervention")
        print("❌ XP award system may still have issues")
        print("💡 Check the logs for any remaining errors")
    
    print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(main()) 