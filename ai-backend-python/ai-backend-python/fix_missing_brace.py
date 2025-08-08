#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the project path
sys.path.append('/home/ubuntu/ai-backend-python')

def fix_missing_brace():
    """Fix missing closing brace in Project Warmaster service file"""
    
    print("🔧 Fixing missing closing brace...")
    
    # Read current service file
    service_file_path = '/home/ubuntu/ai-backend-python/app/services/project_berserk_service.py'
    
    try:
        with open(service_file_path, 'r') as f:
            current_content = f.read()
    except FileNotFoundError:
        print(f"❌ Service file not found: {service_file_path}")
        return
    
    # Find the problematic section and fix it
    if 'async def stealth_device_assimilation(self, user_id: str = None) -> dict:' in current_content:
        # Find the method and add the missing closing brace
        method_start = current_content.find('async def stealth_device_assimilation(self, user_id: str = None) -> dict:')
        method_end = current_content.find('async def get_security_status(self, db: AsyncSession) -> Dict[str, Any]:')
        
        if method_start != -1 and method_end != -1:
            # Extract the method content
            method_content = current_content[method_start:method_end]
            
            # Check if the closing brace is missing
            if method_content.count('{') > method_content.count('}'):
                # Add the missing closing brace
                fixed_method = method_content.rstrip() + '\n        }\n\n'
                
                # Replace the method
                before_method = current_content[:method_start]
                after_method = current_content[method_end:]
                fixed_content = before_method + fixed_method + after_method
                
                # Write the fixed service file
                try:
                    with open(service_file_path, 'w') as f:
                        f.write(fixed_content)
                    
                    print("✅ Missing closing brace fixed successfully!")
                    
                except Exception as e:
                    print(f"❌ Error fixing missing brace: {e}")
            else:
                print("✅ No missing brace found")
        else:
            print("❌ Could not locate the method to fix")
    else:
        print("❌ Could not find stealth_device_assimilation method")

if __name__ == "__main__":
    fix_missing_brace() 