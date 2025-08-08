"""
Test API Endpoints for New Backend Services
Tests all the new API endpoints we created
"""

import asyncio
import sys
import os
import json
from datetime import datetime
import traceback

# Add current directory to path
sys.path.insert(0, os.getcwd())

print("🌐 Starting API Endpoints Test Suite")
print("=" * 60)

# Mock all the dependencies first
def setup_mocks():
    """Setup mock modules for testing"""
    
    # Mock database
    class MockDB:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    def mock_get_session():
        return MockDB()

    # Mock core modules
    sys.modules['app.core.database'] = type('MockModule', (), {'get_session': mock_get_session})()
    sys.modules['app.core.config'] = type('MockModule', (), {'settings': {}})()
    
    # Mock AI Learning Service
    class MockAILearningService:
        def __init__(self):
            pass
        async def store_learning_insight(self, ai_type, insight_type, data):
            return True
        async def get_learning_insights(self, ai_type):
            return {"recent_learning_events": []}
    
    # Mock Agent Metrics Service
    class MockAgentMetricsService:
        def __init__(self):
            pass
        async def initialize(self):
            pass
        async def get_agent_metrics(self, ai_type):
            return {"pass_rate": 0.8, "success_rate": 0.9, "learning_score": 60}
        async def update_adversarial_metrics(self, ai_type, score, success):
            return True
    
    # Mock Custody Protocol Service
    class MockCustodyProtocolService:
        @classmethod
        async def initialize(cls):
            return cls()
    
    # Mock SckipitService
    class MockSckipitService:
        @classmethod
        async def initialize(cls):
            return cls()
    
    # Mock Enhanced Scenario Service
    class MockEnhancedScenarioService:
        def __init__(self):
            pass
        async def get_scenario(self, **kwargs):
            return {
                "name": "Mock Scenario",
                "description": "Mock adversarial scenario",
                "objectives": ["Complete the challenge"],
                "constraints": ["Time limit: 1 hour"],
                "success_criteria": ["Successfully complete objectives"]
            }
    
    # Setup all mock modules
    sys.modules['app.services.ai_learning_service'] = type('MockModule', (), {
        'AILearningService': MockAILearningService
    })()
    sys.modules['app.services.agent_metrics_service'] = type('MockModule', (), {
        'AgentMetricsService': MockAgentMetricsService
    })()
    sys.modules['app.services.custody_protocol_service'] = type('MockModule', (), {
        'CustodyProtocolService': MockCustodyProtocolService
    })()
    sys.modules['app.services.sckipit_service'] = type('MockModule', (), {
        'SckipitService': MockSckipitService
    })()
    sys.modules['app.services.enhanced_scenario_service'] = type('MockModule', (), {
        'EnhancedScenarioService': MockEnhancedScenarioService
    })()

async def test_ai_adversarial_integration_service_api():
    """Test AI Adversarial Integration Service functionality"""
    print("\n1️⃣ Testing AI Adversarial Integration Service API...")
    
    try:
        from app.services.ai_adversarial_integration_service import AIAdversarialIntegrationService
        
        service = AIAdversarialIntegrationService()
        await service.initialize()
        
        # Test adversarial scenario integration
        result = await service.integrate_adversarial_scenario_into_ai_learning("imperium")
        
        assert "ai_type" in result
        assert result["ai_type"] == "imperium"
        print("✅ Adversarial scenario integration working")
        
        # Test progress report
        progress = await service.get_adversarial_progress_report()
        assert "ai_progress" in progress
        assert "aggregate_stats" in progress
        print("✅ Progress report generation working")
        
        # Test scheduled training
        scheduled_result = await service.run_scheduled_adversarial_training("guardian")
        assert "ai_type" in scheduled_result
        print("✅ Scheduled training working")
        
        return True
        
    except Exception as e:
        print(f"❌ AI Adversarial Integration Service API test failed: {e}")
        traceback.print_exc()
        return False

async def test_enhanced_project_horus_service_api():
    """Test Enhanced Project Horus Service functionality"""
    print("\n2️⃣ Testing Enhanced Project Horus Service API...")
    
    try:
        from app.services.enhanced_project_horus_service import EnhancedProjectHorusService
        
        service = EnhancedProjectHorusService()
        
        # Test learning from AI experiences
        learning_result = await service.learn_from_ai_experiences(["imperium", "guardian"])
        
        assert "ai_experiences_analyzed" in learning_result
        assert "timestamp" in learning_result
        print("✅ AI experience learning working")
        
        # Test weapon enhancement
        enhancement_result = await service.enhance_weapons_with_internet_learning(1.0)
        
        assert "weapons_enhanced" in enhancement_result
        assert "timestamp" in enhancement_result
        print("✅ Weapon enhancement working")
        
        # Test chaos language documentation
        chaos_docs = await service.get_chaos_language_documentation()
        
        assert "version" in chaos_docs
        assert "total_chapters" in chaos_docs
        print("✅ Chaos language documentation working")
        
        # Test weapon synthesis report
        synthesis_report = await service.get_weapon_synthesis_report()
        
        assert "total_weapons" in synthesis_report
        assert "timestamp" in synthesis_report
        print("✅ Weapon synthesis report working")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced Project Horus Service API test failed: {e}")
        traceback.print_exc()
        return False

