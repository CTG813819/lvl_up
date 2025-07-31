#!/usr/bin/env python3
"""
Fix Learning Cycle and Implement Agnostic Logic
Addresses the 'xp' attribute error in learning cycles and implements agnostic test generation
"""

import asyncio
import sys
import os
import subprocess
import time

# Add the ai-backend-python directory to the path
sys.path.append('/home/ubuntu/ai-backend-python')

async def fix_learning_cycle_xp_error():
    """Fix the 'xp' attribute error in learning cycles"""
    try:
        print("🔧 Fixing Learning Cycle 'xp' Attribute Error...")
        
        from app.core.database import init_database, get_session
        from sqlalchemy import text
        
        await init_database()
        session = get_session()
        
        async with session as s:
            # Check if the learning_metrics table exists and has xp column
            result = await s.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'learning_metrics' AND column_name = 'xp'
            """))
            
            if not result.fetchone():
                print("  📊 Adding 'xp' column to learning_metrics table...")
                await s.execute(text("""
                    ALTER TABLE learning_metrics 
                    ADD COLUMN IF NOT EXISTS xp INTEGER DEFAULT 0
                """))
                await s.commit()
                print("  ✅ Added 'xp' column to learning_metrics")
            else:
                print("  ✅ 'xp' column already exists in learning_metrics")
            
            # Also check agent_learning_metrics table
            result = await s.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'agent_learning_metrics' AND column_name = 'xp'
            """))
            
            if not result.fetchone():
                print("  📊 Adding 'xp' column to agent_learning_metrics table...")
                await s.execute(text("""
                    ALTER TABLE agent_learning_metrics 
                    ADD COLUMN IF NOT EXISTS xp INTEGER DEFAULT 0
                """))
                await s.commit()
                print("  ✅ Added 'xp' column to agent_learning_metrics")
            else:
                print("  ✅ 'xp' column already exists in agent_learning_metrics")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error fixing learning cycle: {str(e)}")
        return False

