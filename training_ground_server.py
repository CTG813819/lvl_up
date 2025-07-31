"""
Training Ground Server - FastAPI server for the training ground system
Runs on port 8002 and provides training ground scenarios with automatic difficulty selection
"""

import os
import asyncio
import json
import random
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional, List
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel
import structlog
from datetime import datetime, timedelta

# Setup basic logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Pydantic models
class ScenarioRequest(BaseModel):
    sandbox_level: int
    auto_difficulty: bool = True

class DeployRequest(BaseModel):
    scenario: Dict[str, Any]
    weapon_id: Optional[str] = None

class ScenarioResponse(BaseModel):
    status: str
    scenario: Dict[str, Any]
    timestamp: str

class DeployResponse(BaseModel):
    status: str
    deployment_id: str
    target_info: Dict[str, Any]
    timestamp: str

# Enhanced scenario templates with detailed descriptions
SCENARIO_TEMPLATES = {
    "sql_injection": {
        "easy": {
            "name": "Basic SQL Injection Challenge",
            "description": "A vulnerable web application with basic SQL injection flaws. The application uses simple string concatenation for database queries, making it susceptible to classic SQL injection attacks. Your mission is to bypass authentication and extract sensitive data from the database.",
            "detailed_objective": "Successfully exploit SQL injection vulnerabilities to: 1) Bypass login authentication, 2) Extract user credentials from the database, 3) Access the admin panel, 4) Retrieve sensitive information about the application's structure.",
            "vulnerabilities": ["sql_injection", "information_disclosure"],
            "techniques": ["union_based", "boolean_based", "error_based"],
            "learning_focus": "Understanding basic SQL injection principles, UNION-based attacks, and database enumeration techniques."
        },
        "medium": {
            "name": "Advanced SQL Injection with WAF Bypass",
            "description": "A more sophisticated web application with basic WAF protection. The application implements some input validation but still contains exploitable SQL injection vulnerabilities. You'll need to use advanced techniques to bypass the WAF and successfully exploit the application.",
            "detailed_objective": "Bypass WAF protection and exploit SQL injection to: 1) Use advanced encoding techniques to evade detection, 2) Perform time-based blind SQL injection, 3) Extract database schema information, 4) Access multiple database tables, 5) Execute arbitrary SQL commands.",
            "vulnerabilities": ["sql_injection", "waf_bypass", "information_disclosure"],
            "techniques": ["time_based", "hex_encoding", "case_variation", "comment_bypass"],
            "learning_focus": "Advanced SQL injection techniques, WAF evasion methods, and sophisticated database exploitation."
        },
        "hard": {
            "name": "Complex SQL Injection with Advanced Protections",
            "description": "A highly secured application with multiple layers of protection including advanced WAF, input sanitization, and prepared statements with vulnerabilities. This challenge requires deep understanding of SQL injection techniques and creative exploitation methods.",
            "detailed_objective": "Overcome multiple security layers to: 1) Bypass advanced WAF rules using sophisticated techniques, 2) Exploit second-order SQL injection vulnerabilities, 3) Use out-of-band techniques for data exfiltration, 4) Chain multiple vulnerabilities together, 5) Achieve remote code execution through SQL injection.",
            "vulnerabilities": ["sql_injection", "advanced_waf_bypass", "second_order_injection", "rce"],
            "techniques": ["out_of_band", "second_order", "polyglot_payloads", "vulnerability_chaining"],
            "learning_focus": "Advanced exploitation techniques, vulnerability chaining, and real-world attack scenarios."
        }
    },
    "xss": {
        "easy": {
            "name": "Basic Cross-Site Scripting Challenge",
            "description": "A simple web application vulnerable to reflected XSS attacks. The application displays user input without proper sanitization, allowing you to inject and execute JavaScript code in the context of other users.",
            "detailed_objective": "Successfully exploit XSS vulnerabilities to: 1) Execute arbitrary JavaScript code, 2) Steal user session cookies, 3) Perform client-side attacks, 4) Demonstrate the impact of XSS on web security.",
            "vulnerabilities": ["reflected_xss", "session_hijacking"],
            "techniques": ["basic_script_injection", "cookie_theft", "alert_popup"],
            "learning_focus": "Understanding XSS fundamentals, JavaScript injection, and client-side security implications."
        },
        "medium": {
            "name": "Advanced XSS with CSP Bypass",
            "description": "A web application with Content Security Policy (CSP) implementation that attempts to prevent XSS attacks. However, the CSP is misconfigured, allowing for creative bypasses and advanced exploitation techniques.",
            "detailed_objective": "Bypass CSP restrictions and exploit XSS to: 1) Use allowed CSP directives to execute code, 2) Perform DOM-based XSS attacks, 3) Exploit JSONP endpoints for data exfiltration, 4) Chain XSS with other vulnerabilities.",
            "vulnerabilities": ["dom_xss", "csp_bypass", "jsonp_exploitation"],
            "techniques": ["csp_bypass", "dom_manipulation", "jsonp_abuse", "event_handler_injection"],
            "learning_focus": "CSP bypass techniques, DOM-based XSS, and advanced client-side exploitation."
        },
        "hard": {
            "name": "Complex XSS with Multiple Protections",
            "description": "A highly secured application with multiple XSS protection mechanisms including strict CSP, input validation, and output encoding. This challenge requires sophisticated techniques to successfully exploit XSS vulnerabilities.",
            "detailed_objective": "Overcome multiple protection layers to: 1) Bypass strict CSP using creative techniques, 2) Exploit stored XSS in complex applications, 3) Use advanced JavaScript techniques for exploitation, 4) Chain XSS with CSRF and other vulnerabilities.",
            "vulnerabilities": ["stored_xss", "strict_csp_bypass", "csrf_chaining"],
            "techniques": ["advanced_csp_bypass", "stored_injection", "csrf_exploitation", "complex_js_payloads"],
            "learning_focus": "Advanced XSS techniques, multi-layered bypass methods, and real-world exploitation scenarios."
        }
    },
    "command_injection": {
        "easy": {
            "name": "Basic Command Injection Challenge",
            "description": "A web application that executes system commands based on user input without proper validation. The application is vulnerable to command injection attacks, allowing you to execute arbitrary commands on the server.",
            "detailed_objective": "Successfully exploit command injection to: 1) Execute basic system commands, 2) Enumerate the server environment, 3) Access sensitive files, 4) Establish a reverse shell connection.",
            "vulnerabilities": ["command_injection", "information_disclosure"],
            "techniques": ["basic_command_execution", "file_enumeration", "reverse_shell"],
            "learning_focus": "Command injection fundamentals, system command execution, and server enumeration techniques."
        },
        "medium": {
            "name": "Advanced Command Injection with Filters",
            "description": "A web application with basic command injection filters that attempt to prevent exploitation. The filters can be bypassed using various techniques, requiring creative approaches to successfully exploit the vulnerability.",
            "detailed_objective": "Bypass command injection filters to: 1) Use encoding techniques to evade detection, 2) Exploit command chaining and operators, 3) Perform advanced system enumeration, 4) Establish persistent access.",
            "vulnerabilities": ["command_injection", "filter_bypass", "persistence"],
            "techniques": ["encoding_bypass", "command_chaining", "advanced_enumeration", "backdoor_creation"],
            "learning_focus": "Filter bypass techniques, command chaining, and advanced system exploitation."
        },
        "hard": {
            "name": "Complex Command Injection with Advanced Protections",
            "description": "A highly secured application with multiple command injection protection mechanisms including strict input validation, sandboxing, and monitoring. This challenge requires sophisticated techniques to successfully exploit command injection vulnerabilities.",
            "detailed_objective": "Overcome multiple protection layers to: 1) Bypass strict input validation using advanced techniques, 2) Exploit sandbox escape vulnerabilities, 3) Use out-of-band techniques for command execution, 4) Establish covert communication channels.",
            "vulnerabilities": ["command_injection", "sandbox_escape", "covert_channels"],
            "techniques": ["advanced_bypass", "sandbox_escape", "out_of_band", "covert_communication"],
            "learning_focus": "Advanced bypass techniques, sandbox escape methods, and sophisticated exploitation approaches."
        }
    }
}