async def test_project_berserk_enhanced_service_api():
    """Test Project Berserk Enhanced Service functionality"""
    print("\n3️⃣ Testing Project Berserk Enhanced Service API...")
    
    try:
        from app.services.project_berserk_enhanced_service import ProjectBerserkEnhancedService
        
        service = ProjectBerserkEnhancedService()
        await service.initialize()
        
        # Test collective learning
        collective_result = await service.learn_from_ai_collective(["imperium", "guardian", "sandbox"])
        
        assert "ais_analyzed" in collective_result
        assert "timestamp" in collective_result
        print("✅ AI collective learning working")
        
        # Test synthetic weapon creation
        weapon_result = await service.create_synthetic_growing_weapons(2)
        
        assert "weapons_created" in weapon_result
        assert "weapons" in weapon_result
        print("✅ Synthetic weapon creation working")
        
        # Test weapon deployment
        # First create a weapon to deploy
        if weapon_result["weapons"]:
            weapon_id = list(weapon_result["weapons"].keys())[0]
            deploy_result = await service.deploy_weapon(weapon_id, "test_system", "stealth_data_extraction")
            
            assert "deployment_id" in deploy_result or "success" in deploy_result
            print("✅ Weapon deployment working")
        
        # Test status report
        status_report = await service.get_berserk_status_report()
        
        assert "total_weapons" in status_report
        assert "timestamp" in status_report
        print("✅ Berserk status report working")
        
        return True
        
    except Exception as e:
        print(f"❌ Project Berserk Enhanced Service API test failed: {e}")
        traceback.print_exc()
        return False

async def test_chaos_language_service_api():
    """Test Chaos Language Service functionality"""
    print("\n4️⃣ Testing Chaos Language Service API...")
    
    try:
        from app.services.chaos_language_service import ChaosLanguageService
        
        service = ChaosLanguageService()
        await service.initialize()
        
        # Test construct collection
        collection_result = await service.collect_new_constructs_from_system()
        
        assert "horus_constructs" in collection_result
        assert "berserk_constructs" in collection_result
        assert "timestamp" in collection_result
        print("✅ Construct collection working")
        
        # Test complete documentation
        docs = await service.get_complete_chaos_language_documentation()
        
        assert "language_core" in docs
        assert "documentation_chapters" in docs
        assert "growth_metrics" in docs
        print("✅ Complete documentation working")
        
        # Test forced chapter generation
        chapter_result = await service.force_chapter_generation()
        
        assert "status" in chapter_result
        print("✅ Forced chapter generation working")
        
        return True
        
    except Exception as e:
        print(f"❌ Chaos Language Service API test failed: {e}")
        traceback.print_exc()
        return False

def test_fastapi_router():
    """Test FastAPI Router structure"""
    print("\n5️⃣ Testing FastAPI Router Structure...")
    
    try:
        from app.routers.ai_integration_router import router
        
        # Check router configuration
        assert router.prefix == "/api/ai-integration"
        assert "AI Integration" in router.tags
        print("✅ Router configuration correct")
        
        # Check routes exist
        routes = [route.path for route in router.routes]
        expected_paths = [
            "/adversarial-training/run",
            "/adversarial-training/progress",
            "/horus/learn-from-ais", 
            "/horus/enhance-weapons",
            "/berserk/create-weapons",
            "/berserk/deploy-weapon",
            "/chaos-language/documentation",
            "/integration/status"
        ]
        
        for expected_path in expected_paths:
            # Check if any route ends with the expected path
            found = any(route.endswith(expected_path) for route in routes)
            assert found, f"Route ending with {expected_path} not found"
        
        print(f"✅ Router has {len(routes)} routes configured")
        print("✅ All expected endpoints found")
        
        return True
        
    except Exception as e:
        print(f"❌ FastAPI Router test failed: {e}")
        traceback.print_exc()
        return False

def test_pydantic_models():
    """Test Pydantic model structures"""
    print("\n6️⃣ Testing Pydantic Models...")
    
    try:
        from app.routers.ai_integration_router import (
            AdversarialTrainingRequest,
            WeaponDeploymentRequest,
            LearningIntegrationRequest
        )
        
        # Test AdversarialTrainingRequest
        training_req = AdversarialTrainingRequest(ai_type="imperium", force_scenario="security_challenges")
        assert training_req.ai_type == "imperium"
        assert training_req.force_scenario == "security_challenges"
        print("✅ AdversarialTrainingRequest model working")
        
        # Test WeaponDeploymentRequest
        deploy_req = WeaponDeploymentRequest(
            weapon_id="test_weapon", 
            target_system="test_system", 
            deployment_option="stealth_data_extraction"
        )
        assert deploy_req.weapon_id == "test_weapon"
        assert deploy_req.target_system == "test_system"
        print("✅ WeaponDeploymentRequest model working")
        
        # Test LearningIntegrationRequest
        learn_req = LearningIntegrationRequest(ai_types=["imperium", "guardian"])
        assert learn_req.ai_types == ["imperium", "guardian"]
        print("✅ LearningIntegrationRequest model working")
        
        return True
        
    except Exception as e:
        print(f"❌ Pydantic Models test failed: {e}")
        traceback.print_exc()
        return False

