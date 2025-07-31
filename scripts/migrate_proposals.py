#!/usr/bin/env python3
"""
Script to migrate old proposals: ensure all have improvement_type and confidence fields.
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), '../app'))
from app.core import database
from app.models.sql_models import Proposal
from sqlalchemy import update, select

load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

async def migrate():
    await database.init_database()
    async with database.SessionLocal() as session:
        result = await session.execute(select(Proposal))
        proposals = result.scalars().all()
        for p in proposals:
            changed = False
            if not hasattr(p, 'improvement_type') or p.improvement_type is None:
                p.improvement_type = 'unknown'
                changed = True
            if not hasattr(p, 'confidence') or p.confidence is None:
                p.confidence = 0.5
                changed = True
            if changed:
                session.add(p)
        await session.commit()
    print('Migration complete.')

if __name__ == '__main__':
    asyncio.run(migrate()) 