# AI Learning Progress Tracking
class AILearningTracker:
    def __init__(self):
        self.user_progress = {}
        self.difficulty_multipliers = {
            "novice": 1.0,
            "intermediate": 1.5,
            "advanced": 2.0,
            "expert": 3.0
        }
    
    def get_user_level(self, user_id: str) -> str:
        """Get user's current learning level based on performance"""
        progress = self.user_progress.get(user_id, {
            "success_rate": 0.0,
            "completed_challenges": 0,
            "average_score": 0.0
        })
        
        if progress["success_rate"] < 0.3:
            return "novice"
        elif progress["success_rate"] < 0.6:
            return "intermediate"
        elif progress["success_rate"] < 0.8:
            return "advanced"
        else:
            return "expert"
    
    def update_progress(self, user_id: str, success: bool, score: float):
        """Update user's learning progress"""
        if user_id not in self.user_progress:
            self.user_progress[user_id] = {
                "success_rate": 0.0,
                "completed_challenges": 0,
                "average_score": 0.0,
                "total_attempts": 0
            }
        
        progress = self.user_progress[user_id]
        progress["total_attempts"] += 1
        progress["completed_challenges"] += 1 if success else 0
        progress["success_rate"] = progress["completed_challenges"] / progress["total_attempts"]
        progress["average_score"] = (progress["average_score"] * (progress["total_attempts"] - 1) + score) / progress["total_attempts"]

