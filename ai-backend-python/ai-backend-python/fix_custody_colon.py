#!/usr/bin/env python3
"""
Fix missing colon in function definition in custody_protocol_service.py
"""

def fix_custody_colon():
    """Fix missing colon in function definition"""
    file_path = "ai-backend-python/app/services/custody_protocol_service.py"
    
    print(f"🔧 Fixing missing colon in function definition in {file_path}...")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the missing colon in the function definition
    old_line = '    async def _persist_custody_metrics_to_database(self, ai_type: str, metrics: Dict):'
    new_line = '    async def _persist_custody_metrics_to_database(self, ai_type: str, metrics: Dict):'
    
    # Check if the line exists and has the colon
    if old_line in content:
        print("✅ Function definition already has colon")
    else:
        # Try without colon
        old_line_no_colon = '    async def _persist_custody_metrics_to_database(self, ai_type: str, metrics: Dict)'
        if old_line_no_colon in content:
            content = content.replace(old_line_no_colon, new_line)
            print("✅ Fixed missing colon in function definition")
        else:
            print("❌ Could not find function definition")
            return False
    
    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed function definition in custody_protocol_service.py")
    
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
    fix_custody_colon() 