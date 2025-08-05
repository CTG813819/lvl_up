#!/usr/bin/env python3
"""
Fix for the indentation errors around line 1659 in custody_protocol_service.py
"""

def fix_custody_indentation_1659():
    """Fix the indentation errors around line 1659"""
    
    # Read the file
    with open('app/services/custody_protocol_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The exact problematic pattern from the current file
    old_pattern = '''            smart_system = SmartFallbackTesting()
                
                # Generate smart test using learning data
                smart_test = await smart_system.generate_smart_test(
                    ai_type, 
                    difficulty.value, 
                    category.value
                )
                
                # Use the smart test content
                test_content = smart_test
                logger.info(f"[SMART FALLBACK] Smart test generated: {smart_test.get('source', 'unknown')}")'''
    
    # The corrected pattern
    new_pattern = '''            smart_system = SmartFallbackTesting()
            
            # Generate smart test using learning data
            smart_test = await smart_system.generate_smart_test(
                ai_type, 
                difficulty.value, 
                category.value
            )
            
            # Use the smart test content
            test_content = smart_test
            logger.info(f"[SMART FALLBACK] Smart test generated: {smart_test.get('source', 'unknown')}")'''
    
    # Apply the fix
    if old_pattern in content:
        content = content.replace(old_pattern, new_pattern)
        print("Fixed indentation errors around line 1659")
    else:
        print("Pattern not found. Trying alternative approach...")
        
        # Alternative approach: find the specific lines and fix them manually
        lines = content.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Look for the problematic pattern: smart_system = SmartFallbackTesting() followed by over-indented lines
            if ('smart_system = SmartFallbackTesting()' in line and 
                i + 1 < len(lines) and lines[i + 1].strip() == '' and
                i + 2 < len(lines) and '# Generate smart test using learning data' in lines[i + 2]):
                
                # Found the problematic pattern, fix the indentation
                indent = len(line) - len(line.lstrip())
                indent_str = ' ' * indent
                
                # Add the current line
                fixed_lines.append(line)
                
                # Add empty line
                fixed_lines.append('')
                
                # Fix the indentation of the following lines
                for j in range(i + 2, i + 15):  # Fix approximately 13 lines
                    if j < len(lines):
                        if lines[j].strip() == '':
                            fixed_lines.append('')
                        elif lines[j].strip().startswith('#'):
                            fixed_lines.append(f'{indent_str}{lines[j].strip()}')
                        elif lines[j].strip().startswith('smart_test ='):
                            fixed_lines.append(f'{indent_str}{lines[j].strip()}')
                        elif lines[j].strip().startswith('ai_type,'):
                            fixed_lines.append(f'{indent_str}    {lines[j].strip()}')
                        elif lines[j].strip().startswith('difficulty.value,'):
                            fixed_lines.append(f'{indent_str}    {lines[j].strip()}')
                        elif lines[j].strip().startswith('category.value'):
                            fixed_lines.append(f'{indent_str}    {lines[j].strip()}')
                        elif lines[j].strip().startswith('test_content ='):
                            fixed_lines.append(f'{indent_str}{lines[j].strip()}')
                        elif lines[j].strip().startswith('logger.info'):
                            fixed_lines.append(f'{indent_str}{lines[j].strip()}')
                        else:
                            fixed_lines.append(lines[j])
                
                # Skip the problematic lines
                i += 15
                continue
            else:
                fixed_lines.append(line)
            
            i += 1
        
        # Write the fixed content back to the file
        with open('app/services/custody_protocol_service.py', 'w', encoding='utf-8') as f:
            f.write('\n'.join(fixed_lines))
        print("Fixed indentation errors using line-by-line approach")
        return
    
    # Write the fixed content back to the file
    with open('app/services/custody_protocol_service.py', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    fix_custody_indentation_1659()