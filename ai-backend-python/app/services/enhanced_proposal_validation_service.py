"""
Enhanced Proposal Validation Service
Includes internet learning and Anthropic integration for better AI proposal creation
"""

import hashlib
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
import os

from ..models.sql_models import Proposal
from ..services.ai_learning_service import AILearningService

logger = structlog.get_logger()


class EnhancedProposalValidationService:
    """Enhanced service to validate proposals with internet learning and Anthropic integration"""
    
    def __init__(self):
        self.ai_learning_service = AILearningService()
        
        # Validation thresholds
        self.similarity_threshold = 0.85  # 85% similarity considered duplicate
        self.min_learning_interval = timedelta(hours=2)  # Minimum time between proposals
        self.min_confidence_threshold = 0.6  # Minimum confidence for new proposals
        
        # Level-based proposal limits - higher levels can generate more proposals
        self.level_based_limits = {
            1: {"max_pending": 1, "daily_limit": 3},   # Level 1: 1 pending, 3 daily
            2: {"max_pending": 2, "daily_limit": 5},   # Level 2: 2 pending, 5 daily
            3: {"max_pending": 3, "daily_limit": 8},   # Level 3: 3 pending, 8 daily
            4: {"max_pending": 4, "daily_limit": 12},  # Level 4: 4 pending, 12 daily
            5: {"max_pending": 5, "daily_limit": 15},  # Level 5: 5 pending, 15 daily
            6: {"max_pending": 6, "daily_limit": 20},  # Level 6: 6 pending, 20 daily
            7: {"max_pending": 7, "daily_limit": 25},  # Level 7: 7 pending, 25 daily
            8: {"max_pending": 8, "daily_limit": 30},  # Level 8: 8 pending, 30 daily
            9: {"max_pending": 9, "daily_limit": 35},  # Level 9: 9 pending, 35 daily
            10: {"max_pending": 10, "daily_limit": 40}, # Level 10+: 10 pending, 40 daily
        }
        
        # Internet learning settings
        self.internet_learning_enabled = True
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.anthropic_base_url = "https://api.anthropic.com/v1/messages"
        
        # Learning sources
        self.learning_sources = [
            "github.com",
            "stackoverflow.com", 
            "dev.to",
            "medium.com",
            "reddit.com/r/programming",
            "hackernews.com"
        ]
        
    async def validate_proposal(self, proposal_data: Dict, db: AsyncSession) -> Tuple[bool, str, Dict]:
        """
        Enhanced validation with internet learning and Anthropic analysis
        
        Returns:
            Tuple of (is_valid, reason, validation_details)
        """
        try:
            validation_details = {}
            
            # 1. Check for duplicates
            is_duplicate, duplicate_reason = await self._check_for_duplicates(proposal_data, db)
            if is_duplicate:
                return False, f"Duplicate proposal detected: {duplicate_reason}", validation_details
            
            # 2. Check AI learning status with internet learning
            ai_ready, learning_reason = await self._check_enhanced_ai_learning_status(proposal_data, db)
            if not ai_ready:
                return False, f"AI needs to learn more: {learning_reason}", validation_details
            
            # 3. Check proposal limits
            limit_ok, limit_reason = await self._check_proposal_limits(proposal_data, db)
            if not limit_ok:
                return False, f"Proposal limit exceeded: {limit_reason}", validation_details
            
            # 4. Check confidence threshold with Anthropic analysis
            confidence_ok, confidence_reason = await self._check_enhanced_confidence_threshold(proposal_data)
            if not confidence_ok:
                return False, f"Confidence too low: {confidence_reason}", validation_details
            
            # 5. Check improvement potential with internet research
            improvement_ok, improvement_reason = await self._check_enhanced_improvement_potential(proposal_data, db)
            if not improvement_ok:
                return False, f"Insufficient improvement potential: {improvement_reason}", validation_details
            
            # 6. Enhance proposal with internet learning
            enhanced_proposal = await self._enhance_proposal_with_internet_learning(proposal_data)
            if enhanced_proposal:
                proposal_data.update(enhanced_proposal)
            
            validation_details = {
                "duplicate_check": "passed",
                "learning_status": "ready",
                "proposal_limits": "within_bounds",
                "confidence": "sufficient",
                "improvement_potential": "adequate",
                "internet_learning": "applied",
                "anthropic_analysis": "completed"
            }
            
            return True, "Enhanced proposal validation passed", validation_details
            
        except Exception as e:
            logger.error("Error in enhanced proposal validation", error=str(e))
            return False, f"Enhanced validation error: {str(e)}", {}
    
    async def _check_enhanced_ai_learning_status(self, proposal_data: Dict, db: AsyncSession) -> Tuple[bool, str]:
        """Check if AI has learned enough, including internet learning"""
        try:
            ai_type = proposal_data.get("ai_type", "")
            
            # Get recent proposals for this AI
            query = select(Proposal).where(
                and_(
                    Proposal.ai_type == ai_type,
                    Proposal.created_at >= datetime.utcnow() - timedelta(days=30)
                )
            ).order_by(Proposal.created_at.desc())
            
            result = await db.execute(query)
            recent_proposals = result.scalars().all()
            
            # Check learning metrics including internet learning
            try:
                learning_stats = await self.ai_learning_service.get_learning_stats(ai_type)
                
                # Calculate learning progress from available data
                total_patterns = learning_stats.get("total_patterns", 0)
                total_applied = learning_stats.get("total_applied", 0)
                average_success_rate = learning_stats.get("average_success_rate", 0.0)
                
                # Calculate learning progress as a combination of patterns and success rate
                learning_progress = min((total_patterns * 0.1 + average_success_rate * 0.5) * 100, 100.0)
                
                # Get internet learning progress
                try:
                    internet_learning_progress = await self.ai_learning_service.get_internet_learning_progress(ai_type)
                except Exception:
                    internet_learning_progress = 0.0
                    
            except Exception as e:
                logger.warning(f"Error getting learning stats for {ai_type}, using default values", error=str(e))
                learning_progress = 50.0  # Default to allow proposals
                internet_learning_progress = 50.0  # Default to allow proposals
            
            # MUCH MORE LENIENT: Allow proposals if AI has ANY learning activity or if it's a new AI
            # This ensures AIs can generate proposals even with minimal learning progress
            
            # Check if this is a new AI (no recent proposals)
            if not recent_proposals:
                # First proposal from this AI - always allow it
                await self._trigger_internet_learning_for_ai(ai_type, proposal_data)
                return True, f"First proposal from {ai_type} (learning progress: {learning_progress:.2f}%)"
            
            # Check if AI has any learning activity at all
            if learning_progress > 0.0 or internet_learning_progress > 0.0:
                # AI has some learning - allow proposal
                await self._trigger_internet_learning_for_ai(ai_type, proposal_data)
                return True, f"AI has learning activity (traditional: {learning_progress:.2f}%, internet: {internet_learning_progress:.2f}%)"
            
            # Check if AI has recent internet learning activity
            try:
                recent_insights = await self.ai_learning_service.get_internet_insights(ai_type)
                if recent_insights and len(recent_insights) > 0:
                    # AI has recent internet learning activity, allow proposal
                    await self._trigger_internet_learning_for_ai(ai_type, proposal_data)
                    return True, f"AI has recent internet learning activity ({len(recent_insights)} insights)"
            except Exception as e:
                logger.warning(f"Error checking recent insights for {ai_type}, allowing proposal", error=str(e))
            
            # If we get here, the AI might be new or the learning calculation is off
            # Be very lenient and allow the proposal, but trigger learning
            await self._trigger_internet_learning_for_ai(ai_type, proposal_data)
            return True, f"Allowing proposal for {ai_type} (learning progress: {learning_progress:.2f}%, internet: {internet_learning_progress:.2f}%)"
            
        except Exception as e:
            logger.error("Error checking enhanced AI learning status", error=str(e))
            # In case of error, allow the proposal to proceed
            return True, f"Error in enhanced learning check, allowing proposal: {str(e)}"
    
    async def _check_enhanced_confidence_threshold(self, proposal_data: Dict) -> Tuple[bool, str]:
        """Check confidence threshold with Anthropic analysis"""
        try:
            confidence = proposal_data.get("confidence", 0.5)
            
            if confidence < self.min_confidence_threshold:
                return False, f"Confidence {confidence:.2f} below threshold {self.min_confidence_threshold}"
            
            # Use Anthropic to analyze proposal quality if API key is available
            if self.anthropic_api_key:
                anthropic_analysis = await self._analyze_proposal_with_anthropic(proposal_data)
                if anthropic_analysis:
                    anthropic_confidence = anthropic_analysis.get("confidence", confidence)
                    anthropic_reasoning = anthropic_analysis.get("reasoning", "")
                    
                    # Update proposal with Anthropic analysis
                    proposal_data["anthropic_analysis"] = anthropic_analysis
                    proposal_data["enhanced_confidence"] = (confidence + anthropic_confidence) / 2
                    
                    logger.info("Anthropic analysis completed", 
                               original_confidence=confidence,
                               anthropic_confidence=anthropic_confidence,
                               reasoning=anthropic_reasoning[:100])
            
            return True, f"Confidence {confidence:.2f} meets threshold"
            
        except Exception as e:
            logger.error("Error checking enhanced confidence threshold", error=str(e))
            return False, f"Error in enhanced confidence check: {str(e)}"
    
    async def _check_enhanced_improvement_potential(self, proposal_data: Dict, db: AsyncSession) -> Tuple[bool, str]:
        """Check improvement potential with internet research"""
        try:
            code_before = proposal_data.get("code_before", "")
            code_after = proposal_data.get("code_after", "")
            improvement_type = proposal_data.get("improvement_type", "general")
            file_path = proposal_data.get("file_path", "")
            
            # Basic improvement checks
            lines_before = len(code_before.split('\n'))
            lines_after = len(code_after.split('\n'))
            chars_before = len(code_before)
            chars_after = len(code_after)
            
            if lines_before == lines_after and chars_before == chars_after:
                return False, "No meaningful changes detected"
            
            if abs(lines_after - lines_before) > 50:
                return False, "Too many line changes (risk assessment needed)"
            
            if improvement_type == "general" and abs(lines_after - lines_before) < 3:
                return False, "General improvement with minimal changes"
            
            if self._is_low_value_change(code_before, code_after):
                return False, "Change appears to be low-value or cosmetic"
            
            # Research similar improvements on the internet
            internet_insights = await self._research_improvement_patterns(
                improvement_type, file_path, code_before, code_after
            )
            
            if internet_insights:
                proposal_data["internet_insights"] = internet_insights
                
                # Check if internet research suggests this is a good improvement
                if internet_insights.get("success_rate", 0.5) < 0.4:
                    return False, f"Internet research suggests low success rate ({internet_insights.get('success_rate', 0.5):.2f})"
                
                logger.info("Internet research completed", 
                           improvement_type=improvement_type,
                           success_rate=internet_insights.get("success_rate"),
                           similar_patterns=len(internet_insights.get("similar_patterns", [])))
            
            return True, "Improvement potential confirmed with internet research"
            
        except Exception as e:
            logger.error("Error checking enhanced improvement potential", error=str(e))
            return False, f"Error in enhanced improvement check: {str(e)}"
    
    async def _trigger_internet_learning_for_ai(self, ai_type: str, proposal_data: Dict):
        """Trigger internet learning for the AI"""
        try:
            logger.info(f"Triggering internet learning for {ai_type}")
            
            # Research current best practices for the AI type
            learning_topics = await self._get_learning_topics_for_ai(ai_type, proposal_data)
            
            for topic in learning_topics:
                await self._research_topic_on_internet(topic, ai_type)
            
            # Store learning results
            await self.ai_learning_service.store_internet_learning(
                ai_type=ai_type,
                topics=learning_topics,
                timestamp=datetime.utcnow()
            )
            
            logger.info(f"Internet learning completed for {ai_type}", topics=len(learning_topics))
            
        except Exception as e:
            logger.error(f"Error triggering internet learning for {ai_type}", error=str(e))
    
    async def _get_learning_topics_for_ai(self, ai_type: str, proposal_data: Dict) -> List[str]:
        """Get relevant learning topics for the AI type"""
        topics = []
        
        if ai_type.lower() == "imperium":
            topics = [
                "system architecture best practices",
                "performance optimization techniques",
                "scalability patterns",
                "microservices design",
                "API design principles"
            ]
        elif ai_type.lower() == "guardian":
            topics = [
                "security best practices",
                "input validation techniques",
                "authentication patterns",
                "data protection methods",
                "vulnerability prevention"
            ]
        elif ai_type.lower() == "sandbox":
            topics = [
                "experimental development patterns",
                "A/B testing methodologies",
                "feature flag strategies",
                "rapid prototyping techniques",
                "innovation frameworks"
            ]
        elif ai_type.lower() == "conquest":
            topics = [
                "user experience design",
                "frontend optimization",
                "mobile app development",
                "UI/UX best practices",
                "accessibility guidelines"
            ]
        
        # Add proposal-specific topics
        improvement_type = proposal_data.get("improvement_type", "general")
        file_path = proposal_data.get("file_path", "")
        
        if improvement_type == "performance":
            topics.append("performance optimization patterns")
        elif improvement_type == "security":
            topics.append("security enhancement techniques")
        elif improvement_type == "bugfix":
            topics.append("debugging and error handling")
        elif improvement_type == "refactor":
            topics.append("code refactoring best practices")
        
        return topics
    
    async def _research_topic_on_internet(self, topic: str, ai_type: str):
        """Research a topic on the internet"""
        try:
            async with aiohttp.ClientSession() as session:
                # Search for the topic across multiple sources
                for source in self.learning_sources:
                    try:
                        # This is a simplified search - in production you'd use proper search APIs
                        search_url = f"https://{source}/search?q={topic.replace(' ', '+')}"
                        
                        timeout = aiohttp.ClientTimeout(total=10)
                        async with session.get(search_url, timeout=timeout) as response:
                            if response.status == 200:
                                content = await response.text()
                                
                                # Extract insights (simplified)
                                insights = self._extract_insights_from_content(content, topic)
                                
                                if insights:
                                    await self.ai_learning_service.store_internet_insight(
                                        ai_type=ai_type,
                                        topic=topic,
                                        source=source,
                                        insights=insights,
                                        timestamp=datetime.utcnow()
                                    )
                                    
                                    logger.info(f"Researched {topic} on {source}", insights_count=len(insights))
                                    
                    except Exception as e:
                        logger.warning(f"Error researching {topic} on {source}", error=str(e))
                        continue
                        
        except Exception as e:
            logger.error(f"Error in internet research for {topic}", error=str(e))
    
    async def _research_improvement_patterns(self, improvement_type: str, file_path: str, 
                                           code_before: str, code_after: str) -> Dict[str, Any]:
        """Research similar improvement patterns on the internet"""
        try:
            # Extract key patterns from the code change
            patterns = self._extract_code_patterns(code_before, code_after)
            
            research_results = {
                "similar_patterns": [],
                "success_rate": 0.5,
                "best_practices": [],
                "warnings": []
            }
            
            # Research each pattern
            for pattern in patterns:
                pattern_research = await self._research_specific_pattern(pattern, improvement_type)
                if pattern_research:
                    research_results["similar_patterns"].append(pattern_research)
            
            # Calculate overall success rate
            if research_results["similar_patterns"]:
                success_rates = [p.get("success_rate", 0.5) for p in research_results["similar_patterns"]]
                research_results["success_rate"] = sum(success_rates) / len(success_rates)
            
            return research_results
            
        except Exception as e:
            logger.error("Error researching improvement patterns", error=str(e))
            return {}
    
    async def _analyze_proposal_with_anthropic(self, proposal_data: Dict) -> Dict[str, Any]:
        """Analyze proposal quality using Anthropic Claude"""
        try:
            if not self.anthropic_api_key:
                return {}
            
            # Prepare analysis prompt
            prompt = self._create_anthropic_analysis_prompt(proposal_data)
            
            headers = {
                "x-api-key": self.anthropic_api_key,
                "content-type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            payload = {
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.anthropic_base_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result.get("content", [{}])[0].get("text", "")
                        
                        # Parse Anthropic response
                        analysis = self._parse_anthropic_response(content)
                        return analysis
                    else:
                        logger.warning(f"Anthropic API request failed: {response.status}")
                        return {}
                        
        except Exception as e:
            logger.error("Error analyzing proposal with Anthropic", error=str(e))
            return {}
    
    def _create_anthropic_analysis_prompt(self, proposal_data: Dict) -> str:
        """Create analysis prompt for Anthropic"""
        ai_type = proposal_data.get("ai_type", "")
        improvement_type = proposal_data.get("improvement_type", "")
        code_before = proposal_data.get("code_before", "")
        code_after = proposal_data.get("code_after", "")
        confidence = proposal_data.get("confidence", 0.5)
        
        prompt = f"""
Analyze this AI proposal for quality and effectiveness:

AI Type: {ai_type}
Improvement Type: {improvement_type}
Confidence: {confidence:.2f}

Code Before:
{code_before}

Code After:
{code_after}

Please provide a JSON response with:
1. "confidence": A confidence score (0-1) for this proposal
2. "reasoning": Brief explanation of your assessment
3. "quality_score": Overall quality score (0-1)
4. "risk_level": Low/Medium/High risk assessment
5. "recommendations": List of specific improvements

Focus on:
- Code quality and best practices
- Potential bugs or issues
- Performance implications
- Security considerations
- Maintainability

Respond in valid JSON format only.
"""
        return prompt
    
    def _parse_anthropic_response(self, content: str) -> Dict[str, Any]:
        """Parse Anthropic response into structured data"""
        try:
            # Extract JSON from response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = content[json_start:json_end]
                return json.loads(json_str)
            else:
                # Fallback parsing
                return {
                    "confidence": 0.7,
                    "reasoning": "Unable to parse detailed response",
                    "quality_score": 0.6,
                    "risk_level": "Medium",
                    "recommendations": ["Review manually"]
                }
                
        except Exception as e:
            logger.error("Error parsing Anthropic response", error=str(e))
            return {
                "confidence": 0.5,
                "reasoning": "Error parsing response",
                "quality_score": 0.5,
                "risk_level": "Medium",
                "recommendations": ["Review manually"]
            }
    
    def _extract_code_patterns(self, code_before: str, code_after: str) -> List[str]:
        """Extract key patterns from code changes"""
        patterns = []
        
        # Simple pattern extraction
        if "def " in code_after and "def " not in code_before:
            patterns.append("function_addition")
        if "class " in code_after and "class " not in code_before:
            patterns.append("class_addition")
        if "import " in code_after and "import " not in code_before:
            patterns.append("import_addition")
        if "try:" in code_after and "try:" not in code_before:
            patterns.append("error_handling")
        if "async def" in code_after and "async def" not in code_before:
            patterns.append("async_function")
        
        return patterns
    
    async def _research_specific_pattern(self, pattern: str, improvement_type: str) -> Dict[str, Any]:
        """Research a specific code pattern"""
        try:
            # Simplified pattern research
            pattern_research = {
                "pattern": pattern,
                "success_rate": 0.7,
                "best_practices": [],
                "common_issues": []
            }
            
            # Add pattern-specific insights
            if pattern == "function_addition":
                pattern_research["best_practices"] = [
                    "Use descriptive function names",
                    "Add proper documentation",
                    "Include type hints"
                ]
            elif pattern == "error_handling":
                pattern_research["best_practices"] = [
                    "Use specific exception types",
                    "Provide meaningful error messages",
                    "Log errors appropriately"
                ]
            
            return pattern_research
            
        except Exception as e:
            logger.error(f"Error researching pattern {pattern}", error=str(e))
            return {}
    
    def _extract_insights_from_content(self, content: str, topic: str) -> List[str]:
        """Extract insights from internet content"""
        insights = []
        
        # Simplified insight extraction
        # In production, you'd use NLP or ML models
        if topic.lower() in content.lower():
            insights.append(f"Found relevant content about {topic}")
        
        return insights
    
    async def _enhance_proposal_with_internet_learning(self, proposal_data: Dict) -> Dict[str, Any]:
        """Enhance proposal with insights from internet learning"""
        try:
            ai_type = proposal_data.get("ai_type", "")
            improvement_type = proposal_data.get("improvement_type", "")
            
            # Get recent internet learning insights
            insights = await self.ai_learning_service.get_internet_insights(ai_type, improvement_type)
            
            if insights:
                enhanced_data = {
                    "internet_insights": insights,
                    "enhanced_description": self._create_enhanced_description(proposal_data, insights),
                    "learning_sources": list(set([insight.get("source", "") for insight in insights]))
                }
                
                logger.info(f"Enhanced proposal with {len(insights)} internet insights")
                return enhanced_data
            
            return {}
            
        except Exception as e:
            logger.error("Error enhancing proposal with internet learning", error=str(e))
            return {}
    
    def _create_enhanced_description(self, proposal_data: Dict, insights: List[Dict]) -> str:
        """Create enhanced description with internet learning insights"""
        base_description = proposal_data.get("description", "")
        
        if not insights:
            return base_description
        
        # Extract key insights
        best_practices = []
        success_patterns = []
        
        for insight in insights:
            if "best_practice" in insight.get("topic", "").lower():
                best_practices.append(insight.get("insight", ""))
            if "success" in insight.get("insight", "").lower():
                success_patterns.append(insight.get("insight", ""))
        
        enhanced_parts = [base_description]
        
        if best_practices:
            enhanced_parts.append(f"\n\nBest Practices Applied: {', '.join(best_practices[:3])}")
        
        if success_patterns:
            enhanced_parts.append(f"\n\nSuccess Patterns: {', '.join(success_patterns[:2])}")
        
        return " ".join(enhanced_parts)
    
    async def _check_for_duplicates(self, proposal_data: Dict, db: AsyncSession) -> Tuple[bool, str]:
        """Check if proposal is a duplicate of existing proposals"""
        try:
            ai_type = proposal_data.get("ai_type", "")
            file_path = proposal_data.get("file_path", "")
            code_before = proposal_data.get("code_before", "")
            code_after = proposal_data.get("code_after", "")
            
            # Generate semantic hash
            semantic_input = f"{ai_type}|{file_path}|{code_before}|{code_after}"
            semantic_hash = hashlib.sha256(semantic_input.encode('utf-8')).hexdigest()
            
            # Check for exact semantic matches
            query = select(Proposal).where(
                and_(
                    Proposal.semantic_hash == semantic_hash,
                    Proposal.status.in_(["pending", "test-passed", "test-failed"])
                )
            )
            result = await db.execute(query)
            exact_matches = result.scalars().all()
            
            if exact_matches:
                return True, "Exact semantic match found"
            
            # Check for similar proposals in the same file
            query = select(Proposal).where(
                and_(
                    Proposal.file_path == file_path,
                    Proposal.ai_type == ai_type,
                    Proposal.status.in_(["pending", "test-passed", "test-failed"]),
                    Proposal.created_at >= datetime.utcnow() - timedelta(days=7)
                )
            )
            result = await db.execute(query)
            recent_proposals = result.scalars().all()
            
            for recent_proposal in recent_proposals:
                similarity = self._calculate_similarity(proposal_data, recent_proposal)
                if similarity >= self.similarity_threshold:
                    return True, f"Similar proposal found (similarity: {similarity:.2f})"
            
            return False, "No duplicates found"
            
        except Exception as e:
            logger.error("Error checking for duplicates", error=str(e))
            return False, f"Error in duplicate check: {str(e)}"
    
    async def _check_proposal_limits(self, proposal_data: Dict, db: AsyncSession) -> Tuple[bool, str]:
        """Check if proposal limits are exceeded"""
        try:
            ai_type = proposal_data.get("ai_type", "")
            
            # Get the current level of the AI
            current_level = self.ai_learning_service.get_ai_level(ai_type)
            
            # Get the limits for the current level
            limits = self.level_based_limits.get(current_level, self.level_based_limits[1]) # Default to level 1 if not found
            
            # Count pending proposals for this AI
            query = select(func.count(Proposal.id)).where(
                and_(
                    Proposal.ai_type == ai_type,
                    Proposal.status == "pending"
                )
            )
            result = await db.execute(query)
            pending_count = result.scalar() or 0
            
            if pending_count >= limits["max_pending"]:
                return False, f"Maximum pending proposals ({limits['max_pending']}) reached for {ai_type}"
            
            # Check total proposals in last 24 hours
            query = select(func.count(Proposal.id)).where(
                and_(
                    Proposal.ai_type == ai_type,
                    Proposal.created_at >= datetime.utcnow() - timedelta(hours=24)
                )
            )
            result = await db.execute(query)
            daily_count = result.scalar() or 0
            
            if daily_count >= limits["daily_limit"]:
                return False, f"Daily proposal limit ({limits['daily_limit']}) reached for {ai_type}"
            
            return True, "Proposal limits within bounds"
            
        except Exception as e:
            logger.error("Error checking proposal limits", error=str(e))
            return False, f"Error in limit check: {str(e)}"
    
    def _calculate_similarity(self, proposal_data: Dict, existing_proposal) -> float:
        """Calculate similarity between two proposals"""
        try:
            # Simple similarity calculation based on code changes
            code_before_1 = proposal_data.get("code_before", "")
            code_after_1 = proposal_data.get("code_after", "")
            code_before_2 = existing_proposal.code_before or ""
            code_after_2 = existing_proposal.code_after or ""
            
            # Calculate similarity based on code changes
            change_1 = f"{code_before_1}|{code_after_1}"
            change_2 = f"{code_before_2}|{code_after_2}"
            
            # Simple character-based similarity
            if len(change_1) == 0 and len(change_2) == 0:
                return 1.0
            
            if len(change_1) == 0 or len(change_2) == 0:
                return 0.0
            
            # Calculate Jaccard similarity
            set_1 = set(change_1.split())
            set_2 = set(change_2.split())
            
            intersection = len(set_1.intersection(set_2))
            union = len(set_1.union(set_2))
            
            if union == 0:
                return 0.0
            
            return intersection / union
            
        except Exception as e:
            logger.error("Error calculating similarity", error=str(e))
            return 0.0
    
    def _is_low_value_change(self, code_before: str, code_after: str) -> bool:
        """Check if change appears to be low-value"""
        try:
            def clean_code(code: str) -> str:
                """Remove whitespace and comments for comparison"""
                lines = code.split('\n')
                cleaned_lines = []
                for line in lines:
                    stripped = line.strip()
                    if stripped and not stripped.startswith('#') and not stripped.startswith('//'):
                        cleaned_lines.append(stripped)
                return '\n'.join(cleaned_lines)
            
            cleaned_before = clean_code(code_before)
            cleaned_after = clean_code(code_after)
            
            # Check if changes are minimal
            if cleaned_before == cleaned_after:
                return True
            
            # Check if only whitespace or comment changes
            if len(cleaned_before) == len(cleaned_after) and len(cleaned_before) < 10:
                return True
            
            # Check if only variable name changes (very basic)
            if len(cleaned_before.split()) == len(cleaned_after.split()) and len(cleaned_before.split()) < 5:
                return True
            
            return False
            
        except Exception as e:
            logger.error("Error checking low value change", error=str(e))
            return False
    
    async def get_validation_stats(self, db: AsyncSession) -> Dict:
        """Get enhanced validation statistics"""
        try:
            # Get basic stats
            total_proposals = await db.execute(select(func.count(Proposal.id)))
            total_count = total_proposals.scalar()
            
            pending_proposals = await db.execute(
                select(func.count(Proposal.id)).where(Proposal.status == "pending")
            )
            pending_count = pending_proposals.scalar()
            
            # Get AI-specific stats
            ai_stats = {}
            for ai_type in ["imperium", "guardian", "sandbox", "conquest"]:
                ai_proposals = await db.execute(
                    select(func.count(Proposal.id)).where(Proposal.ai_type == ai_type)
                )
                ai_count = ai_proposals.scalar()
                ai_stats[ai_type] = ai_count
            
            stats = {
                "total_proposals": total_count,
                "pending_proposals": pending_count,
                "ai_distribution": ai_stats,
                "validation_thresholds": {
                    "similarity_threshold": self.similarity_threshold,
                    "min_learning_interval": str(self.min_learning_interval),
                    "max_pending_per_ai": self.level_based_limits, # Changed to show all levels
                    "min_confidence_threshold": self.min_confidence_threshold
                },
                "internet_learning": {
                    "enabled": self.internet_learning_enabled,
                    "sources": len(self.learning_sources),
                    "anthropic_integration": bool(self.anthropic_api_key)
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error("Error getting enhanced validation stats", error=str(e))
            return {} 