#!/usr/bin/env python3
"""
Script to fix all syntax errors in custody_protocol_service.py
The file has malformed try-except blocks with empty try statements.
"""

def fix_custody_syntax():
    """Fix all malformed try-except blocks in custody_protocol_service.py"""
    
    file_path = "app/services/custody_protocol_service.py"
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all lines with empty try blocks
    lines = content.split('\n')
    fixed_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check if this is a try: line
        if line.strip() == 'try:':
            # Look ahead to see if the next non-empty line is an except
            j = i + 1
            while j < len(lines) and lines[j].strip() == '':
                j += 1
            
            if j < len(lines) and lines[j].strip().startswith('except'):
                # This is an empty try block, add pass
                fixed_lines.append(line)
                fixed_lines.append('            pass')
                i += 1
                continue
        
        fixed_lines.append(line)
        i += 1
    
    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))
    
    print(f"Fixed all syntax errors in {file_path}")

if __name__ == "__main__":
    fix_custody_syntax()