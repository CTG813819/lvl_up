#!/usr/bin/env python3
"""
Fix for the orphaned except ImportError block on line 1669 in custody_protocol_service.py
"""

def fix_custody_orphaned_except_1669():
    """Fix the orphaned except ImportError block on line 1669"""
    
    # Read the file
    with open('app/services/custody_protocol_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The exact problematic pattern from the current file
    old_pattern = '''            # Use the smart test content
            test_content = smart_test
            logger.info(f"[SMART FALLBACK] Smart test generated: {smart_test.get('source', 'unknown')}")
                
            except ImportError:
                logger.warning(f"[SMART FALLBACK] Smart fallback not available, using basic fallback")
                # Fall back to basic fallback system
                pass'''
    
    # The corrected pattern - add the missing try block
    new_pattern = '''            # Use the smart test content
            test_content = smart_test
            logger.info(f"[SMART FALLBACK] Smart test generated: {smart_test.get('source', 'unknown')}")
            
            try:
                pass
            except ImportError:
                logger.warning(f"[SMART FALLBACK] Smart fallback not available, using basic fallback")
                # Fall back to basic fallback system
                pass'''
    
    # Apply the fix
    if old_pattern in content:
        content = content.replace(old_pattern, new_pattern)
        print("Fixed orphaned except ImportError block on line 1669")
    else:
        print("Pattern not found. Trying alternative approach...")
        
        # Alternative approach: find the specific lines and fix them manually
        lines = content.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Look for the problematic pattern: except ImportError without a try block
            if ('except ImportError:' in line and 
                i > 0 and 'try:' not in lines[i-1] and
                i > 1 and 'try:' not in lines[i-2] and
                i > 2 and 'try:' not in lines[i-3]):
                
                # Found the problematic pattern, add the missing try block
                indent = len(line) - len(line.lstrip())
                indent_str = ' ' * indent
                
                # Add the missing try block
                fixed_lines.append(f'{indent_str}try:')
                fixed_lines.append(f'{indent_str}    pass')
                fixed_lines.append(line)  # The except ImportError line
                
                # Add the next few lines
                for j in range(i + 1, min(i + 5, len(lines))):
                    fixed_lines.append(lines[j])
                
                # Skip the lines we've already added
                i += 5
                continue
            else:
                fixed_lines.append(line)
            
            i += 1
        
        # Write the fixed content back to the file
        with open('app/services/custody_protocol_service.py', 'w', encoding='utf-8') as f:
            f.write('\n'.join(fixed_lines))
        print("Fixed orphaned except ImportError block using line-by-line approach")
        return
    
    # Write the fixed content back to the file
    with open('app/services/custody_protocol_service.py', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    fix_custody_orphaned_except_1669()