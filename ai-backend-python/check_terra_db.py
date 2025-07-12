#!/usr/bin/env python3
"""
Check TerraExtension records in the database
"""

import asyncio
from app.core.database import get_db, init_database
from app.models.terra_extension import TerraExtension
from sqlalchemy import select

async def check_terra_extensions():
    """Check existing TerraExtension records"""
    try:
        await init_database()
        db_gen = get_db()
        db = await db_gen.__anext__()
        try:
            result = await db.execute(select(TerraExtension))
            extensions = result.scalars().all()
            
            print(f"Found {len(extensions)} TerraExtension records")
            
            for ext in extensions:
                print(f"ID: {ext.id}")
                print(f"  created_at: {ext.created_at} (type: {type(ext.created_at)})")
                print(f"  updated_at: {ext.updated_at} (type: {type(ext.updated_at)})")
                print(f"  status: {ext.status}")
                print("---")
        finally:
            await db_gen.aclose()
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    asyncio.run(check_terra_extensions()) 