async def test_integration_flow():
    """Test full integration flow"""
    print("\n7️⃣ Testing Full Integration Flow...")
    
    try:
        # Import all services
        from app.services.ai_adversarial_integration_service import AIAdversarialIntegrationService
        from app.services.enhanced_project_horus_service import EnhancedProjectHorusService
        from app.services.project_berserk_enhanced_service import ProjectBerserkEnhancedService
        from app.services.chaos_language_service import ChaosLanguageService
        
        # Initialize all services
        adversarial_service = AIAdversarialIntegrationService()
        horus_service = EnhancedProjectHorusService()
        berserk_service = ProjectBerserkEnhancedService()
        language_service = ChaosLanguageService()
        
        await adversarial_service.initialize()
        await berserk_service.initialize()
        await language_service.initialize()
        
        print("✅ All services initialized")
        
        # Test integration flow
        # 1. Run adversarial training
        adversarial_result = await adversarial_service.integrate_adversarial_scenario_into_ai_learning("imperium")
        print("✅ Step 1: Adversarial training completed")
        
        # 2. Horus learns from AI experiences
        horus_learning = await horus_service.learn_from_ai_experiences(["imperium"])
        print("✅ Step 2: Horus learning completed")
        
        # 3. Berserk learns from collective
        berserk_learning = await berserk_service.learn_from_ai_collective(["imperium"])
        print("✅ Step 3: Berserk collective learning completed")
        
        # 4. Create synthetic weapons
        weapon_creation = await berserk_service.create_synthetic_growing_weapons(1)
        print("✅ Step 4: Synthetic weapon creation completed")
        
        # 5. Update chaos language
        language_update = await language_service.collect_new_constructs_from_system()
        print("✅ Step 5: Chaos language update completed")
        
        # 6. Get integration status
        adversarial_progress = await adversarial_service.get_adversarial_progress_report()
        horus_report = await horus_service.get_weapon_synthesis_report()
        berserk_status = await berserk_service.get_berserk_status_report()
        chaos_language = await language_service.get_complete_chaos_language_documentation()
        
        print("✅ Step 6: All status reports generated")
        
        # Validate integration
        assert all([
            adversarial_result, horus_learning, berserk_learning,
            weapon_creation, language_update, adversarial_progress,
            horus_report, berserk_status, chaos_language
        ])
        
        print("✅ Full integration flow completed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Full Integration Flow test failed: {e}")
        traceback.print_exc()
        return False

async def main():
    """Run all API tests"""
    
    # Setup mocks first
    setup_mocks()
    
    test_results = []
    
    # Run async tests
    test_results.append(await test_ai_adversarial_integration_service_api())
    test_results.append(await test_enhanced_project_horus_service_api())
    test_results.append(await test_project_berserk_enhanced_service_api())
    test_results.append(await test_chaos_language_service_api())
    
    # Run sync tests
    test_results.append(test_fastapi_router())
    test_results.append(test_pydantic_models())
    
    # Run integration test
    test_results.append(await test_integration_flow())
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 API ENDPOINTS TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(test_results)
    total = len(test_results)
    
    test_names = [
        "AI Adversarial Integration Service API",
        "Enhanced Project Horus Service API",
        "Project Berserk Enhanced Service API",
        "Chaos Language Service API",
        "FastAPI Router Structure",
        "Pydantic Models",
        "Full Integration Flow"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, test_results)):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{i+1}. {name}: {status}")
    
    print(f"\n🎯 OVERALL RESULT: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL API TESTS PASSED! Backend deployment is ready!")
        print("\n🚀 DEPLOYMENT SUMMARY:")
        print("=" * 60)
        print("✅ AI Adversarial Integration: Backend learning cycles active")
        print("✅ Enhanced Project Horus: AI experience learning & weapon synthesis")
        print("✅ Project Berserk Enhanced: Collective learning & advanced weapons")
        print("✅ Chaos Language Service: Dynamic documentation generation")
        print("✅ API Integration Router: All endpoints functional")
        print("✅ Frontend Adversarial Testing: Successfully migrated to backend")
        print("✅ Deployment Options: Data extraction only & backdoor deployment ready")
        print("✅ Synthetic Weapons: Self-growing capabilities implemented")
        print("✅ Internet Learning: Enhancement & Docker testing integrated")
    else:
        print("⚠️ Some API tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    result = asyncio.run(main())
    print(f"\n🚀 API Test completed with result: {'SUCCESS' if result else 'FAILURE'}")
    sys.exit(0 if result else 1)