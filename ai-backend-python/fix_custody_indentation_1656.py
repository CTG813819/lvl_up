#!/usr/bin/env python3
"""
Fix for the indentation error on line 1656 in custody_protocol_service.py
"""

def fix_custody_indentation_1656():
    """Fix the indentation error on line 1656"""
    
    # Read the file
    with open('app/services/custody_protocol_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The exact problematic pattern from the current file
    old_pattern = '''            from smart_fallback_testing import SmartFallbackTesting
                smart_system = SmartFallbackTesting()'''
    
    # The corrected pattern
    new_pattern = '''            from smart_fallback_testing import SmartFallbackTesting
            smart_system = SmartFallbackTesting()'''
    
    # Apply the fix
    if old_pattern in content:
        content = content.replace(old_pattern, new_pattern)
        print("Fixed indentation error on line 1656")
    else:
        print("Pattern not found. Trying alternative approach...")
        
        # Alternative approach: find the specific lines and fix them manually
        lines = content.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Look for the problematic pattern: from smart_fallback_testing followed by over-indented line
            if ('from smart_fallback_testing import SmartFallbackTesting' in line and 
                i + 1 < len(lines) and 'smart_system = SmartFallbackTesting()' in lines[i + 1]):
                
                # Found the problematic pattern, fix the indentation
                indent = len(line) - len(line.lstrip())
                indent_str = ' ' * indent
                
                # Add the current line
                fixed_lines.append(line)
                
                # Fix the indentation of the next line
                fixed_lines.append(f'{indent_str}smart_system = SmartFallbackTesting()')
                
                # Skip the problematic line
                i += 2
                continue
            else:
                fixed_lines.append(line)
            
            i += 1
        
        # Write the fixed content back to the file
        with open('app/services/custody_protocol_service.py', 'w', encoding='utf-8') as f:
            f.write('\n'.join(fixed_lines))
        print("Fixed indentation error using line-by-line approach")
        return
    
    # Write the fixed content back to the file
    with open('app/services/custody_protocol_service.py', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    fix_custody_indentation_1656()