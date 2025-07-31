import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
import asyncio

# Adjust this to match your backend's config
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+asyncpg://user:password@localhost:5432/yourdb')

async def main():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT * FROM agent_metrics;"))
        rows = result.fetchall()
        print(f"Found {len(rows)} rows in agent_metrics table:")
        for row in rows:
            print({k: v for k, v in row._mapping.items()})
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main()) 