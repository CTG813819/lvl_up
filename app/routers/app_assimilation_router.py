"""
App Assimilation Router - Handles APK/iOS file upload and assimilation
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse, FileResponse
from typing import Dict, Any, List
import structlog
import os
import tempfile
import shutil
from datetime import datetime

from ..services.app_assimilation_service import get_app_assimilation_service
from fastapi import BackgroundTasks

logger = structlog.get_logger()
router = APIRouter(prefix="/api/app-assimilation", tags=["app-assimilation"])

@router.post("/upload-and-analyze")
async def upload_and_analyze_app(
    file: UploadFile = File(...),
    user_id: str = "default_user"  # In production, get from auth
) -> Dict[str, Any]:
    """Upload and analyze an APK/iOS file for assimilation"""
    logger.info(f"📤 File upload received: {file.filename}")
    
    # Validate file type
    file_extension = file.filename.lower().split('.')[-1] if file.filename else ""
    if file_extension not in ['apk', 'ipa', 'app']:
        raise HTTPException(
            status_code=400, 
            detail="Unsupported file type. Only APK and iOS app files are supported."
        )
    
    # Determine file type
    file_type = "apk" if file_extension == "apk" else "ios"
    
    # Save uploaded file temporarily
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        logger.info(f"💾 File saved temporarily: {temp_file_path}")
        
        # Analyze the file
        app_assimilation_service = get_app_assimilation_service()
        analysis = await app_assimilation_service.analyze_uploaded_app(temp_file_path, file_type)
        
        # Assimilate the app
        assimilation_result = await app_assimilation_service.assimilate_app(analysis, user_id)

        # Persist the uploaded binary path to enable launching
        app_assimilation_service.set_app_binary(assimilation_result["app_id"], temp_file_path, file_type)
        
        logger.info(f"✅ App analysis and assimilation completed: {assimilation_result['app_id']}")
        
        return {
            "status": "success",
            "message": "App uploaded, analyzed, and assimilated successfully",
            "app_id": assimilation_result["app_id"],
            "analysis": analysis,
            "assimilation": assimilation_result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ File upload and analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            # Keep binary for launching; do not delete
            logger.info(f"📦 Preserved uploaded binary for launching: {temp_file_path}")

@router.get("/assimilated-apps")
async def get_assimilated_apps(user_id: str = "default_user") -> Dict[str, Any]:
    """Get all assimilated apps for a user"""
    try:
        app_assimilation_service = get_app_assimilation_service()
        apps = await app_assimilation_service.get_assimilated_apps(user_id)
        
        logger.info(f"📱 Retrieved {len(apps)} assimilated apps for user: {user_id}")
        
        return {
            "status": "success",
            "apps": apps,
            "total_count": len(apps),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get assimilated apps: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve apps: {str(e)}")

@router.get("/app-status/{app_id}")
async def get_app_status(app_id: str, user_id: str = "default_user") -> Dict[str, Any]:
    """Get the current status of an assimilated app"""
    try:
        app_assimilation_service = get_app_assimilation_service()
        status = await app_assimilation_service.get_app_assimilation_status(app_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="App not found")
        
        # Verify user ownership
        if status.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        logger.info(f"📊 Retrieved status for app: {app_id}")
        
        return {
            "status": "success",
            "app_status": status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get app status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve app status: {str(e)}")


@router.post("/launch/{app_id}")
async def launch_app(app_id: str, user_id: str = "default_user") -> Dict[str, Any]:
    """Launch the stored app binary in a safe sandbox (best-effort)."""
    try:
        svc = get_app_assimilation_service()
        status = await svc.get_app_assimilation_status(app_id)
        if not status or status.get("user_id") != user_id:
            raise HTTPException(status_code=404, detail="App not found")

        binary = svc.get_app_binary(app_id)
        if not binary:
            raise HTTPException(status_code=404, detail="App binary not available")

        # We cannot execute mobile packages on the server; return a signed URL path for client-side runner
        return {
            "status": "ready",
            "launch": {
                "type": binary["type"],
                "path": binary["path"],
                "note": "Client should download and run in an appropriate sandbox/emulator.",
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to prepare launch: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to prepare launch: {str(e)}")


@router.get("/download/{app_id}")
async def download_app_binary(app_id: str, user_id: str = "default_user"):
    """Stream the stored app binary to the client for front-end install/launch."""
    try:
        svc = get_app_assimilation_service()
        status = await svc.get_app_assimilation_status(app_id)
        if not status or status.get("user_id") != user_id:
            raise HTTPException(status_code=404, detail="App not found")

        binary = svc.get_app_binary(app_id)
        if not binary:
            raise HTTPException(status_code=404, detail="App binary not available")

        file_path = binary["path"]
        file_type = binary.get("type", "unknown")
        filename = f"{app_id}.{'apk' if file_type == 'apk' else 'ipa'}"
        media_type = (
            "application/vnd.android.package-archive" if file_type == "apk" else "application/octet-stream"
        )
        return FileResponse(path=file_path, filename=filename, media_type=media_type)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to download app binary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to download app: {str(e)}")


@router.post("/improvement-suggestions/{app_id}")
async def generate_improvement_suggestions(app_id: str, user_id: str = "default_user") -> Dict[str, Any]:
    """Generate chaos-code-driven improvement suggestions for an assimilated app."""
    try:
        svc = get_app_assimilation_service()
        app_status = await svc.get_app_assimilation_status(app_id)
        if not app_status or app_status.get("user_id") != user_id:
            raise HTTPException(status_code=404, detail="App not found")

        analysis = app_status.get("original_analysis", {})
        suggestions = []

        # Simple, actionable suggestions derived from analysis
        if analysis.get("file_type") == "apk":
            if "android.permission.WRITE_EXTERNAL_STORAGE" in analysis.get("permissions", []):
                suggestions.append({
                    "id": f"SUG_{app_id}_perm_ext_storage",
                    "title": "Reduce storage permission scope",
                    "description": "Use scoped storage API instead of WRITE_EXTERNAL_STORAGE.",
                    "impact": "security",
                    "apply_patch": "android:requestLegacyExternalStorage=\"false\""
                })
            if analysis.get("security_analysis", {}).get("vulnerability_score", 0) > 70:
                suggestions.append({
                    "id": f"SUG_{app_id}_obfuscation",
                    "title": "Enable code obfuscation",
                    "description": "Add ProGuard/R8 rules to obfuscate critical classes.",
                    "impact": "security",
                    "apply_patch": "proguard-rules.pro: -keep class com.example.** { *; }"
                })
        else:
            suggestions.append({
                "id": f"SUG_{app_id}_crypto",
                "title": "Use platform keychain for secrets",
                "description": "Store tokens in Keychain/Keystore and rotate keys daily.",
                "impact": "security",
                "apply_patch": "migrate to Keychain/Keystore"
            })

        # Record suggestions
        app_status.setdefault("improvement_suggestions", [])
        app_status["improvement_suggestions"] = suggestions
        return {"status": "success", "suggestions": suggestions, "count": len(suggestions)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to generate suggestions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate suggestions: {str(e)}")


@router.post("/apply-suggestion/{app_id}/{suggestion_id}")
async def apply_suggestion(app_id: str, suggestion_id: str, user_id: str = "default_user") -> Dict[str, Any]:
    """Apply a suggestion (logical application with audit trail)."""
    try:
        svc = get_app_assimilation_service()
        app_status = await svc.get_app_assimilation_status(app_id)
        if not app_status or app_status.get("user_id") != user_id:
            raise HTTPException(status_code=404, detail="App not found")

        suggestions = app_status.get("improvement_suggestions", [])
        found = next((s for s in suggestions if s.get("id") == suggestion_id), None)
        if not found:
            raise HTTPException(status_code=404, detail="Suggestion not found")

        app_status.setdefault("applied_suggestions", [])
        app_status["applied_suggestions"].append({
            **found,
            "applied_at": datetime.utcnow().isoformat(),
        })
        return {"status": "success", "applied": found}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to apply suggestion: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to apply suggestion: {str(e)}")


@router.post("/revert-suggestion/{app_id}/{suggestion_id}")
async def revert_suggestion(app_id: str, suggestion_id: str, user_id: str = "default_user") -> Dict[str, Any]:
    """Revert a previously applied suggestion (logical revert with audit trail)."""
    try:
        svc = get_app_assimilation_service()
        app_status = await svc.get_app_assimilation_status(app_id)
        if not app_status or app_status.get("user_id") != user_id:
            raise HTTPException(status_code=404, detail="App not found")

        applied = app_status.get("applied_suggestions", [])
        remaining = [s for s in applied if s.get("id") != suggestion_id]
        if len(remaining) == len(applied):
            raise HTTPException(status_code=404, detail="Applied suggestion not found")
        app_status["applied_suggestions"] = remaining
        return {"status": "success", "reverted": suggestion_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to revert suggestion: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to revert suggestion: {str(e)}")

@router.delete("/delete-app/{app_id}")
async def delete_assimilated_app(app_id: str, user_id: str = "default_user") -> Dict[str, Any]:
    """Delete an assimilated app"""
    try:
        app_assimilation_service = get_app_assimilation_service()
        success = await app_assimilation_service.delete_assimilated_app(app_id, user_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="App not found or access denied")
        
        logger.info(f"🗑️ Deleted assimilated app: {app_id}")
        
        return {
            "status": "success",
            "message": "App deleted successfully",
            "app_id": app_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete app: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete app: {str(e)}")


@router.post("/rename/{app_id}")
async def rename_app(app_id: str, payload: Dict[str, Any], user_id: str = "default_user") -> Dict[str, Any]:
    """Rename the assimilated app display name."""
    try:
        new_name = str(payload.get("name", "")).strip()
        if not new_name:
            raise HTTPException(status_code=400, detail="Missing 'name'")
        svc = get_app_assimilation_service()
        status = await svc.get_app_assimilation_status(app_id)
        if not status or status.get("user_id") != user_id:
            raise HTTPException(status_code=404, detail="App not found")
        ok = svc.set_app_name(app_id, new_name)
        if not ok:
            raise HTTPException(status_code=500, detail="Failed to rename app")
        return {"status": "success", "app_id": app_id, "name": new_name}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to rename app: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to rename app: {str(e)}")

@router.get("/integration-progress/{app_id}")
async def get_integration_progress(app_id: str, user_id: str = "default_user") -> Dict[str, Any]:
    """Get the real-time integration progress of an assimilated app"""
    try:
        app_assimilation_service = get_app_assimilation_service()
        status = await app_assimilation_service.get_app_assimilation_status(app_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="App not found")
        
        # Verify user ownership
        if status.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        real_time_monitoring = status.get("real_time_monitoring", {})
        
        logger.info(f"📈 Retrieved integration progress for app: {app_id}")
        
        return {
            "status": "success",
            "app_id": app_id,
            "integration_progress": real_time_monitoring.get("integration_progress", 0),
            "chaos_code_applied": real_time_monitoring.get("chaos_code_applied", False),
            "synthetic_code_applied": real_time_monitoring.get("synthetic_code_applied", False),
            "chaos_integration_status": status.get("chaos_integration_status", "pending"),
            "synthetic_code_status": status.get("synthetic_code_status", "pending"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get integration progress: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve progress: {str(e)}")

@router.get("/chaos-integration-points/{app_id}")
async def get_chaos_integration_points(app_id: str, user_id: str = "default_user") -> Dict[str, Any]:
    """Get the identified chaos integration points for an assimilated app"""
    try:
        app_assimilation_service = get_app_assimilation_service()
        status = await app_assimilation_service.get_app_assimilation_status(app_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="App not found")
        
        # Verify user ownership
        if status.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        original_analysis = status.get("original_analysis", {})
        integration_points = original_analysis.get("chaos_integration_points", [])
        
        logger.info(f"🎯 Retrieved {len(integration_points)} chaos integration points for app: {app_id}")
        
        return {
            "status": "success",
            "app_id": app_id,
            "integration_points": integration_points,
            "total_points": len(integration_points),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get chaos integration points: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve integration points: {str(e)}")

@router.get("/security-analysis/{app_id}")
async def get_security_analysis(app_id: str, user_id: str = "default_user") -> Dict[str, Any]:
    """Get the security analysis for an assimilated app"""
    try:
        app_assimilation_service = get_app_assimilation_service()
        status = await app_assimilation_service.get_app_assimilation_status(app_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="App not found")
        
        # Verify user ownership
        if status.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        original_analysis = status.get("original_analysis", {})
        security_analysis = original_analysis.get("security_analysis", {})
        
        logger.info(f"🔒 Retrieved security analysis for app: {app_id}")
        
        return {
            "status": "success",
            "app_id": app_id,
            "security_analysis": security_analysis,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get security analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve security analysis: {str(e)}")
