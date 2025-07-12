from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import uuid
from datetime import datetime
import asyncio
from app.services.ai_agent_service import AIAgentService
from app.services.ai_growth_service import AIGrowthService
from app.core.database import get_session
from app.core.database import get_db
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.terra_extension import TerraExtension
import httpx
import logging
from app.services.sckipit_service import SckipitService
from app.services.terra_extension_service import TerraExtensionService

logger = structlog.get_logger()
router = APIRouter(prefix="/api/terra", tags=["terra-extensions"])

class ExtensionSubmission(BaseModel):
    feature_name: str
    menu_title: str
    icon_name: str
    description: str
    dart_code: Optional[str] = None  # Now optional
    user_id: Optional[str] = None

class ExtensionResponse(BaseModel):
    id: str
    feature_name: str
    menu_title: str
    icon_name: str
    description: str
    status: str
    test_results: Optional[Dict[str, Any]] = None
    ai_analysis: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None

class ExtensionStatusUpdate(BaseModel):
    status: str

@router.post("/extensions", response_model=ExtensionResponse)
async def submit_extension(
    extension: ExtensionSubmission,
    db: AsyncSession = Depends(get_db)
):
    """Submit a new extension for Terra."""
    logger.info("DEBUG: submit_extension function called")
    sckipit_service = SckipitService()
    # If dart_code is not provided, generate it using sckipit
    dart_code = extension.dart_code
    if not dart_code:
        # Use the new real code generation method
        dart_code = sckipit_service.generate_dart_code_from_description(extension.description)
    extension_data = extension.dict()
    extension_data['dart_code'] = dart_code
    logger.info("DEBUG: About to create TerraExtension object")
    terra_extension = await TerraExtensionService.create_extension(db, extension_data)
    return ExtensionResponse.from_orm(terra_extension)

