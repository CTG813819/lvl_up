#!/usr/bin/env python3
"""
Import Path Fix Script
Fixes the incorrect import paths in the backend
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

async def fix_background_service_imports():
    """Fix import paths in background service"""
    print("🔧 Fixing background service imports...")
    
    # Read the current background service
    service_path = Path("app/services/background_service.py")
    
    if not service_path.exists():
        print("❌ Background service file not found!")
        return False
    
    with open(service_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the import paths
    content = content.replace(
        'from core.database import get_session',
        'from app.core.database import get_session'
    )
    
    content = content.replace(
        'from core.config import settings',
        'from app.core.config import settings'
    )
    
    content = content.replace(
        'from core.database import init_database',
        'from app.core.database import init_database'
    )
    
    # Write the fixed content back
    with open(service_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed background service imports")
    return True

async def fix_main_app_imports():
    """Fix import paths in main app"""
    print("🔧 Fixing main app imports...")
    
    # Read the current main app
    main_path = Path("app/main.py")
    
    if not main_path.exists():
        print("❌ Main app file not found!")
        return False
    
    with open(main_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the import paths
    content = content.replace(
        'from core.database import get_session',
        'from app.core.database import get_session'
    )
    
    content = content.replace(
        'from core.config import settings',
        'from app.core.config import settings'
    )
    
    # Write the fixed content back
    with open(main_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed main app imports")
    return True

async def fix_other_service_imports():
    """Fix import paths in other services"""
    print("🔧 Fixing other service imports...")
    
    # List of services to check
    services = [
        "app/services/ai_learning_service.py",
        "app/services/ai_growth_service.py",
        "app/services/imperium_service.py",
        "app/services/guardian_service.py",
        "app/services/conquest_service.py"
    ]
    
    for service_path in services:
        path = Path(service_path)
        if not path.exists():
            continue
            
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix common import patterns
        original_content = content
        
        content = content.replace(
            'from core.database import get_session',
            'from app.core.database import get_session'
        )
        
        content = content.replace(
            'from core.config import settings',
            'from app.core.config import settings'
        )
        
        content = content.replace(
            'from core.database import init_database',
            'from app.core.database import init_database'
        )
        
        # Only write if changes were made
        if content != original_content:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed imports in {service_path}")
    
    return True

async def main():
    """Run all import fixes"""
    print("🔧 Import Path Fix Script")
    print("=" * 40)
    
    success = True
    
    # Fix background service imports
    if not await fix_background_service_imports():
        success = False
    
    # Fix main app imports
    if not await fix_main_app_imports():
        success = False
    
    # Fix other service imports
    if not await fix_other_service_imports():
        success = False
    
    if success:
        print("\n✅ All import fixes applied successfully!")
        print("🔄 Please restart the backend service:")
        print("   sudo systemctl restart ai-backend-python")
    else:
        print("\n❌ Some fixes failed. Please check the errors above.")

if __name__ == "__main__":
    asyncio.run(main()) 