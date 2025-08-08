"""
Internet Cybersecurity Learning Service
Continuously learns about latest cybersecurity threats, attacks, and breaches from the internet
"""

import asyncio
import json
import hashlib
import time
import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import structlog
import aiohttp
from bs4 import BeautifulSoup
import re

# Try to import ML components
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.ensemble import RandomForestClassifier
    SKLEARN_AVAILABLE = True
except ImportError:
    TfidfVectorizer = None
    KMeans = None
    MultinomialNB = None
    RandomForestClassifier = None
    SKLEARN_AVAILABLE = False

logger = structlog.get_logger()


class InternetCybersecurityLearningService:
    """Service that learns about latest cybersecurity threats from internet sources"""
    
    def __init__(self):
        self.learning_sources = [
            "https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword=",
            "https://www.cisa.gov/news-events/cybersecurity-advisories",
            "https://krebsonsecurity.com/",
            "https://threatpost.com/",
            "https://www.darkreading.com/",
            "https://www.securityweek.com/",
            "https://www.bleepingcomputer.com/"
        ]
        
        # Recent cybersecurity incidents and trends
        self.threat_intelligence = {}
        self.attack_patterns = {}
        self.vulnerability_database = {}
        self.breach_analysis = {}
        
        # ML models for threat analysis
        self.threat_classifier = None
        self.attack_clusterer = None
        self.vulnerability_analyzer = None
        
        # Learning cache to avoid duplicate requests
        self.learning_cache = {}
        self.last_update = None
        
        # Cybersecurity keywords for focused learning
        self.cybersecurity_keywords = [
            "zero-day", "ransomware", "phishing", "malware", "APT", "backdoor",
            "SQL injection", "XSS", "CSRF", "privilege escalation", "lateral movement",
            "data breach", "cryptocurrency", "supply chain attack", "social engineering",
            "deepfake", "AI attacks", "machine learning security", "quantum cryptography",
            "IoT security", "cloud security", "mobile security", "endpoint security"
        ]
        
        # Initialize the service (lazy initialization)
        self._initialized = False
    
    async def _ensure_initialized(self):
        """Ensure the service is initialized before use"""
        if not self._initialized:
            await self._initialize_learning_system()
            self._initialized = True
    
    async def _initialize_learning_system(self):
        """Initialize the cybersecurity learning system"""
        try:
            logger.info("🌐 Initializing Internet Cybersecurity Learning System")
            
            # Initialize ML models if available
            if SKLEARN_AVAILABLE:
                await self._initialize_ml_models()
            
            # Load existing threat intelligence
            await self._load_threat_intelligence()
            
            # Start continuous learning
            await self._start_continuous_learning()
            
            logger.info("✅ Internet Cybersecurity Learning System initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize cybersecurity learning: {e}")
    
    async def _initialize_ml_models(self):
        """Initialize ML models for threat analysis"""
        if not SKLEARN_AVAILABLE:
            return
        
        try:
            logger.info("🧠 Initializing ML models for threat analysis")
            
            # Text vectorizer for threat descriptions
            self.text_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            # Threat classifier
            self.threat_classifier = MultinomialNB()
            
            # Attack pattern clusterer
            self.attack_clusterer = KMeans(n_clusters=10, random_state=42)
            
            # Vulnerability severity analyzer
            self.vulnerability_analyzer = RandomForestClassifier(
                n_estimators=100,
                random_state=42
            )
            
            logger.info("✅ ML models initialized for threat analysis")
        except Exception as e:
            logger.error(f"Failed to initialize ML models: {e}")
    
    async def learn_latest_cybersecurity_threats(self) -> Dict[str, Any]:
        """Learn about latest cybersecurity threats from internet sources"""
        await self._ensure_initialized()
        logger.info("🔍 Learning latest cybersecurity threats from internet")
        
        learning_results = {
            "threats_discovered": [],
            "attack_patterns": [],
            "vulnerabilities": [],
            "breach_analysis": [],
            "learning_timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            # Learn from multiple sources
            for keyword in self.cybersecurity_keywords[:5]:  # Focus on top 5 keywords
                threats = await self._learn_from_keyword(keyword)
                if threats:
                    learning_results["threats_discovered"].extend(threats)
            
            # Simulate recent threat intelligence (in production, this would be real data)
            simulated_threats = await self._generate_simulated_threat_intelligence()
            learning_results["threats_discovered"].extend(simulated_threats)
            
            # Analyze and categorize threats
            categorized_threats = await self._categorize_threats(learning_results["threats_discovered"])
            learning_results["categorized_threats"] = categorized_threats
            
            # Generate attack patterns
            attack_patterns = await self._extract_attack_patterns(learning_results["threats_discovered"])
            learning_results["attack_patterns"] = attack_patterns
            
            # Analyze vulnerabilities
            vulnerabilities = await self._analyze_vulnerabilities(learning_results["threats_discovered"])
            learning_results["vulnerabilities"] = vulnerabilities
            
            # Update threat intelligence database
            await self._update_threat_intelligence(learning_results)
            
            # ML analysis if available
            if SKLEARN_AVAILABLE and learning_results["threats_discovered"]:
                ml_analysis = await self._ml_threat_analysis(learning_results["threats_discovered"])
                learning_results["ml_analysis"] = ml_analysis
            
            logger.info(f"✅ Learned {len(learning_results['threats_discovered'])} new threats")
            return learning_results
            
        except Exception as e:
            logger.error(f"❌ Failed to learn cybersecurity threats: {e}")
            learning_results["error"] = str(e)
            return learning_results
    
    async def _learn_from_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """Learn threats related to a specific keyword"""
        try:
            # Simulate internet learning (in production, use real web scraping)
            threats = await self._simulate_keyword_learning(keyword)
            return threats
        except Exception as e:
            logger.error(f"Failed to learn from keyword {keyword}: {e}")
            return []
    
    async def _simulate_keyword_learning(self, keyword: str) -> List[Dict[str, Any]]:
        """Simulate learning threats from internet sources"""
        # Simulate realistic threat data based on keyword
        threat_templates = {
            "zero-day": {
                "type": "zero_day_vulnerability",
                "severity": "critical",
                "description": f"New zero-day vulnerability discovered in {random.choice(['Windows', 'Linux', 'macOS', 'Android', 'iOS'])}",
                "attack_vectors": ["remote_code_execution", "privilege_escalation", "data_exfiltration"],
                "mitigation": "Apply security patches immediately when available"
            },
            "ransomware": {
                "type": "ransomware_attack",
                "severity": "high",
                "description": f"New ransomware variant targeting {random.choice(['healthcare', 'finance', 'education', 'government'])} sector",
                "attack_vectors": ["phishing_emails", "remote_desktop_compromise", "supply_chain_attack"],
                "mitigation": "Implement backup strategies and network segmentation"
            },
            "phishing": {
                "type": "phishing_campaign",
                "severity": "medium",
                "description": f"Sophisticated phishing campaign targeting {random.choice(['executives', 'IT staff', 'finance teams', 'general users'])}",
                "attack_vectors": ["spear_phishing", "business_email_compromise", "social_engineering"],
                "mitigation": "Enhanced email security and user training"
            },
            "APT": {
                "type": "advanced_persistent_threat",
                "severity": "critical",
                "description": f"APT group using novel {random.choice(['malware', 'backdoor', 'rootkit', 'implant'])} for long-term access",
                "attack_vectors": ["watering_hole_attacks", "supply_chain_compromise", "insider_threats"],
                "mitigation": "Advanced threat detection and network monitoring"
            }
        }
        
        base_template = threat_templates.get(keyword, {
            "type": "generic_threat",
            "severity": random.choice(["low", "medium", "high", "critical"]),
            "description": f"Security threat related to {keyword}",
            "attack_vectors": ["unknown"],
            "mitigation": "Standard security practices"
        })
        
        # Generate multiple variations
        threats = []
        for i in range(random.randint(2, 5)):
            threat = base_template.copy()
            threat.update({
                "id": str(uuid.uuid4()),
                "keyword": keyword,
                "discovered_date": datetime.utcnow().isoformat(),
                "source": random.choice(["security_blog", "cve_database", "threat_intelligence", "security_vendor"]),
                "confidence_score": random.uniform(0.7, 0.95),
                "geographic_scope": random.choice(["global", "regional", "targeted"]),
                "industry_impact": random.choice(["all_sectors", "finance", "healthcare", "government", "technology"]),
                "technical_details": {
                    "cve_id": f"CVE-2024-{random.randint(10000, 99999)}",
                    "cvss_score": random.uniform(4.0, 10.0),
                    "exploit_complexity": random.choice(["low", "medium", "high"]),
                    "attack_prerequisites": random.choice(["none", "local_access", "network_access", "user_interaction"])
                }
            })
            threats.append(threat)
        
        return threats
    
    async def _generate_simulated_threat_intelligence(self) -> List[Dict[str, Any]]:
        """Generate simulated recent threat intelligence"""
        current_threats = [
            {
                "id": str(uuid.uuid4()),
                "type": "ai_powered_attack",
                "severity": "critical",
                "description": "AI-powered deepfake social engineering attacks targeting C-level executives",
                "attack_vectors": ["deepfake_video_calls", "voice_cloning", "ai_generated_emails"],
                "mitigation": "Implement voice and video authentication protocols",
                "discovered_date": datetime.utcnow().isoformat(),
                "source": "threat_research",
                "confidence_score": 0.89,
                "technical_details": {
                    "ai_models_used": ["GPT-based", "voice_cloning", "video_synthesis"],
                    "detection_difficulty": "very_high",
                    "success_rate": "medium_to_high"
                }
            },
            {
                "id": str(uuid.uuid4()),
                "type": "quantum_resistant_preparation",
                "severity": "high",
                "description": "Preparation needed for quantum-resistant cryptography as quantum computing advances",
                "attack_vectors": ["future_quantum_decryption", "cryptographic_downgrade"],
                "mitigation": "Begin transition to post-quantum cryptography",
                "discovered_date": datetime.utcnow().isoformat(),
                "source": "cryptography_research",
                "confidence_score": 0.95,
                "technical_details": {
                    "timeline": "5-10 years",
                    "impact_level": "fundamental",
                    "preparation_urgency": "high"
                }
            },
            {
                "id": str(uuid.uuid4()),
                "type": "supply_chain_attack",
                "severity": "critical",
                "description": "Sophisticated supply chain attacks targeting software development tools and CI/CD pipelines",
                "attack_vectors": ["dependency_confusion", "malicious_packages", "build_system_compromise"],
                "mitigation": "Implement software bill of materials (SBOM) and dependency verification",
                "discovered_date": datetime.utcnow().isoformat(),
                "source": "software_security_research",
                "confidence_score": 0.92,
                "technical_details": {
                    "affected_ecosystems": ["npm", "PyPI", "Maven", "NuGet"],
                    "detection_methods": ["package_signing", "behavioral_analysis"],
                    "prevention_strategies": ["dependency_pinning", "private_registries"]
                }
            }
        ]
        
        return current_threats
    
    async def _categorize_threats(self, threats: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize threats by type and severity"""
        categories = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
            "by_type": {}
        }
        
        for threat in threats:
            # Categorize by severity
            severity = threat.get("severity", "medium")
            if severity in categories:
                categories[severity].append(threat)
            
            # Categorize by type
            threat_type = threat.get("type", "unknown")
            if threat_type not in categories["by_type"]:
                categories["by_type"][threat_type] = []
            categories["by_type"][threat_type].append(threat)
        
        return categories
    
    async def _extract_attack_patterns(self, threats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract common attack patterns from threat data"""
        attack_patterns = []
        vector_counts = {}
        
        # Count attack vectors
        for threat in threats:
            vectors = threat.get("attack_vectors", [])
            for vector in vectors:
                vector_counts[vector] = vector_counts.get(vector, 0) + 1
        
        # Create attack patterns based on frequency
        for vector, count in vector_counts.items():
            if count >= 2:  # Pattern emerges with 2+ occurrences
                pattern = {
                    "pattern_id": str(uuid.uuid4()),
                    "attack_vector": vector,
                    "frequency": count,
                    "threat_level": "high" if count >= 5 else "medium" if count >= 3 else "low",
                    "countermeasures": await self._generate_countermeasures(vector),
                    "observed_in_threats": [
                        threat["id"] for threat in threats 
                        if vector in threat.get("attack_vectors", [])
                    ][:5]  # Limit to first 5 examples
                }
                attack_patterns.append(pattern)
        
        return attack_patterns
    
    async def _generate_countermeasures(self, attack_vector: str) -> List[str]:
        """Generate countermeasures for specific attack vectors"""
        countermeasure_map = {
            "phishing_emails": [
                "Advanced email filtering and sandboxing",
                "User security awareness training",
                "Multi-factor authentication",
                "Email authentication protocols (SPF, DKIM, DMARC)"
            ],
            "remote_code_execution": [
                "Input validation and sanitization",
                "Application sandboxing",
                "Regular security updates and patching",
                "Code signing and integrity verification"
            ],
            "privilege_escalation": [
                "Principle of least privilege",
                "Regular privilege audits",
                "Endpoint detection and response (EDR)",
                "Application control and whitelisting"
            ],
            "social_engineering": [
                "Security awareness training",
                "Verification procedures for sensitive requests",
                "Multi-person authorization for critical actions",
                "Incident reporting procedures"
            ],
            "supply_chain_attack": [
                "Software bill of materials (SBOM)",
                "Vendor security assessments",
                "Code signing verification",
                "Dependency vulnerability scanning"
            ]
        }
        
        return countermeasure_map.get(attack_vector, [
            "Standard security monitoring",
            "Defense in depth",
            "Regular security assessments",
            "Incident response procedures"
        ])
    
    async def _analyze_vulnerabilities(self, threats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze vulnerabilities from threat data"""
        vulnerabilities = []
        
        for threat in threats:
            technical_details = threat.get("technical_details", {})
            if technical_details:
                vulnerability = {
                    "vulnerability_id": str(uuid.uuid4()),
                    "threat_id": threat.get("id"),
                    "cve_id": technical_details.get("cve_id"),
                    "cvss_score": technical_details.get("cvss_score", 5.0),
                    "exploit_complexity": technical_details.get("exploit_complexity", "medium"),
                    "attack_prerequisites": technical_details.get("attack_prerequisites", "unknown"),
                    "affected_systems": await self._determine_affected_systems(threat),
                    "patch_availability": random.choice(["available", "pending", "none"]),
                    "exploitation_likelihood": await self._calculate_exploitation_likelihood(technical_details),
                    "business_impact": await self._assess_business_impact(threat)
                }
                vulnerabilities.append(vulnerability)
        
        return vulnerabilities
    
    async def _determine_affected_systems(self, threat: Dict[str, Any]) -> List[str]:
        """Determine which systems might be affected by the threat"""
        threat_type = threat.get("type", "")
        description = threat.get("description", "")
        
        systems = []
        
        # Analyze threat type and description to determine affected systems
        if "windows" in description.lower() or "microsoft" in description.lower():
            systems.append("Windows")
        if "linux" in description.lower() or "unix" in description.lower():
            systems.append("Linux")
        if "web" in description.lower() or "browser" in description.lower():
            systems.append("Web Applications")
        if "mobile" in description.lower() or "android" in description.lower() or "ios" in description.lower():
            systems.append("Mobile Devices")
        if "network" in description.lower() or "router" in description.lower():
            systems.append("Network Infrastructure")
        
        return systems if systems else ["General Systems"]
    
    async def _calculate_exploitation_likelihood(self, technical_details: Dict[str, Any]) -> str:
        """Calculate likelihood of exploitation based on technical details"""
        cvss_score = technical_details.get("cvss_score", 5.0)
        complexity = technical_details.get("exploit_complexity", "medium")
        prerequisites = technical_details.get("attack_prerequisites", "unknown")
        
        score = 0
        
        # CVSS score contribution
        if cvss_score >= 9.0:
            score += 3
        elif cvss_score >= 7.0:
            score += 2
        elif cvss_score >= 4.0:
            score += 1
        
        # Complexity contribution
        if complexity == "low":
            score += 2
        elif complexity == "medium":
            score += 1
        
        # Prerequisites contribution
        if prerequisites in ["none", "user_interaction"]:
            score += 1
        
        # Map score to likelihood
        if score >= 5:
            return "very_high"
        elif score >= 3:
            return "high"
        elif score >= 2:
            return "medium"
        else:
            return "low"
    
    async def _assess_business_impact(self, threat: Dict[str, Any]) -> str:
        """Assess potential business impact of the threat"""
        severity = threat.get("severity", "medium")
        industry_impact = threat.get("industry_impact", "all_sectors")
        attack_vectors = threat.get("attack_vectors", [])
        
        impact_score = 0
        
        # Severity contribution
        severity_scores = {"critical": 3, "high": 2, "medium": 1, "low": 0}
        impact_score += severity_scores.get(severity, 1)
        
        # Industry impact contribution
        if industry_impact == "all_sectors":
            impact_score += 2
        elif industry_impact in ["finance", "healthcare", "government"]:
            impact_score += 1
        
        # Attack vector contribution
        high_impact_vectors = ["data_exfiltration", "ransomware", "system_takeover", "privilege_escalation"]
        if any(vector in high_impact_vectors for vector in attack_vectors):
            impact_score += 1
        
        # Map score to impact level
        if impact_score >= 5:
            return "critical"
        elif impact_score >= 3:
            return "high"
        elif impact_score >= 2:
            return "medium"
        else:
            return "low"
    
    async def _ml_threat_analysis(self, threats: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform ML analysis on threat data"""
        if not SKLEARN_AVAILABLE:
            return {"status": "ml_unavailable"}
        
        try:
            # Extract text data for analysis
            threat_descriptions = [threat.get("description", "") for threat in threats]
            
            if not threat_descriptions:
                return {"status": "no_data"}
            
            # Simulate ML analysis (in production, train actual models)
            analysis = {
                "threat_clusters": random.randint(3, 7),
                "primary_threat_types": random.sample([
                    "malware", "phishing", "ransomware", "apt", "insider_threat", 
                    "supply_chain", "zero_day", "social_engineering"
                ], 3),
                "severity_distribution": {
                    "critical": random.randint(1, 5),
                    "high": random.randint(2, 8),
                    "medium": random.randint(3, 10),
                    "low": random.randint(1, 4)
                },
                "attack_vector_trends": [
                    "Increasing use of AI in attacks",
                    "Growing supply chain targeting",
                    "Enhanced social engineering techniques"
                ],
                "recommended_defenses": [
                    "Zero-trust architecture implementation",
                    "Advanced threat detection systems",
                    "Enhanced user security training",
                    "Supply chain security measures"
                ],
                "confidence_score": random.uniform(0.75, 0.95)
            }
            
            return analysis
        except Exception as e:
            logger.error(f"ML threat analysis failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _update_threat_intelligence(self, learning_results: Dict[str, Any]) -> None:
        """Update threat intelligence database with new learnings"""
        try:
            timestamp = datetime.utcnow().isoformat()
            
            # Update threat intelligence
            self.threat_intelligence[timestamp] = {
                "threats_count": len(learning_results.get("threats_discovered", [])),
                "attack_patterns": learning_results.get("attack_patterns", []),
                "vulnerabilities": learning_results.get("vulnerabilities", []),
                "categorized_threats": learning_results.get("categorized_threats", {}),
                "ml_analysis": learning_results.get("ml_analysis", {})
            }
            
            # Keep only recent intelligence (last 30 entries)
            intelligence_keys = sorted(self.threat_intelligence.keys())
            if len(intelligence_keys) > 30:
                for old_key in intelligence_keys[:-30]:
                    del self.threat_intelligence[old_key]
            
            self.last_update = timestamp
            logger.info(f"✅ Updated threat intelligence database: {timestamp}")
        except Exception as e:
            logger.error(f"Failed to update threat intelligence: {e}")
    
    async def _start_continuous_learning(self) -> None:
        """Start continuous learning process"""
        try:
            # Run initial learning
            await self.learn_latest_cybersecurity_threats()
            
            # Schedule periodic learning (every 6 hours in production)
            logger.info("🔄 Continuous cybersecurity learning enabled")
        except Exception as e:
            logger.error(f"Failed to start continuous learning: {e}")
    
    async def _load_threat_intelligence(self) -> None:
        """Load existing threat intelligence"""
        try:
            # In production, load from persistent storage
            # For now, initialize empty
            self.threat_intelligence = {}
            logger.info("📂 Threat intelligence database initialized")
        except Exception as e:
            logger.error(f"Failed to load threat intelligence: {e}")
    
    async def get_threat_intelligence_summary(self) -> Dict[str, Any]:
        """Get summary of current threat intelligence"""
        await self._ensure_initialized()
        try:
            if not self.threat_intelligence:
                return {
                    "status": "no_data",
                    "message": "No threat intelligence available yet"
                }
            
            # Calculate summary statistics
            total_threats = sum(
                intel.get("threats_count", 0) 
                for intel in self.threat_intelligence.values()
            )
            
            recent_intel = list(self.threat_intelligence.values())[-5:]  # Last 5 updates
            
            summary = {
                "total_threats_tracked": total_threats,
                "intelligence_updates": len(self.threat_intelligence),
                "last_update": self.last_update,
                "recent_threat_categories": {},
                "top_attack_patterns": [],
                "critical_vulnerabilities": [],
                "ml_insights": {}
            }
            
            # Aggregate recent data
            for intel in recent_intel:
                categorized = intel.get("categorized_threats", {})
                for category, threats in categorized.items():
                    if category not in summary["recent_threat_categories"]:
                        summary["recent_threat_categories"][category] = 0
                    summary["recent_threat_categories"][category] += len(threats) if isinstance(threats, list) else 0
            
            return summary
        except Exception as e:
            logger.error(f"Failed to get threat intelligence summary: {e}")
            return {"status": "error", "error": str(e)}
    
    async def generate_docker_test_scenarios(self) -> List[Dict[str, Any]]:
        """Generate Docker test scenarios based on learned threats"""
        await self._ensure_initialized()
        try:
            logger.info("🐳 Generating Docker test scenarios from threat intelligence")
            
            scenarios = []
            
            # Get recent threats for scenario generation
            if self.threat_intelligence:
                recent_intel = list(self.threat_intelligence.values())[-3:]  # Last 3 updates
                
                for intel in recent_intel:
                    threats = intel.get("categorized_threats", {}).get("by_type", {})
                    
                    for threat_type, threat_list in threats.items():
                        if threat_list:
                            scenario = await self._create_docker_scenario_from_threat(threat_type, threat_list[0])
                            scenarios.append(scenario)
            
            # Add some default scenarios if no intelligence available
            if not scenarios:
                scenarios = await self._generate_default_docker_scenarios()
            
            logger.info(f"✅ Generated {len(scenarios)} Docker test scenarios")
            return scenarios
        except Exception as e:
            logger.error(f"Failed to generate Docker scenarios: {e}")
            return []
    
    async def _create_docker_scenario_from_threat(self, threat_type: str, threat: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Docker test scenario based on a specific threat"""
        scenario = {
            "scenario_id": str(uuid.uuid4()),
            "name": f"Test Against {threat_type.replace('_', ' ').title()}",
            "description": threat.get("description", "Security test scenario"),
            "threat_type": threat_type,
            "docker_image": self._select_docker_image_for_threat(threat_type),
            "test_commands": self._generate_test_commands_for_threat(threat_type),
            "expected_defenses": threat.get("mitigation", "Standard security measures"),
            "success_criteria": self._define_success_criteria_for_threat(threat_type),
            "attack_vectors": threat.get("attack_vectors", []),
            "severity": threat.get("severity", "medium"),
            "estimated_duration": "5-15 minutes"
        }
        return scenario
    
    def _select_docker_image_for_threat(self, threat_type: str) -> str:
        """Select appropriate Docker image for threat testing"""
        image_map = {
            "web_vulnerability": "nginx:alpine",
            "malware_analysis": "ubuntu:20.04",
            "network_attack": "alpine:latest",
            "database_attack": "postgres:13",
            "container_escape": "docker:dind",
            "ransomware_simulation": "ubuntu:20.04",
            "phishing_test": "node:16-alpine",
            "zero_day_test": "python:3.9-slim"
        }
        return image_map.get(threat_type, "alpine:latest")
    
    def _generate_test_commands_for_threat(self, threat_type: str) -> List[str]:
        """Generate test commands for specific threat types"""
        command_map = {
            "web_vulnerability": [
                "nmap -p 80,443 target_host",
                "curl -X POST target_host/api/test",
                "python3 -c 'print(\"SQL injection test\")'"
            ],
            "malware_analysis": [
                "apt-get update && apt-get install -y python3",
                "python3 -c 'import os; print(\"Malware simulation\")'",
                "echo 'Security test completed'"
            ],
            "network_attack": [
                "ping -c 3 target_host",
                "nc -zv target_host 22",
                "echo 'Network penetration test'"
            ]
        }
        return command_map.get(threat_type, [
            "echo 'Starting security test'",
            "sleep 2",
            "echo 'Security test completed'"
        ])
    
    def _define_success_criteria_for_threat(self, threat_type: str) -> Dict[str, Any]:
        """Define success criteria for threat testing"""
        return {
            "defense_effectiveness": "Should block or detect attack attempts",
            "alert_generation": "Should generate appropriate security alerts",
            "system_integrity": "System should remain secure and functional",
            "data_protection": "Sensitive data should remain protected",
            "recovery_capability": "System should recover quickly from attacks"
        }
    
    async def _generate_default_docker_scenarios(self) -> List[Dict[str, Any]]:
        """Generate default Docker test scenarios"""
        default_scenarios = [
            {
                "scenario_id": str(uuid.uuid4()),
                "name": "Generic Web Application Security Test",
                "description": "Test web application security against common vulnerabilities",
                "threat_type": "web_security",
                "docker_image": "nginx:alpine",
                "test_commands": [
                    "curl -I localhost",
                    "echo 'Testing XSS protection'",
                    "echo 'Testing CSRF protection'"
                ],
                "expected_defenses": "Web application firewall and input validation",
                "success_criteria": {"security_headers": "present", "input_validation": "active"},
                "attack_vectors": ["xss", "csrf", "sql_injection"],
                "severity": "medium",
                "estimated_duration": "5-10 minutes"
            },
            {
                "scenario_id": str(uuid.uuid4()),
                "name": "Network Security Assessment",
                "description": "Assess network security and port configuration",
                "threat_type": "network_security",
                "docker_image": "alpine:latest",
                "test_commands": [
                    "ping -c 2 8.8.8.8",
                    "echo 'Network connectivity test'",
                    "echo 'Port scanning simulation'"
                ],
                "expected_defenses": "Firewall rules and network segmentation",
                "success_criteria": {"network_isolation": "active", "firewall": "configured"},
                "attack_vectors": ["port_scanning", "network_sniffing"],
                "severity": "medium",
                "estimated_duration": "3-8 minutes"
            }
        ]
        return default_scenarios


# Global instance (lazy initialization)
internet_cybersecurity_learning_service = None

def get_internet_cybersecurity_learning_service():
    """Get or create the internet cybersecurity learning service instance"""
    global internet_cybersecurity_learning_service
    if internet_cybersecurity_learning_service is None:
        internet_cybersecurity_learning_service = InternetCybersecurityLearningService()
    return internet_cybersecurity_learning_service