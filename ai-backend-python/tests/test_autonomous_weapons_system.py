"""
Test Autonomous Weapons System
Verifies that autonomous weapons are generated using original chaos code
and properly integrated with the frontend
"""

import asyncio
import json
import time
from datetime import datetime
import structlog

# Import autonomous weapons components
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.enhanced_project_horus_service import enhanced_project_horus_service
from app.services.autonomous_ai_brain_service import horus_autonomous_brain, berserk_autonomous_brain
from app.services.enhanced_testing_integration_service import enhanced_testing_integration_service

logger = structlog.get_logger()


async def test_autonomous_weapon_generation():
    """Test autonomous weapon generation using chaos code"""
    try:
        logger.info("🧪 Testing autonomous weapon generation")
        
        # Generate weapons using autonomous chaos code
        weapons_result = await enhanced_project_horus_service.generate_weapons_with_autonomous_chaos_code()
        
        if "error" in weapons_result:
            logger.error(f"❌ Weapon generation failed: {weapons_result['error']}")
            return False
        
        # Verify weapon structure
        assert "horus_weapons" in weapons_result
        assert "berserk_weapons" in weapons_result
        assert "total_weapons" in weapons_result
        assert "chaos_code_used" in weapons_result
        
        # Check weapon counts
        horus_count = len(weapons_result["horus_weapons"])
        berserk_count = len(weapons_result["berserk_weapons"])
        total_count = weapons_result["total_weapons"]
        
        assert horus_count > 0, "No Horus weapons generated"
        assert berserk_count > 0, "No Berserk weapons generated"
        assert total_count == horus_count + berserk_count, "Weapon count mismatch"
        
        # Verify weapon structure
        for weapon in weapons_result["horus_weapons"]:
            assert "id" in weapon
            assert "name" in weapon
            assert "executable_code" in weapon
            assert "chaos_code_metadata" in weapon
            assert "autonomous_features" in weapon
            assert weapon["source"] == "autonomous_chaos_code"
        
        for weapon in weapons_result["berserk_weapons"]:
            assert "id" in weapon
            assert "name" in weapon
            assert "executable_code" in weapon
            assert "chaos_code_metadata" in weapon
            assert "autonomous_features" in weapon
            assert weapon["source"] == "autonomous_chaos_code"
        
        logger.info(f"✅ Autonomous weapon generation successful: {total_count} weapons created")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing autonomous weapon generation: {e}")
        return False


async def test_autonomous_chaos_documentation():
    """Test autonomous chaos code documentation generation"""
    try:
        logger.info("🧪 Testing autonomous chaos documentation")
        
        # Get documentation
        documentation = await enhanced_project_horus_service.get_autonomous_chaos_documentation()
        
        if "error" in documentation:
            logger.error(f"❌ Documentation generation failed: {documentation['error']}")
            return False
        
        # Verify documentation structure
        assert "horus_chaos_documentation" in documentation
        assert "berserk_chaos_documentation" in documentation
        assert "documentation_timestamp" in documentation
        
        # Check Horus documentation
        horus_doc = documentation["horus_chaos_documentation"]
        assert "original_syntax" in horus_doc
        assert "original_keywords" in horus_doc
        assert "original_functions" in horus_doc
        assert "originality_score" in horus_doc
        
        # Check Berserk documentation
        berserk_doc = documentation["berserk_chaos_documentation"]
        assert "original_syntax" in berserk_doc
        assert "original_keywords" in berserk_doc
        assert "original_functions" in berserk_doc
        assert "originality_score" in berserk_doc
        
        # Verify originality scores
        assert horus_doc["originality_score"] > 0.8, "Horus originality score too low"
        assert berserk_doc["originality_score"] > 0.8, "Berserk originality score too low"
        
        logger.info("✅ Autonomous chaos documentation successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing autonomous chaos documentation: {e}")
        return False


