#!/usr/bin/env python3
"""
Test script for ML Evolution System in Project Horus
Tests the continuous learning, adaptive goal creation, and complexity evolution
"""

import asyncio
import json
import sys
import os
sys.path.append('.')

from app.services.enhanced_project_horus_service import enhanced_project_horus_service

async def test_ml_evolution_system():
    """Test the complete ML evolution system"""
    
    print("🚀 Testing ML Evolution System for Project Horus...")
    print("=" * 60)
    
    # Test 1: Initial ML system state
    print("\n1. 🧠 Testing Initial ML System State...")
    initial_metrics = await enhanced_project_horus_service.get_ml_performance_metrics()
    print(f"   Initial ML Metrics: {json.dumps(initial_metrics, indent=2)}")
    
    # Test 2: Simulate AI learning and ML training
    print("\n2. 🤖 Testing AI Learning Integration...")
    ai_types = ["imperium", "conquest", "sandbox", "guardian"]
    
    # Force generate synthetic training data
    print("   Generating synthetic training data...")
    await enhanced_project_horus_service._generate_synthetic_training_data({"ai_experiences_analyzed": 1})
    
    learning_results = await enhanced_project_horus_service.learn_from_ai_experiences(ai_types)
    print(f"   Learning Results: {json.dumps(learning_results, indent=2)}")
    
    # Test 3: Check ML models after learning
    print("\n3. 🧠 Testing ML Models After Learning...")
    post_learning_metrics = await enhanced_project_horus_service.get_ml_performance_metrics()
    print(f"   Post-Learning ML Metrics: {json.dumps(post_learning_metrics, indent=2)}")
    
    # Test 4: Test weapon synthesis with ML
    print("\n4. ⚔️ Testing Weapon Synthesis with ML Integration...")
    # Simulate creating a weapon to trigger ML learning
    for i in range(3):
        weapon_data = {
            "category": ["infiltration", "data_extraction", "backdoor_deployment"][i],
            "origin_ai": ai_types[i % len(ai_types)],
            "stats": {
                "complexity": 0.8 + (i * 0.1),
                "stealth": 0.7 + (i * 0.05),
                "persistence": 0.6 + (i * 0.1)
            },
            "synthetic": i > 1  # Make last one synthetic
        }
        
        # This would normally be called during weapon creation
        features = await enhanced_project_horus_service._extract_weapon_features({
            "experiences": {
                "progress": {"level": 3 + i, "success_rate": 0.8},
                "shared_knowledge": [
                    {"success": True, "performance_score": 0.9},
                    {"success": True, "performance_score": 0.7}
                ]
            },
            "weapon_patterns": ["pattern1", "pattern2"],
            "synthesized_weapons": [weapon_data]
        })
        
        print(f"   Weapon {i+1} Features: {features}")
    
    # Test 5: Test complexity evolution
    print("\n5. 🔬 Testing Complexity Evolution...")
    initial_complexity = enhanced_project_horus_service.complexity_evolution_factor
    await enhanced_project_horus_service._evolve_test_complexity_with_ml()
    final_complexity = enhanced_project_horus_service.complexity_evolution_factor
    print(f"   Complexity Evolution: {initial_complexity:.3f} → {final_complexity:.3f}")
    
    # Test 6: Test adaptive goal generation
    print("\n6. 🎯 Testing Adaptive Goal Generation...")
    initial_goals = len(enhanced_project_horus_service.adaptive_goals)
    await enhanced_project_horus_service._generate_adaptive_goals_with_ml()
    final_goals = len(enhanced_project_horus_service.adaptive_goals)
    print(f"   Adaptive Goals: {initial_goals} → {final_goals}")
    
    if enhanced_project_horus_service.adaptive_goals:
        sample_goal = enhanced_project_horus_service.adaptive_goals[0]
        print(f"   Sample Goal: {json.dumps(sample_goal, indent=2)}")
    
    # Test 7: Test weapon synthesis report with ML metrics
    print("\n7. 📊 Testing Weapon Synthesis Report...")
    synthesis_report = await enhanced_project_horus_service.get_weapon_synthesis_report()
    print(f"   Synthesis Report Keys: {list(synthesis_report.keys())}")
    print(f"   Total Weapons: {synthesis_report.get('total_weapons', 0)}")
    
    # Test 8: Final ML metrics
    print("\n8. 🎯 Final ML System State...")
    final_metrics = await enhanced_project_horus_service.get_ml_performance_metrics()
    print(f"   Final ML Metrics: {json.dumps(final_metrics, indent=2)}")
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 ML Evolution System Test Summary:")
    print(f"   • Models Trained: {final_metrics.get('models_trained', 0)}")
    print(f"   • Training Samples: {final_metrics.get('total_training_samples', 0)}")
    print(f"   • Complexity Factor: {final_metrics.get('complexity_evolution_factor', 1.0):.3f}")
    print(f"   • Adaptive Goals: {final_metrics.get('adaptive_goals_active', 0)}")
    print(f"   • ML Learning Events: {final_metrics.get('ml_learning_events', 0)}")
    print(f"   • Model Accuracy: {final_metrics.get('latest_model_accuracy', 0.0):.3f}")
    
    return final_metrics

if __name__ == "__main__":
    try:
        metrics = asyncio.run(test_ml_evolution_system())
        print("\n✅ ML Evolution System test completed successfully!")
        
        # Check if system is working properly
        if metrics.get('models_trained', 0) > 0 and metrics.get('total_training_samples', 0) > 0:
            print("🚀 ML system is functioning correctly!")
        else:
            print("⚠️ ML system may need more training data")
            
    except Exception as e:
        print(f"\n❌ ML Evolution System test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)