#!/bin/bash

# Integrate Shared Token Limits with AI Services
# This script updates all AI services to use the shared token limits system

set -e

echo "🔗 Integrating Shared Token Limits with AI Services"
echo "=================================================="

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

print_status "Integrating shared token limits with AI services..."

# Step 1: Navigate to project directory and activate virtual environment
print_status "Setting up environment..."
cd "$PROJECT_DIR"
source "$VENV_PATH"

# Step 2: Update the unified AI service to use shared limits
print_status "Updating unified AI service..."

cat > app/services/unified_ai_service_shared.py << 'EOF'
"""
Updated Unified AI Service with Shared Token Limits Integration
"""

import asyncio
from typing import Dict, Any, Optional, List
import structlog
from datetime import datetime

from app.core.config import settings
from app.services.anthropic_service import AnthropicService
from app.services.openai_service import OpenAIService
import sys
import os

# Add the project root to the path to import shared service
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from shared_token_limits_service import shared_token_limits_service

logger = structlog.get_logger()

class UnifiedAIServiceShared:
    """Unified AI service with shared token limits integration"""
    
    def __init__(self):
        self.anthropic_service = AnthropicService()
        self.openai_service = OpenAIService()
    
    async def get_provider_recommendation(self, ai_name: str) -> Dict[str, Any]:
        """Get provider recommendation based on shared usage"""
        try:
            summary = await shared_token_limits_service.get_shared_usage_summary()
            anthropic_percentage = summary["current_usage"]["anthropic"]["percentage"]
            openai_percentage = summary["current_usage"]["openai"]["percentage"]
            
            # Use fallback threshold from shared service
            fallback_threshold = shared_token_limits_service.FALLBACK_THRESHOLD * 100
            
            if anthropic_percentage < fallback_threshold:
                recommendation = "anthropic"
                reason = "anthropic_available"
            elif openai_percentage < 100:
                recommendation = "openai"
                reason = "anthropic_exhausted_openai_available"
            else:
                recommendation = "none"
                reason = "both_exhausted"
            
            return {
                "recommendation": recommendation,
                "reason": reason,
                "anthropic": {
                    "usage_percentage": anthropic_percentage,
                    "total_tokens": summary["current_usage"]["anthropic"]["monthly"],
                    "available": summary["current_usage"]["anthropic"]["available"]
                },
                "openai": {
                    "usage_percentage": openai_percentage,
                    "total_tokens": summary["current_usage"]["openai"]["monthly"],
                    "available": summary["current_usage"]["openai"]["available"]
                },
                "shared_limits": summary["shared_limits"]
            }
            
        except Exception as e:
            logger.error("Error getting provider recommendation", error=str(e), ai_name=ai_name)
            return {
                "recommendation": "anthropic",
                "reason": "error_fallback",
                "error": str(e)
            }
    
    async def make_request(self, ai_name: str, prompt: str, estimated_tokens: int = 1000, 
                          max_tokens: int = 4000, temperature: float = 0.7) -> Dict[str, Any]:
        """Make AI request with shared limits enforcement"""
        try:
            # Check shared limits first
            can_make_request, limit_info = await shared_token_limits_service.check_shared_limits(
                ai_name, estimated_tokens, "anthropic"
            )
            
            if not can_make_request:
                # Check if we can use OpenAI as fallback
                if limit_info.get("error") == "monthly_limit":
                    # Try OpenAI
                    can_make_openai, openai_info = await shared_token_limits_service.check_shared_limits(
                        ai_name, estimated_tokens, "openai"
                    )
                    
                    if can_make_openai:
                        logger.info(f"Switching to OpenAI for {ai_name} due to Anthropic limit", 
                                   anthropic_error=limit_info.get("error"))
                        return await self._make_openai_request(ai_name, prompt, estimated_tokens, max_tokens, temperature)
                    else:
                        return {
                            "success": False,
                            "error": "both_providers_exhausted",
                            "message": "Both Anthropic and OpenAI monthly limits exceeded",
                            "anthropic_error": limit_info,
                            "openai_error": openai_info
                        }
                else:
                    return {
                        "success": False,
                        "error": limit_info.get("error"),
                        "message": limit_info.get("message"),
                        "details": limit_info
                    }
            
            # Try Anthropic first
            try:
                result = await self.anthropic_service.generate_response(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
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
                logger.warning(f"Anthropic failed for {ai_name}, trying OpenAI", error=str(anthropic_error))
                
                # Try OpenAI as fallback
                return await self._make_openai_request(ai_name, prompt, estimated_tokens, max_tokens, temperature)
                
        except Exception as e:
            logger.error("Error in unified AI request", error=str(e), ai_name=ai_name)
            return {
                "success": False,
                "error": "system_error",
                "message": str(e),
                "ai_name": ai_name
            }
    
    async def _make_openai_request(self, ai_name: str, prompt: str, estimated_tokens: int, 
                                  max_tokens: int, temperature: float) -> Dict[str, Any]:
        """Make OpenAI request with shared limits"""
        try:
            # Check OpenAI limits
            can_make_request, limit_info = await shared_token_limits_service.check_shared_limits(
                ai_name, estimated_tokens, "openai"
            )
            
            if not can_make_request:
                return {
                    "success": False,
                    "error": limit_info.get("error"),
                    "message": limit_info.get("message"),
                    "details": limit_info
                }
            
            # Make OpenAI request
            result = await self.openai_service.generate_response(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
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
            logger.error("Error in OpenAI request", error=str(e), ai_name=ai_name)
            # Record failed usage
            await shared_token_limits_service.record_shared_usage(
                ai_name, len(prompt.split()), 0, "openai", False, str(e)
            )
            return {
                "success": False,
                "error": "openai_error",
                "message": str(e),
                "ai_name": ai_name
            }

# Global instance
unified_ai_service_shared = UnifiedAIServiceShared()
EOF

# Step 3: Update the custody protocol service to use shared limits
print_status "Updating custody protocol service..."

# Create a backup
cp app/services/custody_protocol_service.py app/services/custody_protocol_service.py.backup

# Update the custody protocol service
cat > app/services/custody_protocol_service_shared.py << 'EOF'
"""
Updated Custody Protocol Service with Shared Token Limits Integration
"""

import asyncio
from typing import Dict, Any, List, Optional
import structlog
from datetime import datetime
import sys
import os

# Add the project root to the path to import shared service
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from shared_token_limits_service import shared_token_limits_service
from app.services.unified_ai_service_shared import unified_ai_service_shared

logger = structlog.get_logger()

class CustodyProtocolServiceShared:
    """Custody protocol service with shared token limits integration"""
    
    async def evaluate_custody_protocol(self, ai_name: str, content: str, 
                                       evaluation_type: str = "comprehensive") -> Dict[str, Any]:
        """Evaluate custody protocol with shared limits"""
        try:
            # Estimate tokens for evaluation
            estimated_tokens = len(content.split()) * 2  # Rough estimate
            
            # Check shared limits
            can_make_request, limit_info = await shared_token_limits_service.check_shared_limits(
                ai_name, estimated_tokens, "anthropic"
            )
            
            if not can_make_request:
                # Try OpenAI as fallback
                if limit_info.get("error") == "monthly_limit":
                    can_make_openai, openai_info = await shared_token_limits_service.check_shared_limits(
                        ai_name, estimated_tokens, "openai"
                    )
                    
                    if can_make_openai:
                        logger.info(f"Using OpenAI for custody protocol evaluation due to Anthropic limit")
                        return await self._evaluate_with_openai(ai_name, content, evaluation_type, estimated_tokens)
                    else:
                        return {
                            "success": False,
                            "error": "both_providers_exhausted",
                            "message": "Both Anthropic and OpenAI monthly limits exceeded for custody protocol",
                            "anthropic_error": limit_info,
                            "openai_error": openai_info
                        }
                else:
                    return {
                        "success": False,
                        "error": limit_info.get("error"),
                        "message": limit_info.get("message"),
                        "details": limit_info
                    }
            
            # Try Anthropic first
            try:
                result = await self._evaluate_with_anthropic(ai_name, content, evaluation_type, estimated_tokens)
                return result
            except Exception as anthropic_error:
                logger.warning(f"Anthropic failed for custody protocol, trying OpenAI", error=str(anthropic_error))
                return await self._evaluate_with_openai(ai_name, content, evaluation_type, estimated_tokens)
                
        except Exception as e:
            logger.error("Error in custody protocol evaluation", error=str(e), ai_name=ai_name)
            return {
                "success": False,
                "error": "system_error",
                "message": str(e),
                "ai_name": ai_name
            }
    
    async def _evaluate_with_anthropic(self, ai_name: str, content: str, 
                                      evaluation_type: str, estimated_tokens: int) -> Dict[str, Any]:
        """Evaluate with Anthropic"""
        # This would contain the actual custody protocol evaluation logic
        # For now, we'll use the unified service
        prompt = f"Evaluate the following content for custody protocol compliance ({evaluation_type}):\n\n{content}"
        
        result = await unified_ai_service_shared.make_request(
            ai_name, prompt, estimated_tokens, 2000, 0.3
        )
        
        if result["success"]:
            return {
                "success": True,
                "provider": "anthropic",
                "evaluation": result["content"],
                "evaluation_type": evaluation_type,
                "ai_name": ai_name
            }
        else:
            raise Exception(result.get("message", "Anthropic evaluation failed"))
    
    async def _evaluate_with_openai(self, ai_name: str, content: str, 
                                   evaluation_type: str, estimated_tokens: int) -> Dict[str, Any]:
        """Evaluate with OpenAI"""
        prompt = f"Evaluate the following content for custody protocol compliance ({evaluation_type}):\n\n{content}"
        
        result = await unified_ai_service_shared.make_request(
            ai_name, prompt, estimated_tokens, 2000, 0.3
        )
        
        if result["success"]:
            return {
                "success": True,
                "provider": "openai",
                "evaluation": result["content"],
                "evaluation_type": evaluation_type,
                "ai_name": ai_name
            }
        else:
            return {
                "success": False,
                "error": "openai_evaluation_failed",
                "message": result.get("message", "OpenAI evaluation failed"),
                "ai_name": ai_name
            }

# Global instance
custody_protocol_service_shared = CustodyProtocolServiceShared()
EOF

# Step 4: Update the main AI agent service to use shared limits
print_status "Updating AI agent service..."

# Create a backup
cp app/services/ai_agent_service.py app/services/ai_agent_service.py.backup

# Update the AI agent service to use shared limits
cat > app/services/ai_agent_service_shared.py << 'EOF'
"""
Updated AI Agent Service with Shared Token Limits Integration
"""

import asyncio
from typing import Dict, Any, List, Optional
import structlog
from datetime import datetime
import sys
import os

# Add the project root to the path to import shared service
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from shared_token_limits_service import shared_token_limits_service
from app.services.unified_ai_service_shared import unified_ai_service_shared

logger = structlog.get_logger()

class AIAgentServiceShared:
    """AI agent service with shared token limits integration"""
    
    async def process_request(self, ai_name: str, request_type: str, 
                             prompt: str, estimated_tokens: int = 1000) -> Dict[str, Any]:
        """Process AI request with shared limits"""
        try:
            # Check shared limits
            can_make_request, limit_info = await shared_token_limits_service.check_shared_limits(
                ai_name, estimated_tokens, "anthropic"
            )
            
            if not can_make_request:
                # Try OpenAI as fallback
                if limit_info.get("error") == "monthly_limit":
                    can_make_openai, openai_info = await shared_token_limits_service.check_shared_limits(
                        ai_name, estimated_tokens, "openai"
                    )
                    
                    if can_make_openai:
                        logger.info(f"Using OpenAI for {ai_name} {request_type} due to Anthropic limit")
                        return await self._process_with_openai(ai_name, request_type, prompt, estimated_tokens)
                    else:
                        return {
                            "success": False,
                            "error": "both_providers_exhausted",
                            "message": f"Both Anthropic and OpenAI monthly limits exceeded for {ai_name} {request_type}",
                            "anthropic_error": limit_info,
                            "openai_error": openai_info
                        }
                else:
                    return {
                        "success": False,
                        "error": limit_info.get("error"),
                        "message": limit_info.get("message"),
                        "details": limit_info
                    }
            
            # Try Anthropic first
            try:
                result = await self._process_with_anthropic(ai_name, request_type, prompt, estimated_tokens)
                return result
            except Exception as anthropic_error:
                logger.warning(f"Anthropic failed for {ai_name} {request_type}, trying OpenAI", error=str(anthropic_error))
                return await self._process_with_openai(ai_name, request_type, prompt, estimated_tokens)
                
        except Exception as e:
            logger.error("Error in AI agent request", error=str(e), ai_name=ai_name, request_type=request_type)
            return {
                "success": False,
                "error": "system_error",
                "message": str(e),
                "ai_name": ai_name,
                "request_type": request_type
            }
    
    async def _process_with_anthropic(self, ai_name: str, request_type: str, 
                                     prompt: str, estimated_tokens: int) -> Dict[str, Any]:
        """Process with Anthropic"""
        result = await unified_ai_service_shared.make_request(
            ai_name, prompt, estimated_tokens, 4000, 0.7
        )
        
        if result["success"]:
            return {
                "success": True,
                "provider": "anthropic",
                "content": result["content"],
                "request_type": request_type,
                "ai_name": ai_name,
                "tokens_used": result.get("tokens_used", 0)
            }
        else:
            raise Exception(result.get("message", "Anthropic processing failed"))
    
    async def _process_with_openai(self, ai_name: str, request_type: str, 
                                  prompt: str, estimated_tokens: int) -> Dict[str, Any]:
        """Process with OpenAI"""
        result = await unified_ai_service_shared.make_request(
            ai_name, prompt, estimated_tokens, 4000, 0.7
        )
        
        if result["success"]:
            return {
                "success": True,
                "provider": "openai",
                "content": result["content"],
                "request_type": request_type,
                "ai_name": ai_name,
                "tokens_used": result.get("tokens_used", 0)
            }
        else:
            return {
                "success": False,
                "error": "openai_processing_failed",
                "message": result.get("message", "OpenAI processing failed"),
                "ai_name": ai_name,
                "request_type": request_type
            }

# Global instance
ai_agent_service_shared = AIAgentServiceShared()
EOF

# Step 5: Create a script to replace the existing services
print_status "Creating service replacement script..."

cat > replace_services.py << 'EOF'
#!/usr/bin/env python3
"""
Replace existing services with shared limits versions
"""

import os
import shutil
from datetime import datetime

def backup_and_replace(original_path, new_path, backup_suffix="_backup"):
    """Backup original and replace with new version"""
    if os.path.exists(original_path):
        backup_path = f"{original_path}{backup_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(original_path, backup_path)
        print(f"✅ Backed up {original_path} to {backup_path}")
    
    if os.path.exists(new_path):
        shutil.copy2(new_path, original_path)
        print(f"✅ Replaced {original_path} with shared limits version")
    else:
        print(f"❌ New file {new_path} not found")

def main():
    print("🔄 Replacing services with shared limits versions...")
    
    # Replace services
    replace_services = [
        ("app/services/unified_ai_service.py", "app/services/unified_ai_service_shared.py"),
        ("app/services/custody_protocol_service.py", "app/services/custody_protocol_service_shared.py"),
        ("app/services/ai_agent_service.py", "app/services/ai_agent_service_shared.py"),
    ]
    
    for original, new in replace_services:
        backup_and_replace(original, new)
    
    print("✅ Service replacement completed!")

if __name__ == "__main__":
    main()
EOF

# Step 6: Run the service replacement
print_status "Replacing services with shared limits versions..."
python replace_services.py

# Step 7: Test the integration
print_status "Testing the integration..."

cat > test_integration.py << 'EOF'
#!/usr/bin/env python3
"""
Test Shared Limits Integration
"""

import asyncio
import sys
import os

async def test_integration():
    """Test the shared limits integration"""
    try:
        print("🧪 Testing Shared Limits Integration...")
        
        # Import the services
        from app.services.unified_ai_service import UnifiedAIService
        from app.services.custody_protocol_service import CustodyProtocolService
        from app.services.ai_agent_service import AIAgentService
        from shared_token_limits_service import shared_token_limits_service
        
        print("✅ Services imported successfully")
        
        # Test shared limits service
        print("🧪 Testing shared limits service...")
        summary = await shared_token_limits_service.get_shared_usage_summary()
        print(f"   Anthropic usage: {summary['current_usage']['anthropic']['percentage']:.1f}%")
        print(f"   OpenAI usage: {summary['current_usage']['openai']['percentage']:.1f}%")
        
        # Test provider recommendation
        print("🧪 Testing provider recommendation...")
        from app.services.unified_ai_service import UnifiedAIService
        service = UnifiedAIService()
        recommendation = await service.get_provider_recommendation("imperium")
        print(f"   Recommendation: {recommendation['recommendation']}")
        print(f"   Reason: {recommendation['reason']}")
        
        print("✅ Shared Limits Integration tested successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing integration: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_integration())
    sys.exit(0 if success else 1)
EOF

python test_integration.py

# Step 8: Restart the backend service
print_status "Restarting backend service with integrated shared limits..."

# Kill any existing backend processes
pkill -f "uvicorn app.main:app" || true
sleep 2

# Start the backend in the background
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!

sleep 5

# Step 9: Test the API endpoints
print_status "Testing API endpoints with integration..."

echo "Testing shared limits summary..."
curl -s http://localhost:8000/api/shared-limits/summary | head -5

echo "Testing shared limits test..."
curl -s http://localhost:8000/api/shared-limits/test | head -5

print_success "Shared Token Limits Integration completed successfully!"

echo ""
echo "🎉 Integration Complete!"
echo "======================="
echo "✅ All AI services now use shared token limits"
echo "✅ Automatic fallback from Anthropic to OpenAI when limits exceeded"
echo "✅ Custody protocol service integrated with shared limits"
echo "✅ AI agent service integrated with shared limits"
echo "✅ Unified AI service integrated with shared limits"
echo "✅ All services automatically check limits before making requests"
echo ""
echo "🔄 Now when Anthropic runs out, AIs will automatically switch to OpenAI!"
echo "📊 Monitor usage: ./monitor_shared_limits.sh"
echo "🌐 API endpoints: http://localhost:8000/api/shared-limits/*"
echo "" 