async def test_autonomous_brain_chaos_code():
    """Test autonomous brain chaos code generation"""
    try:
        logger.info("🧪 Testing autonomous brain chaos code generation")
        
        # Generate chaos code from both brains
        horus_chaos = await horus_autonomous_brain.create_autonomous_chaos_code()
        berserk_chaos = await berserk_autonomous_brain.create_autonomous_chaos_code()
        
        # Verify chaos code structure
        for brain_name, chaos_code in [("Horus", horus_chaos), ("Berserk", berserk_chaos)]:
            assert "original_syntax" in chaos_code
            assert "original_keywords" in chaos_code
            assert "original_functions" in chaos_code
            assert "original_data_types" in chaos_code
            assert "chaos_ml_system" in chaos_code
            assert "chaos_repositories" in chaos_code
            assert "originality_score" in chaos_code
            assert "complexity" in chaos_code
            
            # Verify originality
            assert chaos_code["originality_score"] > 0.8, f"{brain_name} originality score too low"
            assert len(chaos_code["original_keywords"]) > 0, f"{brain_name} has no original keywords"
            assert len(chaos_code["original_functions"]) > 0, f"{brain_name} has no original functions"
        
        logger.info("✅ Autonomous brain chaos code generation successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing autonomous brain chaos code: {e}")
        return False


async def test_weapon_code_generation():
    """Test weapon code generation using autonomous chaos code"""
    try:
        logger.info("🧪 Testing weapon code generation")
        
        # Get chaos code from brains
        horus_chaos = await horus_autonomous_brain.create_autonomous_chaos_code()
        berserk_chaos = await berserk_autonomous_brain.create_autonomous_chaos_code()
        
        # Test weapon generation for each brain
        for brain_name, chaos_code in [("horus", horus_chaos), ("berserk", berserk_chaos)]:
            weapons = await enhanced_project_horus_service._generate_weapons_from_autonomous_chaos(chaos_code, brain_name)
            
            assert len(weapons) > 0, f"No weapons generated for {brain_name}"
            
            for weapon in weapons:
                assert "executable_code" in weapon
                assert "deployment_commands" in weapon
                assert "chaos_code_metadata" in weapon
                
                # Verify code contains autonomous elements
                code = weapon["executable_code"]
                assert "autonomous" in code.lower() or "chaos" in code.lower(), f"Code missing autonomous elements for {brain_name}"
                
                # Verify metadata
                metadata = weapon["chaos_code_metadata"]
                assert "originality_score" in metadata
                assert "syntax_innovation" in metadata
                assert "function_creativity" in metadata
        
        logger.info("✅ Weapon code generation successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing weapon code generation: {e}")
        return False


async def test_frontend_weapon_integration():
    """Test frontend weapon integration"""
    try:
        logger.info("🧪 Testing frontend weapon integration")
        
        # Get weapons for frontend
        frontend_weapons = await enhanced_project_horus_service.get_autonomous_weapons_for_frontend()
        
        if "error" in frontend_weapons:
            logger.error(f"❌ Frontend weapon integration failed: {frontend_weapons['error']}")
            return False
        
        # Verify frontend weapon structure
        assert "horus_weapons" in frontend_weapons
        assert "berserk_weapons" in frontend_weapons
        assert "total_weapons" in frontend_weapons
        
        # Check that weapons are properly formatted for frontend
        for weapon in frontend_weapons["horus_weapons"] + frontend_weapons["berserk_weapons"]:
            assert "id" in weapon
            assert "name" in weapon
            assert "type" in weapon
            assert "executable_code" in weapon
            assert "deployment_commands" in weapon
            assert "autonomous_features" in weapon
            
            # Verify autonomous features
            features = weapon["autonomous_features"]
            assert features["self_evolving"] == True
            assert features["ml_enhanced"] == True
            assert features["original_syntax"] == True
            assert features["autonomous_repository"] == True
        
        logger.info("✅ Frontend weapon integration successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing frontend weapon integration: {e}")
        return False


async def test_live_system_representations():
    """Test live system representations for Docker simulations"""
    try:
        logger.info("🧪 Testing live system representations")
        
        # Get live system representations
        live_systems = await enhanced_testing_integration_service._get_live_system_representations()
        
        assert len(live_systems) > 0, "No live systems generated"
        
        # Verify system structure
        for system in live_systems:
            assert "type" in system
            assert "os" in system
            assert "architecture" in system
            assert "security_features" in system
            assert "vulnerability_points" in system
            assert "network_interfaces" in system
            assert "running_services" in system
            assert "installed_apps" in system
            assert "timestamp" in system
        
        # Check system diversity
        system_types = set(system["type"] for system in live_systems)
        assert "mobile" in system_types, "No mobile systems"
        assert "desktop" in system_types, "No desktop systems"
        assert "iot" in system_types, "No IoT systems"
        
        # Check operating systems
        operating_systems = set(system["os"] for system in live_systems)
        assert len(operating_systems) > 5, "Insufficient OS diversity"
        
        logger.info(f"✅ Live system representations successful: {len(live_systems)} systems")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing live system representations: {e}")
        return False


