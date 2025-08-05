#!/usr/bin/env python3
"""
Fix the specific syntax error in ai_learning_service.py
"""

def fix_specific_syntax_error():
    """Fix the specific syntax error in the logger.info call"""
    file_path = "app/services/ai_learning_service.py"
    
    print(f"🔧 Fixing specific syntax error in {file_path}...")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The issue is in the logger.info call around line 1665-1668
    # We need to fix the mismatched parentheses
    
    # Find and fix the problematic logger.info call
    old_pattern = '''                    logger.info("Updated existing learning pattern",
                                learning_data={'pattern': pattern,
                                success_rate=existing.success_rate,
                                applied_count=existing.applied_count)'''
    
    new_pattern = '''                    logger.info(
                        f"Updated existing learning pattern: pattern={pattern}, success_rate={existing.success_rate}, applied_count={existing.applied_count}"
                    )'''
    
    if old_pattern in content:
        content = content.replace(old_pattern, new_pattern)
        print("✅ Fixed the logger.info call syntax error")
    else:
        print("⚠️ Could not find the exact pattern, trying alternative fix...")
        
        # Alternative fix - look for the specific lines and fix them
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            if i == 1664:  # Line 1665 (0-indexed)
                # Replace the problematic logger.info call
                fixed_lines.append('                    logger.info(')
                fixed_lines.append('                        f"Updated existing learning pattern: pattern={pattern}, success_rate={existing.success_rate}, applied_count={existing.applied_count}"')
                fixed_lines.append('                    )')
            elif i == 1665 or i == 1666 or i == 1667:  # Skip the problematic lines
                continue
            else:
                fixed_lines.append(line)
        
        content = '\n'.join(fixed_lines)
        print("✅ Applied alternative fix")
    
    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ File updated successfully")
    
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
    fix_specific_syntax_error() 