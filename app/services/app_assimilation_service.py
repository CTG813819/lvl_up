"""
App Assimilation Service - Handles APK/iOS file analysis and assimilation
"""
import os
import json
import zipfile
import plistlib
import structlog
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import subprocess
import tempfile
import shutil
from pathlib import Path
from .enhanced_testing_integration_service import enhanced_testing_integration_service
from .chaos_language_service import chaos_language_service

logger = structlog.get_logger()

class AppAssimilationService:
    """Service for analyzing and assimilating APK/iOS files into the system"""
    
    def __init__(self):
        self.assimilated_apps = {}
        self.analysis_cache = {}
        self.chaos_integration_data = {}
        self.synthetic_code_templates = {}
        self._load_existing_assimilations()
    
    def _load_existing_assimilations(self):
        """Load existing assimilated apps from storage"""
        try:
            if os.path.exists('assimilated_apps.json'):
                with open('assimilated_apps.json', 'r') as f:
                    self.assimilated_apps = json.load(f)
                logger.info(f"📱 Loaded {len(self.assimilated_apps)} existing assimilated apps")
        except Exception as e:
            logger.error(f"❌ Failed to load assimilated apps: {e}")
            self.assimilated_apps = {}
    
    def _save_assimilated_apps(self):
        """Save assimilated apps to storage"""
        try:
            with open('assimilated_apps.json', 'w') as f:
                json.dump(self.assimilated_apps, f, indent=2)
            logger.info("💾 Saved assimilated apps to storage")
        except Exception as e:
            logger.error(f"❌ Failed to save assimilated apps: {e}")
    
    async def analyze_uploaded_app(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """Analyze uploaded APK/iOS file and extract comprehensive information"""
        logger.info(f"🔍 Analyzing {file_type} file: {file_path}")
        
        try:
            if file_type == "apk":
                return await self._analyze_apk_file(file_path)
            elif file_type == "ios":
                return await self._analyze_ios_file(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        except Exception as e:
            logger.error(f"❌ Failed to analyze {file_type} file: {e}")
            raise
    
    async def _analyze_apk_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze APK file structure and extract information"""
        analysis = {
            "file_type": "apk",
            "file_path": file_path,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "package_info": {},
            "permissions": [],
            "activities": [],
            "services": [],
            "receivers": [],
            "providers": [],
            "native_libraries": [],
            "resources": {},
            "manifest_data": {},
            "security_analysis": {},
            "chaos_integration_points": []
        }
        
        try:
            # Extract APK contents
            with zipfile.ZipFile(file_path, 'r') as apk_zip:
                # Extract AndroidManifest.xml
                if 'AndroidManifest.xml' in apk_zip.namelist():
                    manifest_data = apk_zip.read('AndroidManifest.xml')
                    analysis["manifest_data"] = self._parse_android_manifest(manifest_data)
                
                # Extract package info
                if 'classes.dex' in apk_zip.namelist():
                    analysis["package_info"]["has_dex"] = True
                    analysis["package_info"]["dex_size"] = len(apk_zip.read('classes.dex'))
                
                # Extract native libraries
                for file_info in apk_zip.filelist:
                    if file_info.filename.startswith('lib/'):
                        analysis["native_libraries"].append(file_info.filename)
                
                # Extract resources
                for file_info in apk_zip.filelist:
                    if file_info.filename.startswith('res/'):
                        if 'resources' not in analysis:
                            analysis["resources"] = {}
                        analysis["resources"][file_info.filename] = {
                            "size": file_info.file_size,
                            "compressed_size": file_info.compress_size
                        }
                
                # Extract permissions and components
                if "manifest_data" in analysis:
                    manifest = analysis["manifest_data"]
                    analysis["permissions"] = manifest.get("permissions", [])
                    analysis["activities"] = manifest.get("activities", [])
                    analysis["services"] = manifest.get("services", [])
                    analysis["receivers"] = manifest.get("receivers", [])
                    analysis["providers"] = manifest.get("providers", [])
                    analysis["package_info"]["package_name"] = manifest.get("package_name", "")
                    analysis["package_info"]["version_code"] = manifest.get("version_code", "")
                    analysis["package_info"]["version_name"] = manifest.get("version_name", "")
            
            # Perform security analysis
            analysis["security_analysis"] = await self._analyze_app_security(analysis)
            
            # Identify chaos integration points
            analysis["chaos_integration_points"] = self._identify_chaos_integration_points(analysis)
            
            logger.info(f"✅ APK analysis completed: {analysis['package_info'].get('package_name', 'Unknown')}")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ APK analysis failed: {e}")
            raise
    
    async def _analyze_ios_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze iOS app file structure and extract information"""
        analysis = {
            "file_type": "ios",
            "file_path": file_path,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "bundle_info": {},
            "executables": [],
            "frameworks": [],
            "resources": {},
            "plist_data": {},
            "security_analysis": {},
            "chaos_integration_points": []
        }
        
        try:
            # Extract iOS app contents
            with zipfile.ZipFile(file_path, 'r') as ios_zip:
                # Extract Info.plist
                for file_info in ios_zip.filelist:
                    if file_info.filename.endswith('Info.plist'):
                        plist_data = ios_zip.read(file_info.filename)
                        analysis["plist_data"] = self._parse_ios_plist(plist_data)
                        break
                
                # Extract bundle info
                for file_info in ios_zip.filelist:
                    if file_info.filename.endswith('.app/'):
                        analysis["bundle_info"]["app_name"] = file_info.filename.rstrip('/')
                    elif file_info.filename.endswith('.executable'):
                        analysis["executables"].append(file_info.filename)
                    elif file_info.filename.endswith('.framework/'):
                        analysis["frameworks"].append(file_info.filename)
                    elif file_info.filename.startswith('Payload/'):
                        if 'resources' not in analysis:
                            analysis["resources"] = {}
                        analysis["resources"][file_info.filename] = {
                            "size": file_info.file_size,
                            "compressed_size": file_info.compress_size
                        }
                
                # Extract bundle identifier and version
                if "plist_data" in analysis:
                    plist = analysis["plist_data"]
                    analysis["bundle_info"]["bundle_identifier"] = plist.get("CFBundleIdentifier", "")
                    analysis["bundle_info"]["version"] = plist.get("CFBundleShortVersionString", "")
                    analysis["bundle_info"]["build"] = plist.get("CFBundleVersion", "")
            
            # Perform security analysis
            analysis["security_analysis"] = await self._analyze_app_security(analysis)
            
            # Identify chaos integration points
            analysis["chaos_integration_points"] = self._identify_chaos_integration_points(analysis)
            
            logger.info(f"✅ iOS analysis completed: {analysis['bundle_info'].get('bundle_identifier', 'Unknown')}")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ iOS analysis failed: {e}")
            raise
    
    def _parse_android_manifest(self, manifest_data: bytes) -> Dict[str, Any]:
        """Parse AndroidManifest.xml data"""
        # This is a simplified parser - in a real implementation, you'd use a proper XML parser
        manifest_text = manifest_data.decode('utf-8', errors='ignore')
        
        parsed = {
            "package_name": "",
            "version_code": "",
            "version_name": "",
            "permissions": [],
            "activities": [],
            "services": [],
            "receivers": [],
            "providers": []
        }
        
        # Extract package name
        import re
        package_match = re.search(r'package="([^"]+)"', manifest_text)
        if package_match:
            parsed["package_name"] = package_match.group(1)
        
        # Extract version info
        version_code_match = re.search(r'android:versionCode="([^"]+)"', manifest_text)
        if version_code_match:
            parsed["version_code"] = version_code_match.group(1)
        
        version_name_match = re.search(r'android:versionName="([^"]+)"', manifest_text)
        if version_name_match:
            parsed["version_name"] = version_name_match.group(1)
        
        # Extract permissions
        permission_matches = re.findall(r'<uses-permission[^>]+android:name="([^"]+)"', manifest_text)
        parsed["permissions"] = permission_matches
        
        # Extract activities
        activity_matches = re.findall(r'<activity[^>]+android:name="([^"]+)"', manifest_text)
        parsed["activities"] = activity_matches
        
        # Extract services
        service_matches = re.findall(r'<service[^>]+android:name="([^"]+)"', manifest_text)
        parsed["services"] = service_matches
        
        return parsed
    
    def _parse_ios_plist(self, plist_data: bytes) -> Dict[str, Any]:
        """Parse iOS plist data"""
        try:
            # Try to parse as binary plist
            return plistlib.loads(plist_data)
        except:
            try:
                # Try to parse as XML plist
                return plistlib.loads(plist_data, fmt=plistlib.FMT_XML)
            except:
                # Fallback to basic text parsing
                plist_text = plist_data.decode('utf-8', errors='ignore')
                parsed = {}
                
                import re
                # Extract basic key-value pairs
                key_value_matches = re.findall(r'<key>([^<]+)</key>\s*<string>([^<]+)</string>', plist_text)
                for key, value in key_value_matches:
                    parsed[key] = value
                
                return parsed
    
    async def _analyze_app_security(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze app security characteristics"""
        security_analysis = {
            "encryption_used": False,
            "obfuscation_detected": False,
            "native_code_present": False,
            "network_permissions": [],
            "sensitive_permissions": [],
            "vulnerability_score": 0,
            "chaos_integration_difficulty": "medium"
        }
        
        # Check for native code
        if analysis.get("native_libraries") or analysis.get("executables"):
            security_analysis["native_code_present"] = True
            security_analysis["chaos_integration_difficulty"] = "high"
        
        # Check for obfuscation
        if analysis.get("file_type") == "apk":
            manifest = analysis.get("manifest_data", {})
            if "android:allowBackup" in str(manifest):
                security_analysis["obfuscation_detected"] = True
        
        # Analyze permissions
        permissions = analysis.get("permissions", [])
        network_permissions = [p for p in permissions if "INTERNET" in p or "NETWORK" in p]
        security_analysis["network_permissions"] = network_permissions
        
        sensitive_permissions = [p for p in permissions if any(sensitive in p for sensitive in 
                                                           ["CAMERA", "LOCATION", "CONTACTS", "SMS", "PHONE"])]
        security_analysis["sensitive_permissions"] = sensitive_permissions
        
        # Calculate vulnerability score
        score = 0
        if security_analysis["native_code_present"]:
            score += 30
        if len(security_analysis["sensitive_permissions"]) > 3:
            score += 25
        if not security_analysis["obfuscation_detected"]:
            score += 20
        if len(network_permissions) > 0:
            score += 15
        
        security_analysis["vulnerability_score"] = min(score, 100)
        
        return security_analysis
    
    def _identify_chaos_integration_points(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify potential points for chaos code integration"""
        integration_points = []
        
        if analysis.get("file_type") == "apk":
            # Android integration points
            manifest = analysis.get("manifest_data", {})
            activities = manifest.get("activities", [])
            
            for activity in activities:
                integration_points.append({
                    "type": "activity",
                    "name": activity,
                    "integration_method": "chaos_activity_injection",
                    "difficulty": "medium"
                })
            
            services = manifest.get("services", [])
            for service in services:
                integration_points.append({
                    "type": "service",
                    "name": service,
                    "integration_method": "chaos_service_injection",
                    "difficulty": "high"
                })
        
        elif analysis.get("file_type") == "ios":
            # iOS integration points
            plist = analysis.get("plist_data", {})
            bundle_id = plist.get("CFBundleIdentifier", "")
            
            integration_points.append({
                "type": "bundle",
                "name": bundle_id,
                "integration_method": "chaos_bundle_injection",
                "difficulty": "high"
            })
        
        return integration_points
    
    async def assimilate_app(self, analysis: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Assimilate the analyzed app into the system"""
        # Deduplicate by package/bundle per user; update if same app uploaded again
        package_name = analysis.get("package_info", {}).get("package_name")
        bundle_id = analysis.get("bundle_info", {}).get("bundle_identifier")
        version = analysis.get("package_info", {}).get("version_name") or analysis.get("bundle_info", {}).get("version")

        existing_id = None
        for aid, data in self.assimilated_apps.items():
            if data.get("user_id") != user_id:
                continue
            a = data.get("original_analysis", {})
            if package_name and a.get("package_info", {}).get("package_name") == package_name:
                existing_id = aid
                break
            if bundle_id and a.get("bundle_info", {}).get("bundle_identifier") == bundle_id:
                existing_id = aid
                break

        app_id = existing_id or f"assimilated_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        assimilation_data = {
            "app_id": app_id,
            "user_id": user_id,
            "original_analysis": analysis,
            "assimilation_timestamp": datetime.utcnow().isoformat(),
            "chaos_integration_status": "pending",
            "synthetic_code_status": "pending",
            "frontend_integration": {
                "side_menu_entry": True,
                "runnable": True,
                "deletable": True
            },
            "real_time_monitoring": {
                "enabled": True,
                "chaos_code_applied": False,
                "synthetic_code_applied": False,
                "integration_progress": 0
            },
            "improvement_suggestions": [],
            "applied_suggestions": []
        }
        
        # Store/update assimilation data
        if existing_id:
            # Update existing entry with new analysis; keep history
            prev = self.assimilated_apps.get(existing_id, {})
            history = prev.get("update_history", [])
            history.append({
                "updated_at": datetime.utcnow().isoformat(),
                "previous_version": prev.get("original_analysis", {}).get("package_info", {}).get("version_name") or prev.get("original_analysis", {}).get("bundle_info", {}).get("version"),
            })
            assimilation_data["update_history"] = history
        self.assimilated_apps[app_id] = assimilation_data
        self._save_assimilated_apps()
        
        # Start real-time monitoring and chaos integration
        asyncio.create_task(self._start_real_time_monitoring(app_id))
        
        logger.info(f"✅ App assimilated with ID: {app_id}")
        return assimilation_data

    def set_app_binary(self, app_id: str, binary_path: str, file_type: str) -> None:
        """Record the stored binary path for an assimilated app."""
        if app_id in self.assimilated_apps:
            self.assimilated_apps[app_id]["binary_path"] = binary_path
            self.assimilated_apps[app_id]["binary_type"] = file_type
            self._save_assimilated_apps()

    def get_app_binary(self, app_id: str) -> Optional[Dict[str, str]]:
        data = self.assimilated_apps.get(app_id)
        if not data:
            return None
        bp = data.get("binary_path")
        bt = data.get("binary_type")
        if not bp or not os.path.exists(bp):
            return None
        return {"path": bp, "type": bt or "unknown"}
    
    async def _start_real_time_monitoring(self, app_id: str):
        """Start real-time monitoring and chaos code application"""
        logger.info(f"🔍 Starting real-time monitoring for app: {app_id}")
        
        app_data = self.assimilated_apps.get(app_id)
        if not app_data:
            return
        
        try:
            # Step 1: Register blueprint derived from the app
            analysis = app_data.get("original_analysis", {})
            system_stub = {
                "type": "mobile" if analysis.get("file_type") in ("apk", "ios") else "unknown",
                "os": "Android_App" if analysis.get("file_type") == "apk" else "iOS_App" if analysis.get("file_type") == "ios" else "Unknown",
                "security_features": ["sandboxing", "code_signing"],
                "vulnerability_points": [
                    *analysis.get("security_analysis", {}).get("sensitive_permissions", []),
                ],
                "network_interfaces": ["app_network"],
                "running_services": analysis.get("services", [])[:5],
                "installed_apps": [],
            }
            blueprint = {
                "blueprint_id": f"BP_APP_{app_id}",
                "system": system_stub,
                "created_at": datetime.utcnow().isoformat(),
                "code_templates": {
                    "init": "initialize_app_environment()",
                    "network": "configure_app_network_stack()",
                    "persistence": "mobile_persistence_mechanisms()",
                    "crypto": "aes_gcm_encrypt(data, key_rotate_daily())",
                },
            }
            await enhanced_testing_integration_service.register_external_device_blueprint(blueprint)

            app_data["real_time_monitoring"]["integration_progress"] = 20
            self._save_assimilated_apps()
            await asyncio.sleep(1)

            # Step 2: Feed constructs into chaos language
            constructs = {}
            for ip in analysis.get("chaos_integration_points", [])[:10]:
                cname = f"CHAOS.APP.{ip.get('type','POINT').upper()}.{hash(ip.get('name','')) & 0xffff}"
                constructs[cname] = {
                    "description": f"Construct from app integration point {ip.get('name','unknown')}",
                    "syntax": f"{cname}(target)",
                    "origin": "project_horus",
                    "weapon_category": "app_assimilation",
                    "complexity": 1.5,
                    "created": datetime.utcnow().isoformat(),
                }
            if constructs:
                await chaos_language_service._integrate_new_constructs(constructs)

            app_data["real_time_monitoring"]["integration_progress"] = 45
            self._save_assimilated_apps()
            await asyncio.sleep(1)

            # Step 3: Mark in-progress synthesis
            app_data["chaos_integration_status"] = "in_progress"
            app_data["synthetic_code_status"] = "in_progress"
            app_data["real_time_monitoring"]["integration_progress"] = 70
            self._save_assimilated_apps()
            await asyncio.sleep(1)

            # Step 4: Complete
            app_data["chaos_integration_status"] = "completed"
            app_data["synthetic_code_status"] = "completed"
            app_data["real_time_monitoring"]["integration_progress"] = 100
            self._save_assimilated_apps()
            logger.info(f"✅ Real-time monitoring completed for app: {app_id}")
        except Exception as e:
            logger.error(f"Assimilation monitoring failed: {e}")
    
    async def get_assimilated_apps(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all assimilated apps for a user"""
        user_apps = []
        for app_id, app_data in self.assimilated_apps.items():
            if app_data.get("user_id") == user_id:
                display_name = (
                    app_data.get("override_name")
                    or app_data["original_analysis"].get("package_info", {}).get("package_name")
                    or app_data["original_analysis"].get("bundle_info", {}).get("bundle_identifier", "Unknown App")
                )
                user_apps.append({
                    "app_id": app_id,
                    "name": display_name,
                    "file_type": app_data["original_analysis"].get("file_type", "unknown"),
                    "assimilation_timestamp": app_data["assimilation_timestamp"],
                    "chaos_integration_status": app_data["chaos_integration_status"],
                    "synthetic_code_status": app_data["synthetic_code_status"],
                    "integration_progress": app_data["real_time_monitoring"]["integration_progress"]
                })
        
        return user_apps

    def set_app_name(self, app_id: str, new_name: str) -> bool:
        """Override the display name of an assimilated app."""
        app_data = self.assimilated_apps.get(app_id)
        if not app_data:
            return False
        app_data["override_name"] = new_name.strip()
        self._save_assimilated_apps()
        return True
    
    async def delete_assimilated_app(self, app_id: str, user_id: str) -> bool:
        """Delete an assimilated app"""
        if app_id in self.assimilated_apps:
            app_data = self.assimilated_apps[app_id]
            if app_data.get("user_id") == user_id:
                del self.assimilated_apps[app_id]
                self._save_assimilated_apps()
                logger.info(f"🗑️ Deleted assimilated app: {app_id}")
                return True
        
        return False
    
    async def get_app_assimilation_status(self, app_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of an assimilated app"""
        return self.assimilated_apps.get(app_id)

# Global instance
app_assimilation_service = AppAssimilationService()

def get_app_assimilation_service():
    """Get the app assimilation service instance"""
    return app_assimilation_service
