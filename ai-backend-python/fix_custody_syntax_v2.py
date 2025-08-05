#!/usr/bin/env python3
"""
Script to fix syntax errors in custody_protocol_service.py
The file has malformed try-except blocks with empty try statements.
"""

def fix_custody_syntax():
    """Fix malformed try-except blocks in custody_protocol_service.py"""
    
    file_path = "app/services/custody_protocol_service.py"
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Process lines to fix empty try blocks
    fixed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        fixed_lines.append(line)
        
        # Check if this is a try: line
        if line.strip() == 'try:':
            # Check if the next line is an except (empty try block)
            if i + 1 < len(lines) and lines[i + 1].strip().startswith('except'):
                # Insert a pass statement after the try:
                fixed_lines.append('            pass\n')
        
        i += 1
    
    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"Fixed syntax errors in {file_path}")

if __name__ == "__main__":
    fix_custody_syntax()