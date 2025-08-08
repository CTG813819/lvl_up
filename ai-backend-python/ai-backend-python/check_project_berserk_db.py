#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the project path
sys.path.append('/home/ubuntu/ai-backend-python')

from app.core.database import engine
from app.models.project_berserk import ProjectBerserk

async def check_database():
    try:
        async with engine.begin() as conn:
            result = await conn.execute('SELECT * FROM project_berserk')
            rows = result.fetchall()
            
            print(f"Database rows: {len(rows)}")
            for i, row in enumerate(rows):
                print(f"Row {i+1}: {row}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_database()) 