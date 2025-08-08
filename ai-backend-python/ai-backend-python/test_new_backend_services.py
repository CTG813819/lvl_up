"""
Test script for new backend services
Tests all functionality without database dependencies
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.getcwd())

# Mock database and external dependencies
class MockDB:
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

def mock_get_session():
    return MockDB()

# Patch imports
sys.modules['app.core.database'] = type('MockModule', (), {'get_session': mock_get_session})()
sys.modules['app.core.config'] = type('MockModule', (), {'settings': {}})()
sys.modules['app.services.custody_protocol_service'] = type('MockModule', (), {
    'CustodyProtocolService': type('MockClass', (), {
        'initialize': lambda: asyncio.create_task(asyncio.sleep(0))
    })()
})()
sys.modules['app.services.ai_learning_service'] = type('MockModule', (), {
    'AILearningService': type('MockClass', (), {
        '__init__': lambda self: None,
        'get_learning_insights': lambda self, ai_type: asyncio.create_task(asyncio.sleep(0)),
        'store_learning_insight': lambda self, ai_type, insight_type, data: asyncio.create_task(asyncio.sleep(0))
    })()
})()
sys.modules['app.services.sckipit_service'] = type('MockModule', (), {
    'SckipitService': type('MockClass', (), {
        'initialize': lambda: asyncio.create_task(asyncio.sleep(0))
    })()
})()
sys.modules['app.services.agent_metrics_service'] = type('MockModule', (), {
    'AgentMetricsService': type('MockClass', (), {
        '__init__': lambda self: None,
        'initialize': lambda self: asyncio.create_task(asyncio.sleep(0)),
        'get_agent_metrics': lambda self, ai_type: asyncio.create_task(asyncio.sleep(0)),
        'update_adversarial_metrics': lambda self, ai_type, score, success: asyncio.create_task(asyncio.sleep(0))
    })()
})()
sys.modules['app.services.enhanced_scenario_service'] = type('MockModule', (), {
    'EnhancedScenarioService': type('MockClass', (), {
        '__init__': lambda self: None,
        'get_scenario': lambda self, **kwargs: asyncio.create_task(asyncio.sleep(0))
    })()
})()

async def test_ai_adversarial_integration_service():
    """Test AI Adversarial Integration Service"""
    print("\n🧪 Testing AI Adversarial Integration Service...")
    
    try:
        from app.services.ai_adversarial_integration_service import AIAdversarialIntegrationService
        
        service = AIAdversarialIntegrationService()
        print("✅ Service instantiated successfully")
        
        # Test AI progress initialization
        assert "imperium" in service.ai_adversarial_progress
        assert "guardian" in service.ai_adversarial_progress
        assert "sandbox" in service.ai_adversarial_progress
        assert "conquest" in service.ai_adversarial_progress
        print("✅ AI progress tracking initialized")
        
        # Test scenario rotation
        assert len(service.scenario_rotation) == 6
        print("✅ Scenario rotation configured")
        
        # Test schedule configuration
        assert all(ai in service.schedule_config for ai in ["imperium", "guardian", "sandbox", "conquest"])
        print("✅ Schedule configuration set")
        
        # Test complexity determination
        progress = {"level": 3, "victories": 15, "defeats": 5}
        complexity = service._determine_scenario_complexity("test_ai", progress)
        print(f"✅ Complexity determination working: {complexity}")
        
        # Test AI capability scoring
        capability = service._get_ai_capability_score("imperium")
        print(f"✅ AI capability scoring working: {capability}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI Adversarial Integration Service test failed: {e}")
        return False

async def test_enhanced_project_horus_service():
    """Test Enhanced Project Horus Service"""
    print("\n🔬 Testing Enhanced Project Horus Service...")
    
    try:
        from app.services.enhanced_project_horus_service import EnhancedProjectHorusService
        
        service = EnhancedProjectHorusService()
        print("✅ Service instantiated successfully")
        
        # Test weapon categories
        assert len(service.weapon_categories) == 5
        print("✅ Weapon categories configured")
        
        # Test chaos language initialization
        assert isinstance(service.chaos_language_chapters, list)
        assert isinstance(service.chaos_language_version, str)
        print("✅ Chaos language system initialized")
        
        # Test AI learning data structure
        assert isinstance(service.ai_learning_data, dict)
        print("✅ AI learning data structure ready")
        
        # Test weapon pattern analysis
        mock_progress = {
            "progress": {"victories": 12, "level": 4},
            "shared_knowledge": [
                {"domain": "security_challenges", "success": True, "lessons": ["test_lesson"]}
            ]
        }
        patterns = await service._analyze_for_weapon_patterns("imperium", mock_progress)
        print(f"✅ Weapon pattern analysis working: {len(patterns)} patterns found")
        
        # Test chaos language updates
        updates = await service._update_chaos_language_from_ai("imperium", mock_progress)
        print(f"✅ Chaos language updates working: {len(updates)} updates")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced Project Horus Service test failed: {e}")
        return False

async def test_project_berserk_enhanced_service():
    """Test Project Berserk Enhanced Service"""
    print("\n⚔️ Testing Project Berserk Enhanced Service...")
    
    try:
        from app.services.project_berserk_enhanced_service import ProjectBerserkEnhancedService
        
        service = ProjectBerserkEnhancedService()
        print("✅ Service instantiated successfully")
        
        # Test Berserk weapon categories
        assert len(service.berserk_weapon_categories) == 5
        assert "neural_infiltrator" in service.berserk_weapon_categories
        assert "quantum_backdoor" in service.berserk_weapon_categories
        print("✅ Berserk weapon categories configured")
        
        # Test deployment statistics
        assert "total_deployments" in service.deployment_statistics
        assert "successful_data_extractions" in service.deployment_statistics
        assert "successful_backdoor_deployments" in service.deployment_statistics
        print("✅ Deployment statistics initialized")
        
        # Test weapon arsenal
        assert isinstance(service.weapon_arsenal, dict)
        print("✅ Weapon arsenal ready")
        
        # Test combat pattern extraction
        patterns = await service._extract_ai_combat_patterns("guardian")
        print(f"✅ Combat pattern extraction working: {len(patterns)} patterns")
        
        # Test synthetic weapon creation
        weapon = await service._create_advanced_synthetic_weapon("neural_infiltrator")
        assert weapon["synthetic"] == True
        assert weapon["self_growing"] == True
        assert "chaos_code" in weapon
        print("✅ Synthetic weapon creation working")
        
        return True
        
    except Exception as e:
        print(f"❌ Project Berserk Enhanced Service test failed: {e}")
        return False

async def test_chaos_language_service():
    """Test Chaos Language Service"""
    print("\n🌀 Testing Chaos Language Service...")
    
    try:
        from app.services.chaos_language_service import ChaosLanguageService
        
        service = ChaosLanguageService()
        print("✅ Service instantiated successfully")
        
        # Test language core structure
        assert "version" in service.language_core
        assert "base_constructs" in service.language_core
        assert "ai_derived_constructs" in service.language_core
        assert "weapon_specific_constructs" in service.language_core
        print("✅ Language core structure ready")
        
        # Test base constructs initialization
        await service._initialize_base_constructs()
        assert len(service.language_core["base_constructs"]) >= 5
        assert "CHAOS.CORE.INIT" in service.language_core["base_constructs"]
        print("✅ Base constructs initialized")
        
        # Test chapter templates
        await service._initialize_chapter_templates()
        assert len(service.chapter_templates) >= 3
        print("✅ Chapter templates configured")
        
        # Test growth metrics
        assert "total_constructs" in service.growth_metrics
        assert "constructs_per_ai" in service.growth_metrics
        print("✅ Growth metrics tracking ready")
        
        # Test construct integration
        test_constructs = {
            "CHAOS.TEST.CONSTRUCT": {
                "description": "Test construct",
                "origin": "test",
                "created": datetime.utcnow().isoformat()
            }
        }
        await service._integrate_new_constructs(test_constructs)
        assert service.growth_metrics["total_constructs"] == 1
        print("✅ Construct integration working")
        
        return True
        
    except Exception as e:
        print(f"❌ Chaos Language Service test failed: {e}")
        return False

async def test_router_imports():
    """Test Router Imports"""
    print("\n🌐 Testing AI Integration Router...")
    
    try:
        from app.routers.ai_integration_router import router
        print("✅ Router imported successfully")
        
        # Check router configuration
        assert router.prefix == "/api/ai-integration"
        assert "AI Integration" in router.tags
        print("✅ Router configuration correct")
        
        # Check number of routes
        routes = [route for route in router.routes]
        print(f"✅ Router has {len(routes)} routes configured")
        
        return True
        
    except Exception as e:
        print(f"❌ AI Integration Router test failed: {e}")
        return False

async def test_service_integration():
    """Test Service Integration"""
    print("\n🔗 Testing Service Integration...")
    
    try:
        # Test that services can interact with each other
        from app.services.ai_adversarial_integration_service import AIAdversarialIntegrationService
        from app.services.enhanced_project_horus_service import EnhancedProjectHorusService
        from app.services.project_berserk_enhanced_service import ProjectBerserkEnhancedService
        from app.services.chaos_language_service import ChaosLanguageService
        
        # Create service instances
        adversarial_service = AIAdversarialIntegrationService()
        horus_service = EnhancedProjectHorusService()
        berserk_service = ProjectBerserkEnhancedService()
        language_service = ChaosLanguageService()
        
        print("✅ All services can be instantiated together")
        
        # Test cross-service data access patterns
        assert hasattr(horus_service, 'weapon_categories')
        assert hasattr(berserk_service, 'berserk_weapon_categories')
        assert hasattr(language_service, 'language_core')
        print("✅ Cross-service data structures accessible")
        
        # Test deployment option generation
        options = await berserk_service._create_advanced_deployment_options("neural_infiltrator")
        assert "stealth_data_extraction" in options
        assert "persistent_chaos_deployment" in options
        assert "hybrid_extraction_backdoor" in options
        print("✅ Deployment options generation working")
        
        return True
        
    except Exception as e:
        print(f"❌ Service Integration test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Backend Services Test Suite")
    print("=" * 60)
    
    test_results = []
    
    # Run all tests
    test_results.append(await test_ai_adversarial_integration_service())
    test_results.append(await test_enhanced_project_horus_service())
    test_results.append(await test_project_berserk_enhanced_service())
    test_results.append(await test_chaos_language_service())
    test_results.append(await test_router_imports())
    test_results.append(await test_service_integration())
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(test_results)
    total = len(test_results)
    
    test_names = [
        "AI Adversarial Integration Service",
        "Enhanced Project Horus Service", 
        "Project Berserk Enhanced Service",
        "Chaos Language Service",
        "AI Integration Router",
        "Service Integration"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, test_results)):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{i+1}. {name}: {status}")
    
    print(f"\n🎯 OVERALL RESULT: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Backend services are ready for deployment!")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)