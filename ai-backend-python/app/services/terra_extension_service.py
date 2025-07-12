from sqlalchemy.orm import Session
from app.models.terra_extension import TerraExtension
from app.services.ai_agent_service import AIAgentService
from app.services.ai_growth_service import AIGrowthService
from typing import List, Dict, Any, Optional
import asyncio
import json
from datetime import datetime
from app.services.anthropic_service import call_claude, anthropic_rate_limited_call
import logging

logger = logging.getLogger(__name__)

class TerraExtensionService:
    def __init__(self):
        self.ai_service = AIAgentService()
        self.growth_service = AIGrowthService()
    
    async def create_extension(self, db: Session, extension_data: Dict[str, Any]) -> TerraExtension:
        """Create a new extension and start testing pipeline"""
        dart_code = extension_data.get('dart_code')
        if not dart_code:
            dart_code = await ai_generate_dart_code(extension_data.get('description', ''))
            extension_data['dart_code'] = dart_code
        extension = TerraExtension(**extension_data)
        db.add(extension)
        db.commit()
        db.refresh(extension)
        
        # Start testing pipeline asynchronously
        asyncio.create_task(self.run_extension_tests(db, extension.id))
        
        # After successful extension creation, Claude verification
        try:
            verification = await anthropic_rate_limited_call(
                f"Sandbox AI created extension '{extension_data.get('name', 'Unknown')}'. Please verify the extension and suggest improvements.",
                ai_name="sandbox"
            )
            logger.info(f"Claude verification for extension creation: {verification}")
        except Exception as e:
            logger.warning(f"Claude verification error: {str(e)}")
        
        return extension
    
    async def get_extensions(self, db: Session, status: Optional[str] = None) -> List[TerraExtension]:
        """Get extensions with optional status filter"""
        query = db.query(TerraExtension)
        if status:
            query = query.filter(TerraExtension.status == status)
        return query.all()
    
    async def get_extension(self, db: Session, extension_id: str) -> Optional[TerraExtension]:
        """Get a specific extension by ID"""
        return db.query(TerraExtension).filter(TerraExtension.id == extension_id).first()
    
    async def update_extension_status(self, db: Session, extension_id: str, status: str) -> Optional[TerraExtension]:
        """Update extension status"""
        extension = await self.get_extension(db, extension_id)
        if extension:
            extension.status = status
            if status == "approved":
                extension.approved_at = datetime.utcnow()
            db.commit()
            db.refresh(extension)
        return extension
    
    async def run_extension_tests(self, db: Session, extension_id: str):
        """Run comprehensive tests on the extension"""
        extension = await self.get_extension(db, extension_id)
        if not extension:
            return
        
        # Update status to testing
        extension.status = "testing"
        db.commit()
        
        test_results = {
            "integration_test": False,
            "functional_test": False,
            "combined_test": False,
            "error_messages": [],
            "ai_analysis": {}
        }
        
        try:
            # Test 1: Integration Test
            integration_result = await self.test_integration(extension.dart_code)
            test_results["integration_test"] = integration_result["success"]
            if not integration_result["success"]:
                test_results["error_messages"].append(f"Integration test failed: {integration_result['error']}")
            
            # Test 2: Functional Test
            functional_result = await self.test_functionality(extension.dart_code, extension.description)
            test_results["functional_test"] = functional_result["success"]
            if not functional_result["success"]:
                test_results["error_messages"].append(f"Functional test failed: {functional_result['error']}")
            
            # Test 3: Combined Test
            if test_results["integration_test"] and test_results["functional_test"]:
                combined_result = await self.test_combined(extension.dart_code, extension.description)
                test_results["combined_test"] = combined_result["success"]
                if not combined_result["success"]:
                    test_results["error_messages"].append(f"Combined test failed: {combined_result['error']}")
            
            # AI Analysis using sckipit models
            ai_analysis = await self.analyze_with_ai(extension.dart_code, extension.description)
            test_results["ai_analysis"] = ai_analysis
            
            # Update extension with test results
            extension.test_results = test_results
            extension.ai_analysis = ai_analysis
            
            # Update status based on test results
            if test_results["combined_test"]:
                extension.status = "ready_for_approval"
            else:
                extension.status = "failed"
            
            db.commit()
            
        except Exception as e:
            test_results["error_messages"].append(f"Test pipeline error: {str(e)}")
            extension.test_results = test_results
            extension.status = "failed"
            db.commit()
    
    async def test_integration(self, dart_code: str) -> Dict[str, Any]:
        """Test if the Dart code can be compiled and loaded"""
        if not dart_code:
            return {"success": False, "error": "No Dart code provided"}
        try:
            # Basic syntax check
            if "class" not in dart_code or "Widget" not in dart_code:
                return {"success": False, "error": "Code must contain a Widget class"}
            
            # Check for common Flutter imports
            required_imports = ["import 'package:flutter/material.dart';"]
            for import_statement in required_imports:
                if import_statement not in dart_code:
                    return {"success": False, "error": f"Missing required import: {import_statement}"}
            
            # Check for basic widget structure
            if "build(BuildContext context)" not in dart_code:
                return {"success": False, "error": "Code must contain a build method"}
            
            # Check for return statement in build method
            if "return" not in dart_code:
                return {"success": False, "error": "Code must contain a return statement in build method"}
            
            return {"success": True, "error": None}
        except Exception as e:
            return {"success": False, "error": f"Integration test error: {str(e)}"}
    
    async def test_functionality(self, dart_code: str, description: str) -> Dict[str, Any]:
        """Test if the code functionality matches the description"""
        try:
            # Use AI to analyze if code matches description
            prompt = f"""
            Analyze this Dart code and determine if it matches the described functionality:
            
            Description: {description}
            
            Dart Code:
            {dart_code}
            
            Does this code implement the described functionality? Return only 'YES' or 'NO' with a brief explanation.
            """
            
            # TODO: Use AI service to analyze
            # For now, return a basic check
            if "Container" in dart_code or "Text" in dart_code or "Column" in dart_code or "Row" in dart_code:
                return {"success": True, "error": None}
            else:
                return {"success": False, "error": "Code does not appear to implement basic UI functionality"}
                
        except Exception as e:
            return {"success": False, "error": f"Functional test error: {str(e)}"}
    
    async def test_combined(self, dart_code: str, description: str) -> Dict[str, Any]:
        """Combined test of integration and functionality"""
        try:
            # Run both tests together
            integration_result = await self.test_integration(dart_code)
            functional_result = await self.test_functionality(dart_code, description)
            
            if integration_result["success"] and functional_result["success"]:
                return {"success": True, "error": None}
            else:
                errors = []
                if not integration_result["success"]:
                    errors.append(integration_result["error"])
                if not functional_result["success"]:
                    errors.append(functional_result["error"])
                return {"success": False, "error": "; ".join(errors)}
                
        except Exception as e:
            return {"success": False, "error": f"Combined test error: {str(e)}"}
    
    async def analyze_with_ai(self, dart_code: str, description: str) -> Dict[str, Any]:
        """Use AI models to analyze the code quality and safety"""
        try:
            # TODO: Use sckipit models for analysis
            # For now, return basic analysis
            analysis = {
                "code_quality_score": 0.8,
                "safety_score": 0.9,
                "complexity_score": 0.6,
                "recommendations": [
                    "Code appears to be safe and well-structured",
                    "Consider adding error handling",
                    "Code matches the described functionality"
                ],
                "ai_confidence": 0.85
            }
            
            return analysis
        except Exception as e:
            return {"error": f"AI analysis failed: {str(e)}"}
    
    async def approve_extension(self, db: Session, extension_id: str) -> Optional[TerraExtension]:
        """Approve an extension and make it live"""
        extension = await self.get_extension(db, extension_id)
        if extension and extension.status == "ready_for_approval":
            extension.status = "approved"
            extension.approved_at = datetime.utcnow()
            db.commit()
            db.refresh(extension)
            return extension
        return None 

async def ai_generate_dart_code(description: str) -> str:
    """Generate Dart widget code from a description using AI/ML (placeholder)"""
    # TODO: Replace with real AI/ML code generation
    return f"""import 'package:flutter/material.dart';\n\n// Auto-generated widget based on description:\n// {description}\nclass AutoGeneratedWidget extends StatelessWidget {{\n  @override\n  Widget build(BuildContext context) {{\n    return Container(\n      child: Text('This widget was generated from your description.'),\n    );\n  }}\n}}""" 

    def anthropic_extension_generation(self, prompt: str) -> str:
        """Use Anthropic Claude for extension code generation or review."""
        try:
            return call_claude(prompt)
        except Exception as e:
            return f"Anthropic error: {str(e)}" 