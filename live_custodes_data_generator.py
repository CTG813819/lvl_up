#!/usr/bin/env python3
"""
Live Custodes Data Generator
Continuously generates and updates JSON data for Flutter frontend
Provides real-time data for Black Library and Custodes Protocol screens
"""

import asyncio
import sys
import os
import json
from datetime import datetime
import time
from typing import Dict, List, Any

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai-backend-python'))

from app.core.database import init_database, get_session
from app.models.sql_models import AgentMetrics, OathPaper
from app.models.training_data import TrainingData
from app.services.custody_protocol_service import CustodyProtocolService, TestCategory
from sqlalchemy import select, text, or_
import structlog

logger = structlog.get_logger()

class LiveCustodesDataGenerator:
    """Live data generator for Flutter frontend consumption"""
    
    def __init__(self):
        self.custodes_service = None
        self.last_update = datetime.utcnow()
        self.update_interval = 30  # Update every 30 seconds
        
    async def initialize(self):
        """Initialize the live data generator"""
        try:
            await init_database()
            self.custodes_service = await CustodyProtocolService.initialize()
            print("✅ Live Custodes Data Generator initialized")
        except Exception as e:
            print(f"❌ Error initializing live data generator: {e}")
    
    async def generate_live_custodes_data(self) -> Dict[str, Any]:
        """Generate live Custodes protocol data"""
        try:
            async with get_session() as session:
                # Get all agent metrics
                metrics_query = select(AgentMetrics)
                result = await session.execute(metrics_query)
                agents = result.scalars().all()
                
                # Group agents by type
                ai_metrics = {}
                overall_metrics = {
                    'total_tests_given': 0,
                    'total_tests_passed': 0,
                    'total_tests_failed': 0,
                    'overall_pass_rate': 0.0,
                    'total_xp_awarded': 0,
                    'total_learning_score': 0.0
                }
                
                for agent in agents:
                    ai_type = agent.agent_type.lower()
                    
                    # Get custody metrics from the service
                    custody_metrics = self.custodes_service.custody_metrics.get(ai_type, {})
                    
                    # Calculate test statistics
                    total_tests = custody_metrics.get('total_tests_given', 0)
                    passed_tests = custody_metrics.get('total_tests_passed', 0)
                    failed_tests = custody_metrics.get('total_tests_failed', 0)
                    custody_xp = custody_metrics.get('custody_xp', 0)
                    
                    # Determine custody level and eligibility
                    custody_level = custody_metrics.get('custody_level', 1)
                    can_level_up = custody_metrics.get('can_level_up', False)
                    can_create_proposals = custody_metrics.get('can_create_proposals', False)
                    
                    # Get level name based on custody level
                    level_name = self._get_custody_level_name(custody_level, ai_type)
                    
                    ai_metrics[ai_type] = {
                        'total_tests_given': total_tests,
                        'total_tests_passed': passed_tests,
                        'total_tests_failed': failed_tests,
                        'pass_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0.0,
                        'custody_level': custody_level,
                        'custody_xp': custody_xp,
                        'learning_score': agent.learning_score or 0.0,
                        'level_name': level_name,
                        'current_difficulty': self._get_difficulty_level(custody_level),
                        'can_level_up': can_level_up,
                        'can_create_proposals': can_create_proposals,
                        'consecutive_failures': custody_metrics.get('consecutive_failures', 0),
                        'test_history': custody_metrics.get('test_history', []),
                        'last_test_date': custody_metrics.get('last_test_date'),
                        'total_learning_cycles': agent.total_learning_cycles or 0,
                        'success_rate': agent.success_rate or 0.0,
                        'learning_patterns': agent.learning_patterns or [],
                        'improvement_suggestions': agent.improvement_suggestions or []
                    }
                    
                    # Update overall metrics
                    overall_metrics['total_tests_given'] += total_tests
                    overall_metrics['total_tests_passed'] += passed_tests
                    overall_metrics['total_tests_failed'] += failed_tests
                    overall_metrics['total_xp_awarded'] += custody_xp
                    overall_metrics['total_learning_score'] += agent.learning_score or 0.0
                
                # Calculate overall pass rate
                if overall_metrics['total_tests_given'] > 0:
                    overall_metrics['overall_pass_rate'] = (
                        overall_metrics['total_tests_passed'] / overall_metrics['total_tests_given'] * 100
                    )
                
                # Generate recommendations
                recommendations = self._generate_recommendations(ai_metrics, overall_metrics)
                
                return {
                    'overall_metrics': overall_metrics,
                    'ai_specific_metrics': ai_metrics,
                    'recommendations': recommendations,
                    'last_updated': datetime.utcnow().isoformat(),
                    'system_status': 'live',
                    'update_interval_seconds': self.update_interval
                }
                
        except Exception as e:
            print(f"❌ Error generating live custodes data: {e}")
            return self._generate_fallback_custodes_data()
    
    async def generate_live_black_library_data(self) -> Dict[str, Any]:
        """Generate live Black Library data with unified leveling"""
        try:
            async with get_session() as session:
                # Get all agent metrics
                metrics_query = select(AgentMetrics)
                result = await session.execute(metrics_query)
                agents = result.scalars().all()
                
                # Get oath papers for learning insights
                oath_papers_query = select(OathPaper).where(
                    OathPaper.status == "learned"
                ).order_by(OathPaper.created_at.desc()).limit(50)
                result = await session.execute(oath_papers_query)
                oath_papers = result.scalars().all()
                
                # Process each AI
                ai_data = {}
                total_learning_score = 0.0
                total_xp = 0
                
                for agent in agents:
                    ai_type = agent.agent_type.lower()
                    learning_score = agent.learning_score or 0.0
                    xp = agent.xp or 0
                    custody_xp = getattr(agent, 'custody_xp', 0) or 0
                    
                    # Calculate combined score for leveling
                    combined_score = learning_score + custody_xp
                    
                    # Get unified level and title
                    level = self._get_unified_level(combined_score)
                    title = self._get_unified_title(combined_score, ai_type)
                    
                    # Calculate knowledge points (0-100 scale)
                    knowledge_points = min(100, int(combined_score / 1000))
                    
                    # Get recent learning insights
                    recent_insights = self._get_recent_insights(ai_type, oath_papers)
                    
                    ai_data[ai_type] = {
                        'level': level,
                        'title': title,
                        'learning_score': learning_score,
                        'xp': xp,
                        'custody_xp': custody_xp,
                        'combined_score': combined_score,
                        'knowledge_points': knowledge_points,
                        'total_learning_cycles': agent.total_learning_cycles or 0,
                        'success_rate': agent.success_rate or 0.0,
                        'recent_insights': recent_insights,
                        'learning_patterns': agent.learning_patterns or [],
                        'improvement_suggestions': agent.improvement_suggestions or [],
                        'last_learning_cycle': agent.last_learning_cycle.isoformat() if agent.last_learning_cycle else None,
                        'status': agent.status or 'idle'
                    }
                    
                    total_learning_score += learning_score
                    total_xp += xp
                
                return {
                    'ai_data': ai_data,
                    'total_learning_score': total_learning_score,
                    'total_xp': total_xp,
                    'total_ais': len(agents),
                    'unified_leveling': {
                        'thresholds': {
                            'level_1': 0,
                            'level_2': 2000,
                            'level_3': 10000,
                            'level_4': 20000,
                            'level_5': 50000,
                            'level_6': 100000,
                            'level_7': 200000,
                            'level_8': 500000,
                            'level_9': 1000000,
                            'level_10': 2000000
                        },
                        'titles': {
                            'imperium': ['Recruit', 'Aspirant', 'Neophyte', 'Battle Brother', 'Veteran', 'Sergeant', 'Lieutenant', 'Librarian', 'Master of the Forge', 'Emperor'],
                            'guardian': ['Recruit', 'Aspirant', 'Neophyte', 'Battle Brother', 'Veteran', 'Sergeant', 'Lieutenant', 'Techmarine', 'Master of the Forge', 'Chapter Master'],
                            'sandbox': ['Cadet', 'Menial', 'Servitor', 'Skitarii', 'Initiate/Apprentice', 'Tech Priest (Cogitator)', 'Magos', 'Tech Priest Dominus', 'Archmagos', 'Fabricator General'],
                            'conquest': ['Cadet', 'Menial', 'Servitor', 'Skitarii', 'Initiate/Apprentice', 'Tech Priest (Engineer)', 'Magos', 'Tech Priest Dominus', 'Archmagos', 'Fabricator General']
                        }
                    },
                    'last_updated': datetime.utcnow().isoformat(),
                    'system_status': 'live',
                    'update_interval_seconds': self.update_interval
                }
                
        except Exception as e:
            print(f"❌ Error generating live black library data: {e}")
            return self._generate_fallback_black_library_data()
    
    def _get_custody_level_name(self, level: int, ai_type: str) -> str:
        """Get custody level name based on level and AI type"""
        if level >= 10:
            if ai_type == 'imperium':
                return 'Emperor'
            elif ai_type == 'guardian':
                return 'Chapter Master'
            else:
                return 'Fabricator General'
        elif level >= 8:
            return 'Master of the Forge'
        elif level >= 6:
            if ai_type == 'imperium':
                return 'Librarian'
            elif ai_type == 'guardian':
                return 'Techmarine'
            else:
                return 'Archmagos'
        elif level >= 4:
            if ai_type in ['sandbox', 'conquest']:
                return 'Tech Priest Dominus'
            else:
                return 'Lieutenant'
        elif level >= 3:
            if ai_type in ['sandbox', 'conquest']:
                return 'Magos'
            else:
                return 'Sergeant'
        elif level >= 2:
            if ai_type in ['sandbox', 'conquest']:
                return 'Tech Priest'
            else:
                return 'Veteran'
        else:
            return 'Recruit'
    
    def _get_difficulty_level(self, custody_level: int) -> str:
        """Get difficulty level based on custody level"""
        if custody_level >= 7:
            return 'expert'
        elif custody_level >= 4:
            return 'advanced'
        elif custody_level >= 2:
            return 'intermediate'
        else:
            return 'basic'
    
    def _get_unified_level(self, combined_score: float) -> int:
        """Get unified level based on combined score"""
        if combined_score >= 2000000:
            return 10
        elif combined_score >= 1000000:
            return 9
        elif combined_score >= 500000:
            return 8
        elif combined_score >= 200000:
            return 7
        elif combined_score >= 100000:
            return 6
        elif combined_score >= 50000:
            return 5
        elif combined_score >= 20000:
            return 4
        elif combined_score >= 10000:
            return 3
        elif combined_score >= 5000:
            return 2
        else:
            return 1
    
    def _get_unified_title(self, combined_score: float, ai_type: str) -> str:
        """Get unified title based on combined score and AI type"""
        level = self._get_unified_level(combined_score)
        
        titles = {
            'imperium': ['Recruit', 'Aspirant', 'Neophyte', 'Battle Brother', 'Veteran', 'Sergeant', 'Lieutenant', 'Librarian', 'Master of the Forge', 'Emperor'],
            'guardian': ['Recruit', 'Aspirant', 'Neophyte', 'Battle Brother', 'Veteran', 'Sergeant', 'Lieutenant', 'Techmarine', 'Master of the Forge', 'Chapter Master'],
            'sandbox': ['Cadet', 'Menial', 'Servitor', 'Skitarii', 'Initiate/Apprentice', 'Tech Priest (Cogitator)', 'Magos', 'Tech Priest Dominus', 'Archmagos', 'Fabricator General'],
            'conquest': ['Cadet', 'Menial', 'Servitor', 'Skitarii', 'Initiate/Apprentice', 'Tech Priest (Engineer)', 'Magos', 'Tech Priest Dominus', 'Archmagos', 'Fabricator General']
        }
        
        ai_titles = titles.get(ai_type, titles['imperium'])
        return ai_titles[min(level - 1, len(ai_titles) - 1)]
    
    def _get_recent_insights(self, ai_type: str, oath_papers: List[OathPaper]) -> List[str]:
        """Get recent learning insights for an AI"""
        insights = []
        
        for paper in oath_papers[:5]:  # Last 5 papers
            if paper.ai_responses and isinstance(paper.ai_responses, dict):
                if paper.ai_responses.get(ai_type) in ['learned', 'completed', 'success']:
                    if paper.subject:
                        insights.append(f"Learned about {paper.subject}")
                    elif paper.title:
                        insights.append(f"Studied {paper.title}")
        
        return insights[:3]  # Return top 3 insights
    
    def _generate_recommendations(self, ai_metrics: Dict, overall_metrics: Dict) -> List[str]:
        """Generate recommendations based on current metrics"""
        recommendations = []
        
        # Overall recommendations
        if overall_metrics['total_tests_given'] == 0:
            recommendations.append("Start administering Custodes tests to evaluate AI capabilities")
        elif overall_metrics['overall_pass_rate'] < 50:
            recommendations.append("Focus on improving AI learning before administering more tests")
        elif overall_metrics['overall_pass_rate'] > 80:
            recommendations.append("AIs are performing well - consider increasing test difficulty")
        
        # AI-specific recommendations
        for ai_type, metrics in ai_metrics.items():
            if metrics['total_tests_given'] == 0:
                recommendations.append(f"{ai_type.title()} needs to take initial Custodes tests")
            elif metrics['pass_rate'] < 30:
                recommendations.append(f"{ai_type.title()} requires additional learning before retesting")
            elif metrics['can_level_up']:
                recommendations.append(f"{ai_type.title()} is ready to level up")
            elif metrics['can_create_proposals']:
                recommendations.append(f"{ai_type.title()} can now create proposals")
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _generate_fallback_custodes_data(self) -> Dict[str, Any]:
        """Generate fallback custodes data when database is unavailable"""
        return {
            'overall_metrics': {
                'total_tests_given': 0,
                'total_tests_passed': 0,
                'total_tests_failed': 0,
                'overall_pass_rate': 0.0,
                'total_xp_awarded': 0,
                'total_learning_score': 0.0
            },
            'ai_specific_metrics': {
                'imperium': {'total_tests_given': 0, 'pass_rate': 0.0, 'custody_level': 1},
                'guardian': {'total_tests_given': 0, 'pass_rate': 0.0, 'custody_level': 1},
                'sandbox': {'total_tests_given': 0, 'pass_rate': 0.0, 'custody_level': 1},
                'conquest': {'total_tests_given': 0, 'pass_rate': 0.0, 'custody_level': 1}
            },
            'recommendations': ['System initializing - please wait for live data'],
            'last_updated': datetime.utcnow().isoformat(),
            'system_status': 'initializing'
        }
    
    def _generate_fallback_black_library_data(self) -> Dict[str, Any]:
        """Generate fallback black library data when database is unavailable"""
        return {
            'ai_data': {
                'imperium': {'level': 1, 'title': 'Recruit', 'knowledge_points': 0},
                'guardian': {'level': 1, 'title': 'Recruit', 'knowledge_points': 0},
                'sandbox': {'level': 1, 'title': 'Cadet', 'knowledge_points': 0},
                'conquest': {'level': 1, 'title': 'Cadet', 'knowledge_points': 0}
            },
            'total_learning_score': 0.0,
            'total_xp': 0,
            'last_updated': datetime.utcnow().isoformat(),
            'system_status': 'initializing'
        }
    
    async def save_live_data_files(self):
        """Save live data to JSON files for Flutter consumption"""
        try:
            # Generate live data
            custodes_data = await self.generate_live_custodes_data()
            black_library_data = await self.generate_live_black_library_data()
            
            # Save custodes data
            with open('live_custodes_data.json', 'w') as f:
                json.dump(custodes_data, f, indent=2, default=str)
            
            # Save black library data
            with open('live_black_library_data.json', 'w') as f:
                json.dump(black_library_data, f, indent=2, default=str)
            
            print(f"✅ Live data files updated at {datetime.utcnow().strftime('%H:%M:%S')}")
            print(f"   📊 Custodes: {custodes_data['overall_metrics']['total_xp_awarded']} total XP")
            print(f"   📚 Black Library: {black_library_data['total_xp']} total XP")
            
        except Exception as e:
            print(f"❌ Error saving live data files: {e}")
    
    async def run_live_data_service(self):
        """Run the live data service continuously"""
        print("🚀 Starting Live Custodes Data Service...")
        print("=" * 60)
        
        await self.initialize()
        
        while True:
            try:
                await self.save_live_data_files()
                await asyncio.sleep(self.update_interval)
            except KeyboardInterrupt:
                print("\n🛑 Live data service stopped by user")
                break
            except Exception as e:
                print(f"❌ Error in live data service: {e}")
                await asyncio.sleep(10)  # Wait 10 seconds before retrying

async def main():
    """Run the live data generator"""
    generator = LiveCustodesDataGenerator()
    await generator.run_live_data_service()

if __name__ == "__main__":
    asyncio.run(main()) 