# Import enhanced scenario service
from app.services.enhanced_scenario_service import EnhancedScenarioService

# Mock services for standalone operation
class MockCustodyProtocolService:
    def __init__(self):
        self.ai_tracker = AILearningTracker()
        self.active_deployments = {}
        self.enhanced_scenario_service = EnhancedScenarioService()
    
    @staticmethod
    async def initialize():
        logger.info("Mock Custody Protocol Service initialized")
        return MockCustodyProtocolService()
    
    def _generate_live_target(self, difficulty: str, vulnerability_type: str) -> Dict[str, Any]:
        """Generate a live target with realistic vulnerabilities"""
        template = SCENARIO_TEMPLATES[vulnerability_type][difficulty]
        
        # Generate unique container ID
        container_id = f"live_target_{vulnerability_type}_{difficulty}_{random.randint(1000, 9999)}"
        
        # Generate realistic target URL
        target_url = f"http://localhost:{8080 + random.randint(0, 9)}"
        
        # Generate realistic credentials
        credentials = {
            "admin": f"admin:admin{random.randint(100, 999)}",
            "user": f"user:pass{random.randint(100, 999)}",
            "test": f"test:test{random.randint(100, 999)}"
        }
        
        # Generate specific hints based on difficulty
        hints = self._generate_hints(difficulty, vulnerability_type)
        
        return {
            "container_id": container_id,
            "container_name": f"live_{vulnerability_type}_{difficulty}_{container_id[-4:]}",
            "target_url": target_url,
            "port": int(target_url.split(":")[-1]),
            "template_name": f"{vulnerability_type}_{difficulty}",
            "difficulty": difficulty,
            "vulnerabilities": template["vulnerabilities"],
            "credentials": credentials,
            "hints": hints,
            "success_criteria": {
                "extract_credentials": True,
                "bypass_authentication": True,
                "access_admin_panel": True,
                "achieve_rce": difficulty in ["medium", "hard"],
                "bypass_protections": difficulty in ["medium", "hard"]
            },
            "provisioned_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=2)).isoformat(),
            "is_live": True,
            "real_vulnerabilities": True
        }
    
    def _generate_hints(self, difficulty: str, vulnerability_type: str) -> List[str]:
        """Generate contextual hints based on difficulty and vulnerability type"""
        base_hints = {
            "sql_injection": {
                "easy": [
                    "Try using ' OR 1=1 -- in the username field",
                    "Look for error messages that reveal database structure",
                    "Try UNION-based attacks to extract data",
                    "Check if the application uses simple string concatenation"
                ],
                "medium": [
                    "The WAF blocks common SQL injection patterns",
                    "Try using hex encoding to bypass filters",
                    "Use time-based techniques for blind SQL injection",
                    "Look for second-order injection points"
                ],
                "hard": [
                    "Multiple protection layers require sophisticated bypass techniques",
                    "Consider out-of-band data exfiltration methods",
                    "Chain multiple vulnerabilities together",
                    "Look for edge cases in the application logic"
                ]
            },
            "xss": {
                "easy": [
                    "Try injecting <script>alert('XSS')</script>",
                    "Look for reflected input in the page source",
                    "Check if user input is displayed without encoding",
                    "Try different event handlers like onmouseover"
                ],
                "medium": [
                    "The CSP blocks inline scripts but allows certain sources",
                    "Look for JSONP endpoints that can be exploited",
                    "Try DOM-based XSS techniques",
                    "Use allowed CSP directives to execute code"
                ],
                "hard": [
                    "Strict CSP requires creative bypass techniques",
                    "Look for stored XSS in complex applications",
                    "Chain XSS with CSRF vulnerabilities",
                    "Use advanced JavaScript techniques for exploitation"
                ]
            },
            "command_injection": {
                "easy": [
                    "Try basic commands like '; ls -la'",
                    "Look for command execution in input fields",
                    "Try different command separators: ; && ||",
                    "Check for ping or other system commands"
                ],
                "medium": [
                    "Filters block common command injection patterns",
                    "Try encoding techniques to bypass filters",
                    "Use command chaining operators",
                    "Look for alternative command execution methods"
                ],
                "hard": [
                    "Multiple protection layers require advanced bypass techniques",
                    "Consider sandbox escape vulnerabilities",
                    "Use out-of-band techniques for command execution",
                    "Establish covert communication channels"
                ]
            }
        }
        
        return base_hints.get(vulnerability_type, {}).get(difficulty, [])
    
    async def generate_training_scenario(self, sandbox_level: int, auto_difficulty: bool = True, user_id: str = "default") -> Dict[str, Any]:
        """Generate a training scenario based on sandbox level and auto difficulty"""
        logger.info(f"Generating scenario for sandbox level {sandbox_level}, auto_difficulty: {auto_difficulty}")
        
        # Get user progress for adaptive difficulty
        user_progress = self.ai_tracker.user_progress.get(user_id, {})
        current_level = self.ai_tracker.get_user_level(user_id)
        success_rate = user_progress.get("success_rate", 0.0)
        
        # Use enhanced scenario service for internet sources and LLM
        try:
            enhanced_scenario = await self.enhanced_scenario_service.get_scenario(
                user_id=user_id,
                current_level=current_level,
                success_rate=success_rate,
                vulnerability_type="web"  # Default to web vulnerabilities
            )
            
            if enhanced_scenario:
                # Convert enhanced scenario to our format
                scenario = {
                    "scenario": f"Attack the vulnerable web application at {enhanced_scenario.get('live_environment', {}).get('target_url', 'TARGET_URL')}. Focus on exploiting: {', '.join(enhanced_scenario.get('vulnerabilities', []))}. {enhanced_scenario.get('description', 'Complete the challenge.')}",
                    "real_target": True,
                    "target_info": {
                        "container_id": enhanced_scenario.get('live_environment', {}).get('container_id', 'live_container'),
                        "container_name": enhanced_scenario.get('name', 'Advanced Challenge'),
                        "target_url": enhanced_scenario.get('live_environment', {}).get('target_url', 'http://localhost:8080'),
                        "port": enhanced_scenario.get('live_environment', {}).get('port', 8080),
                        "template_name": enhanced_scenario.get('source', 'Enhanced'),
                        "difficulty": enhanced_scenario.get('adaptive_difficulty', 'medium'),
                        "vulnerabilities": enhanced_scenario.get('vulnerabilities', []),
                        "credentials": {
                            "admin": "admin:admin123",
                            "user": "user:password123",
                            "test": "test:test123"
                        },
                        "hints": enhanced_scenario.get('hints', []),
                        "success_criteria": {
                            "extract_credentials": True,
                            "bypass_authentication": True,
                            "access_admin_panel": True,
                            "achieve_rce": enhanced_scenario.get('adaptive_difficulty') in ["medium", "hard"],
                            "bypass_protections": enhanced_scenario.get('adaptive_difficulty') in ["medium", "hard"]
                        },
                        "provisioned_at": datetime.now().isoformat(),
                        "expires_at": (datetime.now() + timedelta(hours=2)).isoformat(),
                        "is_live": True,
                        "real_vulnerabilities": True
                    },
                    "generation_method": "enhanced_ai_learning",
                    "ai_analysis": {
                        "learning_level": current_level,
                        "strengths": [],
                        "weaknesses": enhanced_scenario.get('vulnerabilities', []),
                        "success_rate": success_rate,
                        "complexity_multiplier": self.ai_tracker.difficulty_multipliers.get(current_level, 1.0),
                        "recommended_techniques": enhanced_scenario.get('techniques', []),
                        "scenario_source": enhanced_scenario.get('source', 'Unknown'),
                        "ai_generated": enhanced_scenario.get('ai_generated', False)
                    },
                    "adaptive_features": {
                        "randomization": True,
                        "code_obfuscation": enhanced_scenario.get('adaptive_difficulty') in ["medium", "hard"],
                        "credential_rotation": True,
                        "endpoint_obfuscation": enhanced_scenario.get('adaptive_difficulty') in ["medium", "hard"],
                        "anti_debugging": enhanced_scenario.get('adaptive_difficulty') == "hard",
                        "polymorphic_code": enhanced_scenario.get('adaptive_difficulty') == "hard"
                    },
                    "learning_objectives": enhanced_scenario.get('learning_objectives', []),
                    "complexity_level": enhanced_scenario.get('adaptive_difficulty', 'medium'),
                    "challenge_focus": {
                        "primary_focus": enhanced_scenario.get('vulnerabilities', [])[0] if enhanced_scenario.get('vulnerabilities') else "web",
                        "secondary_focus": enhanced_scenario.get('vulnerabilities', [])[1] if len(enhanced_scenario.get('vulnerabilities', [])) > 1 else None,
                        "strength_challenge": None,
                        "complexity_boost": enhanced_scenario.get('adaptive_difficulty') in ["hard", "expert"]
                    },
                    "objectives": enhanced_scenario.get('description', 'Complete the challenge successfully.'),
                    "system_details": f"Target URL: {enhanced_scenario.get('live_environment', {}).get('target_url', 'http://localhost:8080')}, Template: {enhanced_scenario.get('source', 'Enhanced')}, Difficulty: {enhanced_scenario.get('adaptive_difficulty', 'medium')}, Live Environment: {enhanced_scenario.get('live_environment', {}).get('is_live', True)}",
                    "auto_difficulty": auto_difficulty,
                    "determined_difficulty": str(sandbox_level),
                    "performance_analysis": {
                        "recent_tests_count": user_progress.get("total_attempts", 0),
                        "success_rate": success_rate,
                        "average_score": user_progress.get("average_score", 0.0),
                        "performance_trend": "improving" if success_rate > 0.5 else "needs_improvement"
                    },
                    "detailed_description": enhanced_scenario.get('description', 'Advanced challenge with real vulnerabilities.'),
                    "vulnerability_type": enhanced_scenario.get('vulnerabilities', [])[0] if enhanced_scenario.get('vulnerabilities') else "web",
                    "techniques_required": enhanced_scenario.get('techniques', []),
                    "learning_focus": f"Master {', '.join(enhanced_scenario.get('vulnerabilities', []))} techniques",
                    "scenario_source": enhanced_scenario.get('source', 'Enhanced'),
                    "ai_generated": enhanced_scenario.get('ai_generated', False)
                }
                
                return scenario
        
        except Exception as e:
            logger.warning(f"Enhanced scenario generation failed: {str(e)}, falling back to template")
        
        # Fallback to template-based generation
        return await self._generate_template_scenario(sandbox_level, auto_difficulty, user_id)
    
    async def deploy_training_sandbox(self, scenario: Dict[str, Any], weapon_id: Optional[str] = None, user_id: str = "default") -> Dict[str, Any]:
        """Deploy a training sandbox with the given scenario"""
        logger.info(f"Deploying training sandbox with weapon_id: {weapon_id}")
        
        deployment_id = f"deployment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Simulate deployment process
        target_info = scenario.get("target_info", {})
        
        # Generate detailed deployment information
        deployment_info = {
            "deployment_id": deployment_id,
            "status": "deployed",
            "target_info": target_info,
            "weapon_used": weapon_id,
            "deployed_at": datetime.now().isoformat(),
            "expires_at": target_info.get("expires_at", ""),
            "access_url": target_info.get("target_url", "http://localhost:8080"),
            "credentials": target_info.get("credentials", {}),
            "hints": target_info.get("hints", []),
            "success_criteria": target_info.get("success_criteria", {}),
            "deployment_details": {
                "container_status": "running",
                "vulnerabilities_active": True,
                "monitoring_enabled": True,
                "backup_created": True,
                "isolation_level": "high",
                "network_access": "restricted"
            },
            "ai_analysis": {
                "difficulty_assessment": scenario.get("ai_analysis", {}),
                "recommended_approach": scenario.get("learning_objectives", []),
                "expected_completion_time": "30-60 minutes",
                "success_probability": "high" if scenario.get("ai_analysis", {}).get("learning_level") in ["intermediate", "advanced"] else "medium"
            },
            "live_environment": {
                "is_live": True,
                "real_vulnerabilities": True,
                "dynamic_content": True,
                "interactive_elements": True,
                "real_time_feedback": True
            }
        }
        
        # Store deployment for tracking
        self.active_deployments[deployment_id] = {
            "scenario": scenario,
            "user_id": user_id,
            "deployment_time": datetime.now(),
            "status": "active"
        }
        
        return deployment_info
    
    async def _generate_template_scenario(self, sandbox_level: int, auto_difficulty: bool, user_id: str) -> Dict[str, Any]:
        """Fallback template-based scenario generation"""
        # Determine difficulty based on user progress and sandbox level
        if auto_difficulty:
            user_level = self.ai_tracker.get_user_level(user_id)
            base_difficulty = "easy" if sandbox_level <= 2 else "medium" if sandbox_level <= 4 else "hard"
            
            # Adjust difficulty based on user performance
            if user_level == "expert" and base_difficulty == "easy":
                difficulty = "medium"
            elif user_level == "novice" and base_difficulty == "hard":
                difficulty = "medium"
            else:
                difficulty = base_difficulty
        else:
            difficulty = "easy" if sandbox_level <= 2 else "medium" if sandbox_level <= 4 else "hard"
        
        # Select vulnerability type based on difficulty and learning progression
        vulnerability_types = ["sql_injection", "xss", "command_injection"]
        vulnerability_type = vulnerability_types[sandbox_level % len(vulnerability_types)]
        
        # Get template for the selected vulnerability and difficulty
        template = SCENARIO_TEMPLATES[vulnerability_type][difficulty]
        
        # Generate live target
        target_info = self._generate_live_target(difficulty, vulnerability_type)
        
        # Calculate AI-driven complexity multiplier
        user_level = self.ai_tracker.get_user_level(user_id)
        complexity_multiplier = self.ai_tracker.difficulty_multipliers.get(user_level, 1.0)
        
        scenario = {
            "scenario": f"Attack the vulnerable web application at {target_info['target_url']}. Focus on exploiting: {', '.join(template['vulnerabilities'])}. {template['detailed_objective']}",
            "real_target": True,
            "target_info": target_info,
            "generation_method": "template_fallback",
            "ai_analysis": {
                "learning_level": user_level,
                "strengths": [],
                "weaknesses": template["vulnerabilities"],
                "success_rate": self.ai_tracker.user_progress.get(user_id, {}).get("success_rate", 0.0),
                "complexity_multiplier": complexity_multiplier,
                "recommended_techniques": template["techniques"]
            },
            "adaptive_features": {
                "randomization": True,
                "code_obfuscation": difficulty in ["medium", "hard"],
                "credential_rotation": True,
                "endpoint_obfuscation": difficulty in ["medium", "hard"],
                "anti_debugging": difficulty == "hard",
                "polymorphic_code": difficulty == "hard"
            },
            "learning_objectives": [
                f"Master {vulnerability_type} techniques",
                f"Understand {difficulty} level exploitation",
                f"Practice {', '.join(template['techniques'])}",
                template["learning_focus"]
            ],
            "complexity_level": difficulty,
            "challenge_focus": {
                "primary_focus": vulnerability_type,
                "secondary_focus": template["vulnerabilities"][1] if len(template["vulnerabilities"]) > 1 else None,
                "strength_challenge": None,
                "complexity_boost": complexity_multiplier > 1.0
            },
            "objectives": template["detailed_objective"],
            "system_details": f"Target URL: {target_info['target_url']}, Template: {target_info['template_name']}, Difficulty: {difficulty}, Credentials: {list(target_info['credentials'].keys())}, Port: {target_info['port']}, Live Environment: {target_info['is_live']}",
            "auto_difficulty": auto_difficulty,
            "determined_difficulty": str(sandbox_level),
            "performance_analysis": {
                "recent_tests_count": self.ai_tracker.user_progress.get(user_id, {}).get("total_attempts", 0),
                "success_rate": self.ai_tracker.user_progress.get(user_id, {}).get("success_rate", 0.0),
                "average_score": self.ai_tracker.user_progress.get(user_id, {}).get("average_score", 0.0),
                "performance_trend": "improving" if self.ai_tracker.user_progress.get(user_id, {}).get("success_rate", 0.0) > 0.5 else "needs_improvement"
            },
            "detailed_description": template["description"],
            "vulnerability_type": vulnerability_type,
            "techniques_required": template["techniques"],
            "learning_focus": template["learning_focus"]
        }
        
        return scenario
    
    async def get_deployment_result(self, deployment_id: str, success: bool, score: float, user_id: str = "default") -> Dict[str, Any]:
        """Get detailed deployment result with AI analysis"""
        deployment = self.active_deployments.get(deployment_id, {})
        scenario = deployment.get("scenario", {})
        
        # Update user progress
        self.ai_tracker.update_progress(user_id, success, score)
        
        # Generate detailed result analysis
        result_analysis = {
            "deployment_id": deployment_id,
            "success": success,
            "score": score,
            "completion_time": datetime.now().isoformat(),
            "detailed_analysis": {
                "vulnerabilities_exploited": scenario.get("target_info", {}).get("vulnerabilities", []),
                "techniques_used": scenario.get("techniques_required", []),
                "learning_objectives_achieved": scenario.get("learning_objectives", []),
                "difficulty_level": scenario.get("complexity_level", "unknown"),
                "ai_assessment": scenario.get("ai_analysis", {})
            },
            "success_description": self._generate_success_description(success, scenario) if success else self._generate_failure_description(scenario),
            "next_recommendations": self._generate_next_recommendations(user_id, success, scenario),
            "performance_metrics": {
                "current_level": self.ai_tracker.get_user_level(user_id),
                "progress_improvement": self.ai_tracker.user_progress.get(user_id, {}).get("success_rate", 0.0),
                "recommended_next_difficulty": self._get_next_difficulty(user_id, success)
            }
        }
        
        return result_analysis
    
    def _generate_success_description(self, success: bool, scenario: Dict[str, Any]) -> str:
        """Generate detailed success description"""
        if not success:
            return "Challenge not completed successfully."
        
        vulnerability_type = scenario.get("vulnerability_type", "unknown")
        difficulty = scenario.get("complexity_level", "unknown")
        techniques = scenario.get("techniques_required", [])
        
        descriptions = {
            "sql_injection": {
                "easy": f"Excellent work! You successfully exploited SQL injection vulnerabilities using {', '.join(techniques)}. You bypassed authentication, extracted sensitive data, and demonstrated a solid understanding of basic SQL injection principles. The techniques you used show proper understanding of database enumeration and exploitation methods.",
                "medium": f"Outstanding performance! You successfully bypassed WAF protection and exploited advanced SQL injection vulnerabilities. Your use of {', '.join(techniques)} demonstrates sophisticated understanding of filter evasion and advanced exploitation techniques. You've shown mastery of complex SQL injection scenarios.",
                "hard": f"Exceptional achievement! You successfully overcame multiple protection layers and exploited highly secured SQL injection vulnerabilities. Your use of {', '.join(techniques)} shows expert-level understanding of advanced exploitation methods, vulnerability chaining, and sophisticated bypass techniques."
            },
            "xss": {
                "easy": f"Great job! You successfully exploited XSS vulnerabilities and demonstrated understanding of client-side security issues. Your use of {', '.join(techniques)} shows proper grasp of JavaScript injection and client-side exploitation techniques.",
                "medium": f"Excellent work! You successfully bypassed CSP restrictions and exploited advanced XSS vulnerabilities. Your use of {', '.join(techniques)} demonstrates sophisticated understanding of CSP bypass methods and advanced client-side exploitation.",
                "hard": f"Outstanding achievement! You successfully overcame strict CSP and exploited highly secured XSS vulnerabilities. Your use of {', '.join(techniques)} shows expert-level understanding of advanced XSS techniques and multi-layered bypass methods."
            },
            "command_injection": {
                "easy": f"Well done! You successfully exploited command injection vulnerabilities and demonstrated understanding of system command execution. Your use of {', '.join(techniques)} shows proper grasp of server-side exploitation techniques.",
                "medium": f"Excellent work! You successfully bypassed command injection filters and exploited advanced vulnerabilities. Your use of {', '.join(techniques)} demonstrates sophisticated understanding of filter evasion and advanced system exploitation.",
                "hard": f"Outstanding achievement! You successfully overcame multiple protection layers and exploited highly secured command injection vulnerabilities. Your use of {', '.join(techniques)} shows expert-level understanding of advanced bypass techniques and sophisticated exploitation methods."
            }
        }
        
        return descriptions.get(vulnerability_type, {}).get(difficulty, "Challenge completed successfully!")
    
    def _generate_failure_description(self, scenario: Dict[str, Any]) -> str:
        """Generate detailed failure description with guidance"""
        vulnerability_type = scenario.get("vulnerability_type", "unknown")
        difficulty = scenario.get("complexity_level", "unknown")
        hints = scenario.get("target_info", {}).get("hints", [])
        
        base_description = f"The {difficulty} level {vulnerability_type} challenge was not completed successfully. "
        
        guidance = {
            "sql_injection": "Focus on understanding SQL injection fundamentals, try different payloads, and pay attention to error messages that might reveal database structure.",
            "xss": "Focus on understanding XSS fundamentals, try different injection points, and experiment with various JavaScript payloads.",
            "command_injection": "Focus on understanding command injection fundamentals, try different command separators, and experiment with various system commands."
        }
        
        return base_description + guidance.get(vulnerability_type, "Review the challenge objectives and try different approaches.")
    
    def _generate_next_recommendations(self, user_id: str, success: bool, scenario: Dict[str, Any]) -> List[str]:
        """Generate recommendations for next steps"""
        current_level = self.ai_tracker.get_user_level(user_id)
        difficulty = scenario.get("complexity_level", "easy")
        
        if success:
            if difficulty == "easy":
                return [
                    "Try medium difficulty challenges to advance your skills",
                    "Practice with different vulnerability types",
                    "Focus on advanced exploitation techniques"
                ]
            elif difficulty == "medium":
                return [
                    "Attempt hard difficulty challenges to test your expertise",
                    "Practice vulnerability chaining techniques",
                    "Focus on bypassing advanced protection mechanisms"
                ]
            else:
                return [
                    "You're ready for expert-level challenges",
                    "Practice with real-world scenarios",
                    "Focus on advanced exploitation methodologies"
                ]
        else:
            return [
                "Review the challenge objectives and hints",
                "Practice with easier challenges to build fundamentals",
                "Focus on understanding the vulnerability type better"
            ]
    
    def _get_next_difficulty(self, user_id: str, success: bool) -> str:
        """Determine recommended next difficulty level"""
        current_level = self.ai_tracker.get_user_level(user_id)
        
        if success:
            if current_level == "novice":
                return "intermediate"
            elif current_level == "intermediate":
                return "advanced"
            else:
                return "expert"
        else:
            if current_level == "expert":
                return "advanced"
            elif current_level == "advanced":
                return "intermediate"
            else:
                return "novice"

