#!/usr/bin/env python3
"""
Fix for the syntax error on line 1658 in custody_protocol_service.py
"""

def fix_custody_line_1658():
    """Fix the syntax error on line 1658"""
    
    # Read the file
    with open('app/services/custody_protocol_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The exact problematic pattern from the current file
    old_pattern = '''            try:

            
                except ImportError:
                logger.warning(f"[SMART FALLBACK] Smart fallback not available, using basic fallback")
                # Fall back to basic fallback system
                pass'''
    
    # The corrected pattern - fix the indentation and structure
    new_pattern = '''            try:
                pass
            except ImportError:
                logger.warning(f"[SMART FALLBACK] Smart fallback not available, using basic fallback")
                # Fall back to basic fallback system
                pass'''
    
    # Apply the fix
    if old_pattern in content:
        content = content.replace(old_pattern, new_pattern)
        print("Fixed syntax error on line 1658")
    else:
        print("Pattern not found. Trying alternative approach...")
        
        # Alternative approach: find the specific lines and fix them manually
        lines = content.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Look for the problematic pattern: try: followed by empty line and malformed except
            if ('try:' in line and 
                i + 1 < len(lines) and lines[i + 1].strip() == '' and
                i + 2 < len(lines) and 'except ImportError:' in lines[i + 2]):
                
                # Found the problematic pattern, fix it
                indent = len(line) - len(line.lstrip())
                indent_str = ' ' * indent
                
                # Add the corrected try-except block
                fixed_lines.append(line)  # try:
                fixed_lines.append(f'{indent_str}    pass')  # Add pass inside try
                fixed_lines.append(f'{indent_str}except ImportError:')  # Fix except indentation
                
                # Add the next few lines with correct indentation
                for j in range(i + 3, min(i + 7, len(lines))):
                    if lines[j].strip().startswith('logger.warning'):
                        fixed_lines.append(f'{indent_str}    {lines[j].strip()}')
                    elif lines[j].strip().startswith('#'):
                        fixed_lines.append(f'{indent_str}    {lines[j].strip()}')
                    elif lines[j].strip() == 'pass':
                        fixed_lines.append(f'{indent_str}    pass')
                    else:
                        fixed_lines.append(lines[j])
                
                # Skip the problematic lines
                i += 7
                continue
            else:
                fixed_lines.append(line)
            
            i += 1
        
        # Write the fixed content back to the file
        with open('app/services/custody_protocol_service.py', 'w', encoding='utf-8') as f:
            f.write('\n'.join(fixed_lines))
        print("Fixed syntax error using line-by-line approach")
        return
    
    # Write the fixed content back to the file
    with open('app/services/custody_protocol_service.py', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    fix_custody_line_1658()