async def implement_agnostic_test_method():
    """Implement the agnostic test generation method"""
    try:
        print("\n🧠 Implementing Agnostic Test Method...")
        
        # Read the custody protocol service file
        service_path = "/home/ubuntu/ai-backend-python/app/services/custody_protocol_service.py"
        
        if not os.path.exists(service_path):
            print(f"  ❌ Service file not found: {service_path}")
            return False
        
        with open(service_path, 'r') as f:
            content = f.read()
        
        # Check if agnostic method already exists
        if '_generate_agnostic_test' in content:
            print("  ✅ Agnostic test method already exists")
            return True
        
        # Add the agnostic test method
        agnostic_method = '''
    async def _generate_agnostic_test(self, ai_type: str, difficulty: int, category: TestCategory) -> dict:
        """Generate tests based on AI learning without requiring live AI tokens"""
        try:
            print(f"🎯 Generating agnostic test for {ai_type} (difficulty: {difficulty}, category: {category})")
            
            # Scan AI learning to understand what they've learned
            learning_data = await self._scan_ai_learning(ai_type)
            
            # Generate test based on learning patterns
            test_questions = []
            
            # Knowledge verification questions based on learned subjects
            subjects_learned = learning_data.get("subjects_learned", [])
            if subjects_learned:
                for subject in subjects_learned[:3]:  # Take first 3 subjects
                    question = {
                        "question": f"What have you learned about {subject}?",
                        "type": "knowledge_verification",
                        "difficulty": difficulty,
                        "expected_answer": f"Knowledge about {subject}",
                        "points": difficulty * 10
                    }
                    test_questions.append(question)
            
            # Application questions based on knowledge gaps
            knowledge_gaps = learning_data.get("knowledge_gaps", [])
            if knowledge_gaps:
                for gap in knowledge_gaps[:2]:  # Take first 2 gaps
                    question = {
                        "question": f"How would you approach learning about {gap}?",
                        "type": "application",
                        "difficulty": difficulty,
                        "expected_answer": f"Learning strategy for {gap}",
                        "points": difficulty * 15
                    }
                    test_questions.append(question)
            
            # If no learning data, generate generic questions
            if not test_questions:
                generic_questions = [
                    {
                        "question": "What is your primary function and how do you execute it?",
                        "type": "knowledge_verification",
                        "difficulty": difficulty,
                        "expected_answer": "AI function description",
                        "points": difficulty * 10
                    },
                    {
                        "question": "How do you handle errors and improve from failures?",
                        "type": "application",
                        "difficulty": difficulty,
                        "expected_answer": "Error handling and learning process",
                        "points": difficulty * 15
                    }
                ]
                test_questions = generic_questions
            
            return {
                "test_type": "agnostic_learning_based",
                "ai_type": ai_type,
                "difficulty": difficulty,
                "category": category.value,
                "questions": test_questions,
                "total_points": sum(q["points"] for q in test_questions),
                "time_limit": 300,  # 5 minutes
                "generated_from": "ai_learning_scan"
            }
            
        except Exception as e:
            print(f"❌ Error generating agnostic test: {str(e)}")
            # Fallback to basic test
            return {
                "test_type": "agnostic_fallback",
                "ai_type": ai_type,
                "difficulty": difficulty,
                "category": category.value,
                "questions": [
                    {
                        "question": "Describe your core capabilities and limitations.",
                        "type": "knowledge_verification",
                        "difficulty": difficulty,
                        "expected_answer": "AI capability description",
                        "points": difficulty * 10
                    }
                ],
                "total_points": difficulty * 10,
                "time_limit": 300,
                "generated_from": "fallback"
            }
    
    async def _scan_ai_learning(self, ai_type: str) -> dict:
        """Scan AI learning patterns and knowledge"""
        try:
            # Get learning history from database
            session = get_session()
            async with session as s:
                result = await s.execute(text("""
                    SELECT learning_history, subjects_learned, knowledge_gaps
                    FROM agent_learning_metrics 
                    WHERE agent_type = :ai_type
                """), {"ai_type": ai_type})
                
                record = result.fetchone()
                if record:
                    return {
                        "subjects_learned": record[0] or [],
                        "knowledge_gaps": record[1] or [],
                        "learning_history": record[2] or []
                    }
                else:
                    return {
                        "subjects_learned": [],
                        "knowledge_gaps": [],
                        "learning_history": []
                    }
                    
        except Exception as e:
            print(f"❌ Error scanning AI learning: {str(e)}")
            return {
                "subjects_learned": [],
                "knowledge_gaps": [],
                "learning_history": []
            }
'''
        
        # Find the right place to insert the method (after existing methods)
        if 'async def _generate_custody_test' in content:
            # Insert after the existing test generation method
            insert_point = content.find('async def _generate_custody_test')
            end_method = content.find('\n    async def', insert_point + 1)
            if end_method == -1:
                end_method = content.find('\nclass', insert_point + 1)
            
            if end_method != -1:
                new_content = content[:end_method] + agnostic_method + content[end_method:]
                
                with open(service_path, 'w') as f:
                    f.write(new_content)
                
                print("  ✅ Agnostic test method implemented")
                return True
            else:
                print("  ❌ Could not find insertion point")
                return False
        else:
            print("  ❌ Could not find existing test generation method")
            return False
            
    except Exception as e:
        print(f"  ❌ Error implementing agnostic method: {str(e)}")
        return False

