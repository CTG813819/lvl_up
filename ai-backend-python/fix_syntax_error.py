#!/usr/bin/env python3
"""
Fix Syntax Error in Custody Protocol Service
===========================================

This script fixes the syntax error created by the regex replacement.
"""

import os
import re

def fix_syntax_error():
    """Fix the syntax error in custody protocol service"""
    
    file_path = "app/services/custody_protocol_service.py"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    print("🔧 Fixing syntax error in custody protocol service...")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the syntax error on line 4714
    # The error is: "communication_scenario = try:"
    # It should be: "try:\n    communication_scenario = await self.enhanced_test_generator.generate_ai_communication_scenario(...)"
    
    # Find and fix the problematic line
    content = re.sub(
        r'communication_scenario = try:',
        '''try:
            communication_scenario = await self.enhanced_test_generator.generate_ai_communication_scenario(''',
        content
    )
    
    # Also fix any other similar syntax errors
    content = re.sub(
        r'collaborative_score = try:',
        '''try:
            collaborative_score = await self.enhanced_test_generator._calculate_collaborative_score(''',
        content
    )
    
    # Fix any incomplete try blocks
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
    
    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Syntax error fixed successfully")
    return True

def main():
    """Run the syntax fix"""
    print("🚀 Starting syntax error fix...")
    
    try:
        if fix_syntax_error():
            print("✅ Syntax error fix completed successfully")
        else:
            print("❌ Failed to fix syntax error")
            return False
        
    except Exception as e:
        print(f"❌ Error during syntax fix: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 