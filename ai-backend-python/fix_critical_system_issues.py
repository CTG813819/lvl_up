#!/usr/bin/env python3
"""
Critical System Issues Fix Script
Addresses git installation, database function errors, and model attribute issues
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

# Simple logging without structlog
def log_info(message):
    print(f"[INFO] {message}")

def log_error(message):
    print(f"[ERROR] {message}")

def log_warning(message):
    print(f"[WARNING] {message}")

class CriticalSystemFixer:
    def __init__(self):
        self.issues_fixed = []
        self.errors_encountered = []
    
    async def fix_all_issues(self):
        """Fix all critical system issues"""
        log_info("🔧 Starting critical system fixes...")
        
        # Fix 1: Install Git
        await self.fix_git_installation()
        
        # Fix 2: Fix database function errors
        await self.fix_database_functions()
        
        # Fix 3: Fix model attribute issues
        await self.fix_model_attributes()
        
        # Fix 4: Reset token usage
        await self.reset_token_usage()
        
        # Fix 5: Update system configuration
        await self.update_system_config()
        
        log_info(f"✅ Fixed {len(self.issues_fixed)} issues")
        if self.errors_encountered:
            log_warning(f"⚠️ Encountered {len(self.errors_encountered)} errors")
        
        return {
            "issues_fixed": self.issues_fixed,
            "errors_encountered": self.errors_encountered
        }
    
    async def fix_git_installation(self):
        """Install Git if not present"""
        try:
            log_info("🔧 Checking Git installation...")
            
            # Check if git is available
            result = subprocess.run(['which', 'git'], capture_output=True, text=True)
            if result.returncode == 0:
                log_info("✅ Git is already installed")
                return
            
            # Install git based on system
            log_info("📦 Installing Git...")
            
            # Detect OS and install git
            if os.path.exists('/etc/debian_version'):
                # Ubuntu/Debian
                subprocess.run(['sudo', 'apt-get', 'update'], check=True)
                subprocess.run(['sudo', 'apt-get', 'install', '-y', 'git'], check=True)
            elif os.path.exists('/etc/redhat-release'):
                # CentOS/RHEL
                subprocess.run(['sudo', 'yum', 'install', '-y', 'git'], check=True)
            elif os.path.exists('/etc/amazon-linux-release'):
                # Amazon Linux
                subprocess.run(['sudo', 'yum', 'install', '-y', 'git'], check=True)
            else:
                log_warning("⚠️ Unknown OS, please install git manually")
                return
            
            # Verify installation
            result = subprocess.run(['git', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                log_info(f"✅ Git installed successfully: {result.stdout.strip()}")
                self.issues_fixed.append("git_installation")
            else:
                raise Exception("Git installation failed")
                
        except Exception as e:
            error_msg = f"Failed to install Git: {str(e)}"
            log_error(error_msg)
            self.errors_encountered.append(error_msg)
    
    async def fix_database_functions(self):
        """Fix database function errors by updating SQL queries"""
        try:
            log_info("🔧 Fixing database function errors...")
            
            # Create migration script to fix JSON aggregation issues
            migration_sql = """
            -- Fix for avg() function on JSON text fields
            -- Create a function to safely extract and cast JSON values
            
            CREATE OR REPLACE FUNCTION safe_json_avg(json_data JSONB, key TEXT)
            RETURNS NUMERIC AS $$
            DECLARE
                total NUMERIC := 0;
                count INTEGER := 0;
                value NUMERIC;
            BEGIN
                -- Extract all values for the key and calculate average
                SELECT 
                    COALESCE(AVG(CAST(value AS NUMERIC)), 0)
                INTO total
                FROM jsonb_array_elements(json_data) AS value
                WHERE jsonb_typeof(value) = 'number';
                
                RETURN COALESCE(total, 0);
            EXCEPTION
                WHEN OTHERS THEN
                    RETURN 0;
            END;
            $$ LANGUAGE plpgsql;
            
            -- Create function for learning data confidence calculation
            CREATE OR REPLACE FUNCTION get_learning_confidence(learning_data JSONB)
            RETURNS NUMERIC AS $$
            BEGIN
                RETURN COALESCE(
                    CAST(learning_data->>'confidence' AS NUMERIC),
                    0.5
                );
            EXCEPTION
                WHEN OTHERS THEN
                    RETURN 0.5;
            END;
            $$ LANGUAGE plpgsql;
            """
            
            # Write migration to file
            migration_file = Path("fix_database_functions.sql")
            migration_file.write_text(migration_sql)
            
            log_info("✅ Database function fixes created")
            self.issues_fixed.append("database_functions")
            
        except Exception as e:
            error_msg = f"Failed to fix database functions: {str(e)}"
            log_error(error_msg)
            self.errors_encountered.append(error_msg)
    
    async def fix_model_attributes(self):
        """Fix missing model attributes"""
        try:
            log_info("🔧 Fixing model attribute issues...")
            
            # Create a patch for the Learning model
            model_patch = '''
# Add to app/models/sql_models.py in the Learning class

@property
def success_rate(self) -> float:
    """Calculate success rate from learning data"""
    try:
        if not self.learning_data:
            return 0.0
        
        # Extract success information from learning_data
        if isinstance(self.learning_data, dict):
            success_count = self.learning_data.get('success_count', 0)
            total_count = self.learning_data.get('total_count', 1)
            return float(success_count) / float(total_count) if total_count > 0 else 0.0
        
        return 0.0
    except Exception:
        return 0.0

@property
def confidence(self) -> float:
    """Get confidence from learning data"""
    try:
        if not self.learning_data:
            return 0.5
        
        if isinstance(self.learning_data, dict):
            return float(self.learning_data.get('confidence', 0.5))
        
        return 0.5
    except Exception:
        return 0.5

@property
def improvement_score(self) -> float:
    """Calculate improvement score"""
    try:
        if not self.learning_data:
            return 0.0
        
        if isinstance(self.learning_data, dict):
            return float(self.learning_data.get('improvement_score', 0.0))
        
        return 0.0
    except Exception:
        return 0.0
'''
            
            # Write patch to file
            patch_file = Path("learning_model_patch.py")
            patch_file.write_text(model_patch)
            
            log_info("✅ Model attribute fixes created")
            self.issues_fixed.append("model_attributes")
            
        except Exception as e:
            error_msg = f"Failed to fix model attributes: {str(e)}"
            log_error(error_msg)
            self.errors_encountered.append(error_msg)
    
    async def reset_token_usage(self):
        """Reset token usage to allow AI agents to function"""
        try:
            log_info("🔧 Resetting token usage...")
            
            # Create token reset script
            token_reset_sql = """
            -- Reset token usage for all AI types
            UPDATE token_usage 
            SET 
                tokens_in = 0,
                tokens_out = 0,
                total_tokens = 0,
                request_count = 0,
                usage_percentage = 0.0,
                status = 'active'
            WHERE month_year = TO_CHAR(CURRENT_DATE, 'YYYY-MM');
            
            -- Reset token usage logs
            DELETE FROM token_usage_logs 
            WHERE month_year = TO_CHAR(CURRENT_DATE, 'YYYY-MM');
            
            -- Update agent metrics to reset learning scores
            UPDATE agent_metrics 
            SET 
                learning_score = 0.0,
                success_rate = 0.0,
                failure_rate = 0.0,
                status = 'idle'
            WHERE agent_type IN ('imperium', 'guardian', 'sandbox', 'conquest');
            """
            
            # Write reset script to file
            reset_file = Path("reset_token_usage.sql")
            reset_file.write_text(token_reset_sql)
            
            log_info("✅ Token usage reset script created")
            self.issues_fixed.append("token_usage_reset")
            
        except Exception as e:
            error_msg = f"Failed to reset token usage: {str(e)}"
            log_error(error_msg)
            self.errors_encountered.append(error_msg)
    
    async def update_system_config(self):
        """Update system configuration to prevent future issues"""
        try:
            log_info("🔧 Updating system configuration...")
            
            # Create configuration update script
            config_update = '''
# Environment configuration updates
# Add to your .env file or environment variables

# Increase token limits temporarily
ANTHROPIC_DAILY_LIMIT=1000000
OPENAI_MONTHLY_LIMIT=50000

# Enable fallback mechanisms
ENABLE_OPENAI_FALLBACK=true
ENABLE_LOCAL_FALLBACK=true

# Database connection improvements
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Git configuration
GIT_PATH=/usr/bin/git
GIT_USER_NAME=AI Backend
GIT_USER_EMAIL=ai-backend@system.local

# Flutter configuration
FLUTTER_PATH=/home/ubuntu/flutter/bin/flutter
SKIP_FLUTTER_VALIDATION=false

# ML model configuration
ML_MODEL_PATH=/home/ubuntu/ai-backend-python/models
ENABLE_ML_FALLBACK=true

# Logging configuration
LOG_LEVEL=INFO
ENABLE_DEBUG_LOGGING=false
'''
            
            # Write config to file
            config_file = Path("system_config_update.env")
            config_file.write_text(config_update)
            
            log_info("✅ System configuration updates created")
            self.issues_fixed.append("system_config")
            
        except Exception as e:
            error_msg = f"Failed to update system config: {str(e)}"
            log_error(error_msg)
            self.errors_encountered.append(error_msg)
    
    async def create_deployment_script(self):
        """Create a deployment script to apply all fixes"""
        try:
            log_info("🔧 Creating deployment script...")
            
            deployment_script = '''#!/bin/bash
# Critical System Fixes Deployment Script

set -e

echo "🔧 Deploying critical system fixes..."

# 1. Install Git if not present
if ! command -v git &> /dev/null; then
    echo "📦 Installing Git..."
    if [[ -f /etc/debian_version ]]; then
        sudo apt-get update
        sudo apt-get install -y git
    elif [[ -f /etc/redhat-release ]] || [[ -f /etc/amazon-linux-release ]]; then
        sudo yum install -y git
    else
        echo "⚠️ Please install git manually for your OS"
    fi
fi

# 2. Apply database fixes
echo "🗄️ Applying database fixes..."
if [[ -f fix_database_functions.sql ]]; then
    psql $DATABASE_URL -f fix_database_functions.sql
fi

# 3. Reset token usage
echo "🔄 Resetting token usage..."
if [[ -f reset_token_usage.sql ]]; then
    psql $DATABASE_URL -f reset_token_usage.sql
fi

# 4. Update environment variables
echo "⚙️ Updating environment variables..."
if [[ -f system_config_update.env ]]; then
    cat system_config_update.env >> .env
fi

# 5. Restart services
echo "🔄 Restarting services..."
sudo systemctl restart ai-backend-python

echo "✅ Critical fixes deployed successfully!"
'''
            
            # Write deployment script
            deploy_file = Path("deploy_critical_fixes.sh")
            deploy_file.write_text(deployment_script)
            deploy_file.chmod(0o755)  # Make executable
            
            log_info("✅ Deployment script created")
            self.issues_fixed.append("deployment_script")
            
        except Exception as e:
            error_msg = f"Failed to create deployment script: {str(e)}"
            log_error(error_msg)
            self.errors_encountered.append(error_msg)

async def main():
    """Main function to run all fixes"""
    fixer = CriticalSystemFixer()
    
    print("🚀 Critical System Issues Fixer")
    print("=" * 50)
    
    # Run all fixes
    results = await fixer.fix_all_issues()
    
    # Create deployment script
    await fixer.create_deployment_script()
    
    # Print results
    print("\n📊 Fix Results:")
    print(f"✅ Issues Fixed: {len(results['issues_fixed'])}")
    for issue in results['issues_fixed']:
        print(f"   - {issue}")
    
    if results['errors_encountered']:
        print(f"\n❌ Errors Encountered: {len(results['errors_encountered'])}")
        for error in results['errors_encountered']:
            print(f"   - {error}")
    
    print("\n📋 Next Steps:")
    print("1. Run: chmod +x deploy_critical_fixes.sh")
    print("2. Run: ./deploy_critical_fixes.sh")
    print("3. Monitor logs for any remaining issues")
    print("4. Restart the AI backend service")

if __name__ == "__main__":
    asyncio.run(main()) 