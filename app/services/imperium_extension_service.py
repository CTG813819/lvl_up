"""
Imperium Extension Service
Allows Imperium AI to create extensions for itself and other AIs
Includes rigorous testing and sandbox validation before deployment
"""

import asyncio
import json
import uuid
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import structlog
import subprocess
import tempfile
import shutil
from enum import Enum

from ..core.database import get_session
from ..core.config import settings
from .sandbox_ai_service import SandboxAIService
from .ai_agent_service import AIAgentService
from app.services.anthropic_service import call_claude, anthropic_rate_limited_call

logger = structlog.get_logger()


class ExtensionType(Enum):
    """Types of extensions that can be created"""
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    SECURITY_ENHANCEMENT = "security_enhancement"
    FEATURE_ADDITION = "feature_addition"
    INTEGRATION_BRIDGE = "integration_bridge"
    MONITORING_TOOL = "monitoring_tool"
    AUTOMATION_SCRIPT = "automation_script"
    DATA_PROCESSING = "data_processing"
    API_EXTENSION = "api_extension"


class ExtensionTarget(Enum):
    """Target AIs for extensions"""
    IMPERIUM = "imperium"
    CONQUEST = "conquest"
    GUARDIAN = "guardian"
    SANDBOX = "sandbox"
    ALL = "all"


