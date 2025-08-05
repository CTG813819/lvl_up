#!/usr/bin/env python3
"""
Script to fix duplicate methods in custody_protocol_service.py
"""

import re

def fix_duplicate_methods():
    """Remove duplicate methods"""
    
    file_path = "app/services/custody_protocol_service.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Remove duplicate _check_proposal_eligibility method
    pattern1 = r'(\s+async def _check_proposal_eligibility\(self, ai_type: str\) -> bool:.*?)(?=\s+async def|\s+def|\s+class|\s*$)'
    matches1 = list(re.finditer(pattern1, content, re.DOTALL))
    
    if len(matches1) >= 2:
        # Remove the second occurrence (duplicate)
        second_match = matches1[1]
        start = second_match.start()
        end = second_match.end()
        
        # Replace with a comment
        replacement = "\n    # REMOVED: Duplicate _check_proposal_eligibility method\n"
        
        content = content[:start] + replacement + content[end:]
        print("✅ Removed duplicate _check_proposal_eligibility method")
    else:
        print("❌ Could not find duplicate _check_proposal_eligibility method")
    
    # Fix 2: Remove duplicate _execute_collaborative_test method
    pattern2 = r'(\s+async def _execute_collaborative_test\(self, participants: list, scenario: str, context: dict = None\) -> dict:.*?)(?=\s+async def|\s+def|\s+class|\s*$)'
    matches2 = list(re.finditer(pattern2, content, re.DOTALL))
    
    if len(matches2) >= 2:
        # Remove the second occurrence (duplicate)
        second_match = matches2[1]
        start = second_match.start()
        end = second_match.end()
        
        # Replace with a comment
        replacement = "\n    # REMOVED: Duplicate _execute_collaborative_test method\n"
        
        content = content[:start] + replacement + content[end:]
        print("✅ Removed duplicate _execute_collaborative_test method")
    else:
        print("❌ Could not find duplicate _execute_collaborative_test method")
    
    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    fix_duplicate_methods()