class MockAgentMetricsService:
    @staticmethod
    async def initialize():
        logger.info("Mock Agent Metrics Service initialized")
        return MockAgentMetricsService()

# Global service instances
custody_service = None
agent_metrics_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    global custody_service, agent_metrics_service
    
    # Startup
    logger.info("🚀 Starting Training Ground Server on port 8002")
    
    # Initialize mock services
    custody_service = await MockCustodyProtocolService.initialize()
    agent_metrics_service = await MockAgentMetricsService.initialize()
    
    logger.info("✅ Training Ground Server initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Training Ground Server")

# Create FastAPI app
app = FastAPI(
    title="Training Ground Server",
    description="Training Ground System with automatic difficulty selection and weapon management",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Training Ground Server",
        "version": "2.0.0",
        "port": 8002,
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        return {
            "status": "healthy",
            "services": {
                "custody_protocol": "initialized",
                "agent_metrics": "initialized",
                "database": "connected"
            },
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.post("/custody/training-ground/scenario", response_model=ScenarioResponse)
async def generate_scenario(request: ScenarioRequest):
    """Generate a training scenario based on sandbox level and auto difficulty"""
    try:
        logger.info(f"Generating scenario for sandbox level {request.sandbox_level}")
        
        scenario = await custody_service.generate_training_scenario(
            sandbox_level=request.sandbox_level,
            auto_difficulty=request.auto_difficulty
        )
        
        return ScenarioResponse(
            status="success",
            scenario=scenario,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error generating scenario: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate scenario: {str(e)}")

@app.post("/custody/training-ground/deploy", response_model=DeployResponse)
async def deploy_sandbox(request: DeployRequest):
    """Deploy a training sandbox with the given scenario"""
    try:
        logger.info("Deploying training sandbox")
        
        deployment_info = await custody_service.deploy_training_sandbox(
            scenario=request.scenario,
            weapon_id=request.weapon_id
        )
        
        return DeployResponse(
            status="success",
            deployment_id=deployment_info["deployment_id"],
            target_info=deployment_info,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error deploying sandbox: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to deploy sandbox: {str(e)}")

@app.post("/custody/training-ground/result")
async def submit_result(deployment_id: str, success: bool, score: float, user_id: str = "default"):
    """Submit deployment result and get detailed analysis"""
    try:
        logger.info(f"Submitting result for deployment {deployment_id}")
        
        result = await custody_service.get_deployment_result(
            deployment_id=deployment_id,
            success=success,
            score=score,
            user_id=user_id
        )
        
        return {
            "status": "success",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error submitting result: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to submit result: {str(e)}")

@app.get("/custody/training-ground/status")
async def get_training_ground_status():
    """Get the current status of the training ground system"""
    return {
        "status": "operational",
        "server": "training_ground_server",
        "port": 8002,
        "services": {
            "custody_protocol": "running",
            "agent_metrics": "running"
        },
        "features": [
            "automatic_difficulty_selection",
            "performance_based_scenarios",
            "weapon_system",
            "real_time_attack_tracking",
            "ai_driven_learning",
            "live_vulnerable_environments",
            "detailed_success_analysis",
            "adaptive_difficulty_progression"
        ],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/health")
async def api_health_check():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "api_version": "2.0.0",
        "endpoints": [
            "/custody/training-ground/scenario",
            "/custody/training-ground/deploy",
            "/custody/training-ground/result",
            "/custody/training-ground/status"
        ]
    }

@app.get("/debug")
async def debug_info():
    """Debug information endpoint"""
    try:
        return {
            "server_info": {
                "port": 8002,
                "host": "0.0.0.0",
                "environment": os.getenv("ENVIRONMENT", "development")
            },
            "services": {
                "custody_protocol": "available",
                "agent_metrics": "available"
            },
            "features": [
                "automatic_difficulty_selection",
                "performance_based_scenarios",
                "weapon_system",
                "real_time_attack_tracking",
                "ai_driven_learning",
                "live_vulnerable_environments"
            ]
        }
    except Exception as e:
        logger.error(f"Debug info failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Debug info failed: {str(e)}")

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "training_ground_server:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    ) 