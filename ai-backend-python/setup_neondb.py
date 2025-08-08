#!/usr/bin/env python3
"""
NeonDB Setup Script
This script helps you configure your NeonDB connection for the AI Backend.
"""

import os
import re
from urllib.parse import urlparse

def validate_neon_url(url):
    """Validate NeonDB connection URL format"""
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ['postgresql', 'postgresql+asyncpg']:
            return False, "URL must start with postgresql:// or postgresql+asyncpg://"
        
        if not parsed.hostname:
            return False, "Hostname is required"
        
        if not parsed.username:
            return False, "Username is required"
        
        if not parsed.password:
            return False, "Password is required"
        
        if not parsed.path or parsed.path == '/':
            return False, "Database name is required"
        
        return True, "URL format is valid"
    except Exception as e:
        return False, f"Invalid URL format: {str(e)}"

def setup_neondb():
    """Interactive setup for NeonDB"""
    print("🚀 NeonDB Setup for AI Backend")
    print("=" * 50)
    print()
    print("To get your NeonDB connection string:")
    print("1. Go to https://console.neon.tech")
    print("2. Create a new project or select existing one")
    print("3. Go to 'Connection Details'")
    print("4. Copy the connection string")
    print()
    
    while True:
        neon_url = input("Enter your NeonDB connection string: ").strip()
        
        if not neon_url:
            print("❌ Connection string cannot be empty")
            continue
        
        # Validate the URL
        is_valid, message = validate_neon_url(neon_url)
        
        if not is_valid:
            print(f"❌ {message}")
            continue
        
        # Convert to asyncpg format if needed
        if neon_url.startswith('postgresql://'):
            neon_url = neon_url.replace('postgresql://', 'postgresql+asyncpg://', 1)
        
        print(f"✅ {message}")
        print(f"📝 Your connection string: {neon_url}")
        
        # Update .env file
        env_file = "ai-backend-python/.env"
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                content = f.read()
            
            # Replace DATABASE_URL
            if 'DATABASE_URL=' in content:
                content = re.sub(
                    r'DATABASE_URL=.*',
                    f'DATABASE_URL={neon_url}',
                    content
                )
            else:
                content += f'\nDATABASE_URL={neon_url}'
            
            with open(env_file, 'w') as f:
                f.write(content)
            
            print(f"✅ Updated {env_file} with your NeonDB connection")
        else:
            print(f"⚠️  {env_file} not found. Please manually add:")
            print(f"   DATABASE_URL={neon_url}")
        
        break

if __name__ == "__main__":
    setup_neondb() 