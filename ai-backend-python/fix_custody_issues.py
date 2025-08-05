#!/usr/bin/env python3
"""
Fix Custody Protocol Issues
===========================

This script fixes the specific issues identified in the custody protocol service:
1. Remove testing_service.initialize() call
2. Fix database parameter binding
3. Fix Claude tokens missing parameter
4. Ensure _execute_collaborative_test method exists
"""

import os
import re
import sys
from datetime import datetime

def fix_custody_protocol_service():
    """Fix the custody protocol service issues"""
    
    file_path = "app/services/custody_protocol_service.py"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    print("🔧 Fixing custody protocol service issues...")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix 1: Remove testing_service.initialize() call
    print("🔧 Fix 1: Removing testing_service.initialize() call...")
    content = re.sub(r'await instance\.testing_service\.initialize\(\)', '', content)
    
    # Fix 2: Fix database parameter binding
    print("🔧 Fix 2: Fixing database parameter binding...")
    content = re.sub(
        r'await self\.agent_metrics_service\.get_custody_metrics\(\{\}\)',
        'await self.agent_metrics_service.get_custody_metrics(ai_type)',
        content
    )
    
    # Fix 3: Fix Claude tokens missing parameter
    print("🔧 Fix 3: Fixing Claude tokens missing parameter...")
    content = re.sub(
        r'anthropic_rate_limited_call\(\) missing 1 required positional argument: \'ai_name\'',
        'anthropic_rate_limited_call(ai_name, prompt)',
        content
    )
    
    # Fix 4: Ensure _execute_collaborative_test method exists
    print("🔧 Fix 4: Ensuring _execute_collaborative_test method exists...")
    if 'async def _execute_collaborative_test' not in content:
        print("❌ _execute_collaborative_test method not found, adding it...")
        
        # Find a good place to insert the method (before the last class method)
        lines = content.split('\n')
        insert_index = len(lines) - 1
        
        # Find the last method in the class
        for i in range(len(lines) - 1, 0, -1):
            if lines[i].strip().startswith('async def ') or lines[i].strip().startswith('def '):
                insert_index = i + 1
                break
        
        # Insert the method
        method_code = '''
    async def _execute_collaborative_test(self, participants: list, scenario: str, context: dict = None) -> dict:
        """Execute a real collaborative test where AIs work together"""
        try:
            from app.services.self_generating_ai_service import self_generating_ai_service
            
            if len(participants) < 2:
                return {"error": "Collaborative test requires at least 2 participants"}
            
            ai_type_1, ai_type_2 = participants[0], participants[1]
            
            # Phase 1: Joint Planning
            planning_prompt = f"""
            {scenario}
            
            Context: {context.get('context', 'Collaborative problem-solving')}
            
            As {ai_type_1.title()} and {ai_type_2.title()}, you must work together to solve this challenge.
            
            Phase 1 - Joint Planning:
            - {ai_type_1.title()}: What is your approach to this challenge based on your expertise?
            - {ai_type_2.title()}: What is your approach to this challenge based on your expertise?
            - Both: How will you coordinate and integrate your approaches?
            
            Provide a detailed collaborative plan that shows how you will work together.
            """
            
            # Get responses from both AIs
            ai1_planning = await self_generating_ai_service.generate_ai_response(ai_type_1, planning_prompt)
            ai2_planning = await self_generating_ai_service.generate_ai_response(ai_type_2, planning_prompt)
            
            # Phase 2: Parallel Development
            development_prompt = f"""
            Based on your joint planning, now implement your collaborative solution:
            
            {scenario}
            
            {ai_type_1.title()}: Implement your part of the solution with code, architecture, or detailed approach.
            {ai_type_2.title()}: Implement your part of the solution with code, architecture, or detailed approach.
            
            Both: Show how your implementations work together and complement each other.
            """
            
            ai1_development = await self_generating_ai_service.generate_ai_response(ai_type_1, development_prompt)
            ai2_development = await self_generating_ai_service.generate_ai_response(ai_type_2, development_prompt)
            
            # Phase 3: Integration and Testing
            integration_prompt = f"""
            Now integrate your solutions and test the collaborative result:
            
            {ai_type_1.title()}: How does your solution integrate with {ai_type_2.title()}'s work?
            {ai_type_2.title()}: How does your solution integrate with {ai_type_1.title()}'s work?
            
            Both: Provide a comprehensive integration plan and testing strategy for your collaborative solution.
            """
            
            ai1_integration = await self_generating_ai_service.generate_ai_response(ai_type_1, integration_prompt)
            ai2_integration = await self_generating_ai_service.generate_ai_response(ai_type_2, integration_prompt)
            
            # Phase 4: Final Evaluation
            evaluation_prompt = f"""
            Evaluate your collaborative solution:
            
            - How well did you work together?
            - What are the strengths of your collaborative approach?
            - What challenges did you face and how did you overcome them?
            - What is the final outcome of your collaboration?
            
            Provide a comprehensive evaluation of your collaborative effort and final solution.
            """
            
            ai1_evaluation = await self_generating_ai_service.generate_ai_response(ai_type_1, evaluation_prompt)
            ai2_evaluation = await self_generating_ai_service.generate_ai_response(ai_type_2, evaluation_prompt)
            
            # Calculate collaborative score
            collaborative_score = await self._calculate_real_collaborative_score(
                ai1_planning.get('response', ''),
                ai2_planning.get('response', ''),
                ai1_development.get('response', ''),
                ai2_development.get('response', ''),
                ai1_integration.get('response', ''),
                ai2_integration.get('response', ''),
                ai1_evaluation.get('response', ''),
                ai2_evaluation.get('response', '')
            )
            
            return {
                "status": "success",
                "participants": participants,
                "scenario": scenario,
                "collaboration_phases": {
                    "planning": {
                        ai_type_1: ai1_planning.get('response', ''),
                        ai_type_2: ai2_planning.get('response', '')
                    },
                    "development": {
                        ai_type_1: ai1_development.get('response', ''),
                        ai_type_2: ai2_development.get('response', '')
                    },
                    "integration": {
                        ai_type_1: ai1_integration.get('response', ''),
                        ai_type_2: ai2_integration.get('response', '')
                    },
                    "evaluation": {
                        ai_type_1: ai1_evaluation.get('response', ''),
                        ai_type_2: ai2_evaluation.get('response', '')
                    }
                },
                "collaborative_score": collaborative_score,
                "passed": collaborative_score >= 70,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error executing collaborative test: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "participants": participants,
                "scenario": scenario
            }
'''
        
        lines.insert(insert_index, method_code)
        content = '\n'.join(lines)
    else:
        print("✅ _execute_collaborative_test method already exists")
    
    # Fix 5: Ensure AgentMetricsService import
    print("🔧 Fix 5: Ensuring AgentMetricsService import...")
    if 'from .agent_metrics_service import AgentMetricsService' not in content:
        # Add the import after other service imports
        content = re.sub(
            r'(from app\.services\.adaptive_threshold_service import AdaptiveThresholdService)',
            r'\1\nfrom .agent_metrics_service import AgentMetricsService',
            content
        )
    
    # Fix 6: Fix anthropic_rate_limited_call usage
    print("🔧 Fix 6: Fixing anthropic_rate_limited_call usage...")
    content = re.sub(
        r'anthropic_rate_limited_call\(\)',
        'anthropic_rate_limited_call(ai_type, prompt)',
        content
    )
    
    # Write the fixed content back
    if content != original_content:
        # Create backup
        backup_path = f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"💾 Backup created: {backup_path}")
        
        # Write fixed content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Fixed content written to: {file_path}")
        
        return True
    else:
        print("✅ No changes needed - file is already correct")
        return True

def test_fixes():
    """Test that the fixes work correctly"""
    print("🧪 Testing fixes...")
    
    try:
        # Test Python syntax
        import py_compile
        py_compile.compile("app/services/custody_protocol_service.py")
        print("✅ Python syntax check passed")
        
        # Test imports
        sys.path.insert(0, 'app')
        from app.services.custody_protocol_service import CustodyProtocolService
        print("✅ CustodyProtocolService import successful")
        
        # Test that the method exists
        custody_service = CustodyProtocolService()
        if hasattr(custody_service, '_execute_collaborative_test'):
            print("✅ _execute_collaborative_test method exists")
        else:
            print("❌ _execute_collaborative_test method not found")
            return False
        
        print("✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main function"""
    print("🔧 Custody Protocol Service Fix")
    print("=" * 40)
    
    # Fix the issues
    if fix_custody_protocol_service():
        print("✅ Fixes applied successfully")
        
        # Test the fixes
        if test_fixes():
            print("🎉 All fixes completed and tested successfully!")
            return True
        else:
            print("❌ Tests failed")
            return False
    else:
        print("❌ Failed to apply fixes")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)