"""
Enhanced Proposal Description Service

This service generates detailed, user-friendly descriptions for proposals that explain:
1. What the AI has learned from previous interactions
2. What type of changes it's making (frontend/backend/etc.)
3. The scope and impact of the changes
4. Risk assessment and expected outcomes
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import structlog
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.sql_models import Proposal, Learning, ErrorLearning
from ..core.database import get_session

logger = structlog.get_logger()


class EnhancedProposalDescriptionService:
    """Service for generating enhanced proposal descriptions"""
    
    def __init__(self):
        self.file_type_patterns = {
            'frontend': [
                r'\.dart$', r'\.js$', r'\.jsx$', r'\.ts$', r'\.tsx$', r'\.vue$', 
                r'\.html$', r'\.css$', r'\.scss$', r'\.sass$', r'\.less$',
                r'lib/', r'frontend/', r'ui/', r'components/', r'screens/'
            ],
            'backend': [
                r'\.py$', r'\.java$', r'\.go$', r'\.rb$', r'\.php$', r'\.cs$',
                r'app/', r'backend/', r'services/', r'controllers/', r'api/'
            ],
            'database': [
                r'\.sql$', r'\.db$', r'migrations/', r'schema/', r'models/'
            ],
            'config': [
                r'\.json$', r'\.yaml$', r'\.yml$', r'\.toml$', r'\.ini$',
                r'config/', r'settings/', r'\.env'
            ],
            'other': [
                r'\.md$', r'\.txt$', r'\.log$', r'docs/', r'tests/'
            ]
        }
        
        self.improvement_type_descriptions = {
            'performance': 'performance optimization',
            'security': 'security enhancement',
            'readability': 'code readability improvement',
            'bug-fix': 'bug fix',
            'refactor': 'code refactoring',
            'feature': 'new feature addition',
            'system': 'system-level improvement',
            'general': 'general improvement'
        }
        
        self.change_scope_descriptions = {
            'minor': 'minor change with minimal impact',
            'moderate': 'moderate change affecting specific functionality',
            'major': 'major change affecting multiple components',
            'critical': 'critical change affecting system stability'
        }
    
    async def generate_enhanced_description(self, proposal_data: Dict) -> Dict[str, str]:
        """
        Generate enhanced description for a proposal
        
        Returns:
            Dict containing enhanced description fields
        """
        try:
            file_path = proposal_data.get('file_path', '')
            ai_type = proposal_data.get('ai_type', '')
            improvement_type = proposal_data.get('improvement_type', 'general')
            code_before = proposal_data.get('code_before', '')
            code_after = proposal_data.get('code_after', '')
            
            # Determine change type based on file path
            change_type = self._determine_change_type(file_path)
            
            # Determine change scope based on code analysis
            change_scope = self._determine_change_scope(code_before, code_after)
            
            # Generate AI learning summary
            ai_learning_summary = await self._generate_ai_learning_summary(ai_type)
            
            # Generate expected impact
            expected_impact = self._generate_expected_impact(improvement_type, change_type, change_scope)
            
            # Generate risk assessment
            risk_assessment = self._generate_risk_assessment(change_type, change_scope, ai_type)
            
            # Generate affected components
            affected_components = self._determine_affected_components(file_path, change_type)
            
            # Generate learning sources
            learning_sources = await self._get_learning_sources(ai_type)
            
            # Generate enhanced description
            enhanced_description = self._generate_enhanced_description_text(
                ai_type, file_path, improvement_type, change_type, change_scope,
                ai_learning_summary, expected_impact, risk_assessment
            )
            
            return {
                'ai_learning_summary': ai_learning_summary,
                'change_type': change_type,
                'change_scope': change_scope,
                'affected_components': affected_components,
                'learning_sources': learning_sources,
                'expected_impact': expected_impact,
                'risk_assessment': risk_assessment,
                'enhanced_description': enhanced_description
            }
            
        except Exception as e:
            logger.error("Error generating enhanced description", error=str(e))
            return {
                'ai_learning_summary': 'Unable to generate learning summary',
                'change_type': 'unknown',
                'change_scope': 'unknown',
                'affected_components': [],
                'learning_sources': [],
                'expected_impact': 'Unable to determine impact',
                'risk_assessment': 'Unable to assess risk',
                'enhanced_description': 'Enhanced description unavailable'
            }
    
    def _determine_change_type(self, file_path: str) -> str:
        """Determine the type of change based on file path"""
        file_path_lower = file_path.lower()
        
        for change_type, patterns in self.file_type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, file_path_lower):
                    return change_type
        
        return 'other'
    
    def _determine_change_scope(self, code_before: str, code_after: str) -> str:
        """Determine the scope of change based on code analysis"""
        before_lines = len(code_before.split('\n'))
        after_lines = len(code_after.split('\n'))
        line_diff = abs(after_lines - before_lines)
        
        # Simple heuristic based on line count changes
        if line_diff <= 5:
            return 'minor'
        elif line_diff <= 20:
            return 'moderate'
        elif line_diff <= 50:
            return 'major'
        else:
            return 'critical'
    
    async def _generate_ai_learning_summary(self, ai_type: str) -> str:
        """Generate a summary of what the AI has learned"""
        try:
            async with get_session() as session:
                # Get recent learning events for this AI type
                recent_learning = await session.execute(
                    select(Learning)
                    .where(Learning.ai_type == ai_type)
                    .where(Learning.created_at >= datetime.utcnow() - timedelta(days=30))
                    .order_by(Learning.created_at.desc())
                    .limit(5)
                )
                learning_events = recent_learning.scalars().all()
                
                # Get recent error learning
                recent_errors = await session.execute(
                    select(ErrorLearning)
                    .where(ErrorLearning.ai_type == ai_type)
                    .where(ErrorLearning.created_at >= datetime.utcnow() - timedelta(days=30))
                    .order_by(ErrorLearning.created_at.desc())
                    .limit(3)
                )
                error_events = recent_errors.scalars().all()
                
                # Get proposal success rate
                total_proposals = await session.execute(
                    select(func.count(Proposal.id))
                    .where(Proposal.ai_type == ai_type)
                    .where(Proposal.created_at >= datetime.utcnow() - timedelta(days=30))
                )
                total_count = total_proposals.scalar() or 0
                
                successful_proposals = await session.execute(
                    select(func.count(Proposal.id))
                    .where(Proposal.ai_type == ai_type)
                    .where(Proposal.status.in_(['applied', 'accepted']))
                    .where(Proposal.created_at >= datetime.utcnow() - timedelta(days=30))
                )
                success_count = successful_proposals.scalar() or 0
                
                success_rate = (success_count / total_count * 100) if total_count > 0 else 0
                
                # Generate learning summary
                summary_parts = []
                
                if learning_events:
                    summary_parts.append(f"Based on {len(learning_events)} recent learning events")
                
                if error_events:
                    summary_parts.append(f"and {len(error_events)} error patterns identified")
                
                if total_count > 0:
                    summary_parts.append(f"with a {success_rate:.1f}% success rate in the last 30 days")
                
                if summary_parts:
                    return f"The {ai_type} AI has " + ", ".join(summary_parts) + "."
                else:
                    return f"The {ai_type} AI is applying general best practices and patterns."
                    
        except Exception as e:
            logger.error("Error generating AI learning summary", error=str(e))
            return f"The {ai_type} AI is applying learned patterns and best practices."
    
    def _generate_expected_impact(self, improvement_type: str, change_type: str, change_scope: str) -> str:
        """Generate expected impact description"""
        improvement_desc = self.improvement_type_descriptions.get(improvement_type, improvement_type)
        scope_desc = self.change_scope_descriptions.get(change_scope, change_scope)
        
        impact_templates = {
            'frontend': {
                'performance': 'Improve user interface responsiveness and reduce loading times',
                'security': 'Enhance client-side security and input validation',
                'readability': 'Improve code maintainability and developer experience',
                'bug-fix': 'Fix user-facing issues and improve user experience',
                'refactor': 'Improve code structure and maintainability',
                'feature': 'Add new user-facing functionality',
                'system': 'Improve overall frontend system architecture',
                'general': 'Enhance frontend functionality and user experience'
            },
            'backend': {
                'performance': 'Improve server response times and resource efficiency',
                'security': 'Enhance server-side security and data protection',
                'readability': 'Improve code maintainability and debugging',
                'bug-fix': 'Fix server-side issues and improve reliability',
                'refactor': 'Improve code structure and system architecture',
                'feature': 'Add new server-side functionality',
                'system': 'Improve overall backend system performance',
                'general': 'Enhance backend functionality and system reliability'
            },
            'database': {
                'performance': 'Optimize database queries and improve data access speed',
                'security': 'Enhance data security and access controls',
                'readability': 'Improve database schema clarity and documentation',
                'bug-fix': 'Fix data integrity issues and improve reliability',
                'refactor': 'Improve database structure and relationships',
                'feature': 'Add new data storage capabilities',
                'system': 'Improve overall database system performance',
                'general': 'Enhance database functionality and data management'
            },
            'config': {
                'performance': 'Optimize system configuration for better performance',
                'security': 'Enhance security configuration and access controls',
                'readability': 'Improve configuration clarity and documentation',
                'bug-fix': 'Fix configuration issues and improve system stability',
                'refactor': 'Improve configuration structure and organization',
                'feature': 'Add new configuration options',
                'system': 'Improve overall system configuration management',
                'general': 'Enhance system configuration and management'
            }
        }
        
        impact = impact_templates.get(change_type, {}).get(improvement_type, f"Improve {improvement_desc}")
        return f"{impact}. This is a {scope_desc}."
    
    def _generate_risk_assessment(self, change_type: str, change_scope: str, ai_type: str) -> str:
        """Generate risk assessment"""
        risk_levels = {
            'minor': 'Low risk - minimal impact on system stability',
            'moderate': 'Medium risk - may affect specific functionality',
            'major': 'High risk - affects multiple components',
            'critical': 'Critical risk - may impact system stability'
        }
        
        risk_level = risk_levels.get(change_scope, 'Unknown risk level')
        
        # Add AI-specific risk considerations
        ai_risk_factors = {
            'Imperium': 'Imperium AI focuses on system stability and performance',
            'Guardian': 'Guardian AI prioritizes security and error prevention',
            'Sandbox': 'Sandbox AI experiments with new approaches',
            'Conquest': 'Conquest AI optimizes for user experience'
        }
        
        ai_factor = ai_risk_factors.get(ai_type, 'AI applies standard safety measures')
        
        return f"{risk_level}. {ai_factor}."
    
    def _determine_affected_components(self, file_path: str, change_type: str) -> List[str]:
        """Determine which components are affected by this change"""
        components = []
        
        # Extract component name from file path
        file_name = file_path.split('/')[-1] if '/' in file_path else file_path
        base_name = file_name.split('.')[0] if '.' in file_name else file_name
        
        components.append(base_name)
        
        # Add change type specific components
        if change_type == 'frontend':
            components.extend(['User Interface', 'Client-side Logic'])
        elif change_type == 'backend':
            components.extend(['Server Logic', 'API Endpoints'])
        elif change_type == 'database':
            components.extend(['Data Storage', 'Data Access Layer'])
        elif change_type == 'config':
            components.extend(['System Configuration', 'Environment Settings'])
        
        return list(set(components))  # Remove duplicates
    
    async def _get_learning_sources(self, ai_type: str) -> List[str]:
        """Get sources of learning for this AI type"""
        try:
            async with get_session() as session:
                # Get recent learning events
                recent_learning = await session.execute(
                    select(Learning.learning_type)
                    .where(Learning.ai_type == ai_type)
                    .where(Learning.created_at >= datetime.utcnow() - timedelta(days=7))
                    .distinct()
                )
                learning_types = recent_learning.scalars().all()
                
                sources = []
                for learning_type in learning_types:
                    if learning_type == 'proposal_feedback':
                        sources.append('Previous proposal feedback')
                    elif learning_type == 'user_feedback':
                        sources.append('User feedback and preferences')
                    elif learning_type == 'system_analysis':
                        sources.append('System performance analysis')
                
                if not sources:
                    sources.append('General best practices')
                
                return sources
                
        except Exception as e:
            logger.error("Error getting learning sources", error=str(e))
            return ['General best practices']
    
    def _generate_enhanced_description_text(self, ai_type: str, file_path: str, 
                                          improvement_type: str, change_type: str, 
                                          change_scope: str, ai_learning_summary: str,
                                          expected_impact: str, risk_assessment: str) -> str:
        """Generate the full enhanced description text"""
        
        file_name = file_path.split('/')[-1] if '/' in file_path else file_path
        improvement_desc = self.improvement_type_descriptions.get(improvement_type, improvement_type)
        
        description = f"""
The {ai_type} AI has analyzed the codebase and identified an opportunity for {improvement_desc}.

**What the AI has learned:**
{ai_learning_summary}

**Change Details:**
- **File:** {file_name}
- **Type:** {change_type.title()} change
- **Scope:** {change_scope.title()} impact
- **Category:** {improvement_type.replace('-', ' ').title()}

**Expected Impact:**
{expected_impact}

**Risk Assessment:**
{risk_assessment}

**What this change accomplishes:**
This {change_type} modification will {improvement_desc.lower()} in the {file_name} file, 
contributing to overall system improvement and better user experience.

The AI has confidence in this proposal based on learned patterns and best practices.
        """.strip()
        
        return description 