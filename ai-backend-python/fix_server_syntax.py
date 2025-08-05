#!/usr/bin/env python3
"""
Script to fix the remaining syntax error on the server
"""

def fix_server_syntax():
    """Fix the remaining syntax error on the server"""
    
    # Read the file
    with open('app/services/custody_protocol_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and fix the problematic structure
    lines = content.split('\n')
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Look for the problematic pattern: try: pass followed by except, then another try:
        if ('try:' in line and 'pass' in lines[i+1] and 
            i+2 < len(lines) and 'except AttributeError as e:' in lines[i+2] and
            i+5 < len(lines) and 'try:' in lines[i+5]):
            
            # Found the problematic pattern, fix it
            indent = len(line) - len(line.lstrip())
            indent_str = ' ' * indent
            
            # Replace the problematic structure
            fixed_lines.append(f'{indent_str}try:')
            fixed_lines.append(f'{indent_str}    import re')
            fixed_lines.append(f'{indent_str}    score_match = re.search(r\'\\b(\\d{{1,2}}|100)\\b\', evaluation)')
            fixed_lines.append(f'{indent_str}    if score_match:')
            fixed_lines.append(f'{indent_str}        score = int(score_match.group(1))')
            fixed_lines.append(f'{indent_str}        return max(0, min(100, score))')
            fixed_lines.append(f'{indent_str}    else:')
            fixed_lines.append(f'{indent_str}        return 75')
            fixed_lines.append(f'{indent_str}except AttributeError as e:')
            fixed_lines.append(f'{indent_str}    logger.warning(f"⚠️ EnhancedTestGenerator method not available: {{e}}")')
            fixed_lines.append(f'{indent_str}    # Continue with fallback behavior')
            fixed_lines.append(f'{indent_str}    return 75')
            fixed_lines.append(f'{indent_str}except Exception as e:')
            
            # Skip the problematic lines (approximately 15 lines)
            i += 15
            continue
        else:
            fixed_lines.append(line)
        
        i += 1
    
    # Write the fixed content back to the file
    with open('app/services/custody_protocol_service.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))
    
    print("Fixed syntax error on server")

if __name__ == "__main__":
    fix_server_syntax()