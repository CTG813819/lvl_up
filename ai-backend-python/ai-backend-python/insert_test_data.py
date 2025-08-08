import asyncio
import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import init_database, engine
from app.models.sql_models import Proposal, GuardianSuggestion
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text
import uuid
from datetime import datetime

async def insert_test_proposal():
    async with AsyncSession(engine) as session:
        proposal = Proposal(
            ai_type="Imperium",
            file_path="lib/main.dart",
            code_before="print('Hello World');",
            code_after="print('Hello, World!');",
            status="pending",
            improvement_type="readability",
            confidence=0.8,
            created_at=datetime.utcnow(),
        )
        session.add(proposal)
        await session.commit()
        await session.refresh(proposal)
        print(f"Inserted proposal with id: {proposal.id}")
        return proposal.id

async def insert_test_suggestion():
    async with AsyncSession(engine) as session:
        suggestion = GuardianSuggestion(
            issue_type="mission",
            affected_item_type="mission",
            affected_item_id=str(uuid.uuid4()),
            affected_item_name="Test Mission",
            issue_description="Test issue for approval endpoint.",
            current_value="old_value",
            proposed_fix="new_value",
            severity="medium",
            health_check_type="id_validation",
            logical_consistency=True,
            data_integrity_score=1.0,
            status="pending",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(suggestion)
        await session.commit()
        await session.refresh(suggestion)
        print(f"Inserted suggestion with id: {suggestion.id}")
        return suggestion.id

async def main():
    try:
        await init_database()
        await insert_test_proposal()
        await insert_test_suggestion()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 