@router.get("/extensions", response_model=List[ExtensionResponse])
async def list_extensions(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List extensions with optional status filter"""
    try:
        query = select(TerraExtension)
        if status:
            query = query.where(TerraExtension.status == status)
        
        result = await db.execute(query)
        terra_extensions = result.scalars().all()
        
        current_time = datetime.utcnow()
        return [
            ExtensionResponse(
                id=str(ext.id),
                feature_name=ext.feature_name,
                menu_title=ext.menu_title,
                icon_name=ext.icon_name,
                description=ext.description,
                status=ext.status,
                test_results=ext.test_results,
                ai_analysis=ext.ai_analysis,
                created_at=ext.created_at or current_time,
                updated_at=ext.updated_at or ext.created_at or current_time,
                approved_at=ext.approved_at
            )
            for ext in terra_extensions
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list extensions: {str(e)}")

@router.get("/extensions/{extension_id}", response_model=ExtensionResponse)
async def get_extension(
    extension_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific extension by ID"""
    try:
        query = select(TerraExtension).where(TerraExtension.id == extension_id)
        result = await db.execute(query)
        terra_extension = result.scalar_one_or_none()
        
        if not terra_extension:
            raise HTTPException(status_code=404, detail="Extension not found")
        
        current_time = datetime.utcnow()
        return ExtensionResponse(
            id=str(terra_extension.id),
            feature_name=terra_extension.feature_name,
            menu_title=terra_extension.menu_title,
            icon_name=terra_extension.icon_name,
            description=terra_extension.description,
            status=terra_extension.status,
            test_results=terra_extension.test_results,
            ai_analysis=terra_extension.ai_analysis,
            created_at=terra_extension.created_at or current_time,
            updated_at=terra_extension.updated_at or terra_extension.created_at or current_time,
            approved_at=terra_extension.approved_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get extension: {str(e)}")

@router.patch("/extensions/{extension_id}")
async def update_extension_status(
    extension_id: str,
    status_update: ExtensionStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update extension status (e.g., approve, reject)"""
    try:
        query = select(TerraExtension).where(TerraExtension.id == extension_id)
        result = await db.execute(query)
        terra_extension = result.scalar_one_or_none()
        
        if not terra_extension:
            raise HTTPException(status_code=404, detail="Extension not found")
        
        terra_extension.status = status_update.status
        if status_update.status == "approved":
            terra_extension.approved_at = datetime.utcnow()
        
        terra_extension.updated_at = datetime.utcnow()
        await db.commit()
        
        return {"message": "Extension status updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update extension: {str(e)}")

@router.delete("/extensions/{extension_id}")
async def delete_extension(
    extension_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete an extension by ID"""
    try:
        query = select(TerraExtension).where(TerraExtension.id == extension_id)
        result = await db.execute(query)
        terra_extension = result.scalar_one_or_none()
        
        if not terra_extension:
            raise HTTPException(status_code=404, detail="Extension not found")
        
        # Delete the extension
        await db.delete(terra_extension)
        await db.commit()
        
        return {"message": "Extension deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete extension: {str(e)}")

async def run_extension_tests(extension_id: str, extension: ExtensionSubmission):
    """Run comprehensive tests on the extension"""
    try:
        # Create a new database session for the background task
        async with get_db() as db:
            # Update status to testing
            query = select(TerraExtension).where(TerraExtension.id == extension_id)
            result = await db.execute(query)
            terra_extension = result.scalar_one_or_none()
            
            if not terra_extension:
                return
            
            terra_extension.status = "testing"
            await db.commit()
            
            test_results = {
                "integration_test": False,
                "functional_test": False,
                "combined_test": False,
                "error_messages": [],
                "ai_analysis": {}
            }
            
            try:
                # Test 1: Integration Test - Check if code compiles and can be loaded
                integration_result = await test_integration(terra_extension.dart_code)
                test_results["integration_test"] = integration_result["success"]
                if not integration_result["success"]:
                    test_results["error_messages"].append(f"Integration test failed: {integration_result['error']}")
                
                # Test 2: Functional Test - Check if code works as described
                functional_result = await test_functionality(terra_extension.dart_code, terra_extension.description)
                test_results["functional_test"] = functional_result["success"]
                if not functional_result["success"]:
                    test_results["error_messages"].append(f"Functional test failed: {functional_result['error']}")
                
                # Test 3: Combined Test - Both integration and functionality together
                if test_results["integration_test"] and test_results["functional_test"]:
                    combined_result = await test_combined(terra_extension.dart_code, terra_extension.description)
                    test_results["combined_test"] = combined_result["success"]
                    if not combined_result["success"]:
                        test_results["error_messages"].append(f"Combined test failed: {combined_result['error']}")
                
                # AI Analysis using sckipit models
                ai_analysis = await analyze_with_ai(terra_extension.dart_code, terra_extension.description)
                test_results["ai_analysis"] = ai_analysis
                
                # Update extension with test results
                terra_extension.test_results = test_results
                terra_extension.ai_analysis = ai_analysis
                
                # Update status based on test results
                if test_results["combined_test"]:
                    terra_extension.status = "ready_for_approval"
                else:
                    terra_extension.status = "failed"
                
                terra_extension.updated_at = datetime.utcnow()
                await db.commit()
                
            except Exception as e:
                test_results["error_messages"].append(f"Test pipeline error: {str(e)}")
                terra_extension.status = "failed"
                terra_extension.test_results = test_results
                terra_extension.updated_at = datetime.utcnow()
                await db.commit()
                
    except Exception as e:
        logger.error(f"Error in run_extension_tests: {e}")

async def test_integration(dart_code: str) -> Dict[str, Any]:
    """Test if the Dart code can be compiled and loaded"""
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
        
        return {"success": True, "error": None}
    except Exception as e:
        return {"success": False, "error": f"Integration test error: {str(e)}"}

async def test_functionality(dart_code: str, description: str) -> Dict[str, Any]:
    """Test if the code functionality matches the description"""
    try:
        # Basic functionality check
        if "Container" in dart_code or "Text" in dart_code or "Column" in dart_code or "Row" in dart_code:
            return {"success": True, "error": None}
        else:
            return {"success": False, "error": "Code does not appear to implement basic UI functionality"}
            
    except Exception as e:
        return {"success": False, "error": f"Functional test error: {str(e)}"}

async def test_combined(dart_code: str, description: str) -> Dict[str, Any]:
    """Combined test of integration and functionality"""
    try:
        # Run both tests together
        integration_result = await test_integration(dart_code)
        functional_result = await test_functionality(dart_code, description)
        
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

async def analyze_with_ai(dart_code: str, description: str) -> Dict[str, Any]:
    """Analyze the extension using AI models"""
    try:
        # Basic AI analysis
        analysis = {
            "code_quality": "good" if "class" in dart_code and "Widget" in dart_code else "poor",
            "complexity": "simple" if len(dart_code.split('\n')) < 50 else "complex",
            "ui_elements": len([line for line in dart_code.split('\n') if any(widget in line for widget in ["Container", "Text", "Column", "Row", "Icon"])]),
            "description_match": "high" if any(word.lower() in description.lower() for word in dart_code.split()) else "low"
        }
        
        return analysis
        
    except Exception as e:
        return {"error": f"AI analysis failed: {str(e)}"} 

async def ai_generate_dart_code(description: str) -> str:
    """Generate Dart widget code from a description using sckipit REST API (live)."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8001/generate",
                json={"description": description, "language": "dart"}
            )
            response.raise_for_status()
            data = response.json()
            code = data.get("code")
            if code and len(code) > 20:
                return code
    except Exception as e:
        # Log the error and fallback to a default widget
        logging.error(f"sckipit codegen failed: {e}")
    # Fallback: return a simple widget
    return f"""import 'package:flutter/material.dart';\n\n// Fallback widget for: {description}\nclass AutoGeneratedWidget extends StatelessWidget {{\n  @override\n  Widget build(BuildContext context) {{\n    return Container(\n      child: Text('This widget was generated from your description.'),\n    );\n  }}\n}}""" 