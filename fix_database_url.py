#!/usr/bin/env python3
"""
Fix Database URL and Initialize Database
"""

import os
import re

def fix_database_url():
    """Fix the database URL format for asyncpg"""
    print("🔧 Fixing database URL format...")
    
    env_file = ".env"
    if not os.path.exists(env_file):
        print("❌ .env file not found")
        return False
    
    # Read the current .env file
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Find the DATABASE_URL line
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('DATABASE_URL='):
            # Extract the base URL without query parameters
            url = line.split('=')[1]
            # Remove query parameters that cause issues with asyncpg
            base_url = url.split('?')[0]
            # Create the fixed URL
            fixed_url = f"DATABASE_URL={base_url}"
            lines[i] = fixed_url
            print(f"✅ Fixed database URL: {fixed_url}")
            break
    
    # Write the fixed content back
    with open(env_file, 'w') as f:
        f.write('\n'.join(lines))
    
    print("✅ Database URL fixed successfully")
    return True

if __name__ == "__main__":
    fix_database_url() 