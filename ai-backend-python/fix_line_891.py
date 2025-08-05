#!/usr/bin/env python3
"""
Fix the syntax error on line 891 in imperium_learning_controller.py
"""

def fix_line_891():
    """Fix the async with syntax error on line 891"""
    
    # Read the file
    with open("app/services/imperium_learning_controller.py", "r") as f:
        lines = f.readlines()
    
    # Check line 891 (0-indexed is 890)
    if len(lines) >= 891:
        line_891 = lines[890]  # 0-indexed
        print(f"Line 891: {line_891.strip()}")
        
        # Check if this is the async with line
        if "async with get_session() as session:" in line_891:
            print("Found the problematic line")
            
            # Check if the method is properly defined as async
            # Look for the method definition
            method_start = None
            for i in range(890, 0, -1):
                if lines[i].strip().startswith("async def _load_persisted_agent_metrics"):
                    method_start = i
                    break
                elif lines[i].strip().startswith("def _load_persisted_agent_metrics"):
                    print(f"Found method definition on line {i+1}, but it's not async!")
                    # Fix: make it async
                    lines[i] = lines[i].replace("def _load_persisted_agent_metrics", "async def _load_persisted_agent_metrics")
                    print("Fixed: Made method async")
                    break
            
            if method_start is None:
                print("Could not find method definition")
                return False
        else:
            print("Line 891 is not the expected async with line")
            return False
    else:
        print("File has fewer than 891 lines")
        return False
    
    # Write the fixed content back
    with open("app/services/imperium_learning_controller.py", "w") as f:
        f.writelines(lines)
    
    print("Fixed the file")
    return True

def test_syntax():
    """Test if the file has valid syntax"""
    try:
        with open("app/services/imperium_learning_controller.py", "r") as f:
            content = f.read()
        
        compile(content, "imperium_learning_controller.py", "exec")
        print("✓ File compiles successfully")
        return True
    except SyntaxError as e:
        print(f"✗ Syntax error: {e}")
        print(f"Line {e.lineno}: {e.text}")
        return False

def main():
    """Main function"""
    print("Fixing line 891 syntax error...")
    
    if fix_line_891():
        print("Applied fix. Testing syntax...")
        if test_syntax():
            print("✓ Syntax error fixed!")
        else:
            print("✗ Still has syntax errors")
    else:
        print("Could not apply fix")

if __name__ == "__main__":
    main() 