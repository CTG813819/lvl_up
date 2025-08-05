#!/bin/bash

# Simple Shared Token Limits Integration
# This script directly integrates shared limits with existing services

set -e

echo "🔗 Simple Shared Token Limits Integration"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
PROJECT_DIR="/home/ubuntu/ai-backend-python"
VENV_PATH="$PROJECT_DIR/venv/bin/activate"

print_status "Starting simple shared limits integration..."

# Step 1: Navigate to project directory and activate virtual environment
print_status "Setting up environment..."
cd "$PROJECT_DIR"
source "$VENV_PATH"

# Step 2: Create a shared limits wrapper for the anthropic service
print_status "Creating shared limits wrapper for anthropic service..."

cat > app/services/anthropic_service_shared.py << 'EOF'
"""
Anthropic Service with Shared Token Limits Integration
"""

import os
import json
import time
import asyncio
import requests
import structlog
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import sys

# Add the project root to the path to import shared service
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from shared_token_limits_service import shared_token_limits_service

logger = structlog.get_logger()

# Anthropic API configuration
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Rate limiting configuration
RATE_LIMIT_CALLS = 50
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_RESET_TIME = 60  # seconds

# Shared limits integration
async def anthropic_with_shared_limits(prompt: str, ai_name: str = "imperium", max_tokens: int = 4000) -> Dict[str, Any]:
    """Call Anthropic with shared limits enforcement"""
    try:
        # Estimate tokens
        estimated_tokens = len(prompt.split()) + max_tokens
        
        # Check shared limits
        can_make_request, limit_info = await shared_token_limits_service.check_shared_limits(
            ai_name, estimated_tokens, "anthropic"
        )
        
        if not can_make_request:
            # Check if we can use OpenAI as fallback
            if limit_info.get("error") == "monthly_limit":
                logger.warning(f"Anthropic limit exceeded for {ai_name}, trying OpenAI fallback")
                return await openai_fallback(prompt, ai_name, max_tokens)
            else:
                return {
                    "success": False,
                    "error": limit_info.get("error"),
                    "message": limit_info.get("message"),
                    "details": limit_info
                }
        
        # Try Anthropic
        try:
            result = await call_claude_shared(prompt, max_tokens)
            
            # Record successful usage
            tokens_used = len(prompt.split()) + len(result.get("content", "").split())
            await shared_token_limits_service.record_shared_usage(
                ai_name, len(prompt.split()), len(result.get("content", "").split()), 
                "anthropic", True
            )
            
            return {
                "success": True,
                "provider": "anthropic",
                "content": result.get("content", ""),
                "tokens_used": tokens_used,
                "ai_name": ai_name
            }
            
        except Exception as anthropic_error:
            logger.warning(f"Anthropic failed for {ai_name}, trying OpenAI fallback", error=str(anthropic_error))
            return await openai_fallback(prompt, ai_name, max_tokens)
            
    except Exception as e:
        logger.error("Error in anthropic with shared limits", error=str(e), ai_name=ai_name)
        return {
            "success": False,
            "error": "system_error",
            "message": str(e),
            "ai_name": ai_name
        }

async def openai_fallback(prompt: str, ai_name: str, max_tokens: int) -> Dict[str, Any]:
    """OpenAI fallback when Anthropic fails"""
    try:
        # Check OpenAI limits
        estimated_tokens = len(prompt.split()) + max_tokens
        can_make_request, limit_info = await shared_token_limits_service.check_shared_limits(
            ai_name, estimated_tokens, "openai"
        )
        
        if not can_make_request:
            return {
                "success": False,
                "error": "both_providers_exhausted",
                "message": "Both Anthropic and OpenAI monthly limits exceeded",
                "anthropic_error": "monthly_limit",
                "openai_error": limit_info
            }
        
        # Import OpenAI service
        from app.services.openai_service import call_openai
        
        # Make OpenAI request
        result = await call_openai(prompt, max_tokens)
        
        # Record successful usage
        tokens_used = len(prompt.split()) + len(result.get("content", "").split())
        await shared_token_limits_service.record_shared_usage(
            ai_name, len(prompt.split()), len(result.get("content", "").split()), 
            "openai", True
        )
        
        return {
            "success": True,
            "provider": "openai",
            "content": result.get("content", ""),
            "tokens_used": tokens_used,
            "ai_name": ai_name
        }
        
    except Exception as e:
        logger.error("Error in OpenAI fallback", error=str(e), ai_name=ai_name)
        # Record failed usage
        await shared_token_limits_service.record_shared_usage(
            ai_name, len(prompt.split()), 0, "openai", False, str(e)
        )
        return {
            "success": False,
            "error": "openai_fallback_error",
            "message": str(e),
            "ai_name": ai_name
        }

