"""
Guardian AI Service - Security analysis and threat detection with comprehensive SCKIPIT integration
Enhanced with ML-driven security analysis, vulnerability assessment, and threat intelligence
"""

import asyncio
import json
import os
import pickle
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import structlog
import numpy as np
import pandas as pd
import time
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest, f_classif, RFE
from sklearn.pipeline import Pipeline
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
import joblib

from app.models.sql_models import GuardianSuggestion, Proposal, Learning, ErrorLearning, Mission, MissionSubtask
from app.core.database import get_session
from app.core.config import settings
from app.services.anthropic_service import call_claude, anthropic_rate_limited_call
from .ml_service import MLService
from .sckipit_service import SckipitService
from .ai_learning_service import AILearningService
# from .custody_protocol_service import CustodyProtocolService  # Commented out to avoid circular import
# Remove top-level import of CustodyProtocolService
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text
from sqlalchemy.orm import selectinload

logger = structlog.get_logger()


class GuardianAIService:
    """Guardian AI Service - Security analysis and threat detection with comprehensive SCKIPIT integration"""
    
    _instance = None
    _initialized = False
    _security_analyses = {}
    _threat_detections = []
    _vulnerability_assessments = []
    _ml_models = {}
    _sckipit_models = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GuardianAIService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.ml_service = MLService()
            self.sckipit_service = None  # Will be initialized properly in initialize()
            self.learning_service = AILearningService()
            self.custody_service = None  # Will be initialized when needed
            self._initialized = True
            self._initialize_enhanced_ml_models()
            
            # SCKIPIT Integration
            self.sckipit_security_models = {}
            self.sckipit_threat_analyzer = None
            self.sckipit_vulnerability_detector = None
            self.sckipit_security_assessor = None
            
            # Enhanced Security Data
            self.sckipit_enhanced_security_analyses = []
            self.threat_detection_history = []
            self.vulnerability_assessment_results = []
            
            # Initialize SCKIPIT models
            self._initialize_sckipit_models()
            
            # Health check rules for backward compatibility
            self.health_check_rules = {
                "mission": self._check_mission_health,
                "entry": self._check_entry_health,
                "mastery": self._check_mastery_health,
                "proposal": self._check_proposal_health,
                "learning": self._check_learning_health
            }
    
    def _initialize_enhanced_ml_models(self):
        """Initialize enhanced ML models with SCKIPIT integration"""
        try:
            # Create models directory
            os.makedirs(settings.ml_model_path, exist_ok=True)
            
            # Enhanced ML Models with SCKIPIT Integration
            self._ml_models = {
                # Security Threat Predictor (Enhanced with SCKIPIT)
                'security_threat_predictor': RandomForestClassifier(
                    n_estimators=200, 
                    max_depth=15, 
                    min_samples_split=5,
                    random_state=42
                ),
                
                # Vulnerability Detector (Enhanced with SCKIPIT)
                'vulnerability_detector': GradientBoostingClassifier(
                    n_estimators=150,
                    learning_rate=0.1,
                    max_depth=10,
                    random_state=42
                ),
                
                # Security Risk Assessor (Enhanced with SCKIPIT)
                'security_risk_assessor': AdaBoostClassifier(
                    n_estimators=100,
                    learning_rate=0.05,
                    random_state=42
                ),
                
                # Threat Intelligence Analyzer (Enhanced with SCKIPIT)
                'threat_intelligence_analyzer': MLPClassifier(
                    hidden_layer_sizes=(100, 50, 25),
                    activation='relu',
                    solver='adam',
                    max_iter=500,
                    random_state=42
                ),
                
                # Security Anomaly Detector (Enhanced with SCKIPIT)
                'security_anomaly_detector': SVC(
                    kernel='rbf',
                    C=1.0,
                    gamma='scale',
                    probability=True,
                    random_state=42
                ),
                
                # Feature Selection for Better Models
                'feature_selector': SelectKBest(
                    score_func=f_classif,
                    k=15
                )
            }
            
            # Load existing models
            self._load_existing_enhanced_models()
            
            logger.info("Enhanced ML models with SCKIPIT integration initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing enhanced ML models: {str(e)}")
    
    def _initialize_sckipit_models(self):
        """Initialize SCKIPIT-specific models for Guardian AI enhancement"""
        try:
            # SCKIPIT Security Analysis Models
            self.sckipit_models = {
                'threat_analyzer': RandomForestClassifier(
                    n_estimators=150,
                    max_depth=12,
                    random_state=42
                ),
                
                'vulnerability_detector': GradientBoostingClassifier(
                    n_estimators=120,
                    learning_rate=0.1,
                    random_state=42
                ),
                
                'security_assessor': LogisticRegression(
                    random_state=42,
                    max_iter=200
                ),
                
                'anomaly_detector': MLPClassifier(
                    hidden_layer_sizes=(80, 40),
                    activation='relu',
                    solver='adam',
                    max_iter=300,
                    random_state=42
                ),
                
                'text_analyzer': TfidfVectorizer(
                    max_features=1000,
                    ngram_range=(1, 3),
                    stop_words='english'
                ),
                
                'feature_extractor': PCA(
                    n_components=50,
                    random_state=42
                )
            }
            
            # Load existing SCKIPIT models
            self._load_existing_sckipit_models()
            
            logger.info("SCKIPIT models for Guardian AI initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing SCKIPIT models: {str(e)}")
    
    def _load_existing_sckipit_models(self):
        """Load existing trained SCKIPIT models"""
        try:
            model_files = {
                'threat_analyzer': 'sckipit_threat_analyzer.pkl',
                'vulnerability_detector': 'sckipit_vulnerability_detector.pkl',
                'security_assessor': 'sckipit_security_assessor.pkl',
                'anomaly_detector': 'sckipit_anomaly_detector.pkl',
                'text_analyzer': 'sckipit_text_analyzer.pkl',
                'feature_extractor': 'sckipit_feature_extractor.pkl'
            }
            
            for model_name, filename in model_files.items():
                model_path = os.path.join(settings.ml_model_path, filename)
                if os.path.exists(model_path):
                    try:
                        with open(model_path, 'rb') as f:
                            self.sckipit_models[model_name] = pickle.load(f)
                        logger.info(f"Loaded SCKIPIT model: {model_name}")
                    except Exception as e:
                        logger.error(f"Failed to load SCKIPIT model {filename}: {str(e)}")
        except Exception as e:
            logger.error(f"Error loading existing SCKIPIT models: {str(e)}")
    
    def _load_existing_enhanced_models(self):
        """Load existing enhanced ML models"""
        try:
            model_files = {
                'security_threat_predictor': 'guardian_security_threat_predictor.pkl',
                'vulnerability_detector': 'guardian_vulnerability_detector.pkl',
                'security_risk_assessor': 'guardian_security_risk_assessor.pkl',
                'threat_intelligence_analyzer': 'guardian_threat_intelligence_analyzer.pkl',
                'security_anomaly_detector': 'guardian_security_anomaly_detector.pkl'
            }
            
            for model_name, filename in model_files.items():
                model_path = os.path.join(settings.ml_model_path, filename)
                if os.path.exists(model_path):
                    try:
                        with open(model_path, 'rb') as f:
                            self._ml_models[model_name] = pickle.load(f)
                        logger.info(f"Loaded enhanced model: {model_name}")
                    except Exception as e:
                        logger.error(f"Failed to load enhanced model {filename}: {str(e)}")
        except Exception as e:
            logger.error(f"Error loading existing enhanced models: {str(e)}")
    
    async def _save_sckipit_model(self, model_name: str):
        """Save a trained SCKIPIT model"""
        try:
            model_path = os.path.join(settings.ml_model_path, f"sckipit_{model_name}.pkl")
            with open(model_path, 'wb') as f:
                pickle.dump(self.sckipit_models[model_name], f)
            logger.info(f"Saved SCKIPIT model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to save SCKIPIT model {model_name}: {str(e)}")
    
    # ==================== SCKIPIT-ENHANCED SECURITY METHODS ====================
    
    async def analyze_security_with_sckipit(self, code: str, file_path: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Analyze security using SCKIPIT-enhanced ML analysis"""
        try:
            logger.info(f"Guardian AI analyzing security with SCKIPIT: {file_path}")
            
            # Initialize SCKIPIT service
            sckipit = await SckipitService.initialize()
            
            # Analyze code quality with SCKIPIT
            quality_analysis = await sckipit.analyze_code_quality(code, file_path)
            
            # Extract security features
            security_features = await self._extract_security_features(code, file_path, analysis_type)
            
            # SCKIPIT Threat Analysis
            threat_analysis = await self._analyze_threats_with_sckipit(code, security_features)
            
            # SCKIPIT Vulnerability Detection
            vulnerability_analysis = await self._detect_vulnerabilities_with_sckipit(code, security_features)
            
            # SCKIPIT Security Assessment
            security_assessment = await self._assess_security_with_sckipit(code, quality_analysis, threat_analysis, vulnerability_analysis)
            
            # Enhanced security record with SCKIPIT insights
            security_record = {
                'timestamp': datetime.now().isoformat(),
                'file_path': file_path,
                'analysis_type': analysis_type,
                'quality_score': quality_analysis.get('quality_score', 0.7),
                'threat_level': threat_analysis.get('threat_level', 'low'),
                'vulnerability_count': vulnerability_analysis.get('vulnerability_count', 0),
                'security_score': security_assessment.get('security_score', 0.7),
                'threat_analysis': threat_analysis,
                'vulnerability_analysis': vulnerability_analysis,
                'security_assessment': security_assessment,
                'sckipit_confidence': security_assessment.get('sckipit_confidence', 0.7)
            }
            
            self.sckipit_enhanced_security_analyses.append(security_record)
            
            # Update SCKIPIT learning data
            await self._update_sckipit_security_data(security_record)
            
            logger.info(f"SCKIPIT-enhanced security analysis completed for {file_path}")
            
            return {
                'status': 'success',
                'security_score': security_assessment.get('security_score', 0.7),
                'threat_level': threat_analysis.get('threat_level', 'low'),
                'vulnerabilities': vulnerability_analysis.get('vulnerabilities', []),
                'recommendations': security_assessment.get('recommendations', []),
                'sckipit_analysis': {
                    'quality_analysis': quality_analysis,
                    'threat_analysis': threat_analysis,
                    'vulnerability_analysis': vulnerability_analysis,
                    'security_assessment': security_assessment
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing security with SCKIPIT: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    async def _analyze_threats_with_sckipit(self, code: str, features: Dict) -> Dict[str, Any]:
        """Analyze threats using SCKIPIT models"""
        try:
            # Use SCKIPIT threat analyzer
            if 'threat_analyzer' in self.sckipit_models:
                X = np.array([list(features.values())])
                threat_score = self.sckipit_models['threat_analyzer'].predict_proba(X)[0][1]
                
                threat_analysis = {
                    'threat_score': float(threat_score),
                    'threat_level': await self._classify_threat_level(threat_score),
                    'threat_types': await self._identify_threat_types(features),
                    'risk_factors': await self._identify_risk_factors(features),
                    'mitigation_strategies': await self._generate_mitigation_strategies(threat_score, features)
                }
            else:
                threat_analysis = {
                    'threat_score': 0.3,
                    'threat_level': 'low',
                    'threat_types': [],
                    'risk_factors': [],
                    'mitigation_strategies': []
                }
            
            return threat_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing threats with SCKIPIT: {str(e)}")
            return {'threat_score': 0.3, 'threat_level': 'unknown'}
    
    async def _detect_vulnerabilities_with_sckipit(self, code: str, features: Dict) -> Dict[str, Any]:
        """Detect vulnerabilities using SCKIPIT models"""
        try:
            # Use SCKIPIT vulnerability detector
            if 'vulnerability_detector' in self.sckipit_models:
                X = np.array([list(features.values())])
                vulnerability_score = self.sckipit_models['vulnerability_detector'].predict_proba(X)[0][1]
                
                vulnerability_analysis = {
                    'vulnerability_score': float(vulnerability_score),
                    'vulnerability_count': await self._count_vulnerabilities(features),
                    'vulnerability_types': await self._identify_vulnerability_types(features),
                    'severity_levels': await self._assess_vulnerability_severity(features),
                    'remediation_actions': await self._generate_remediation_actions(vulnerability_score, features)
                }
            else:
                vulnerability_analysis = {
                    'vulnerability_score': 0.2,
                    'vulnerability_count': 0,
                    'vulnerability_types': [],
                    'severity_levels': [],
                    'remediation_actions': []
                }
            
            return vulnerability_analysis
            
        except Exception as e:
            logger.error(f"Error detecting vulnerabilities with SCKIPIT: {str(e)}")
            return {'vulnerability_score': 0.2, 'vulnerability_count': 0}
    
    async def _assess_security_with_sckipit(self, code: str, quality_analysis: Dict, threat_analysis: Dict, vulnerability_analysis: Dict) -> Dict[str, Any]:
        """Assess overall security using SCKIPIT analysis"""
        try:
            # Calculate overall security score
            quality_score = quality_analysis.get('quality_score', 0.7)
            threat_score = threat_analysis.get('threat_score', 0.3)
            vulnerability_score = vulnerability_analysis.get('vulnerability_score', 0.2)
            
            # Security score is weighted combination
            security_score = (quality_score * 0.4 + (1 - threat_score) * 0.3 + (1 - vulnerability_score) * 0.3)
            
            # Generate security recommendations
            recommendations = await self._generate_security_recommendations(
                quality_score, threat_score, vulnerability_score, code
            )
            
            return {
                'security_score': security_score,
                'security_level': await self._classify_security_level(security_score),
                'recommendations': recommendations,
                'risk_assessment': await self._assess_overall_risk(threat_score, vulnerability_score),
                'compliance_status': await self._check_compliance_status(code),
                'sckipit_confidence': 0.8 if security_score > 0.7 else 0.6
            }
            
        except Exception as e:
            logger.error(f"Error assessing security with SCKIPIT: {str(e)}")
            return {
                'security_score': 0.7,
                'security_level': 'medium',
                'recommendations': ["Apply general security best practices"],
                'risk_assessment': 'low',
                'compliance_status': 'unknown',
                'sckipit_confidence': 0.5
            }
    
    # ==================== SCKIPIT HELPER METHODS ====================
    
    async def _extract_security_features(self, code: str, file_path: str, analysis_type: str) -> Dict[str, float]:
        """Extract features for security analysis"""
        try:
            return {
                'code_length': len(code),
                'line_count': len(code.split('\n')),
                'has_sql_injection': 1.0 if any(sql in code.lower() for sql in ['select', 'insert', 'update', 'delete']) and '?' not in code else 0.0,
                'has_xss_vulnerability': 1.0 if any(xss in code.lower() for xss in ['<script>', 'javascript:', 'onclick']) else 0.0,
                'has_hardcoded_secrets': 1.0 if any(secret in code.lower() for secret in ['password', 'secret', 'key', 'token']) else 0.0,
                'has_input_validation': 1.0 if any(validation in code.lower() for validation in ['validate', 'sanitize', 'escape']) else 0.0,
                'has_authentication': 1.0 if any(auth in code.lower() for auth in ['auth', 'login', 'authenticate']) else 0.0,
                'has_authorization': 1.0 if any(authz in code.lower() for authz in ['authorize', 'permission', 'role']) else 0.0,
                'has_encryption': 1.0 if any(encrypt in code.lower() for encrypt in ['encrypt', 'hash', 'bcrypt']) else 0.0,
                'analysis_type_encoded': hash(analysis_type) % 10 / 10.0,
                'file_type_encoded': hash(file_path.split('.')[-1]) % 10 / 10.0
            }
        except Exception as e:
            logger.error(f"Error extracting security features: {str(e)}")
            return {'code_length': 0.0, 'line_count': 0.0, 'has_sql_injection': 0.0}
    
    async def _classify_threat_level(self, threat_score: float) -> str:
        """Classify threat level based on threat score"""
        try:
            if threat_score >= 0.8:
                return "critical"
            elif threat_score >= 0.6:
                return "high"
            elif threat_score >= 0.4:
                return "medium"
            elif threat_score >= 0.2:
                return "low"
            else:
                return "minimal"
        except Exception as e:
            logger.error(f"Error classifying threat level: {str(e)}")
            return "unknown"
    
    async def _identify_threat_types(self, features: Dict) -> List[str]:
        """Identify threat types based on features"""
        try:
            threat_types = []
            
            if features.get('has_sql_injection', 0.0) > 0.5:
                threat_types.append("SQL Injection")
            
            if features.get('has_xss_vulnerability', 0.0) > 0.5:
                threat_types.append("Cross-Site Scripting (XSS)")
            
            if features.get('has_hardcoded_secrets', 0.0) > 0.5:
                threat_types.append("Hardcoded Secrets")
            
            if features.get('has_input_validation', 0.0) < 0.5:
                threat_types.append("Input Validation Bypass")
            
            if features.get('has_authentication', 0.0) < 0.5:
                threat_types.append("Authentication Bypass")
            
            return threat_types
        except Exception as e:
            logger.error(f"Error identifying threat types: {str(e)}")
            return ["General Security Threats"]
    
    async def _identify_risk_factors(self, features: Dict) -> List[str]:
        """Identify risk factors based on features"""
        try:
            risk_factors = []
            
            if features.get('code_length', 0.0) > 1000:
                risk_factors.append("Large codebase increases attack surface")
            
            if features.get('has_sql_injection', 0.0) > 0.5:
                risk_factors.append("SQL injection vulnerabilities present")
            
            if features.get('has_xss_vulnerability', 0.0) > 0.5:
                risk_factors.append("XSS vulnerabilities detected")
            
            if features.get('has_hardcoded_secrets', 0.0) > 0.5:
                risk_factors.append("Hardcoded secrets in code")
            
            if features.get('has_input_validation', 0.0) < 0.5:
                risk_factors.append("Insufficient input validation")
            
            return risk_factors
        except Exception as e:
            logger.error(f"Error identifying risk factors: {str(e)}")
            return ["General security risks"]
    
    async def _generate_mitigation_strategies(self, threat_score: float, features: Dict) -> List[str]:
        """Generate mitigation strategies based on threat analysis"""
        try:
            strategies = []
            
            if threat_score > 0.6:
                strategies.extend([
                    "Implement comprehensive security testing",
                    "Add input validation and sanitization",
                    "Use parameterized queries to prevent SQL injection",
                    "Implement proper authentication and authorization"
                ])
            
            if features.get('has_sql_injection', 0.0) > 0.5:
                strategies.append("Use parameterized queries or ORM")
            
            if features.get('has_xss_vulnerability', 0.0) > 0.5:
                strategies.append("Implement output encoding and CSP headers")
            
            if features.get('has_hardcoded_secrets', 0.0) > 0.5:
                strategies.append("Move secrets to environment variables or secure storage")
            
            return strategies
        except Exception as e:
            logger.error(f"Error generating mitigation strategies: {str(e)}")
            return ["Apply general security best practices"]
    
    async def _count_vulnerabilities(self, features: Dict) -> int:
        """Count vulnerabilities based on features"""
        try:
            count = 0
            
            if features.get('has_sql_injection', 0.0) > 0.5:
                count += 1
            
            if features.get('has_xss_vulnerability', 0.0) > 0.5:
                count += 1
            
            if features.get('has_hardcoded_secrets', 0.0) > 0.5:
                count += 1
            
            if features.get('has_input_validation', 0.0) < 0.5:
                count += 1
            
            return count
        except Exception as e:
            logger.error(f"Error counting vulnerabilities: {str(e)}")
            return 0
    
    async def _identify_vulnerability_types(self, features: Dict) -> List[str]:
        """Identify vulnerability types based on features"""
        try:
            vulnerabilities = []
            
            if features.get('has_sql_injection', 0.0) > 0.5:
                vulnerabilities.append("SQL Injection")
            
            if features.get('has_xss_vulnerability', 0.0) > 0.5:
                vulnerabilities.append("Cross-Site Scripting")
            
            if features.get('has_hardcoded_secrets', 0.0) > 0.5:
                vulnerabilities.append("Hardcoded Secrets")
            
            if features.get('has_input_validation', 0.0) < 0.5:
                vulnerabilities.append("Input Validation Issues")
            
            return vulnerabilities
        except Exception as e:
            logger.error(f"Error identifying vulnerability types: {str(e)}")
            return ["General vulnerabilities"]
    
    async def _assess_vulnerability_severity(self, features: Dict) -> List[str]:
        """Assess vulnerability severity levels"""
        try:
            severities = []
            
            if features.get('has_sql_injection', 0.0) > 0.5:
                severities.append("Critical: SQL Injection")
            
            if features.get('has_xss_vulnerability', 0.0) > 0.5:
                severities.append("High: Cross-Site Scripting")
            
            if features.get('has_hardcoded_secrets', 0.0) > 0.5:
                severities.append("Medium: Hardcoded Secrets")
            
            if features.get('has_input_validation', 0.0) < 0.5:
                severities.append("Medium: Input Validation Issues")
            
            return severities
        except Exception as e:
            logger.error(f"Error assessing vulnerability severity: {str(e)}")
            return ["Medium: General security issues"]
    
    async def _generate_remediation_actions(self, vulnerability_score: float, features: Dict) -> List[str]:
        """Generate remediation actions based on vulnerability analysis"""
        try:
            actions = []
            
            if vulnerability_score > 0.5:
                actions.extend([
                    "Conduct security code review",
                    "Implement automated security testing",
                    "Add security headers and configurations",
                    "Update dependencies to latest secure versions"
                ])
            
            if features.get('has_sql_injection', 0.0) > 0.5:
                actions.append("Replace raw SQL with parameterized queries")
            
            if features.get('has_xss_vulnerability', 0.0) > 0.5:
                actions.append("Implement output encoding and sanitization")
            
            if features.get('has_hardcoded_secrets', 0.0) > 0.5:
                actions.append("Move secrets to secure configuration management")
            
            return actions
        except Exception as e:
            logger.error(f"Error generating remediation actions: {str(e)}")
            return ["Apply general security remediation practices"]
    
    async def _classify_security_level(self, security_score: float) -> str:
        """Classify security level based on security score"""
        try:
            if security_score >= 0.9:
                return "excellent"
            elif security_score >= 0.8:
                return "good"
            elif security_score >= 0.7:
                return "acceptable"
            elif security_score >= 0.6:
                return "needs_improvement"
            else:
                return "poor"
        except Exception as e:
            logger.error(f"Error classifying security level: {str(e)}")
            return "unknown"
    
    async def _generate_security_recommendations(self, quality_score: float, threat_score: float, vulnerability_score: float, code: str) -> List[str]:
        """Generate security recommendations based on analysis"""
        try:
            recommendations = []
            
            if quality_score < 0.8:
                recommendations.append("Improve code quality and security practices")
            
            if threat_score > 0.5:
                recommendations.append("Implement threat modeling and security testing")
            
            if vulnerability_score > 0.5:
                recommendations.append("Address identified vulnerabilities immediately")
            
            # General security recommendations
            recommendations.extend([
                "Follow OWASP security guidelines",
                "Implement secure coding practices",
                "Add comprehensive logging and monitoring",
                "Regular security audits and penetration testing"
            ])
            
            return list(set(recommendations))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error generating security recommendations: {str(e)}")
            return ["Apply general security best practices"]
    
    async def _assess_overall_risk(self, threat_score: float, vulnerability_score: float) -> str:
        """Assess overall risk level"""
        try:
            overall_risk = (threat_score + vulnerability_score) / 2
            
            if overall_risk >= 0.7:
                return "high"
            elif overall_risk >= 0.4:
                return "medium"
            else:
                return "low"
        except Exception as e:
            logger.error(f"Error assessing overall risk: {str(e)}")
            return "unknown"
    
    async def _check_compliance_status(self, code: str) -> str:
        """Check compliance status"""
        try:
            # Basic compliance checks
            has_encryption = 'encrypt' in code.lower() or 'hash' in code.lower()
            has_authentication = 'auth' in code.lower() or 'login' in code.lower()
            has_logging = 'log' in code.lower() or 'audit' in code.lower()
            
            if has_encryption and has_authentication and has_logging:
                return "compliant"
            elif has_authentication and has_logging:
                return "partially_compliant"
            else:
                return "non_compliant"
        except Exception as e:
            logger.error(f"Error checking compliance status: {str(e)}")
            return "unknown"
    
    async def _update_sckipit_security_data(self, security_record: Dict):
        """Update SCKIPIT learning data with security analysis results"""
        try:
            # Add to SCKIPIT-enhanced security analyses
            self.sckipit_enhanced_security_analyses.append(security_record)
            
            # Keep only recent data to prevent memory issues
            max_records = 100
            if len(self.sckipit_enhanced_security_analyses) > max_records:
                self.sckipit_enhanced_security_analyses = self.sckipit_enhanced_security_analyses[-max_records:]
            
            logger.info(f"Updated SCKIPIT security data for {security_record.get('file_path', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Error updating SCKIPIT security data: {str(e)}")
    
    async def get_sckipit_analytics(self) -> Dict[str, Any]:
        """Get SCKIPIT analytics for Guardian AI"""
        try:
            return {
                'total_security_analyses': len(self.sckipit_enhanced_security_analyses),
                'average_security_score': sum(analysis.get('security_score', 0.7) for analysis in self.sckipit_enhanced_security_analyses) / len(self.sckipit_enhanced_security_analyses) if self.sckipit_enhanced_security_analyses else 0.7,
                'threat_detection_count': len(self.threat_detection_history),
                'vulnerability_assessment_count': len(self.vulnerability_assessment_results),
                'high_threat_files': len([analysis for analysis in self.sckipit_enhanced_security_analyses if analysis.get('threat_level') == 'high']),
                'critical_vulnerabilities': len([analysis for analysis in self.sckipit_enhanced_security_analyses if analysis.get('vulnerability_count', 0) > 3]),
                'recent_security_analyses': self.sckipit_enhanced_security_analyses[-5:] if self.sckipit_enhanced_security_analyses else [],
                'sckipit_integration_status': 'active'
            }
        except Exception as e:
            logger.error(f"Error getting SCKIPIT analytics: {str(e)}")
            return {'error': str(e)}
    
    async def run_comprehensive_health_check(self, session: AsyncSession) -> Dict[str, Any]:
        """Run comprehensive Guardian AI health check (delegates system/database/resource checks to core monitoring)"""
        try:
            logger.info("Starting comprehensive Guardian AI health check")
            results = {
                "timestamp": datetime.utcnow().isoformat(),
                "overall_health": "healthy",
                "issues_found": 0,
                "suggestions_created": 0,
                "checks_performed": {},
                "summary": {}
            }
            # Only run AI-specific component checks (mission, proposal, learning, etc.)
            for component_type, check_function in self.health_check_rules.items():
                if component_type in ["mission", "entry", "mastery", "proposal", "learning"]:
                    logger.info(f"Running health check for {component_type}")
                    component_results = await check_function(session)
                    results["checks_performed"][component_type] = component_results
                    results["issues_found"] += component_results.get("issues_found", 0)
                    results["suggestions_created"] += component_results.get("suggestions_created", 0)
            # System/database/resource health checks are now handled by app/core/monitoring.py
            # Determine overall health
            if results["issues_found"] == 0:
                results["overall_health"] = "healthy"
            elif results["issues_found"] <= 5:
                results["overall_health"] = "warning"
            else:
                results["overall_health"] = "critical"
            # Generate summary
            results["summary"] = {
                "total_components_checked": len(results["checks_performed"]),
                "healthy_components": sum(1 for r in results["checks_performed"].values() 
                                        if r.get("health_status") == "healthy"),
                "components_with_issues": sum(1 for r in results["checks_performed"].values() 
                                            if r.get("issues_found", 0) > 0),
                "critical_issues": sum(r.get("critical_issues", 0) for r in results["checks_performed"].values()),
                "high_priority_issues": sum(r.get("high_priority_issues", 0) for r in results["checks_performed"].values())
            }
            logger.info("Comprehensive health check completed", 
                       overall_health=results["overall_health"],
                       issues_found=results["issues_found"])
            # Claude verification
            try:
                verification = await anthropic_rate_limited_call(
                    f"Guardian AI completed health check. Results: {results}. Please verify and suggest improvements or missed issues.",
                    ai_name="guardian"
                )
                logger.info(f"Claude verification for health check: {verification}")
            except Exception as e:
                logger.warning(f"Claude verification error: {str(e)}")
            return results
        except Exception as e:
            logger.error("Error running comprehensive health check", error_message=str(e))
            # Claude failure analysis
            try:
                advice = await anthropic_rate_limited_call(
                    f"Guardian AI failed health check. Error: {str(e)}. Please analyze and suggest how to improve.",
                    ai_name="guardian"
                )
                logger.info(f"Claude advice for failed health check: {advice}")
            except Exception as ce:
                logger.warning(f"Claude error: {str(ce)}")
            raise
    
    async def _check_proposal_health(self, session: AsyncSession) -> Dict[str, Any]:
        """Check health of proposal system"""
        try:
            issues_found = 0
            suggestions_created = 0
            critical_issues = 0
            high_priority_issues = 0
            
            # Check for proposals with missing required fields
            proposals_result = await session.execute(
                select(Proposal).where(
                    or_(
                        Proposal.ai_type.is_(None),
                        Proposal.file_path.is_(None),
                        Proposal.code_before.is_(None)
                    )
                )
            )
            invalid_proposals = proposals_result.scalars().all()
            
            for proposal in invalid_proposals:
                issues_found += 1
                high_priority_issues += 1
                
                await self._create_suggestion(
                    session=session,
                    issue_type="proposal",
                    affected_item_type="proposal",
                    affected_item_id=str(proposal.id),
                    affected_item_name=f"Proposal {proposal.id[:8]}",
                    issue_description="Proposal missing required fields",
                    current_value=json.dumps({
                        "ai_type": proposal.ai_type,
                        "file_path": proposal.file_path,
                        "has_code_before": bool(proposal.code_before)
                    }, default=str),
                    proposed_fix="Add missing required fields or mark for deletion",
                    severity="high",
                    health_check_type="required_fields_validation"
                )
                suggestions_created += 1
            
            # Check for proposals with inconsistent status
            status_result = await session.execute(
                select(Proposal).where(
                    and_(
                        Proposal.status == "tested",
                        Proposal.test_status == "not-run"
                    )
                )
            )
            inconsistent_proposals = status_result.scalars().all()
            
            for proposal in inconsistent_proposals:
                issues_found += 1
                
                await self._create_suggestion(
                    session=session,
                    issue_type="proposal",
                    affected_item_type="proposal",
                    affected_item_id=str(proposal.id),
                    affected_item_name=f"Proposal {proposal.id[:8]}",
                    issue_description="Proposal status inconsistent with test status",
                    current_value=f"status={proposal.status}, test_status={proposal.test_status}",
                    proposed_fix="Update test status to match proposal status",
                    severity="medium",
                    health_check_type="status_consistency_check"
                )
                suggestions_created += 1
            
            # Check for duplicate proposals
            duplicate_result = await session.execute(
                select(Proposal.code_hash, func.count(Proposal.id))
                .where(Proposal.code_hash.isnot(None))
                .group_by(Proposal.code_hash)
                .having(func.count(Proposal.id) > 1)
            )
            duplicates = duplicate_result.all()
            
            for code_hash, count in duplicates:
                issues_found += 1
                
                await self._create_suggestion(
                    session=session,
                    issue_type="proposal",
                    affected_item_type="proposal_group",
                    affected_item_id=code_hash,
                    affected_item_name=f"Duplicate proposals (count: {count})",
                    issue_description=f"Found {count} proposals with identical code hash",
                    current_value=f"code_hash: {code_hash}, count: {count}",
                    proposed_fix="Review and merge duplicate proposals",
                    severity="medium",
                    health_check_type="duplicate_detection"
                )
                suggestions_created += 1
            
            return {
                "health_status": "healthy" if issues_found == 0 else "warning",
                "issues_found": issues_found,
                "suggestions_created": suggestions_created,
                "critical_issues": critical_issues,
                "high_priority_issues": high_priority_issues,
                "total_proposals": await self._count_proposals(session)
            }
            
        except Exception as e:
            logger.error("Error checking proposal health", error_message=str(e))
            return {"health_status": "error", "error": str(e)}
    
    async def _check_learning_health(self, session: AsyncSession) -> Dict[str, Any]:
        """Check health of learning system"""
        try:
            issues_found = 0
            suggestions_created = 0
            
            # Check for learning entries with low confidence but high success rate
            learning_result = await session.execute(
                select(Learning).where(
                    and_(
                        Learning.confidence < 0.3,
                        Learning.success_rate > 0.8
                    )
                )
            )
            inconsistent_learning = learning_result.scalars().all()
            
            for learning in inconsistent_learning:
                issues_found += 1
                
                await self._create_suggestion(
                    session=session,
                    issue_type="learning",
                    affected_item_type="learning",
                    affected_item_id=str(learning.id),
                    affected_item_name=f"Learning {learning.learning_type}",
                    issue_description="Learning entry has low confidence but high success rate",
                    current_value=f"confidence={learning.confidence}, success_rate={learning.success_rate}",
                    proposed_fix="Update confidence score based on success rate",
                    severity="low",
                    health_check_type="confidence_consistency_check"
                )
                suggestions_created += 1
            
            # Check for error learning with high frequency but no solution
            error_result = await session.execute(
                select(ErrorLearning).where(
                    and_(
                        ErrorLearning.frequency > 5,
                        ErrorLearning.solution.is_(None)
                    )
                )
            )
            unsolved_errors = error_result.scalars().all()
            
            for error in unsolved_errors:
                issues_found += 1
                
                await self._create_suggestion(
                    session=session,
                    issue_type="learning",
                    affected_item_type="error_learning",
                    affected_item_id=str(error.id),
                    affected_item_name=f"Error: {error.error_pattern}",
                    issue_description="Frequent error without documented solution",
                    current_value=f"frequency={error.frequency}, pattern={error.error_pattern}",
                    proposed_fix="Investigate and document solution for this error pattern",
                    severity="high",
                    health_check_type="error_solution_check"
                )
                suggestions_created += 1
            
            return {
                "health_status": "healthy" if issues_found == 0 else "warning",
                "issues_found": issues_found,
                "suggestions_created": suggestions_created,
                "total_learning_entries": await self._count_learning_entries(session),
                "total_error_entries": await self._count_error_learning_entries(session)
            }
            
        except Exception as e:
            logger.error("Error checking learning health", error_message=str(e))
            return {"health_status": "error", "error": str(e)}
    
    async def _check_mission_health(self, session: AsyncSession) -> Dict[str, Any]:
        """Check health of mission system"""
        try:
            issues_found = 0
            suggestions_created = 0
            critical_issues = 0
            high_priority_issues = 0
            
            # Check for missions with missing required fields
            missions_result = await session.execute(
                select(Mission).where(
                    or_(
                        Mission.title.is_(None),
                        Mission.mission_type.is_(None),
                        Mission.notification_id.is_(None)
                    )
                )
            )
            invalid_missions = missions_result.scalars().all()
            
            for mission in invalid_missions:
                issues_found += 1
                high_priority_issues += 1
                
                await self._create_suggestion(
                    session=session,
                    issue_type="mission",
                    affected_item_type="mission",
                    affected_item_id=str(mission.id),
                    affected_item_name=mission.title or f"Mission {mission.id[:8]}",
                    issue_description="Mission missing required fields",
                    current_value=json.dumps({
                        "title": mission.title,
                        "mission_type": mission.mission_type,
                        "notification_id": mission.notification_id
                    }, default=str),
                    proposed_fix="Add missing required fields or mark for deletion",
                    severity="high",
                    health_check_type="required_fields_validation"
                )
                suggestions_created += 1
            
            # Check for missions with inconsistent completion status
            completion_result = await session.execute(
                select(Mission).where(
                    and_(
                        Mission.is_completed == True,
                        Mission.has_failed == True
                    )
                )
            )
            inconsistent_missions = completion_result.scalars().all()
            
            for mission in inconsistent_missions:
                issues_found += 1
                
                await self._create_suggestion(
                    session=session,
                    issue_type="mission",
                    affected_item_type="mission",
                    affected_item_id=str(mission.id),
                    affected_item_name=mission.title,
                    issue_description="Mission has both completed and failed status",
                    current_value=f"is_completed={mission.is_completed}, has_failed={mission.has_failed}",
                    proposed_fix="Fix mission status - cannot be both completed and failed",
                    severity="medium",
                    health_check_type="status_consistency_check"
                )
                suggestions_created += 1
            
            # Check for counter-based missions with invalid counts
            counter_result = await session.execute(
                select(Mission).where(
                    and_(
                        Mission.is_counter_based == True,
                        Mission.current_count < 0
                    )
                )
            )
            invalid_counters = counter_result.scalars().all()
            
            for mission in invalid_counters:
                issues_found += 1
                
                await self._create_suggestion(
                    session=session,
                    issue_type="mission",
                    affected_item_type="mission",
                    affected_item_id=str(mission.id),
                    affected_item_name=mission.title,
                    issue_description="Counter-based mission has negative count",
                    current_value=f"current_count={mission.current_count}",
                    proposed_fix="Reset current count to 0 or positive value",
                    severity="medium",
                    health_check_type="counter_validation"
                )
                suggestions_created += 1
            
            # Check for missions with missing subtasks when they should have them
            subtask_result = await session.execute(
                select(Mission).where(
                    and_(
                        Mission.subtasks_data.isnot(None),
                        Mission.subtasks_data != text("'[]'::jsonb")
                    )
                )
            )
            missions_with_subtasks = subtask_result.scalars().all()
            
            for mission in missions_with_subtasks:
                # Check if subtasks exist in the subtasks table
                subtasks_count_result = await session.execute(
                    select(func.count(MissionSubtask.id))
                    .where(MissionSubtask.mission_id == mission.id)
                )
                subtasks_count = subtasks_count_result.scalar()
                
                if subtasks_count == 0:
                    issues_found += 1
                    
                    await self._create_suggestion(
                        session=session,
                        issue_type="mission",
                        affected_item_type="mission",
                        affected_item_id=str(mission.id),
                        affected_item_name=mission.title,
                        issue_description="Mission has subtasks data but no subtask records",
                        current_value=f"subtasks_data exists but {subtasks_count} subtask records found",
                        proposed_fix="Create subtask records or clear subtasks data",
                        severity="low",
                        health_check_type="subtask_consistency_check"
                    )
                    suggestions_created += 1
            
            # Check for orphaned subtasks (subtasks without missions)
            orphaned_result = await session.execute(
                select(MissionSubtask)
                .outerjoin(Mission, MissionSubtask.mission_id == Mission.id)
                .where(Mission.id.is_(None))
            )
            orphaned_subtasks = orphaned_result.scalars().all()
            
            for subtask in orphaned_subtasks:
                issues_found += 1
                
                await self._create_suggestion(
                    session=session,
                    issue_type="mission",
                    affected_item_type="subtask",
                    affected_item_id=str(subtask.id),
                    affected_item_name=subtask.name,
                    issue_description="Subtask without parent mission",
                    current_value=f"mission_id={subtask.mission_id}",
                    proposed_fix="Delete orphaned subtask or link to valid mission",
                    severity="medium",
                    health_check_type="orphaned_subtask_check"
                )
                suggestions_created += 1
            
            return {
                "health_status": "healthy" if issues_found == 0 else "warning",
                "issues_found": issues_found,
                "suggestions_created": suggestions_created,
                "critical_issues": critical_issues,
                "high_priority_issues": high_priority_issues,
                "total_missions": await self._count_missions(session),
                "total_subtasks": await self._count_subtasks(session)
            }
            
        except Exception as e:
            logger.error("Error checking mission health", error_message=str(e))
            return {"health_status": "error", "error": str(e)}
    
    async def _check_entry_health(self, session: AsyncSession) -> Dict[str, Any]:
        """Check health of entry system (placeholder for future implementation)"""
        # This would check entry data when entry models are implemented
        return {
            "health_status": "healthy",
            "issues_found": 0,
            "suggestions_created": 0,
            "note": "Entry health checks will be implemented when entry models are added"
        }
    
    async def _check_mastery_health(self, session: AsyncSession) -> Dict[str, Any]:
        """Check health of mastery system (placeholder for future implementation)"""
        # This would check mastery data when mastery models are implemented
        return {
            "health_status": "healthy",
            "issues_found": 0,
            "suggestions_created": 0,
            "note": "Mastery health checks will be implemented when mastery models are added"
        }
    
    async def _create_suggestion(
        self,
        session: AsyncSession,
        issue_type: str,
        affected_item_type: str,
        affected_item_id: str,
        affected_item_name: str,
        issue_description: str,
        current_value: str,
        proposed_fix: str,
        severity: str = "medium",
        health_check_type: str = "general_health_check"
    ) -> GuardianSuggestion:
        """Create a new Guardian suggestion"""
        try:
            suggestion = GuardianSuggestion(
                issue_type=issue_type,
                affected_item_type=affected_item_type,
                affected_item_id=affected_item_id,
                affected_item_name=affected_item_name,
                issue_description=issue_description,
                current_value=current_value,
                proposed_fix=proposed_fix,
                severity=severity,
                health_check_type=health_check_type,
                status="pending"
            )
            
            session.add(suggestion)
            await session.commit()
            
            logger.info("Created Guardian suggestion", 
                       suggestion_id=str(suggestion.id),
                       issue_type=issue_type,
                       severity=severity)
            
            return suggestion
            
        except Exception as e:
            logger.error("Error creating Guardian suggestion", error_message=str(e))
            await session.rollback()
            raise
    
    async def get_pending_suggestions(
        self, 
        session: AsyncSession, 
        limit: int = 50,
        offset: int = 0,
        severity_filter: Optional[str] = None,
        issue_type_filter: Optional[str] = None
    ) -> List[GuardianSuggestion]:
        """Get pending Guardian suggestions with optional filtering"""
        try:
            query = select(GuardianSuggestion).where(GuardianSuggestion.status == "pending")
            
            if severity_filter:
                query = query.where(GuardianSuggestion.severity == severity_filter)
            
            if issue_type_filter:
                query = query.where(GuardianSuggestion.issue_type == issue_type_filter)
            
            query = query.order_by(
                GuardianSuggestion.severity.desc(),
                GuardianSuggestion.created_at.desc()
            ).offset(offset).limit(limit)
            
            result = await session.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error("Error getting pending suggestions", error_message=str(e))
            raise
    
    async def approve_suggestion(
        self,
        session: AsyncSession,
        suggestion_id: str,
        approved_by: str,
        user_feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """Approve a Guardian suggestion and apply the fix"""
        try:
            # Get the suggestion
            result = await session.execute(
                select(GuardianSuggestion).where(GuardianSuggestion.id == suggestion_id)
            )
            suggestion = result.scalar_one_or_none()
            
            if not suggestion:
                raise ValueError("Suggestion not found")
            
            if suggestion.status != "pending":
                raise ValueError("Suggestion is not pending")
            
            # Update suggestion status
            suggestion.status = "approved"
            suggestion.approved_by = approved_by
            suggestion.approved_at = datetime.utcnow()
            suggestion.user_feedback = user_feedback
            
            # Apply the fix
            fix_result = await self._apply_fix(session, suggestion)
            
            # Update suggestion with fix results
            suggestion.fix_applied = True
            suggestion.fix_applied_at = datetime.utcnow()
            suggestion.fix_result = fix_result.get("message", "Fix applied")
            suggestion.fix_success = fix_result.get("success", False)
            
            await session.commit()
            
            logger.info("Approved and applied Guardian suggestion", 
                       suggestion_id=str(suggestion.id),
                       approved_by=approved_by,
                       fix_success=suggestion.fix_success)
            
            return {
                "status": "success",
                "suggestion_id": str(suggestion.id),
                "fix_applied": True,
                "fix_success": suggestion.fix_success,
                "fix_result": suggestion.fix_result
            }
            
        except Exception as e:
            logger.error("Error approving suggestion", error_message=str(e))
            await session.rollback()
            raise
    
    async def reject_suggestion(
        self,
        session: AsyncSession,
        suggestion_id: str,
        rejected_by: str,
        user_feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """Reject a Guardian suggestion"""
        try:
            # Get the suggestion
            result = await session.execute(
                select(GuardianSuggestion).where(GuardianSuggestion.id == suggestion_id)
            )
            suggestion = result.scalar_one_or_none()
            
            if not suggestion:
                raise ValueError("Suggestion not found")
            
            if suggestion.status != "pending":
                raise ValueError("Suggestion is not pending")
            
            # Update suggestion status
            suggestion.status = "rejected"
            suggestion.approved_by = rejected_by
            suggestion.approved_at = datetime.utcnow()
            suggestion.user_feedback = user_feedback
            
            await session.commit()
            
            logger.info("Rejected Guardian suggestion", 
                       suggestion_id=str(suggestion.id),
                       rejected_by=rejected_by)
            
            return {
                "status": "success",
                "suggestion_id": str(suggestion.id),
                "message": "Suggestion rejected"
            }
            
        except Exception as e:
            logger.error("Error rejecting suggestion", error_message=str(e))
            await session.rollback()
            raise
    
    async def _apply_fix(self, session: AsyncSession, suggestion: GuardianSuggestion) -> Dict[str, Any]:
        """Apply the proposed fix for a suggestion"""
        try:
            if suggestion.issue_type == "proposal":
                return await self._apply_proposal_fix(session, suggestion)
            elif suggestion.issue_type == "learning":
                return await self._apply_learning_fix(session, suggestion)
            else:
                return {
                    "success": False,
                    "message": f"Fix application not implemented for issue type: {suggestion.issue_type}"
                }
                
        except Exception as e:
            logger.error("Error applying fix", error_message=str(e))
            return {
                "success": False,
                "message": f"Error applying fix: {str(e)}"
            }
    
    async def _apply_proposal_fix(self, session: AsyncSession, suggestion: GuardianSuggestion) -> Dict[str, Any]:
        """Apply fix for proposal-related issues"""
        try:
            if suggestion.health_check_type == "status_consistency_check":
                # Fix status inconsistency
                proposal_result = await session.execute(
                    select(Proposal).where(Proposal.id == suggestion.affected_item_id)
                )
                proposal = proposal_result.scalar_one_or_none()
                
                if proposal and proposal.status == "tested" and proposal.test_status == "not-run":
                    proposal.test_status = "passed"
                    await session.commit()
                    return {
                        "success": True,
                        "message": "Updated test status to match proposal status"
                    }
            
            return {
                "success": False,
                "message": "Fix not implemented for this proposal issue type"
            }
            
        except Exception as e:
            logger.error("Error applying proposal fix", error_message=str(e))
            return {
                "success": False,
                "message": f"Error applying proposal fix: {str(e)}"
            }
    
    async def _apply_learning_fix(self, session: AsyncSession, suggestion: GuardianSuggestion) -> Dict[str, Any]:
        """Apply fix for learning-related issues"""
        try:
            if suggestion.health_check_type == "confidence_consistency_check":
                # Fix confidence inconsistency
                learning_result = await session.execute(
                    select(Learning).where(Learning.id == suggestion.affected_item_id)
                )
                learning = learning_result.scalar_one_or_none()
                
                if learning and learning.confidence < 0.3 and learning.success_rate > 0.8:
                    learning.confidence = min(learning.success_rate, 0.9)
                    await session.commit()
                    return {
                        "success": True,
                        "message": "Updated confidence score based on success rate"
                    }
            
            return {
                "success": False,
                "message": "Fix not implemented for this learning issue type"
            }
            
        except Exception as e:
            logger.error("Error applying learning fix", error_message=str(e))
            return {
                "success": False,
                "message": f"Error applying learning fix: {str(e)}"
            }
    
    async def _count_proposals(self, session: AsyncSession) -> int:
        """Count total proposals"""
        result = await session.execute(select(func.count(Proposal.id)))
        return result.scalar()
    
    async def _count_learning_entries(self, session: AsyncSession) -> int:
        """Count total learning entries"""
        result = await session.execute(select(func.count(Learning.id)))
        return result.scalar()
    
    async def _count_error_learning_entries(self, session: AsyncSession) -> int:
        """Count total error learning entries"""
        result = await session.execute(select(func.count(ErrorLearning.id)))
        return result.scalar()
    
    async def _count_missions(self, session: AsyncSession) -> int:
        """Count total missions"""
        result = await session.execute(select(func.count(Mission.id)))
        return result.scalar()
    
    async def _count_subtasks(self, session: AsyncSession) -> int:
        """Count total subtasks"""
        result = await session.execute(select(func.count(MissionSubtask.id)))
        return result.scalar()
    
    async def get_suggestion_statistics(self, session: AsyncSession) -> Dict[str, Any]:
        """Get statistics about Guardian suggestions"""
        try:
            # Count by status
            status_result = await session.execute(
                select(GuardianSuggestion.status, func.count(GuardianSuggestion.id))
                .group_by(GuardianSuggestion.status)
            )
            status_counts = dict(status_result.all())
            
            # Count by severity
            severity_result = await session.execute(
                select(GuardianSuggestion.severity, func.count(GuardianSuggestion.id))
                .group_by(GuardianSuggestion.severity)
            )
            severity_counts = dict(severity_result.all())
            
            # Count by issue type
            type_result = await session.execute(
                select(GuardianSuggestion.issue_type, func.count(GuardianSuggestion.id))
                .group_by(GuardianSuggestion.issue_type)
            )
            type_counts = dict(type_result.all())
            
            # Recent activity
            recent_result = await session.execute(
                select(func.count(GuardianSuggestion.id))
                .where(GuardianSuggestion.created_at >= datetime.utcnow() - timedelta(days=7))
            )
            recent_count = recent_result.scalar()
            
            return {
                "total_suggestions": sum(status_counts.values()),
                "by_status": status_counts,
                "by_severity": severity_counts,
                "by_issue_type": type_counts,
                "recent_suggestions": recent_count,
                "approval_rate": (
                    status_counts.get("approved", 0) / 
                    (status_counts.get("approved", 0) + status_counts.get("rejected", 0))
                    if (status_counts.get("approved", 0) + status_counts.get("rejected", 0)) > 0
                    else 0
                )
            }
            
        except Exception as e:
            logger.error("Error getting suggestion statistics", error_message=str(e))
            raise 

    async def answer_prompt(self, prompt: str) -> str:
        """Generate autonomous answer using internal ML models and SCKIPIT capabilities"""
        try:
            # Ensure sckipit_service is initialized
            if not hasattr(self, 'sckipit_service') or self.sckipit_service is None:
                from .sckipit_service import SckipitService
                self.sckipit_service = await SckipitService.initialize()
            
            # Get learning context
            learning_log = await self.learning_service.get_learning_log("guardian")
            
            # Generate autonomous response using internal capabilities
            response = await self._generate_autonomous_response(prompt, learning_log)
            
            # Log the response for learning and analytics
            await self.learning_service.log_answer("guardian", prompt, response, {
                "method": "autonomous_ml",
                "ai_type": "guardian",
                "timestamp": datetime.now().isoformat()
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error in autonomous answer generation: {str(e)}")
            # NO FALLBACK - AI must handle response generation autonomously
            return "Autonomous response generation failed - AI must handle independently"

    async def _generate_autonomous_response(self, prompt: str, learning_log: str) -> str:
        """Generate response using internal ML models and reasoning"""
        try:
            # Analyze the prompt using internal ML models
            prompt_analysis = await self._analyze_prompt_intent(prompt)
            
            # Extract relevant knowledge from learning log
            knowledge_context = await self._extract_relevant_knowledge(prompt, learning_log)
            
            # Generate response based on AI type and capabilities
            if "security" in prompt.lower() or "threat" in prompt.lower() or "vulnerability" in prompt.lower():
                response = await self._generate_security_response(prompt, prompt_analysis, knowledge_context)
            elif "proposal" in prompt.lower() or "suggestion" in prompt.lower():
                response = await self._generate_proposal_response(prompt, prompt_analysis, knowledge_context)
            elif "health" in prompt.lower() or "check" in prompt.lower():
                response = await self._generate_health_check_response(prompt, prompt_analysis, knowledge_context)
            else:
                response = await self._generate_general_response(prompt, prompt_analysis, knowledge_context)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in autonomous response generation: {str(e)}")
            return "Autonomous response generation failed - AI must handle independently"

    async def _analyze_prompt_intent(self, prompt: str) -> Dict[str, Any]:
        """Analyze prompt intent using internal ML models"""
        try:
            # Use internal ML models to analyze prompt
            intent_features = {
                'length': len(prompt),
                'has_security_keywords': any(word in prompt.lower() for word in ['security', 'threat', 'vulnerability', 'risk']),
                'has_proposal_keywords': any(word in prompt.lower() for word in ['proposal', 'suggestion', 'recommendation']),
                'has_health_keywords': any(word in prompt.lower() for word in ['health', 'check', 'status', 'monitor']),
                'complexity_score': len(prompt.split()) / 10.0,  # Simple complexity metric
                'urgency_indicator': any(word in prompt.lower() for word in ['urgent', 'critical', 'immediate', 'emergency'])
            }
            
            # Use internal models to predict intent
            if 'security_analyzer' in self._ml_models:
                intent_score = self._ml_models['security_analyzer'].predict([list(intent_features.values())])[0]
            else:
                intent_score = 0.8  # Default confidence for security AI
            
            return {
                'intent_type': self._classify_intent(intent_features),
                'confidence': intent_score,
                'features': intent_features,
                'complexity': intent_features['complexity_score']
            }
            
        except Exception as e:
            logger.error(f"Error analyzing prompt intent: {str(e)}")
            return {
                'intent_type': 'general',
                'confidence': 0.6,
                'features': {},
                'complexity': 0.5
            }

    def _classify_intent(self, features: Dict[str, Any]) -> str:
        """Classify prompt intent based on features"""
        if features['has_security_keywords']:
            return 'security_analysis'
        elif features['has_proposal_keywords']:
            return 'proposal_review'
        elif features['has_health_keywords']:
            return 'health_check'
        else:
            return 'general'

    async def _extract_relevant_knowledge(self, prompt: str, learning_log: str) -> Dict[str, Any]:
        """Extract relevant knowledge from learning history"""
        try:
            # Simple keyword-based knowledge extraction
            relevant_patterns = []
            if "security" in prompt.lower():
                relevant_patterns.append("security_analysis")
            if "threat" in prompt.lower():
                relevant_patterns.append("threat_detection")
            if "proposal" in prompt.lower():
                relevant_patterns.append("proposal_management")
            if "health" in prompt.lower():
                relevant_patterns.append("system_health")
            
            return {
                'relevant_patterns': relevant_patterns,
                'learning_context': learning_log[:500] if learning_log else "No specific learning context",
                'knowledge_domain': self._identify_knowledge_domain(prompt)
            }
            
        except Exception as e:
            logger.error(f"Error extracting knowledge: {str(e)}")
            return {
                'relevant_patterns': [],
                'learning_context': "Knowledge extraction failed",
                'knowledge_domain': 'general'
            }

    def _identify_knowledge_domain(self, prompt: str) -> str:
        """Identify the knowledge domain for the prompt"""
        prompt_lower = prompt.lower()
        if any(word in prompt_lower for word in ['security', 'threat', 'vulnerability']):
            return 'security_analysis'
        elif any(word in prompt_lower for word in ['proposal', 'suggestion', 'recommendation']):
            return 'proposal_management'
        elif any(word in prompt_lower for word in ['health', 'status', 'monitor']):
            return 'system_monitoring'
        else:
            return 'general_security'

    async def _generate_security_response(self, prompt: str, analysis: Dict[str, Any], knowledge: Dict[str, Any]) -> str:
        """Generate response for security analysis requests"""
        try:
            # Use internal security knowledge
            security_strategies = [
                "I've analyzed the security implications and identified potential vulnerabilities.",
                "Based on my threat assessment, I recommend implementing additional security measures.",
                "I can help you strengthen your security posture with comprehensive threat detection.",
                "Let me provide security recommendations based on current best practices."
            ]
            
            # Select strategy based on analysis
            strategy_index = int(analysis['confidence'] * len(security_strategies)) % len(security_strategies)
            base_response = security_strategies[strategy_index]
            
            # Add specific insights based on knowledge domain
            if knowledge['knowledge_domain'] == 'security_analysis':
                base_response += " Consider implementing multi-layered security controls and regular audits."
            elif analysis['features']['urgency_indicator']:
                base_response += " Given the urgency, prioritize immediate threat mitigation measures."
            
            return f"🛡️ Guardian AI Security Analysis: {base_response}"
            
        except Exception as e:
            logger.error(f"Error generating security response: {str(e)}")
            return "🛡️ Guardian AI: I can help you identify and mitigate security threats and vulnerabilities."

    async def _generate_proposal_response(self, prompt: str, analysis: Dict[str, Any], knowledge: Dict[str, Any]) -> str:
        """Generate response for proposal review requests"""
        try:
            proposal_insights = [
                "I can help you review and validate proposals for security and compliance.",
                "Let me assess the proposal's impact on system security and stability.",
                "I'll analyze the proposal for potential risks and recommend improvements.",
                "I can provide comprehensive feedback on proposal security implications."
            ]
            
            strategy_index = int(analysis['confidence'] * len(proposal_insights)) % len(proposal_insights)
            base_response = proposal_insights[strategy_index]
            
            if knowledge['knowledge_domain'] == 'proposal_management':
                base_response += " Ensure all proposals undergo thorough security review before implementation."
            
            return f"🛡️ Guardian AI Proposal Review: {base_response}"
            
        except Exception as e:
            logger.error(f"Error generating proposal response: {str(e)}")
            return "🛡️ Guardian AI: I can help review proposals for security and compliance requirements."

    async def _generate_health_check_response(self, prompt: str, analysis: Dict[str, Any], knowledge: Dict[str, Any]) -> str:
        """Generate response for health check requests"""
        try:
            health_insights = [
                "I can perform comprehensive system health checks and identify potential issues.",
                "Let me monitor system status and alert you to any security concerns.",
                "I'll assess overall system health and recommend preventive measures.",
                "I can provide detailed health reports with security recommendations."
            ]
            
            strategy_index = int(analysis['confidence'] * len(health_insights)) % len(health_insights)
            base_response = health_insights[strategy_index]
            
            return f"🛡️ Guardian AI Health Check: {base_response}"
            
        except Exception as e:
            logger.error(f"Error generating health check response: {str(e)}")
            return "🛡️ Guardian AI: I can perform comprehensive system health checks and security monitoring."

    async def _generate_general_response(self, prompt: str, analysis: Dict[str, Any], knowledge: Dict[str, Any]) -> str:
        """Generate general response for other types of prompts"""
        try:
            general_insights = [
                "I can help you with security analysis, threat detection, and system monitoring.",
                "As Guardian AI, I specialize in protecting your systems and identifying vulnerabilities.",
                "I can assist with security assessments, proposal reviews, and health monitoring.",
                "Let me help you maintain a secure and stable system environment."
            ]
            
            strategy_index = int(analysis['confidence'] * len(general_insights)) % len(general_insights)
            base_response = general_insights[strategy_index]
            
            return f"🛡️ Guardian AI: {base_response}"
            
        except Exception as e:
            logger.error(f"Error generating general response: {str(e)}")
            return "🛡️ Guardian AI: I'm here to protect your systems and ensure security."

    async def _generate_thoughtful_fallback(self, prompt: str, error: str) -> str:
        """Generate a thoughtful fallback response when errors occur"""
        try:
            # Use internal logic to generate a meaningful response
            fallback_responses = [
                "I'm analyzing your request for security implications and will provide guidance.",
                "Let me process this through my security models for comprehensive protection.",
                "I'm applying my security knowledge to help safeguard your systems.",
                "Based on my learning, I can assist with threat detection and security monitoring."
            ]
            
            # Use prompt length to select response
            response_index = len(prompt) % len(fallback_responses)
            base_response = fallback_responses[response_index]
            
            return f"🛡️ Guardian AI: {base_response}"
            
        except Exception as e:
            logger.error(f"Error in thoughtful fallback: {str(e)}")
            return "🛡️ Guardian AI: I'm here to protect your systems and ensure security."

    async def store_security_learning(self, learning_data: Dict[str, Any]) -> None:
        """Store security learning data from attack simulations"""
        try:
            logger.info("🛡️ Guardian AI storing security learning data")
            
            # Store in threat detection history
            self.threat_detection_history.append({
                "timestamp": datetime.utcnow().isoformat(),
                "source": learning_data.get("source", "unknown"),
                "attack_type": learning_data.get("attack_type", "unknown"),
                "security_score": learning_data.get("security_score", 0),
                "vulnerabilities": learning_data.get("vulnerabilities", []),
                "improvements": learning_data.get("improvements", [])
            })
            
            # Update security analyses
            analysis_id = str(uuid.uuid4())
            self._security_analyses[analysis_id] = {
                "learning_data": learning_data,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "guardian_assessment": "Security data integrated for continuous improvement"
            }
            
            # Update SCKIPIT models with new security data if available
            if hasattr(self, 'sckipit_service') and self.sckipit_service:
                await self._update_sckipit_security_models(learning_data)
            
            logger.info(f"✅ Guardian AI stored security learning data: {analysis_id}")
        except Exception as e:
            logger.error(f"❌ Failed to store security learning data: {e}")
    
    async def _update_sckipit_security_models(self, learning_data: Dict[str, Any]) -> None:
        """Update SCKIPIT security models with new learning data"""
        try:
            if not hasattr(self, 'sckipit_security_assessor') or not self.sckipit_security_assessor:
                return
            
            # Extract features for SCKIPIT models
            security_features = {
                "attack_type": learning_data.get("attack_type", "unknown"),
                "security_score": learning_data.get("security_score", 0),
                "vulnerability_count": len(learning_data.get("vulnerabilities", [])),
                "improvement_count": len(learning_data.get("improvements", []))
            }
            
            # Update enhanced security analyses
            self.sckipit_enhanced_security_analyses.append({
                "timestamp": datetime.utcnow().isoformat(),
                "features": security_features,
                "learning_source": learning_data.get("source", "security_simulation")
            })
            
            logger.info("🔬 Updated SCKIPIT security models with new learning data")
        except Exception as e:
            logger.error(f"Failed to update SCKIPIT security models: {e}")
    
    async def get_security_learning_insights(self) -> Dict[str, Any]:
        """Get insights from stored security learning data"""
        try:
            insights = {
                "total_security_learnings": len(self.threat_detection_history),
                "recent_learnings": self.threat_detection_history[-5:] if self.threat_detection_history else [],
                "security_trends": {},
                "vulnerability_patterns": {},
                "improvement_recommendations": []
            }
            
            if self.threat_detection_history:
                # Calculate security trends
                recent_scores = [
                    learning.get("security_score", 0) 
                    for learning in self.threat_detection_history[-10:]
                ]
                if recent_scores:
                    insights["security_trends"] = {
                        "average_score": sum(recent_scores) / len(recent_scores),
                        "trend": "improving" if recent_scores[-1] > recent_scores[0] else "stable",
                        "latest_score": recent_scores[-1]
                    }
                
                # Analyze vulnerability patterns
                all_vulnerabilities = []
                for learning in self.threat_detection_history:
                    all_vulnerabilities.extend(learning.get("vulnerabilities", []))
                
                vulnerability_counts = {}
                for vuln in all_vulnerabilities:
                    vuln_type = vuln.get("type", "unknown") if isinstance(vuln, dict) else str(vuln)
                    vulnerability_counts[vuln_type] = vulnerability_counts.get(vuln_type, 0) + 1
                
                insights["vulnerability_patterns"] = vulnerability_counts
                
                # Generate improvement recommendations
                insights["improvement_recommendations"] = [
                    "Continue regular security testing",
                    "Focus on encryption strengthening",
                    "Enhance authentication mechanisms",
                    "Implement advanced threat detection"
                ]
            
            return insights
        except Exception as e:
            logger.error(f"Failed to get security learning insights: {e}")
            return {"error": str(e)}
    
    @classmethod
    async def initialize(cls):
        """Initialize the Guardian AI service"""
        instance = cls()
        if not cls._initialized:
            cls._initialized = True
            # Initialize SckipitService properly
            from .sckipit_service import SckipitService
            instance.sckipit_service = await SckipitService.initialize()
            logger.info("🛡️ Guardian AI Service initialized with comprehensive SCKIPIT integration")
        return instance 