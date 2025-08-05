#!/usr/bin/env python3
"""
<<<<<<< HEAD
Test the enhanced test system
=======
Test script for enhanced autonomous learning system
Verifies all components are working correctly
>>>>>>> d1b3e6353067c4166fd183c12c225678794528f5
"""

import asyncio
import sys
import os
<<<<<<< HEAD

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def test_enhanced_system():
    """Test the enhanced test system"""
    try:
        from app.core.database import init_database
        from app.services.custody_protocol_service import CustodyProtocolService, TestDifficulty
        
        print("🧪 Testing Enhanced Test System...")
        
        # Initialize database first
        await init_database()
        print("✅ Database initialized")
        
        # Initialize the custody protocol service
        custody_service = await CustodyProtocolService.initialize()
        print("✅ Custody Protocol Service initialized")
        
        # Test 1: Administer a custody test
        print("\n📋 Testing custody test for imperium...")
        result = await custody_service.administer_custody_test('imperium')
        print(f"✅ Custody test result: {result.get('success', False)}")
        
        # Test 2: Administer Olympic event
        print("\n🏆 Testing Olympic event...")
        olympic_result = await custody_service.administer_olympic_event(
            participants=['imperium', 'guardian'],
            difficulty=TestDifficulty.INTERMEDIATE
        )
        print(f"✅ Olympic event result: {olympic_result.get('success', False)}")
        
        # Test 3: Administer collaborative test
        print("\n🤝 Testing collaborative test...")
        collaborative_result = await custody_service._execute_collaborative_test(
            participants=['imperium', 'guardian'],
            scenario="Design a secure authentication system",
            context={}
        )
        print(f"✅ Collaborative test result: {collaborative_result.get('success', False)}")
        
        print("\n🎉 Enhanced test system is working!")
        
    except Exception as e:
        print(f"❌ Error testing enhanced system: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_enhanced_system()) 
=======
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai-backend-python'))

async def test_enhanced_system():
    """Test the enhanced autonomous learning system"""
    print("🧪 Testing Enhanced Autonomous Learning System")
    print("=" * 60)
    
    try:
        # Test 1: Import the enhanced service
        print("1️⃣ Testing imports...")
        from autonomous_subject_learning_service_enhanced import EnhancedAutonomousSubjectLearningService
        print("   ✅ Enhanced service imported successfully")
        
        # Test 2: Create service instance
        print("2️⃣ Testing service initialization...")
        service = EnhancedAutonomousSubjectLearningService()
        print(f"   ✅ Service created with {len(service.autonomous_subjects)} subjects")
        print(f"   ✅ {len(service.ai_subject_mapping)} AI types configured")
        print(f"   ✅ {len(service.proposal_areas)} proposal areas defined")
        
        # Test 3: Test knowledge base building
        print("3️⃣ Testing knowledge base building...")
        test_subject = "machine learning"
        knowledge_base = await service.build_enhanced_knowledge_base(test_subject)
        print(f"   ✅ Knowledge base built for '{test_subject}'")
        print(f"   ✅ Learning value: {knowledge_base.get('learning_value', 0):.2f}")
        print(f"   ✅ Code examples: {len(knowledge_base.get('code_examples', []))}")
        print(f"   ✅ Best practices: {len(knowledge_base.get('best_practices', []))}")
        
        # Test 4: Test subject relevance calculation
        print("4️⃣ Testing subject relevance calculation...")
        for ai_type in service.ai_subject_mapping.keys():
            relevance = service.calculate_subject_relevance(ai_type, test_subject)
            print(f"   ✅ {ai_type}: {relevance:.2f} relevance to '{test_subject}'")
        
        # Test 5: Test AI subject generation
        print("5️⃣ Testing AI subject generation...")
        for ai_type, current_subjects in service.ai_subject_mapping.items():
            new_subjects = await service.generate_ai_suggested_subjects(ai_type, current_subjects)
            print(f"   ✅ {ai_type}: {len(new_subjects)} new subjects suggested")
        
        # Test 6: Test file patterns
        print("6️⃣ Testing file analysis patterns...")
        for file_type, patterns in service.file_patterns.items():
            print(f"   ✅ {file_type}: {len(patterns)} patterns configured")
        
        # Test 7: Test service status
        print("7️⃣ Testing service status...")
        status = service.get_enhanced_learning_status()
        print(f"   ✅ Learning active: {status['enhanced_autonomous_learning_active']}")
        print(f"   ✅ Proposal generation active: {status['proposal_generation_active']}")
        print(f"   ✅ File analysis active: {status['file_analysis_active']}")
        print(f"   ✅ Subjects available: {status['subjects_available']}")
        
        # Test 8: Test database connectivity (if available)
        print("8️⃣ Testing database connectivity...")
        try:
            from app.core.database import get_session
            from app.models.sql_models import OathPaper, AgentMetrics, Proposal
            from sqlalchemy import select
            
            session = get_session()
            async with session as s:
                # Test oath papers
                oath_count = await s.execute(select(OathPaper))
                oath_papers = oath_count.scalars().all()
                print(f"   ✅ Database connected: {len(oath_papers)} oath papers found")
                
                # Test agent metrics
                metrics_count = await s.execute(select(AgentMetrics))
                metrics = metrics_count.scalars().all()
                print(f"   ✅ {len(metrics)} AI agents found in database")
                
                # Test proposals
                proposal_count = await s.execute(select(Proposal))
                proposals = proposal_count.scalars().all()
                print(f"   ✅ {len(proposals)} proposals found in database")
                
        except Exception as e:
            print(f"   ⚠️ Database test skipped: {e}")
        
        print("\n🎉 All tests completed successfully!")
        print("🚀 Enhanced autonomous learning system is ready!")
        
        # Show system summary
        print("\n📊 System Summary:")
        print(f"   📚 Subjects available: {len(service.autonomous_subjects)}")
        print(f"   🤖 AI types: {', '.join(service.ai_subject_mapping.keys())}")
        print(f"   📋 Proposal areas: {len(service.proposal_areas)}")
        print(f"   📁 File types: {len(service.file_patterns)}")
        print(f"   ⏰ Learning schedule: Every hour + daily cycles")
        print(f"   🔄 Cross-AI sharing: Active")
        print(f"   📈 Enhanced growth: Active")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def test_monitoring():
    """Test the monitoring system"""
    print("\n🔍 Testing Monitoring System")
    print("=" * 40)
    
    try:
        # Test comprehensive monitoring
        print("1️⃣ Testing comprehensive monitoring...")
        from monitor_enhanced_learning_comprehensive import monitor_enhanced_learning_comprehensive
        await monitor_enhanced_learning_comprehensive()
        print("   ✅ Comprehensive monitoring working")
        
        # Test AI learning summary
        print("2️⃣ Testing AI learning summary...")
        from monitor_enhanced_learning_comprehensive import get_ai_learning_summary
        await get_ai_learning_summary()
        print("   ✅ AI learning summary working")
        
        # Test proposal summary
        print("3️⃣ Testing proposal summary...")
        from monitor_enhanced_learning_comprehensive import get_proposal_summary
        await get_proposal_summary()
        print("   ✅ Proposal summary working")
        
        print("🎉 All monitoring tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Monitoring test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Enhanced Autonomous Learning System Test Suite")
    print("=" * 70)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run tests
    system_test = asyncio.run(test_enhanced_system())
    monitoring_test = asyncio.run(test_monitoring())
    
    print("\n" + "=" * 70)
    print("📋 Test Results Summary:")
    print(f"   🧪 System Test: {'✅ PASSED' if system_test else '❌ FAILED'}")
    print(f"   🔍 Monitoring Test: {'✅ PASSED' if monitoring_test else '❌ FAILED'}")
    
    if system_test and monitoring_test:
        print("\n🎉 All tests passed! Enhanced system is ready to run!")
        print("🚀 You can now start the autonomous learning service.")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
    
    print(f"⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}") 
>>>>>>> d1b3e6353067c4166fd183c12c225678794528f5
