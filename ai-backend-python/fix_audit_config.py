#!/usr/bin/env python3
"""
Fix Audit Configuration Script
This script updates the audit script to use the correct Neon database connection
"""

import os
import re
from urllib.parse import urlparse

def parse_neon_url(database_url):
    """Parse Neon database URL to extract connection parameters"""
    # Remove the extra path that was accidentally added
    clean_url = database_url.split('/ubuntu@')[0]
    
    parsed = urlparse(clean_url)
    
    # Extract username and password from the URL
    username = parsed.username
    password = parsed.password
    
    # Extract host and database name
    host = parsed.hostname
    database = parsed.path.lstrip('/')
    
    # Extract port if present
    port = parsed.port or 5432
    
    return {
        'host': host,
        'port': port,
        'database': database,
        'user': username,
        'password': password,
        'sslmode': 'require'
    }

def update_audit_script():
    """Update the audit script with correct database configuration"""
    
    # Your Neon database URL
    database_url = "postgresql+asyncpg://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    
    # Parse the database URL
    db_config = parse_neon_url(database_url)
    
    # Read the original audit script
    with open('comprehensive_system_audit.py', 'r') as f:
        content = f.read()
    
    # Update the database configuration section
    new_db_config = f"""        self.db_config = {{
            'host': '{db_config['host']}',
            'port': {db_config['port']},
            'database': '{db_config['database']}',
            'user': '{db_config['user']}',
            'password': '{db_config['password']}',
            'sslmode': '{db_config['sslmode']}'
        }}"""
    
    # Replace the old database configuration
    pattern = r'self\.db_config = \{[\s\S]*?\}'
    updated_content = re.sub(pattern, new_db_config, content)
    
    # Also update the base URL to use the correct port (8000 as per your memory)
    base_url_pattern = r'self\.base_url = "http://localhost:\d+"'
    updated_content = re.sub(base_url_pattern, 'self.base_url = "http://localhost:8000"', updated_content)
    
    # Write the updated script
    with open('comprehensive_system_audit_fixed.py', 'w') as f:
        f.write(updated_content)
    
    print("✅ Audit script updated with correct database configuration")
    print(f"📊 Database: {db_config['database']} on {db_config['host']}")
    print(f"🔗 Backend URL: http://localhost:8000")
    
    return 'comprehensive_system_audit_fixed.py'

def create_environment_setup():
    """Create environment setup script"""
    
    env_content = """#!/bin/bash
# Environment setup for LVL_UP AI Backend

# Database Configuration
export DB_HOST="ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech"
export DB_PORT="5432"
export DB_NAME="neondb"
export DB_USER="neondb_owner"
export DB_PASSWORD="npg_TV1hbOzC9ReA"
export DB_SSL_MODE="require"

# Backend Configuration
export BACKEND_PORT="8000"
export BACKEND_HOST="localhost"

# AI Service Configuration
export OPENAI_API_KEY="your-openai-api-key-here"
export GITHUB_TOKEN="your-github-token-here"

# Other configurations
export ENVIRONMENT="production"
export LOG_LEVEL="INFO"

echo "✅ Environment variables set for LVL_UP AI Backend"
echo "📊 Database: $DB_NAME on $DB_HOST"
echo "🔗 Backend: http://$BACKEND_HOST:$BACKEND_PORT"
"""
    
    with open('setup_environment.sh', 'w') as f:
        f.write(env_content)
    
    print("✅ Environment setup script created: setup_environment.sh")

def create_quick_fix_script():
    """Create a quick fix script to run the corrected audit"""
    
    fix_content = """#!/bin/bash
# Quick Fix Script for LVL_UP AI Backend Audit

echo "🔧 Fixing LVL_UP AI Backend Audit Configuration..."

# Set environment variables
export DB_HOST="ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech"
export DB_PORT="5432"
export DB_NAME="neondb"
export DB_USER="neondb_owner"
export DB_PASSWORD="npg_TV1hbOzC9ReA"
export DB_SSL_MODE="require"

# Activate virtual environment
source audit_env/bin/activate

# Run the fixed audit script
echo "🚀 Running comprehensive system audit with correct configuration..."
python comprehensive_system_audit_fixed.py

echo "✅ Audit completed! Check the results above."
"""
    
    with open('run_fixed_audit.sh', 'w') as f:
        f.write(fix_content)
    
    print("✅ Quick fix script created: run_fixed_audit.sh")

def main():
    """Main function to fix all audit configuration issues"""
    
    print("🔧 Fixing LVL_UP AI Backend Audit Configuration")
    print("=" * 60)
    
    try:
        # Update the audit script
        fixed_script = update_audit_script()
        
        # Create environment setup
        create_environment_setup()
        
        # Create quick fix script
        create_quick_fix_script()
        
        print("\n" + "=" * 60)
        print("✅ All fixes completed!")
        print("\n📋 Next steps:")
        print("1. Run: chmod +x run_fixed_audit.sh")
        print("2. Run: ./run_fixed_audit.sh")
        print("3. Or manually: source audit_env/bin/activate && python comprehensive_system_audit_fixed.py")
        print("\n🔧 The audit will now:")
        print("   - Connect to your Neon database correctly")
        print("   - Use the correct backend port (8000)")
        print("   - Have proper environment variables set")
        
    except Exception as e:
        print(f"❌ Error during fix: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    main() 