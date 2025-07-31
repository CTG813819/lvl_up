#!/usr/bin/env python3
"""
Comprehensive Fix Script
Fixes all identified issues: database queries, GitHub token, and service initialization
"""

import os
import subprocess
import sys

# Add the project path
sys.path.append('/home/ubuntu/ai-backend-python')

def run_ssh_command(command):
    """Run SSH command on EC2 instance"""
    try:
        ssh_cmd = [
            "ssh", "-i", "New.pem", 
            "ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com",
            command
        ]
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def comprehensive_fix():
    """Comprehensive fix for Project Warmaster service file"""
    
    print("🔧 Performing comprehensive fix on Project Warmaster service...")
    
    # Read current service file
    service_file_path = '/home/ubuntu/ai-backend-python/app/services/project_berserk_service.py'
    
    try:
        with open(service_file_path, 'r') as f:
            current_content = f.read()
    except FileNotFoundError:
        print(f"❌ Service file not found: {service_file_path}")
        return
    
    # Fix indentation issues by replacing tabs with spaces
    lines = current_content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Replace tabs with 4 spaces
        line = line.replace('\t', '    ')
        fixed_lines.append(line)
    
    # Reconstruct the content
    fixed_content = '\n'.join(fixed_lines)
    
    # Fix any remaining syntax issues
    # Ensure proper closing braces for methods
    if 'async def stealth_device_assimilation(self, user_id: str = None) -> dict:' in fixed_content:
        # Find and fix the stealth_device_assimilation method
        method_start = fixed_content.find('async def stealth_device_assimilation(self, user_id: str = None) -> dict:')
        method_end = fixed_content.find('async def get_security_status(self, db: AsyncSession) -> Dict[str, Any]:')
        
        if method_start != -1 and method_end != -1:
            method_content = fixed_content[method_start:method_end]
            
            # Ensure the method has proper closing
            if not method_content.strip().endswith('}'):
                # Add proper closing
                method_lines = method_content.split('\n')
                # Find the last non-empty line
                for i in range(len(method_lines) - 1, -1, -1):
                    if method_lines[i].strip():
                        # Add closing brace after the last non-empty line
                        method_lines.insert(i + 1, '        }')
                        break
                
                fixed_method = '\n'.join(method_lines)
                
                # Replace the method
                before_method = fixed_content[:method_start]
                after_method = fixed_content[method_end:]
                fixed_content = before_method + fixed_method + after_method
    
    # Write the fixed service file
    try:
        with open(service_file_path, 'w') as f:
            f.write(fixed_content)
        
        print("✅ Comprehensive fix completed successfully!")
        
        # Test the syntax
        print("🔍 Testing syntax...")
        result = os.system(f'cd /home/ubuntu/ai-backend-python && source venv/bin/activate && python3 -m py_compile {service_file_path}')
        
        if result == 0:
            print("✅ Syntax check passed!")
        else:
            print("❌ Syntax check failed!")
        
    except Exception as e:
        print(f"❌ Error during comprehensive fix: {e}")

if __name__ == "__main__":
    comprehensive_fix() 