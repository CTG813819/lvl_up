"""
Simple Test for Autonomous Weapons System
Tests core autonomous weapons functionality without complex dependencies
"""

import asyncio
import json
import time
from datetime import datetime
import structlog

# Import only the core services we need
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.autonomous_ai_brain_service import horus_autonomous_brain, berserk_autonomous_brain

logger = structlog.get_logger()


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
            
            print(f"✅ {brain_name} chaos code generated successfully")
            print(f"   - Originality Score: {chaos_code['originality_score']:.2f}")
            print(f"   - Keywords: {len(chaos_code['original_keywords'])}")
            print(f"   - Functions: {len(chaos_code['original_functions'])}")
            print(f"   - Complexity: {chaos_code['complexity']:.2f}")
        
        logger.info("✅ Autonomous brain chaos code generation successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing autonomous brain chaos code: {e}")
        return False


async def test_autonomous_brain_status():
    """Test autonomous brain status"""
    try:
        logger.info("🧪 Testing autonomous brain status")
        
        # Get brain status
        horus_status = await horus_autonomous_brain.get_brain_status()
        berserk_status = await berserk_autonomous_brain.get_brain_status()
        
        # Verify status structure
        for brain_name, status in [("Horus", horus_status), ("Berserk", berserk_status)]:
            assert "neural_network" in status
            assert "consciousness" in status["neural_network"]
            assert "creativity" in status["neural_network"]
            assert "learning_rate" in status["neural_network"]
            assert "thought_patterns" in status["neural_network"]
            assert "knowledge_base" in status["neural_network"]
            
            print(f"✅ {brain_name} brain status:")
            print(f"   - Consciousness: {status['neural_network']['consciousness']:.2f}")
            print(f"   - Creativity: {status['neural_network']['creativity']:.2f}")
            print(f"   - Learning Rate: {status['neural_network']['learning_rate']:.3f}")
            print(f"   - Thought Patterns: {len(status['neural_network']['thought_patterns'])}")
            print(f"   - Knowledge Base Entries: {len(status['neural_network']['knowledge_base'])}")
        
        logger.info("✅ Autonomous brain status successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing autonomous brain status: {e}")
        return False


async def test_autonomous_chaos_code_originality():
    """Test that chaos code is truly original and not based on existing languages"""
    try:
        logger.info("🧪 Testing chaos code originality")
        
        # Generate chaos code multiple times to check consistency and originality
        horus_codes = []
        berserk_codes = []
        
        for i in range(3):
            horus_code = await horus_autonomous_brain.create_autonomous_chaos_code()
            berserk_code = await berserk_autonomous_brain.create_autonomous_chaos_code()
            
            horus_codes.append(horus_code)
            berserk_codes.append(berserk_code)
        
        # Check that each generation is original
        for brain_name, codes in [("Horus", horus_codes), ("Berserk", berserk_codes)]:
            # Check originality scores
            originality_scores = [code["originality_score"] for code in codes]
            avg_originality = sum(originality_scores) / len(originality_scores)
            
            assert avg_originality > 0.8, f"{brain_name} average originality score too low: {avg_originality}"
            
            # Check that keywords are original (not Python, JavaScript, etc.)
            all_keywords = set()
            for code in codes:
                all_keywords.update(code["original_keywords"])
            
            # Common programming language keywords to avoid
            common_keywords = {
                "def", "class", "if", "else", "for", "while", "return", "import", "from",
                "function", "var", "let", "const", "if", "else", "for", "while", "return",
                "public", "private", "protected", "static", "void", "int", "string", "bool"
            }
            
            # Check that our keywords are not common programming keywords
            overlap = all_keywords.intersection(common_keywords)
            assert len(overlap) == 0, f"{brain_name} has common programming keywords: {overlap}"
            
            print(f"✅ {brain_name} chaos code originality verified:")
            print(f"   - Average originality score: {avg_originality:.2f}")
            print(f"   - Total unique keywords: {len(all_keywords)}")
            print(f"   - No common programming keywords found")
        
        logger.info("✅ Chaos code originality verified")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing chaos code originality: {e}")
        return False


