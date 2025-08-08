#!/usr/bin/env python3
"""
Direct fix for custody_protocol_service.py syntax error
"""

def fix_custody_direct():
    """Direct fix for the syntax error"""
    file_path = "ai-backend-python/app/services/custody_protocol_service.py"
    
    print(f"🔧 Direct fix for {file_path}...")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the problematic lines and fix them
    fixed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check if this is the function definition line
        if 'async def _persist_custody_metrics_to_database' in line:
            # Ensure it has proper indentation and colon
            if not line.strip().endswith(':'):
                line = line.rstrip() + ':\n'
            fixed_lines.append(line)
            i += 1
            
            # Next line should be the docstring with 8 spaces indentation
            if i < len(lines) and '"""Persist custody metrics to the database"""' in lines[i]:
                fixed_lines.append('        """Persist custody metrics to the database"""\n')
                i += 1
            else:
                # Add the docstring if missing
                fixed_lines.append('        """Persist custody metrics to the database"""\n')
            
            # Continue with the rest of the method
            while i < len(lines):
                next_line = lines[i]
                if 'async def _load_custody_metrics_from_database' in next_line:
                    break
                if 'class ' in next_line and i > 0:
                    break
                
                # Fix indentation for the method body
                if next_line.strip() == 'try:':
                    fixed_lines.append('        try:\n')
                elif next_line.strip() == 'except Exception as e:':
                    fixed_lines.append('        except Exception as e:\n')
                elif next_line.strip() == 'logger.error(':
                    fixed_lines.append('            logger.error(f"Error persisting custody metrics to database: {str(e)}")\n')
                elif next_line.strip() == '':
                    fixed_lines.append('\n')
                else:
                    # Keep other lines as they are
                    fixed_lines.append(next_line)
                
                i += 1
        else:
            fixed_lines.append(line)
            i += 1
    
    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print("✅ Fixed custody protocol service")
    
    # Test the syntax
    try:
        import ast
        with open(file_path, 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        print("✅ Syntax check passed!")
    except SyntaxError as e:
        print(f"❌ Syntax check failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    fix_custody_direct() 