#!/usr/bin/env python3
"""
Fix Indentation Error in Custody Protocol Service
===============================================

This script fixes the indentation error created by the regex replacement.
"""

import os
import re

def fix_indentation_error():
    """Fix the indentation error in custody protocol service"""
    
    file_path = "app/services/custody_protocol_service.py"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    print("🔧 Fixing indentation error in custody protocol service...")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and fix the problematic indentation around line 4714-4715
    # The issue is: "try:" followed by unindented code
    
    # Fix the specific pattern that's causing the issue
    content = re.sub(
        r'try:\s*\n\s*communication_scenario = await self\.enhanced_test_generator\.generate_ai_communication_scenario\(',
        '''try:
            communication_scenario = await self.enhanced_test_generator.generate_ai_communication_scenario(''',
        content
    )
    
    # Also fix any similar patterns for collaborative_score
    content = re.sub(
        r'try:\s*\n\s*collaborative_score = await self\.enhanced_test_generator\._calculate_collaborative_score\(',
        '''try:
            collaborative_score = await self.enhanced_test_generator._calculate_collaborative_score(''',
        content
    )
    
    # Fix any incomplete try blocks that might have been created
    content = re.sub(
        r'try:\s*\n\s*await self\.enhanced_test_generator\.generate_ai_communication_scenario\(',
        '''try:
            communication_scenario = await self.enhanced_test_generator.generate_ai_communication_scenario(''',
        content
    )
    
    content = re.sub(
        r'try:\s*\n\s*await self\.enhanced_test_generator\._calculate_collaborative_score\(',
        '''try:
            collaborative_score = await self.enhanced_test_generator._calculate_collaborative_score(''',
        content
    )
    
    # Add proper except blocks for any incomplete try blocks
    # Look for try blocks that don't have corresponding except blocks
    lines = content.split('\n')
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        fixed_lines.append(line)
        
        # If we find a try: line, check if the next line is properly indented
        if line.strip() == 'try:':
            # Check if the next line is properly indented
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                if not next_line.strip().startswith('    ') and not next_line.strip().startswith('\t'):
                    # The next line is not properly indented, fix it
                    if 'communication_scenario = await self.enhanced_test_generator.generate_ai_communication_scenario(' in next_line:
                        fixed_lines[-1] = '''try:
            communication_scenario = await self.enhanced_test_generator.generate_ai_communication_scenario('''
                        # Skip the next line since we've incorporated it
                        i += 1
                    elif 'collaborative_score = await self.enhanced_test_generator._calculate_collaborative_score(' in next_line:
                        fixed_lines[-1] = '''try:
            collaborative_score = await self.enhanced_test_generator._calculate_collaborative_score('''
                        # Skip the next line since we've incorporated it
                        i += 1
        
        i += 1
    
    # Reconstruct the content
    content = '\n'.join(fixed_lines)
    
    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Indentation error fixed successfully")
    return True

def main():
    """Run the indentation fix"""
    print("🚀 Starting indentation error fix...")
    
    try:
        if fix_indentation_error():
            print("✅ Indentation error fix completed successfully")
        else:
            print("❌ Failed to fix indentation error")
            return False
        
    except Exception as e:
        print(f"❌ Error during indentation fix: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)