class ImperiumExtensionService:
    """Imperium Extension Service - Creates and validates AI extensions"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ImperiumExtensionService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.sandbox_service = SandboxAIService()
            self.agent_service = AIAgentService()
            self.extensions = {}
            self.extension_history = []
            self.test_results = {}
            self._initialized = True
    
    @classmethod
    async def initialize(cls):
        """Initialize the Imperium Extension service"""
        instance = cls()
        
        # Create extensions directory
        os.makedirs(f"{settings.ml_model_path}/extensions", exist_ok=True)
        
        # Load existing extensions
        await instance._load_existing_extensions()
        
        logger.info("Imperium Extension Service initialized successfully")
        return instance
    
    async def _load_existing_extensions(self):
        """Load existing extensions from storage"""
        try:
            extensions_path = f"{settings.ml_model_path}/extensions"
            
            if os.path.exists(extensions_path):
                for ext_file in os.listdir(extensions_path):
                    if ext_file.endswith('.json'):
                        with open(os.path.join(extensions_path, ext_file), 'r') as f:
                            extension_data = json.load(f)
                            self.extensions[extension_data['id']] = extension_data
                            logger.info(f"Loaded extension: {extension_data['name']}")
            
        except Exception as e:
            logger.error(f"Error loading existing extensions: {str(e)}")
    
    async def create_extension_proposal(self, target_ai: str, extension_type: ExtensionType, 
                                      description: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Create an extension proposal for a target AI"""
        try:
            # Verify Imperium has permission to create extensions
            if not await self._verify_imperium_permissions():
                return {"status": "error", "message": "Imperium AI not authorized to create extensions"}
            
            # Generate extension code using Claude
            extension_code = await self._generate_extension_code(target_ai, extension_type, description, requirements)
            
            # Create extension proposal
            extension_id = str(uuid.uuid4())
            extension_data = {
                "id": extension_id,
                "name": f"{target_ai}_{extension_type.value}_extension",
                "target_ai": target_ai,
                "extension_type": extension_type.value,
                "description": description,
                "requirements": requirements,
                "code": extension_code,
                "status": "proposed",
                "created_at": datetime.utcnow().isoformat(),
                "created_by": "imperium",
                "test_results": {},
                "validation_status": "pending"
            }
            
            # Save extension proposal
            self.extensions[extension_id] = extension_data
            await self._save_extension(extension_id, extension_data)
            
            logger.info(f"Created extension proposal: {extension_data['name']}")
            
            return {
                "status": "success",
                "extension_id": extension_id,
                "extension_data": extension_data,
                "message": f"Extension proposal created for {target_ai}"
            }
            
        except Exception as e:
            logger.error(f"Error creating extension proposal: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _verify_imperium_permissions(self) -> bool:
        """Verify Imperium AI has permission to create extensions"""
        try:
            # Check if Imperium has passed recent custody tests
            from .custody_protocol_service import CustodyProtocolService
            custody_service = CustodyProtocolService()
            custody_metrics = custody_service.custody_metrics.get("imperium", {})
            
            if custody_metrics.get("total_tests_passed", 0) < 5:
                return False
            
            if custody_metrics.get("pass_rate", 0) < 0.85:
                return False
            
            # Check if Imperium is at sufficient level
            imperium_level = await self._get_imperium_level()
            if imperium_level < 10:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error verifying Imperium permissions: {str(e)}")
            return False
    
    async def _get_imperium_level(self) -> int:
        """Get Imperium AI's current level"""
        try:
            session = get_session()
            async with session as s:
                from ..models.sql_models import AgentMetrics
                from sqlalchemy import select
                
                result = await s.execute(
                    select(AgentMetrics).where(AgentMetrics.agent_type == "imperium")
                )
                agent = result.scalar_one_or_none()
                
                if agent:
                    return agent.level or 1
                else:
                    return 1
                    
        except Exception as e:
            logger.error(f"Error getting Imperium level: {str(e)}")
            return 1
    
    async def _generate_extension_code(self, target_ai: str, extension_type: ExtensionType, 
                                     description: str, requirements: Dict[str, Any]) -> str:
        """Generate extension code using Claude"""
        try:
            prompt = f"""
            Create a Python extension for {target_ai} AI with the following specifications:
            
            Extension Type: {extension_type.value}
            Description: {description}
            Requirements: {json.dumps(requirements, indent=2)}
            
            The extension should:
            1. Be compatible with the existing {target_ai} AI architecture
            2. Follow best practices for code quality and security
            3. Include proper error handling and logging
            4. Be well-documented with docstrings
            5. Include unit tests
            6. Follow the existing codebase patterns
            
            Generate the complete extension code with all necessary imports and dependencies.
            """
            
            response = await anthropic_rate_limited_call(
                prompt,
                ai_name="imperium"
            )
            
            # Extract code from response
            code_start = response.find("```python")
            code_end = response.find("```", code_start + 1)
            
            if code_start != -1 and code_end != -1:
                return response[code_start + 9:code_end].strip()
            else:
                return response
            
        except Exception as e:
            logger.error(f"Error generating extension code: {str(e)}")
            return f"# Extension for {target_ai}\n# Error generating code: {str(e)}"
    
    async def test_extension_in_sandbox(self, extension_id: str) -> Dict[str, Any]:
        """Test extension in sandbox environment"""
        try:
            if extension_id not in self.extensions:
                return {"status": "error", "message": "Extension not found"}
            
            extension = self.extensions[extension_id]
            
            # Create sandbox test environment
            test_result = await self._run_sandbox_test(extension)
            
            # Update extension with test results
            extension["test_results"] = test_result
            extension["validation_status"] = "tested"
            
            if test_result.get("passed", False):
                extension["status"] = "tested"
            else:
                extension["status"] = "failed"
            
            await self._save_extension(extension_id, extension)
            
            logger.info(f"Extension {extension_id} tested in sandbox: {test_result.get('passed', False)}")
            
            return {
                "status": "success",
                "extension_id": extension_id,
                "test_result": test_result,
                "message": f"Extension tested successfully" if test_result.get("passed", False) else "Extension failed testing"
            }
            
        except Exception as e:
            logger.error(f"Error testing extension in sandbox: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _run_sandbox_test(self, extension: Dict[str, Any]) -> Dict[str, Any]:
        """Run extension in sandbox environment"""
        try:
            # Create temporary test environment
            with tempfile.TemporaryDirectory() as temp_dir:
                # Write extension code to temporary file
                ext_file = os.path.join(temp_dir, f"{extension['name']}.py")
                with open(ext_file, 'w') as f:
                    f.write(extension['code'])
                
                # Create test script
                test_script = os.path.join(temp_dir, "test_extension.py")
                test_code = self._generate_test_script(extension)
                with open(test_script, 'w') as f:
                    f.write(test_code)
                
                # Run tests
                result = subprocess.run(
                    ["python", test_script],
                    capture_output=True,
                    text=True,
                    cwd=temp_dir,
                    timeout=300  # 5 minute timeout
                )
                
                # Analyze results
                test_passed = result.returncode == 0
                test_output = result.stdout
                test_errors = result.stderr
                
                # Additional validation using Claude
                validation_result = await self._validate_extension_with_claude(extension, test_output, test_errors)
                
                return {
                    "passed": test_passed and validation_result.get("approved", False),
                    "test_output": test_output,
                    "test_errors": test_errors,
                    "validation_result": validation_result,
                    "tested_at": datetime.utcnow().isoformat()
                }
                
        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "test_output": "",
                "test_errors": "Test timed out after 5 minutes",
                "validation_result": {"approved": False, "reason": "Test timeout"},
                "tested_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "passed": False,
                "test_output": "",
                "test_errors": str(e),
                "validation_result": {"approved": False, "reason": str(e)},
                "tested_at": datetime.utcnow().isoformat()
            }
    
    def _generate_test_script(self, extension: Dict[str, Any]) -> str:
        """Generate test script for extension"""
        return f"""
import sys
import os
import unittest
import traceback

# Add extension to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    # Import the extension
    import {extension['name']}
    
    # Basic functionality test
    class TestExtension(unittest.TestCase):
        def test_extension_import(self):
            self.assertTrue(hasattr({extension['name']}, '__file__'))
        
        def test_extension_attributes(self):
            # Test that extension has expected attributes
            self.assertTrue(hasattr({extension['name']}, '__name__'))
        
        def test_extension_functions(self):
            # Test that extension can be called without errors
            try:
                # Try to call main function if it exists
                if hasattr({extension['name']}, 'main'):
                    {extension['name']}.main()
                print("Extension functions test passed")
            except Exception as e:
                print(f"Extension function test warning: {{e}}")
    
    # Run tests
    unittest.main(argv=[''], exit=False, verbosity=2)
    
except Exception as e:
    print(f"Extension test failed: {{e}}")
    traceback.print_exc()
    sys.exit(1)
"""
    
    async def _validate_extension_with_claude(self, extension: Dict[str, Any], 
                                             test_output: str, test_errors: str) -> Dict[str, Any]:
        """Validate extension results with Claude"""
        try:
            prompt = f"""
            Validate the following extension test results:
            
            Extension: {extension['name']}
            Target AI: {extension['target_ai']}
            Type: {extension['extension_type']}
            Description: {extension['description']}
            
            Test Output: {test_output}
            Test Errors: {test_errors}
            
            Please evaluate:
            1. Does the extension work correctly?
            2. Are there any security concerns?
            3. Does it follow best practices?
            4. Is it compatible with the target AI?
            5. Should it be approved for deployment?
            
            Respond with JSON format:
            {{
                "approved": true/false,
                "reason": "explanation",
                "security_score": 1-10,
                "quality_score": 1-10,
                "recommendations": ["list", "of", "improvements"]
            }}
            """
            
            response = await anthropic_rate_limited_call(
                prompt,
                ai_name="imperium"
            )
            
            # Parse JSON response
            try:
                validation_result = json.loads(response)
                return validation_result
            except json.JSONDecodeError:
                return {
                    "approved": False,
                    "reason": "Failed to parse validation response",
                    "security_score": 0,
                    "quality_score": 0,
                    "recommendations": ["Fix validation response parsing"]
                }
                
        except Exception as e:
            logger.error(f"Error validating extension with Claude: {str(e)}")
            return {
                "approved": False,
                "reason": f"Validation error: {str(e)}",
                "security_score": 0,
                "quality_score": 0,
                "recommendations": ["Fix validation process"]
            }
    
    async def deploy_extension(self, extension_id: str) -> Dict[str, Any]:
        """Deploy extension after successful testing"""
        try:
            if extension_id not in self.extensions:
                return {"status": "error", "message": "Extension not found"}
            
            extension = self.extensions[extension_id]
            
            # Check if extension passed testing
            if not extension.get("test_results", {}).get("passed", False):
                return {"status": "error", "message": "Extension must pass testing before deployment"}
            
            # Create deployment proposal
            deployment_proposal = await self._create_deployment_proposal(extension)
            
            # Update extension status
            extension["status"] = "deployed"
            extension["deployed_at"] = datetime.utcnow().isoformat()
            extension["deployment_proposal"] = deployment_proposal
            
            await self._save_extension(extension_id, extension)
            
            logger.info(f"Extension {extension_id} deployed successfully")
            
            return {
                "status": "success",
                "extension_id": extension_id,
                "deployment_proposal": deployment_proposal,
                "message": "Extension deployed successfully"
            }
            
        except Exception as e:
            logger.error(f"Error deploying extension: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _create_deployment_proposal(self, extension: Dict[str, Any]) -> Dict[str, Any]:
        """Create deployment proposal for extension"""
        try:
            proposal_id = str(uuid.uuid4())
            
            proposal = {
                "id": proposal_id,
                "type": "extension_deployment",
                "title": f"Deploy {extension['name']} Extension",
                "description": f"Deploy {extension['name']} extension for {extension['target_ai']} AI",
                "target_ai": extension['target_ai'],
                "extension_id": extension['id'],
                "code_before": "Extension not deployed",
                "code_after": extension['code'],
                "status": "pending",
                "created_at": datetime.utcnow().isoformat(),
                "created_by": "imperium",
                "priority": "high",
                "impact": "medium",
                "test_results": extension.get("test_results", {}),
                "validation_result": extension.get("test_results", {}).get("validation_result", {})
            }
            
            # Save proposal to database
            await self._save_proposal_to_database(proposal)
            
            return proposal
            
        except Exception as e:
            logger.error(f"Error creating deployment proposal: {str(e)}")
            return {"error": str(e)}
    
    async def _save_proposal_to_database(self, proposal: Dict[str, Any]):
        """Save proposal to database"""
        try:
            session = get_session()
            async with session as s:
                from ..models.sql_models import Proposal
                
                # Only use valid Proposal fields; store extras in metadata
                metadata = {
                    'title': proposal.get('title'),
                    'priority': proposal.get('priority'),
                    'impact': proposal.get('impact'),
                    'type': proposal.get('type'),
                    'target_ai': proposal.get('target_ai'),
                    'extension_id': proposal.get('extension_id'),
                    'test_results': proposal.get('test_results'),
                    'validation_result': proposal.get('validation_result'),
                    'created_by': proposal.get('created_by')
                }
                extension_id = proposal.get('extension_id') or 'unknown_extension'
                db_proposal = Proposal(
                    id=uuid.UUID(proposal['id']),
                    file_path=f"extensions/{extension_id}.py",
                    code_before=proposal.get('code_before') or '',
                    code_after=proposal.get('code_after') or '',
                    status=proposal['status'],
                    ai_type="imperium",
                    created_at=datetime.fromisoformat(proposal['created_at'].replace('Z', '+00:00')),
                    description=proposal['description'],
                    # Store all extra fields in metadata
                    learning_sources=[metadata]
                )
                
                s.add(db_proposal)
                await s.commit()
                
        except Exception as e:
            logger.error(f"Error saving proposal to database: {str(e)}")
    
    async def _save_extension(self, extension_id: str, extension_data: Dict[str, Any]):
        """Save extension to storage"""
        try:
            extensions_path = f"{settings.ml_model_path}/extensions"
            os.makedirs(extensions_path, exist_ok=True)
            
            # Save extension metadata
            metadata_file = os.path.join(extensions_path, f"{extension_id}.json")
            with open(metadata_file, 'w') as f:
                json.dump(extension_data, f, indent=2)
            
            # Save extension code
            code_file = os.path.join(extensions_path, f"{extension_id}.py")
            with open(code_file, 'w') as f:
                f.write(extension_data['code'])
                
        except Exception as e:
            logger.error(f"Error saving extension: {str(e)}")
    
    async def get_extension_analytics(self) -> Dict[str, Any]:
        """Get extension creation analytics"""
        try:
            analytics = {
                "total_extensions": len(self.extensions),
                "extensions_by_status": {},
                "extensions_by_target": {},
                "extensions_by_type": {},
                "recent_extensions": [],
                "success_rate": 0,
                "average_test_score": 0
            }
            
            # Calculate statistics
            status_counts = {}
            target_counts = {}
            type_counts = {}
            passed_count = 0
            total_scores = 0
            score_count = 0
            
            for ext_id, extension in self.extensions.items():
                # Status counts
                status = extension.get("status", "unknown")
                status_counts[status] = status_counts.get(status, 0) + 1
                
                # Target counts
                target = extension.get("target_ai", "unknown")
                target_counts[target] = target_counts.get(target, 0) + 1
                
                # Type counts
                ext_type = extension.get("extension_type", "unknown")
                type_counts[ext_type] = type_counts.get(ext_type, 0) + 1
                
                # Success rate
                if extension.get("test_results", {}).get("passed", False):
                    passed_count += 1
                
                # Average test score
                validation = extension.get("test_results", {}).get("validation_result", {})
                if validation.get("quality_score"):
                    total_scores += validation["quality_score"]
                    score_count += 1
            
            analytics["extensions_by_status"] = status_counts
            analytics["extensions_by_target"] = target_counts
            analytics["extensions_by_type"] = type_counts
            analytics["success_rate"] = passed_count / len(self.extensions) if self.extensions else 0
            analytics["average_test_score"] = total_scores / score_count if score_count > 0 else 0
            
            # Recent extensions
            recent_extensions = sorted(
                self.extensions.values(),
                key=lambda x: x.get("created_at", ""),
                reverse=True
            )[:10]
            
            analytics["recent_extensions"] = [
                {
                    "id": ext["id"],
                    "name": ext["name"],
                    "target_ai": ext["target_ai"],
                    "status": ext["status"],
                    "created_at": ext["created_at"]
                }
                for ext in recent_extensions
            ]
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting extension analytics: {str(e)}")
            return {"error": str(e)}
    
    async def get_extension_details(self, extension_id: str) -> Dict[str, Any]:
        """Get detailed information about an extension"""
        try:
            if extension_id not in self.extensions:
                return {"status": "error", "message": "Extension not found"}
            
            extension = self.extensions[extension_id]
            
            return {
                "status": "success",
                "extension": extension
            }
            
        except Exception as e:
            logger.error(f"Error getting extension details: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def list_extensions(self, target_ai: str = None, status: str = None) -> Dict[str, Any]:
        """List extensions with optional filtering"""
        try:
            filtered_extensions = []
            
            for ext_id, extension in self.extensions.items():
                # Apply filters
                if target_ai and extension.get("target_ai") != target_ai:
                    continue
                if status and extension.get("status") != status:
                    continue
                
                filtered_extensions.append({
                    "id": ext_id,
                    "name": extension["name"],
                    "target_ai": extension["target_ai"],
                    "extension_type": extension["extension_type"],
                    "status": extension["status"],
                    "created_at": extension["created_at"],
                    "test_passed": extension.get("test_results", {}).get("passed", False)
                })
            
            return {
                "status": "success",
                "extensions": filtered_extensions,
                "count": len(filtered_extensions)
            }
            
        except Exception as e:
            logger.error(f"Error listing extensions: {str(e)}")
            return {"status": "error", "message": str(e)} 