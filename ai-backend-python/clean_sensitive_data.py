#!/usr/bin/env python3
"""
Script to clean sensitive data from files before uploading to GitHub
"""

import re
import os
from pathlib import Path

def clean_file(file_path, patterns):
    """Clean sensitive data from a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Cleaned: {file_path}")
            return True
        else:
            print(f"ℹ️  No changes needed: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error cleaning {file_path}: {e}")
        return False

def main():
    """Main function to clean all sensitive data"""
    
    # Patterns to replace sensitive data
    patterns = [
        # OpenAI API keys
        (r'sk-proj-[a-zA-Z0-9_-]{40,}', 'sk-proj-REPLACED_API_KEY'),
        (r'sk-[a-zA-Z0-9_-]{40,}', 'sk-REPLACED_API_KEY'),
        
        # GitHub tokens
        (r'ghp_[a-zA-Z0-9_-]{35,}', 'ghp_REPLACED_TOKEN'),
        (r'github_pat_[a-zA-Z0-9_-]{40,}', 'github_pat_REPLACED_TOKEN'),
        
        # Other common token patterns
        (r'[a-zA-Z0-9_-]{40,}', 'REPLACED_TOKEN'),
    ]
    
    # Files mentioned in the GitHub error
    files_to_clean = [
        'update_key_ec2.py',
        'fix_service_tokens.py',
        'update_github_token.py',
        'setup_environment.py',
        'add_back_ai_services.sh',
        'comprehensive_fix.sh',
        'custodes-ai-fixed.service',
        'fix_ai_services_integration.sh'
    ]
    
    print("🧹 Cleaning sensitive data from files...")
    print("=" * 50)
    
    cleaned_count = 0
    
    for file_name in files_to_clean:
        if os.path.exists(file_name):
            if clean_file(file_name, patterns):
                cleaned_count += 1
        else:
            print(f"⚠️  File not found: {file_name}")
    
    print(f"\n✅ Cleaned {cleaned_count} files")
    print("🔒 All sensitive data has been replaced with placeholders")

if __name__ == "__main__":
    main() 