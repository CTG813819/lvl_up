#!/usr/bin/env python3
"""
Comprehensive fix for diverse test generation and timestamp issues
"""

import re
import os

class ComprehensiveDiverseTestFixer:
    def __init__(self):
        self.custody_service_file = "app/services/custody_protocol_service.py"
        
    async def fix_diverse_test_integration(self):
        """Fix the diverse test generator integration"""
        print("🔧 Fixing diverse test generator integration...")
        
        # Read the current file
        with open(self.custody_service_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add imports if missing
        if "from diverse_test_generator import" not in content:
            print("📝 Adding diverse test generator import...")
            # Find the import section and add the import
            import_pattern = r'(from transformers import.*?)\n'
            replacement = r'\1\nfrom diverse_test_generator import DiverseTestGenerator\nfrom improved_scoring_system import ImprovedScoringSystem\n'
            content = re.sub(import_pattern, replacement, content, flags=re.DOTALL)
        
        # Add initialization in __init__ method
        if "self.diverse_test_generator" not in content:
            print("📝 Adding diverse test generator initialization...")
            # Find the __init__ method
            init_pattern = r'(def __init__\(self.*?\):.*?)(\n\s+)(self\.ml_models = None)'
            replacement = r'\1\2self.diverse_test_generator = None\n\2self.improved_scorer = None\n\2\3'
            content = re.sub(init_pattern, replacement, content, flags=re.DOTALL)
        
        # Add initialization in initialize method
        if "self.diverse_test_generator = DiverseTestGenerator()" not in content:
            print("📝 Adding diverse test generator initialization in initialize method...")
            # Find the initialize method
            init_pattern = r'(async def initialize\(self\):.*?)(\n\s+)(self\.ml_models = {})'
            replacement = r'\1\2self.diverse_test_generator = DiverseTestGenerator()\n\2self.improved_scorer = ImprovedScoringSystem()\n\2\3'
            content = re.sub(init_pattern, replacement, content, flags=re.DOTALL)
        
        # Write the updated content
        with open(self.custody_service_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Diverse test generator integration fixed")
    
    async def fix_timestamp_error(self):
        """Fix the timestamp KeyError in _update_custody_metrics"""
        print("🔧 Fixing timestamp KeyError...")
        
        # Read the current file
        with open(self.custody_service_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the problematic line and fix it
        timestamp_pattern = r'("timestamp": test_result\["timestamp"\],)'
        replacement = r'"timestamp": test_result.get("timestamp", datetime.utcnow().isoformat()),'
        content = re.sub(timestamp_pattern, replacement, content)
        
        # Also fix the duration line
        duration_pattern = r'("duration": test_result\["duration"\])'
        replacement = r'"duration": test_result.get("duration", 0)'
        content = re.sub(duration_pattern, replacement, content)
        
        # Write the updated content
        with open(self.custody_service_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Timestamp error fixed")
    
    async def ensure_diverse_test_logic(self):
        """Ensure the diverse test generation logic is properly integrated"""
        print("🔧 Ensuring diverse test generation logic...")
        
        # Read the current file
        with open(self.custody_service_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if the diverse test logic is in the _generate_custody_test method
        if "diverse_test_generator.generate_diverse_test" not in content:
            print("📝 Adding diverse test generation logic...")
            
            # Find the _generate_custody_test method
            method_pattern = r'(async def _generate_custody_test\(self, ai_type: str, difficulty: TestDifficulty, category: TestCategory\) -> Dict\[str, Any\]:)'
            
            diverse_logic = '''
        # Try diverse test generator first
        if hasattr(self, "diverse_test_generator") and self.diverse_test_generator:
            try:
                scenario = self.diverse_test_generator.generate_diverse_test("custody", ai_type)
                response = self.diverse_test_generator.generate_ai_response(ai_type, scenario)
                test_content = {
                    "test_type": "diverse_custody",
                    "scenario": scenario,
                    "ai_response": response,
                    "difficulty": difficulty.value,
                    "category": category.value,
                    "ai_type": ai_type,
                    "timestamp": datetime.utcnow().isoformat()
                }
                logger.info(f"Generated diverse custody test for {ai_type}: {scenario['title']}")
                return test_content
            except Exception as e:
                logger.warning(f"Failed to generate diverse test: {e}")
                # Fall back to original method
        '''
            
            replacement = r'\1' + diverse_logic
            content = re.sub(method_pattern, replacement, content)
        
        # Write the updated content
        with open(self.custody_service_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Diverse test generation logic ensured")
    
    async def run_comprehensive_fix(self):
        """Run all fixes"""
        print("🚀 Running comprehensive diverse test and timestamp fixes...")
        
        await self.fix_diverse_test_integration()
        await self.fix_timestamp_error()
        await self.ensure_diverse_test_logic()
        
        print("🎉 All fixes completed!")

async def main():
    fixer = ComprehensiveDiverseTestFixer()
    await fixer.run_comprehensive_fix()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 