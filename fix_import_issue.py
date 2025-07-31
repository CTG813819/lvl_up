#!/usr/bin/env python3
"""
Fix import issue in enhanced_subject_learning_service.py
"""

import re

def fix_import_issue():
    """Fix the import issue in enhanced_subject_learning_service.py"""
    
    # Read the current file
    with open('app/services/enhanced_subject_learning_service.py', 'r') as f:
        content = f.read()
    
    # Fix the import line
    old_import = "from app.services.openai_service import call_openai"
    new_import = "from app.services.openai_service import OpenAIService"
    
    # Replace the import
    content = content.replace(old_import, new_import)
    
    # Find all instances of call_openai and replace with proper method calls
    # We need to create an instance first
    content = re.sub(
        r'call_openai\(',
        'OpenAIService().call_openai(',
        content
    )
    
    # Write the fixed content back
    with open('app/services/enhanced_subject_learning_service.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed import issue in enhanced_subject_learning_service.py")

if __name__ == "__main__":
    fix_import_issue() 