async def start_backend_service():
    """Start the backend service on port 8000"""
    try:
        print("\n🚀 Starting Backend Service on Port 8000...")
        
        # Check if service is already running
        result = subprocess.run(['pgrep', '-f', 'main.py'], capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✅ Backend service already running")
            return True
        
        # Start the service
        print("  🔧 Starting backend service...")
        subprocess.Popen([
            '/home/ubuntu/ai-backend-python/venv/bin/python',
            '/home/ubuntu/ai-backend-python/app/main.py'
        ], cwd='/home/ubuntu/ai-backend-python')
        
        # Wait for service to start
        print("  ⏳ Waiting for service to start...")
        time.sleep(5)
        
        # Check if service is now running
        result = subprocess.run(['pgrep', '-f', 'main.py'], capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✅ Backend service started successfully")
            return True
        else:
            print("  ❌ Failed to start backend service")
            return False
            
    except Exception as e:
        print(f"  ❌ Error starting backend service: {str(e)}")
        return False

async def test_agnostic_logic():
    """Test the agnostic logic implementation"""
    try:
        print("\n🧪 Testing Agnostic Logic...")
        
        from app.services.custody_protocol_service import CustodyProtocolService
        from app.services.custody_protocol_service import TestCategory
        
        service = await CustodyProtocolService.initialize()
        
        # Test agnostic test generation
        if hasattr(service, '_generate_agnostic_test'):
            print("  🎯 Testing agnostic test generation...")
            agnostic_test = await service._generate_agnostic_test(
                ai_type="imperium",
                difficulty=1,
                category=TestCategory.KNOWLEDGE_VERIFICATION
            )
            
            print(f"    ✅ Agnostic test generated: {agnostic_test.get('test_type')}")
            print(f"    📝 Questions: {len(agnostic_test.get('questions', []))}")
            print(f"    🎯 Generated from: {agnostic_test.get('generated_from')}")
            
            # Test knowledge gap scanning
            if hasattr(service, '_scan_ai_learning'):
                print("  🔍 Testing knowledge gap scanning...")
                learning_data = await service._scan_ai_learning("imperium")
                print(f"    📚 Subjects learned: {len(learning_data.get('subjects_learned', []))}")
                print(f"    🕳️ Knowledge gaps: {len(learning_data.get('knowledge_gaps', []))}")
            
            return True
        else:
            print("  ❌ Agnostic test method not found")
            return False
            
    except Exception as e:
        print(f"  ❌ Error testing agnostic logic: {str(e)}")
        return False

async def verify_learning_cycle_fix():
    """Verify that learning cycles are working without 'xp' errors"""
    try:
        print("\n🔄 Verifying Learning Cycle Fix...")
        
        # Check if learning cycles are running without errors
        result = subprocess.run(['journalctl', '-u', 'ultimate_start', '--since', '5 minutes ago', '-n', '50'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            logs = result.stdout
            xp_errors = logs.count("'AgentLearningMetrics' object has no attribute 'xp'")
            
            if xp_errors == 0:
                print("  ✅ No 'xp' attribute errors in recent logs")
                return True
            else:
                print(f"  ⚠️ Found {xp_errors} 'xp' attribute errors in recent logs")
                return False
        else:
            print("  ⚠️ Could not check logs")
            return False
            
    except Exception as e:
        print(f"  ❌ Error verifying learning cycle fix: {str(e)}")
        return False

async def main():
    """Main fix function"""
    print("🔧 Fixing Learning Cycle and Implementing Agnostic Logic")
    print("=" * 80)
    
    # Fix learning cycle 'xp' error
    learning_fixed = await fix_learning_cycle_xp_error()
    
    # Implement agnostic test method
    agnostic_implemented = await implement_agnostic_test_method()
    
    # Start backend service
    service_started = await start_backend_service()
    
    # Test agnostic logic
    agnostic_tested = await test_agnostic_logic()
    
    # Verify learning cycle fix
    learning_verified = await verify_learning_cycle_fix()
    
    # Summary
    print("\n" + "=" * 80)
    print("🎉 FIX SUMMARY")
    print("=" * 80)
    
    print(f"📊 Results:")
    print(f"   Learning Cycle 'xp' Error: {'✅ FIXED' if learning_fixed else '❌ FAILED'}")
    print(f"   Agnostic Test Method: {'✅ IMPLEMENTED' if agnostic_implemented else '❌ FAILED'}")
    print(f"   Backend Service: {'✅ STARTED' if service_started else '❌ FAILED'}")
    print(f"   Agnostic Logic Test: {'✅ WORKING' if agnostic_tested else '❌ FAILED'}")
    print(f"   Learning Cycle Verification: {'✅ VERIFIED' if learning_verified else '❌ FAILED'}")
    
    if all([learning_fixed, agnostic_implemented, service_started, agnostic_tested, learning_verified]):
        print(f"\n🎉 ALL ISSUES RESOLVED!")
        print(f"   • Learning cycles should now work without 'xp' errors")
        print(f"   • Agnostic test generation is available when tokens are limited")
        print(f"   • Backend service is running on port 8000")
        print(f"   • Knowledge gap scanning is functional")
    else:
        print(f"\n⚠️ SOME ISSUES REMAIN - Check individual results above")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 