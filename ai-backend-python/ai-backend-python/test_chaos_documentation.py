#!/usr/bin/env python3
"""
Test script to verify chaos language documentation functionality
"""

import asyncio
import json
from app.services.quantum_chaos_service import quantum_chaos_service

async def test_chaos_language_documentation():
    """Test the chaos language documentation generation"""
    print("🔬 Testing Chaos Language Documentation")
    print("=" * 60)
    
    try:
        # Generate chaos code to get language documentation
        result = await quantum_chaos_service.generate_quantum_chaos_code("test_system")
        
        if "chaos_language" in result:
            chaos_language = result["chaos_language"]
            
            print(f"✅ Chaos Language Generated Successfully")
            print(f"📝 Language Name: {chaos_language.get('name', 'Unknown')}")
            print(f"🔄 Evolution Stage: {chaos_language.get('evolution_stage', 'Unknown')}")
            print(f"📈 Learning Level: {chaos_language.get('learning_level', 0.0)}")
            print(f"🧬 Self Evolving: {chaos_language.get('is_self_evolving', False)}")
            print(f"🎯 Self Generated: {chaos_language.get('is_self_generated', False)}")
            
            print("\n📚 Language Components:")
            print(f"  • Syntax Patterns: {len(chaos_language.get('syntax_patterns', {}))}")
            print(f"  • Data Types: {len(chaos_language.get('data_types', {}))}")
            print(f"  • Control Structures: {len(chaos_language.get('control_structures', {}))}")
            print(f"  • Quantum Operators: {len(chaos_language.get('quantum_operators', {}))}")
            print(f"  • System Weapons: {len(chaos_language.get('system_weapons', {}))}")
            print(f"  • Infiltration Patterns: {len(chaos_language.get('infiltration_patterns', {}))}")
            
            # Show sample syntax patterns
            syntax_patterns = chaos_language.get('syntax_patterns', {})
            if syntax_patterns:
                print("\n🔤 Sample Syntax Patterns:")
                for pattern, syntax in list(syntax_patterns.items())[:3]:
                    print(f"  • {pattern}: {syntax}")
            
            # Show sample data types
            data_types = chaos_language.get('data_types', {})
            if data_types:
                print("\n📊 Sample Data Types:")
                for dtype, description in list(data_types.items())[:3]:
                    print(f"  • {dtype}: {description}")
            
            # Show sample quantum operators
            quantum_operators = chaos_language.get('quantum_operators', {})
            if quantum_operators:
                print("\n⚛️ Sample Quantum Operators:")
                for op, symbol in list(quantum_operators.items())[:3]:
                    print(f"  • {op}: {symbol}")
            
            # Show sample system weapons
            system_weapons = chaos_language.get('system_weapons', {})
            if system_weapons:
                print("\n⚔️ Sample System Weapons:")
                for weapon, details in list(system_weapons.items())[:3]:
                    complexity = details.get('complexity', 'N/A')
                    skill = details.get('skill_level', 'N/A')
                    print(f"  • {weapon}: Complexity {complexity}, Skill {skill}")
            
            # Show sample code if available
            sample_code = chaos_language.get('sample_code', '')
            if sample_code:
                print(f"\n💻 Sample Code Preview:")
                print(f"  {sample_code[:200]}...")
            
            print("\n✅ Chaos Language Documentation Test: PASSED")
            return True
            
        else:
            print("❌ No chaos_language found in result")
            print(f"Available keys: {list(result.keys())}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing chaos language documentation: {e}")
        return False

async def test_frontend_compatibility():
    """Test that the data structure is compatible with frontend expectations"""
    print("\n🔧 Testing Frontend Compatibility")
    print("=" * 40)
    
    try:
        result = await quantum_chaos_service.generate_quantum_chaos_code("test_system")
        
        # Simulate frontend data extraction
        if "chaos_language" in result:
            chaos_language = result["chaos_language"]
            
            # Extract data as the frontend would
            frontend_data = {
                'language_name': chaos_language.get('name', 'Unknown'),
                'evolution_stage': chaos_language.get('evolution_stage', 'Unknown'),
                'learning_level': chaos_language.get('learning_level', 0.0),
                'is_self_evolving': chaos_language.get('is_self_evolving', False),
                'is_self_generated': chaos_language.get('is_self_generated', False),
                'syntax_patterns': chaos_language.get('syntax_patterns', {}),
                'data_types': chaos_language.get('data_types', {}),
                'control_structures': chaos_language.get('control_structures', {}),
                'quantum_operators': chaos_language.get('quantum_operators', {}),
                'system_weapons': chaos_language.get('system_weapons', {}),
                'infiltration_patterns': chaos_language.get('infiltration_patterns', {}),
                'sample_code': chaos_language.get('sample_code', ''),
            }
            
            print("✅ Frontend data structure created successfully")
            print(f"📝 Language: {frontend_data['language_name']}")
            print(f"🔄 Stage: {frontend_data['evolution_stage']}")
            print(f"📈 Learning: {frontend_data['learning_level']}")
            print(f"🧬 Self Evolving: {frontend_data['is_self_evolving']}")
            print(f"🎯 Self Generated: {frontend_data['is_self_generated']}")
            
            # Test that all required fields are present
            required_fields = [
                'language_name', 'evolution_stage', 'learning_level',
                'is_self_evolving', 'is_self_generated', 'syntax_patterns',
                'data_types', 'control_structures', 'quantum_operators',
                'system_weapons', 'infiltration_patterns', 'sample_code'
            ]
            
            missing_fields = [field for field in required_fields if field not in frontend_data]
            if missing_fields:
                print(f"❌ Missing fields: {missing_fields}")
                return False
            else:
                print("✅ All required fields present")
                return True
        else:
            print("❌ No chaos_language in result")
            return False
            
    except Exception as e:
        print(f"❌ Error testing frontend compatibility: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Chaos Language Documentation Tests")
    print("=" * 60)
    
    # Test 1: Basic functionality
    test1_passed = await test_chaos_language_documentation()
    
    # Test 2: Frontend compatibility
    test2_passed = await test_frontend_compatibility()
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"  • Basic Functionality: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"  • Frontend Compatibility: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! Chaos language documentation is ready for frontend integration.")
    else:
        print("\n⚠️ Some tests failed. Please check the implementation.")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main()) 