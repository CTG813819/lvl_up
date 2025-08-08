#!/usr/bin/env python3
"""
Fix script for imperium_learning_controller.py syntax error
"""

import os
import shutil
from datetime import datetime

def fix_imperium_learning_controller():
    """Fix the syntax error in imperium_learning_controller.py"""
    
    # Create backup
    backup_file = f"imperium_learning_controller_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    shutil.copy("app/services/imperium_learning_controller.py", backup_file)
    print(f"Created backup: {backup_file}")
    
    # Read the file
    with open("app/services/imperium_learning_controller.py", "r") as f:
        content = f.read()
    
    # Check for common syntax issues
    issues_found = []
    
    # Check for unclosed parentheses, brackets, braces
    open_paren = content.count("(")
    close_paren = content.count(")")
    if open_paren != close_paren:
        issues_found.append(f"Mismatched parentheses: {open_paren} open, {close_paren} close")
    
    open_bracket = content.count("[")
    close_bracket = content.count("]")
    if open_bracket != close_bracket:
        issues_found.append(f"Mismatched brackets: {open_bracket} open, {close_bracket} close")
    
    open_brace = content.count("{")
    close_brace = content.count("}")
    if open_brace != close_brace:
        issues_found.append(f"Mismatched braces: {open_brace} open, {close_brace} close")
    
    # Check for unclosed quotes
    single_quotes = content.count("'")
    double_quotes = content.count('"')
    if single_quotes % 2 != 0:
        issues_found.append("Unclosed single quotes")
    if double_quotes % 2 != 0:
        issues_found.append("Unclosed double quotes")
    
    if issues_found:
        print("Syntax issues found:")
        for issue in issues_found:
            print(f"  - {issue}")
        return False
    
    # Try to compile the file to check for syntax errors
    try:
        compile(content, "imperium_learning_controller.py", "exec")
        print("File compiles successfully - no syntax errors found")
    except SyntaxError as e:
        print(f"Syntax error found: {e}")
        print(f"Line {e.lineno}: {e.text}")
        return False
    
    # If we get here, the file should be syntactically correct
    print("File appears to be syntactically correct")
    return True

def check_imports():
    """Check if all imports are working correctly"""
    print("\nChecking imports...")
    
    try:
        import sys
        sys.path.insert(0, ".")
        
        # Try importing the module
        from app.services.imperium_learning_controller import ImperiumLearningController
        print("✓ ImperiumLearningController imported successfully")
        
        # Try creating an instance
        controller = ImperiumLearningController()
        print("✓ ImperiumLearningController instance created successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def main():
    """Main function"""
    print("Fixing imperium_learning_controller.py syntax error...")
    
    # Check if file exists
    if not os.path.exists("app/services/imperium_learning_controller.py"):
        print("Error: imperium_learning_controller.py not found")
        print("Current directory:", os.getcwd())
        print("Looking for: app/services/imperium_learning_controller.py")
        return
    
    # Fix the file
    if fix_imperium_learning_controller():
        print("\nFile syntax check passed")
        
        # Check imports
        if check_imports():
            print("\n✓ All checks passed - file should work correctly")
        else:
            print("\n✗ Import check failed - there may still be issues")
    else:
        print("\n✗ Syntax check failed - manual intervention required")

if __name__ == "__main__":
    main() 