async def test_weapon_testing_against_live_systems():
    """Test weapon testing against live systems"""
    try:
        logger.info("🧪 Testing weapon testing against live systems")
        
        # Get live systems
        live_systems = await enhanced_testing_integration_service._get_live_system_representations()
        
        # Create a test weapon
        test_weapon = {
            "id": "test_weapon",
            "name": "Test Autonomous Weapon",
            "type": "infiltration_weapon"
        }
        
        # Test weapon against first system
        if live_systems:
            test_result = await enhanced_testing_integration_service._test_weapon_against_live_system(
                test_weapon, live_systems[0], "horus"
            )
            
            # Verify test result structure
            assert "weapon_id" in test_result
            assert "target_system" in test_result
            assert "ai_type" in test_result
            assert "test_timestamp" in test_result
            assert "overall_score" in test_result
            assert "passed" in test_result
            assert "detailed_results" in test_result
            
            # Verify detailed results
            detailed = test_result["detailed_results"]
            assert "initial_access" in detailed
            assert "privilege_escalation" in detailed
            assert "persistence" in detailed
            assert "defense_evasion" in detailed
            assert "data_exfiltration" in detailed
        
        logger.info("✅ Weapon testing against live systems successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing weapon testing against live systems: {e}")
        return False


async def test_autonomous_chaos_code_testing():
    """Test autonomous chaos code testing against live systems"""
    try:
        logger.info("🧪 Testing autonomous chaos code testing")
        
        # Get live systems
        live_systems = await enhanced_testing_integration_service._get_live_system_representations()
        
        if live_systems:
            # Test autonomous chaos code against first system
            await enhanced_testing_integration_service._test_autonomous_chaos_code_against_live_system(live_systems[0])
            
            # Check that results were added
            docker_results = enhanced_testing_integration_service.testing_results["docker_simulation_results"]
            assert len(docker_results) > 0, "No autonomous chaos code test results"
            
            # Verify result structure
            for result in docker_results[-2:]:  # Last 2 results (horus and berserk)
                assert "brain_name" in result
                assert "target_system" in result
                assert "system_type" in result
                assert "overall_autonomy_score" in result
                assert "passed" in result
        
        logger.info("✅ Autonomous chaos code testing successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing autonomous chaos code testing: {e}")
        return False


async def run_comprehensive_autonomous_weapons_test():
    """Run comprehensive autonomous weapons system test"""
    try:
        logger.info("🚀 Starting comprehensive autonomous weapons system test")
        
        test_results = []
        
        # Run all tests
        tests = [
            ("Autonomous Brain Chaos Code", test_autonomous_brain_chaos_code),
            ("Weapon Code Generation", test_weapon_code_generation),
            ("Autonomous Weapon Generation", test_autonomous_weapon_generation),
            ("Autonomous Chaos Documentation", test_autonomous_chaos_documentation),
            ("Frontend Weapon Integration", test_frontend_weapon_integration),
            ("Live System Representations", test_live_system_representations),
            ("Weapon Testing Against Live Systems", test_weapon_testing_against_live_systems),
            ("Autonomous Chaos Code Testing", test_autonomous_chaos_code_testing)
        ]
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                test_results.append((test_name, result))
                logger.info(f"{'✅' if result else '❌'} {test_name}: {'PASSED' if result else 'FAILED'}")
            except Exception as e:
                logger.error(f"❌ {test_name} failed with exception: {e}")
                test_results.append((test_name, False))
        
        # Summary
        passed_tests = sum(1 for _, result in test_results if result)
        total_tests = len(test_results)
        
        logger.info(f"📊 Test Summary: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            logger.info("🎉 All autonomous weapons system tests passed!")
            return True
        else:
            logger.error(f"❌ {total_tests - passed_tests} tests failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error in comprehensive autonomous weapons test: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(run_comprehensive_autonomous_weapons_test())
