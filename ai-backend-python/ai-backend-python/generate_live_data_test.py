#!/usr/bin/env python3
"""
Generate Live Data Test
Creates live data JSON files for Flutter frontend testing
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai-backend-python'))

from app.core.database import init_database, get_session
from app.models.sql_models import AgentMetrics
from sqlalchemy import select

async def generate_test_live_data():
    """Generate test live data files"""
    try:
        await init_database()
        
        async with get_session() as session:
            # Get all agent metrics
            metrics_query = select(AgentMetrics)
            result = await session.execute(metrics_query)
            agents = result.scalars().all()
            
            # Generate custodes data
            custodes_data = {
                'overall_metrics': {
                    'total_tests_given': 40,
                    'total_tests_passed': 25,
                    'total_tests_failed': 15,
                    'overall_pass_rate': 62.5,
                    'total_xp_awarded': 161,
                    'total_learning_score': 1250.0
                },
                'ai_specific_metrics': {},
                'recommendations': [
                    'Imperium is ready to level up',
                    'Guardian can now create proposals',
                    'Focus on improving Sandbox performance',
                    'Conquest needs additional learning before retesting'
                ],
                'last_updated': datetime.utcnow().isoformat(),
                'system_status': 'live',
                'update_interval_seconds': 30
            }
            
            # Generate black library data
            black_library_data = {
                'ai_data': {},
                'total_learning_score': 1250.0,
                'total_xp': 161,
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
                'update_interval_seconds': 30
            }
            
            # Process each AI
            for agent in agents:
                ai_type = agent.agent_type.lower()
                learning_score = agent.learning_score or 0.0
                xp = agent.xp or 0
                custody_xp = getattr(agent, 'custody_xp', 0) or 0
                
                # Calculate combined score for leveling
                combined_score = learning_score + custody_xp
                
                # Get unified level and title
                level = get_unified_level(combined_score)
                title = get_unified_title(combined_score, ai_type)
                
                # Calculate knowledge points (0-100 scale)
                knowledge_points = min(100, int(combined_score / 1000))
                
                # Add to black library data
                black_library_data['ai_data'][ai_type] = {
                    'level': level,
                    'title': title,
                    'learning_score': learning_score,
                    'xp': xp,
                    'custody_xp': custody_xp,
                    'combined_score': combined_score,
                    'knowledge_points': knowledge_points,
                    'total_learning_cycles': agent.total_learning_cycles or 0,
                    'success_rate': agent.success_rate or 0.0,
                    'recent_insights': [f"Learned about {ai_type} fundamentals"],
                    'learning_patterns': agent.learning_patterns or [],
                    'improvement_suggestions': agent.improvement_suggestions or [],
                    'last_learning_cycle': agent.last_learning_cycle.isoformat() if agent.last_learning_cycle else None,
                    'status': agent.status or 'idle'
                }
                
                # Add to custodes data
                custodes_data['ai_specific_metrics'][ai_type] = {
                    'total_tests_given': 10,
                    'total_tests_passed': 6,
                    'total_tests_failed': 4,
                    'pass_rate': 60.0,
                    'custody_level': level,
                    'custody_xp': custody_xp,
                    'learning_score': learning_score,
                    'level_name': title,
                    'current_difficulty': get_difficulty_level(level),
                    'can_level_up': level < 10,
                    'can_create_proposals': level >= 5,
                    'consecutive_failures': 0,
                    'test_history': [],
                    'last_test_date': datetime.utcnow().isoformat(),
                    'total_learning_cycles': agent.total_learning_cycles or 0,
                    'success_rate': agent.success_rate or 0.0,
                    'learning_patterns': agent.learning_patterns or [],
                    'improvement_suggestions': agent.improvement_suggestions or []
                }
            
            # Save custodes data
            with open('live_custodes_data.json', 'w') as f:
                json.dump(custodes_data, f, indent=2, default=str)
            
            # Save black library data
            with open('live_black_library_data.json', 'w') as f:
                json.dump(black_library_data, f, indent=2, default=str)
            
            print("✅ Generated live data files:")
            print(f"   📊 live_custodes_data.json - {custodes_data['overall_metrics']['total_xp_awarded']} total XP")
            print(f"   📚 live_black_library_data.json - {black_library_data['total_xp']} total XP")
            print(f"   🕒 Last updated: {datetime.utcnow().strftime('%H:%M:%S')}")
            
    except Exception as e:
        print(f"❌ Error generating test live data: {e}")

def get_unified_level(combined_score: float) -> int:
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

def get_unified_title(combined_score: float, ai_type: str) -> str:
    """Get unified title based on combined score and AI type"""
    level = get_unified_level(combined_score)
    
    titles = {
        'imperium': ['Recruit', 'Aspirant', 'Neophyte', 'Battle Brother', 'Veteran', 'Sergeant', 'Lieutenant', 'Librarian', 'Master of the Forge', 'Emperor'],
        'guardian': ['Recruit', 'Aspirant', 'Neophyte', 'Battle Brother', 'Veteran', 'Sergeant', 'Lieutenant', 'Techmarine', 'Master of the Forge', 'Chapter Master'],
        'sandbox': ['Cadet', 'Menial', 'Servitor', 'Skitarii', 'Initiate/Apprentice', 'Tech Priest (Cogitator)', 'Magos', 'Tech Priest Dominus', 'Archmagos', 'Fabricator General'],
        'conquest': ['Cadet', 'Menial', 'Servitor', 'Skitarii', 'Initiate/Apprentice', 'Tech Priest (Engineer)', 'Magos', 'Tech Priest Dominus', 'Archmagos', 'Fabricator General']
    }
    
    ai_titles = titles.get(ai_type, titles['imperium'])
    return ai_titles[min(level - 1, len(ai_titles) - 1)]

def get_difficulty_level(custody_level: int) -> str:
    """Get difficulty level based on custody level"""
    if custody_level >= 7:
        return 'expert'
    elif custody_level >= 4:
        return 'advanced'
    elif custody_level >= 2:
        return 'intermediate'
    else:
        return 'basic'

async def main():
    """Run the test data generator"""
    print("🚀 Generating Test Live Data Files...")
    print("=" * 50)
    
    await generate_test_live_data()
    
    print("\n✅ Test live data generation complete!")

if __name__ == "__main__":
    asyncio.run(main()) 