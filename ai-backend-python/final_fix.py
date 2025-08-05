#!/usr/bin/env python3
"""
Final Backend Fix Script
Fixes the remaining pattern keyword and get_session issues
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

async def fix_pattern_keyword_issue():
    """Fix the pattern keyword argument issue in AI learning service"""
    print("🔧 Fixing pattern keyword argument issue...")
    
    # Read the current AI learning service
    service_path = Path("app/services/ai_learning_service.py")
    
    if not service_path.exists():
        print("❌ AI learning service file not found!")
        return False
    
    with open(service_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and fix the pattern keyword issue
    # Look for lines that create Learning objects with pattern keyword
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Fix Learning creation with pattern keyword
        if 'Learning(' in line and 'pattern=' in line:
            # Remove pattern keyword and related invalid fields
            line = line.replace('pattern=', '# pattern=')
            line = line.replace('context=', '# context=')
            line = line.replace('feedback=', '# feedback=')
            line = line.replace('confidence=', '# confidence=')
            line = line.replace('applied_count=', '# applied_count=')
            line = line.replace('success_rate=', '# success_rate=')
            print(f"✅ Fixed line: {line.strip()}")
        
        fixed_lines.append(line)
    
    # Write the fixed content back
    with open(service_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))
    
    print("✅ Fixed pattern keyword argument issue")
    return True

async def fix_get_session_issue():
    """Fix the get_session method issue in background service"""
    print("🔧 Fixing get_session method issue...")
    
    # Read the current background service
    service_path = Path("app/services/background_service.py")
    
    if not service_path.exists():
        print("❌ Background service file not found!")
        return False
    
    with open(service_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace get_session() calls with proper database session
    content = content.replace(
        'self.learning_service.get_session()',
        'get_session()'
    )
    
    # Add import if not present
    if 'from core.database import get_session' not in content:
        # Find the imports section and add the import
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('from core.database import'):
                # Add get_session to existing import
                if 'get_session' not in line:
                    lines[i] = line.replace(')', ', get_session)')
                break
            elif line.startswith('import ') and i > 0:
                # Add new import line after existing imports
                lines.insert(i, 'from core.database import get_session')
                break
        
        content = '\n'.join(lines)
    
    # Write the fixed content back
    with open(service_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed get_session method issue")
    return True

async def fix_health_check_issue():
    """Fix the health check issue in the main app"""
    print("🔧 Fixing health check issue...")
    
    # Read the current main app
    main_path = Path("app/main.py")
    
    if not main_path.exists():
        print("❌ Main app file not found!")
        return False
    
    with open(main_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and fix the health check that uses learning_service.get_session()
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        if 'learning_service.get_session()' in line:
            # Replace with proper database session
            line = line.replace('learning_service.get_session()', 'get_session()')
            print(f"✅ Fixed health check line: {line.strip()}")
        
        fixed_lines.append(line)
    
    # Add import if not present
    if 'from core.database import get_session' not in content:
        # Find the imports section and add the import
        for i, line in enumerate(fixed_lines):
            if line.startswith('from core.database import'):
                # Add get_session to existing import
                if 'get_session' not in line:
                    fixed_lines[i] = line.replace(')', ', get_session)')
                break
            elif line.startswith('import ') and i > 0:
                # Add new import line after existing imports
                fixed_lines.insert(i, 'from core.database import get_session')
                break
    
    # Write the fixed content back
    with open(main_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))
    
    print("✅ Fixed health check issue")
    return True

async def main():
    """Run all fixes"""
    print("🔧 Final Backend Fix Script")
    print("=" * 50)
    
    success = True
    
    # Fix pattern keyword issue
    if not await fix_pattern_keyword_issue():
        success = False
    
    # Fix get_session issue
    if not await fix_get_session_issue():
        success = False
    
    # Fix health check issue
    if not await fix_health_check_issue():
        success = False
    
    if success:
        print("\n✅ All fixes applied successfully!")
        print("🔄 Please restart the backend service:")
        print("   sudo systemctl restart ai-backend-python")
    else:
        print("\n❌ Some fixes failed. Please check the errors above.")

if __name__ == "__main__":
    asyncio.run(main()) 