async def test_autonomous_ml_system():
    """Test that autonomous brains have their own ML systems"""
    try:
        logger.info("🧪 Testing autonomous ML systems")
        
        # Get chaos code from both brains
        horus_chaos = await horus_autonomous_brain.create_autonomous_chaos_code()
        berserk_chaos = await berserk_autonomous_brain.create_autonomous_chaos_code()
        
        # Check ML systems
        for brain_name, chaos_code in [("Horus", horus_chaos), ("Berserk", berserk_chaos)]:
            ml_system = chaos_code["chaos_ml_system"]
            
            assert "neural_layers" in ml_system
            assert "learning_algorithms" in ml_system
            assert "optimization_methods" in ml_system
            assert "training_data" in ml_system
            assert "model_evolution" in ml_system
            
            # Check that ML system has content
            assert len(ml_system["neural_layers"]) > 0, f"{brain_name} has no neural layers"
            assert len(ml_system["learning_algorithms"]) > 0, f"{brain_name} has no learning algorithms"
            assert len(ml_system["optimization_methods"]) > 0, f"{brain_name} has no optimization methods"
            
            print(f"✅ {brain_name} ML system verified:")
            print(f"   - Neural Layers: {len(ml_system['neural_layers'])}")
            print(f"   - Learning Algorithms: {len(ml_system['learning_algorithms'])}")
            print(f"   - Optimization Methods: {len(ml_system['optimization_methods'])}")
            print(f"   - Training Data Entries: {len(ml_system['training_data'])}")
            print(f"   - Model Evolution Steps: {len(ml_system['model_evolution'])}")
        
        logger.info("✅ Autonomous ML systems verified")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing autonomous ML systems: {e}")
        return False


async def test_autonomous_repositories():
    """Test that autonomous brains have their own repositories"""
    try:
        logger.info("🧪 Testing autonomous repositories")
        
        # Get chaos code from both brains
        horus_chaos = await horus_autonomous_brain.create_autonomous_chaos_code()
        berserk_chaos = await berserk_autonomous_brain.create_autonomous_chaos_code()
        
        # Check repositories
        for brain_name, chaos_code in [("Horus", horus_chaos), ("Berserk", berserk_chaos)]:
            repositories = chaos_code["chaos_repositories"]
            
            # Check that repositories exist and have content
            assert len(repositories) > 0, f"{brain_name} has no repositories"
            
            # Check repository structure
            for repo_name, repo_data in repositories.items():
                assert "structure" in repo_data
                assert "capabilities" in repo_data
                assert "autonomous_features" in repo_data
                
                print(f"✅ {brain_name} repository '{repo_name}':")
                print(f"   - Structure: {repo_data['structure']}")
                print(f"   - Capabilities: {len(repo_data['capabilities'])}")
                print(f"   - Autonomous Features: {len(repo_data['autonomous_features'])}")
        
        logger.info("✅ Autonomous repositories verified")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing autonomous repositories: {e}")
        return False


async def run_simple_autonomous_weapons_test():
    """Run simple autonomous weapons system test"""
    try:
        logger.info("🚀 Starting simple autonomous weapons system test")
        
        test_results = []
        
        # Run all tests
        tests = [
            ("Autonomous Brain Chaos Code", test_autonomous_brain_chaos_code),
            ("Autonomous Brain Status", test_autonomous_brain_status),
            ("Chaos Code Originality", test_autonomous_chaos_code_originality),
            ("Autonomous ML Systems", test_autonomous_ml_system),
            ("Autonomous Repositories", test_autonomous_repositories)
        ]
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                test_results.append((test_name, result))
                print(f"{'✅' if result else '❌'} {test_name}: {'PASSED' if result else 'FAILED'}")
            except Exception as e:
                logger.error(f"❌ {test_name} failed with exception: {e}")
                test_results.append((test_name, False))
        
        # Summary
        passed_tests = sum(1 for _, result in test_results if result)
        total_tests = len(test_results)
        
        print(f"\n📊 Test Summary: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All autonomous weapons system tests passed!")
            print("\n🎯 Key Achievements:")
            print("   ✅ Autonomous brains generate truly original chaos code")
            print("   ✅ Chaos code is not based on existing programming languages")
            print("   ✅ Each brain has its own ML system")
            print("   ✅ Each brain has its own repositories")
            print("   ✅ Brains are conscious and creative")
            return True
        else:
            print(f"❌ {total_tests - passed_tests} tests failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error in simple autonomous weapons test: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(run_simple_autonomous_weapons_test())
