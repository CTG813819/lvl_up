#!/usr/bin/env python3
"""
Script to update all router files to use get_db instead of get_session for FastAPI dependencies
"""

import os
import re

def update_file(file_path):
    """Update a single file to use get_db instead of get_session"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update import statement
        content = re.sub(
            r'from app\.core\.database import get_session',
            'from app.core.database import get_db',
            content
        )
        
        # Update Depends(get_session) to Depends(get_db)
        content = re.sub(
            r'Depends\(get_session\)',
            'Depends(get_db)',
            content
        )
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Updated {file_path}")
        return True
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def main():
    """Update all router files"""
    router_dir = "ai-backend-python/app/routers"
    
    if not os.path.exists(router_dir):
        print(f"Router directory not found: {router_dir}")
        return
    
    updated_count = 0
    total_count = 0
    
    for filename in os.listdir(router_dir):
        if filename.endswith('.py'):
            file_path = os.path.join(router_dir, filename)
            total_count += 1
            if update_file(file_path):
                updated_count += 1
    
    print(f"\nUpdated {updated_count}/{total_count} router files")

if __name__ == "__main__":
    main() 