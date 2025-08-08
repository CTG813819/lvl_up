from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
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
    sckipit_service = await SckipitService.initialize()
    # If dart_code is not provided, generate it using sckipit
    dart_code = extension.dart_code
    if not dart_code:
        # Use the new real code generation method
        dart_code = await sckipit_service.generate_dart_code_from_description_async(extension.description)
    extension_data = extension.model_dump()
    extension_data['dart_code'] = dart_code
    logger.info("DEBUG: About to create TerraExtension object")
    terra_extension = await TerraExtensionService.create_extension(db, extension_data)
    return ExtensionResponse(
        id=str(terra_extension.id),
        feature_name=terra_extension.feature_name,
        menu_title=terra_extension.menu_title,
        icon_name=terra_extension.icon_name,
        description=terra_extension.description,
        status=terra_extension.status,
        test_results=terra_extension.test_results,
        ai_analysis=terra_extension.ai_analysis,
        created_at=terra_extension.created_at,
        updated_at=terra_extension.updated_at,
        approved_at=terra_extension.approved_at
    )


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
    """Run tests for an extension"""
    try:
        # Test integration
        integration_result = await test_integration(extension.dart_code or "")
        # Test functionality
        functionality_result = await test_functionality(extension.dart_code or "", extension.description)
        # Test combined
        combined_result = await test_combined(extension.dart_code or "", extension.description)
        # AI analysis
        ai_analysis = await analyze_with_ai(extension.dart_code or "", extension.description)

        return {
            "integration_test": integration_result,
            "functionality_test": functionality_result,
            "combined_test": combined_result,
            "ai_analysis": ai_analysis
        }
    except Exception as e:
        logger.error(f"Error running extension tests: {str(e)}")
        return {"error": str(e)}


async def test_integration(dart_code: str) -> Dict[str, Any]:
    """Test if the extension integrates well with the existing codebase"""
    try:
        # Simple integration test - check for common Flutter patterns
        integration_score = 0.0
        issues = []

        if "class" in dart_code and "extends" in dart_code:
            integration_score += 0.3
        else:
            issues.append("Missing proper class definition")

        if "build(" in dart_code:
            integration_score += 0.3
        else:
            issues.append("Missing build method")

        if "return" in dart_code:
            integration_score += 0.2
        else:
            issues.append("Missing return statement")

        if "Widget" in dart_code:
            integration_score += 0.2
        else:
            issues.append("Missing Widget import or usage")

        return {
            "score": integration_score,
            "issues": issues,
            "passed": integration_score >= 0.7
        }
    except Exception as e:
        return {"error": str(e), "score": 0.0, "passed": False}


async def test_functionality(dart_code: str, description: str) -> Dict[str, Any]:
    """Test if the extension provides the functionality described"""
    try:
        # Simple functionality test based on description keywords
        functionality_score = 0.0
        issues = []

        description_lower = description.lower()
        dart_code_lower = dart_code.lower()

        # Check if code contains elements mentioned in description
        if "button" in description_lower and "elevatedbutton" in dart_code_lower:
            functionality_score += 0.3
        elif "button" in description_lower:
            issues.append("Button mentioned in description but not found in code")

        if "text" in description_lower and "text(" in dart_code_lower:
            functionality_score += 0.2
        elif "text" in description_lower:
            issues.append("Text mentioned in description but not found in code")

        if "icon" in description_lower and "icon(" in dart_code_lower:
            functionality_score += 0.2
        elif "icon" in description_lower:
            issues.append("Icon mentioned in description but not found in code")

        if "color" in description_lower and "color:" in dart_code_lower:
            functionality_score += 0.1
        elif "color" in description_lower:
            issues.append("Color mentioned in description but not found in code")

        if "padding" in description_lower and "padding(" in dart_code_lower:
            functionality_score += 0.1
        elif "padding" in description_lower:
            issues.append("Padding mentioned in description but not found in code")

        if "margin" in description_lower and "margin(" in dart_code_lower:
            functionality_score += 0.1
        elif "margin" in description_lower:
            issues.append("Margin mentioned in description but not found in code")

        return {
            "score": functionality_score,
            "issues": issues,
            "passed": functionality_score >= 0.5
        }
    except Exception as e:
        return {"error": str(e), "score": 0.0, "passed": False}


async def test_combined(dart_code: str, description: str) -> Dict[str, Any]:
    """Combined test of integration and functionality"""
    try:
        integration_result = await test_integration(dart_code)
        functionality_result = await test_functionality(dart_code, description)

        combined_score = (integration_result.get("score", 0.0) + functionality_result.get("score", 0.0)) / 2
        all_issues = integration_result.get("issues", []) + functionality_result.get("issues", [])

        return {
            "score": combined_score,
            "integration_score": integration_result.get("score", 0.0),
            "functionality_score": functionality_result.get("score", 0.0),
            "issues": all_issues,
            "passed": combined_score >= 0.6
        }
    except Exception as e:
        return {"error": str(e), "score": 0.0, "passed": False}


async def analyze_with_ai(dart_code: str, description: str) -> Dict[str, Any]:
    """Analyze the extension using AI"""
    try:
        # Simple AI analysis based on code quality metrics
        analysis_score = 0.0
        suggestions = []

        # Check code length
        if len(dart_code) > 100:
            analysis_score += 0.2
        else:
            suggestions.append("Code seems too short for a meaningful extension")

        # Check for proper structure
        if "class" in dart_code and "build(" in dart_code:
            analysis_score += 0.3
        else:
            suggestions.append("Missing proper Flutter widget structure")

        # Check for documentation
        if "///" in dart_code or "//" in dart_code:
            analysis_score += 0.2
        else:
            suggestions.append("Consider adding documentation comments")

        # Check for error handling
        if "try" in dart_code or "catch" in dart_code:
            analysis_score += 0.2
        else:
            suggestions.append("Consider adding error handling")

        # Check for accessibility
        if "semantics" in dart_code or "accessibility" in dart_code:
            analysis_score += 0.1
        else:
            suggestions.append("Consider adding accessibility features")

        return {
            "score": analysis_score,
            "suggestions": suggestions,
            "quality": "high" if analysis_score >= 0.7 else "medium" if analysis_score >= 0.4 else "low"
        }
    except Exception as e:
        return {"error": str(e), "score": 0.0, "quality": "unknown"}


async def ai_generate_dart_code(description: str) -> str:
    """Generate Dart code using AI based on description"""
    try:
        sckipit_service = await SckipitService.initialize()
        return await sckipit_service.generate_dart_code_from_description_async(description)
    except Exception as e:
        logger.error(f"Error generating Dart code: {str(e)}")
        return f"// Error generating code: {str(e)}" 