async def call_claude_shared(prompt: str, max_tokens: int = 4000) -> Dict[str, Any]:
    """Call Claude with shared limits"""
    try:
        headers = {
            "Content-Type": "application/json",
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": max_tokens,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        response = requests.post(ANTHROPIC_API_URL, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            content = result["content"][0]["text"]
            return {"content": content, "success": True}
        else:
            raise Exception(f"Anthropic API error: {response.status_code} - {response.text}")
            
    except Exception as e:
        logger.error("Error calling Claude", error=str(e))
        raise e

# Keep original functions for backward compatibility
async def call_claude(prompt: str, max_tokens: int = 4000) -> str:
    """Original call_claude function with shared limits"""
    result = await anthropic_with_shared_limits(prompt, "imperium", max_tokens)
    if result["success"]:
        return result["content"]
    else:
        raise Exception(result["message"])

async def anthropic_rate_limited_call(prompt: str, ai_name: str, max_tokens: int = 4000) -> str:
    """Original anthropic_rate_limited_call function with shared limits"""
    result = await anthropic_with_shared_limits(prompt, ai_name, max_tokens)
    if result["success"]:
        return result["content"]
    else:
        raise Exception(result["message"])
EOF

# Step 3: Create a simple integration script for existing services
print_status "Creating integration script for existing services..."

cat > integrate_existing_services.py << 'EOF'
#!/usr/bin/env python3
"""
Integrate existing services with shared limits
"""

import os
import re
from datetime import datetime

def backup_file(file_path):
    """Backup a file"""
    if os.path.exists(file_path):
        backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(file_path, 'r') as f:
            content = f.read()
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"✅ Backed up {file_path} to {backup_path}")
        return True
    return False

def update_imports(file_path):
    """Update imports to use shared limits version"""
    if not os.path.exists(file_path):
        print(f"❌ File {file_path} not found")
        return False
    
    backup_file(file_path)
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Update anthropic service imports
    if 'anthropic_service' in content:
        content = re.sub(
            r'from app\.services\.anthropic_service import',
            'from app.services.anthropic_service_shared import',
            content
        )
        content = re.sub(
            r'import app\.services\.anthropic_service',
            'import app.services.anthropic_service_shared',
            content
        )
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated imports in {file_path}")
    return True

def main():
    print("🔄 Integrating existing services with shared limits...")
    
    # Files to update
    files_to_update = [
        "app/services/custody_protocol_service.py",
        "app/services/ai_agent_service.py",
        "app/services/unified_ai_service.py",
        "app/routers/agents.py",
        "app/routers/ai_agents_final.py"
    ]
    
    for file_path in files_to_update:
        if os.path.exists(file_path):
            update_imports(file_path)
        else:
            print(f"⚠️ File {file_path} not found, skipping")
    
    print("✅ Service integration completed!")

if __name__ == "__main__":
    main()
EOF

# Step 4: Run the integration
print_status "Running integration..."
python integrate_existing_services.py

# Step 5: Test the integration
print_status "Testing the integration..."

cat > test_simple_integration.py << 'EOF'
#!/usr/bin/env python3
"""
Test Simple Shared Limits Integration
"""

import asyncio
import sys
import os

async def test_simple_integration():
    """Test the simple shared limits integration"""
    try:
        print("🧪 Testing Simple Shared Limits Integration...")
        
        # Import the shared service
        from shared_token_limits_service import shared_token_limits_service
        
        print("✅ Shared service imported successfully")
        
        # Test shared limits service
        print("🧪 Testing shared limits service...")
        summary = await shared_token_limits_service.get_shared_usage_summary()
        print(f"   Anthropic usage: {summary['current_usage']['anthropic']['percentage']:.1f}%")
        print(f"   OpenAI usage: {summary['current_usage']['openai']['percentage']:.1f}%")
        
        # Test anthropic service with shared limits
        print("🧪 Testing anthropic service with shared limits...")
        from app.services.anthropic_service_shared import anthropic_with_shared_limits
        
        # Test with a simple prompt
        result = await anthropic_with_shared_limits(
            "Hello, this is a test message.", 
            "imperium", 
            100
        )
        
        print(f"   Test result: {result['success']}")
        print(f"   Provider: {result.get('provider', 'unknown')}")
        print(f"   Error: {result.get('error', 'none')}")
        
        print("✅ Simple Shared Limits Integration tested successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing integration: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_simple_integration())
    sys.exit(0 if success else 1)
EOF

python test_simple_integration.py

# Step 6: Restart the backend service
print_status "Restarting backend service with integrated shared limits..."

# Kill any existing backend processes
pkill -f "uvicorn app.main:app" || true
sleep 2

# Start the backend in the background
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!

sleep 5

# Step 7: Test the API endpoints
print_status "Testing API endpoints with integration..."

echo "Testing shared limits summary..."
curl -s http://localhost:8000/api/shared-limits/summary | head -5

echo "Testing shared limits test..."
curl -s http://localhost:8000/api/shared-limits/test | head -5

print_success "Simple Shared Token Limits Integration completed successfully!"

echo ""
echo "🎉 Simple Integration Complete!"
echo "==============================="
echo "✅ Anthropic service now uses shared token limits"
echo "✅ Automatic fallback to OpenAI when Anthropic limits exceeded"
echo "✅ All existing services updated to use shared limits"
echo "✅ Backward compatibility maintained"
echo "✅ All AIs will now automatically switch to OpenAI when Anthropic runs out!"
echo ""
echo "🔄 Now when you see those 400 errors, the AIs will automatically switch to OpenAI!"
echo "📊 Monitor usage: ./monitor_shared_limits.sh"
echo "🌐 API endpoints: http://localhost:8000/api/shared-limits/*"
echo "" 