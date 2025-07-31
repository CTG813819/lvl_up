#!/usr/bin/env python3
"""
Test script to verify the leaderboard query fix
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.core.database import get_session, init_database

async def test_leaderboard_query():
    """Test the fixed leaderboard query"""
    try:
        # Initialize database
        await init_database()
        session = get_session()
        
        async with session as s:
            # Test the fixed query
            result = await s.execute(
                text("""
                SELECT participant as ai, COUNT(*) as wins
                FROM olympic_events,
                     LATERAL (SELECT json_array_elements_text(participants) as participant) sub
                WHERE winners::jsonb @> json_build_array(participant)::jsonb
                GROUP BY participant
                ORDER BY wins DESC
                LIMIT :limit
                """),
                {"limit": 10}
            )
            
            leaderboard = [dict(row) for row in result]
            print(f"✅ Leaderboard query executed successfully!")
            print(f"📊 Found {len(leaderboard)} participants in leaderboard")
            
            for entry in leaderboard:
                print(f"  - {entry['ai']}: {entry['wins']} wins")
                
    except Exception as e:
        print(f"❌ Error testing leaderboard query: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_leaderboard_query()) 