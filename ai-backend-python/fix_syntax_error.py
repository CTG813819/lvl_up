#!/usr/bin/env python3
"""
Fix syntax error in ai_learning_service.py
"""

import re

def fix_syntax_error():
    """Fix the syntax error in ai_learning_service.py"""
    file_path = "app/services/ai_learning_service.py"
    
    print(f"🔧 Fixing syntax error in {file_path}...")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for the specific problematic line
    lines = content.split('\n')
    
    # Look for the problematic area around line 1668
    for i, line in enumerate(lines):
        if i >= 1660 and i <= 1675:  # Around the error line
            if 'applied_count=existing.applied_count' in line:
                print(f"Found problematic line {i+1}: {line}")
                
                # Check if there's a syntax issue
                if line.strip().endswith(')'):
                    # The line looks correct, let's check the context
                    print(f"Line {i+1} looks correct: {line}")
                    
                    # Check the previous lines for any unclosed parentheses
                    for j in range(max(0, i-10), i+1):
                        open_parens = lines[j].count('(')
                        close_parens = lines[j].count(')')
                        if open_parens != close_parens:
                            print(f"Unbalanced parentheses in line {j+1}: {lines[j]}")
    
    # Let's also check for any hidden characters or encoding issues
    print("Checking for encoding issues...")
    
    # Re-read the file with different encoding to check for issues
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content_utf8 = f.read()
    except UnicodeDecodeError as e:
        print(f"Unicode decode error: {e}")
        return False
    
    # Check for any problematic characters
    problematic_chars = ['\x00', '\x01', '\x02', '\x03', '\x04', '\x05', '\x06', '\x07']
    for char in problematic_chars:
        if char in content:
            print(f"Found problematic character: {repr(char)}")
            content = content.replace(char, '')
    
    # Let's also check the specific area around line 1668 more carefully
    lines = content.split('\n')
    if len(lines) >= 1668:
        print(f"Line 1666: {lines[1665]}")
        print(f"Line 1667: {lines[1666]}")
        print(f"Line 1668: {lines[1667]}")
        print(f"Line 1669: {lines[1668]}")
        print(f"Line 1670: {lines[1669]}")
    
    # Let's try to fix any potential issues by rewriting the file
    print("Rewriting file to fix any potential encoding issues...")
    
    # Create a backup
    backup_path = f"{file_path}.backup"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created backup: {backup_path}")
    
    # Rewrite the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ File rewritten successfully")
    
    # Test syntax
    import subprocess
    result = subprocess.run(['python3', '-m', 'py_compile', file_path], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Syntax check passed")
        return True
    else:
        print(f"❌ Syntax check failed: {result.stderr}")
        return False

if __name__ == "__main__":
    fix_syntax_error() 