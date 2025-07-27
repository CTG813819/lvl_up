#!/usr/bin/env python3
"""
Debug database connection and schema issues
"""

import asyncio
import sys
import os
from sqlalchemy import text

# Add the current directory to the Python path
sys.path.append(os.path.dirname(__file__))

from app.core.database import init_database

async def debug_database():
    """Debug database connection and schema issues"""
    try:
        print("🔍 Starting database debug...")
        
        # Initialize database connection
        await init_database()
        
        # Import engine after initialization
        from app.core.database import engine
        
        if not engine:
            print("❌ Database engine is None after initialization")
            return
        
        print("✅ Database engine initialized")
        
        async with engine.begin() as conn:
            print("✅ Database connection established")
            
            # Check database info
            result = await conn.execute(text("SELECT current_database(), current_user, version()"))
            db_info = result.fetchone()
            print(f"📊 Database: {db_info[0]}")
            print(f"👤 User: {db_info[1]}")
            print(f"🔧 Version: {db_info[2][:50]}...")
            
            # Check if proposals table exists
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'proposals'
                );
            """))
            table_exists = result.scalar()
            print(f"📋 Proposals table exists: {table_exists}")
            
            if table_exists:
                # Get all columns in proposals table
                result = await conn.execute(text("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = 'proposals' 
                    AND table_schema = 'public'
                    ORDER BY ordinal_position
                """))
                columns = result.fetchall()
                
                print(f"📝 Found {len(columns)} columns in proposals table:")
                for col in columns:
                    print(f"  - {col[0]} ({col[1]}, nullable: {col[2]})")
                
                # Check specifically for ai_learning_summary
                ai_learning_summary_exists = any(col[0] == 'ai_learning_summary' for col in columns)
                print(f"🎯 ai_learning_summary column exists: {ai_learning_summary_exists}")
                
                if not ai_learning_summary_exists:
                    print("❌ ai_learning_summary column is missing!")
                    print("🔧 Attempting to add the column...")
                    
                    try:
                        await conn.execute(text("""
                            ALTER TABLE proposals 
                            ADD COLUMN ai_learning_summary TEXT
                        """))
                        print("✅ ai_learning_summary column added successfully")
                    except Exception as e:
                        print(f"❌ Error adding column: {e}")
                else:
                    print("✅ ai_learning_summary column exists")
                
                # Test the exact query that's failing
                print("🧪 Testing the failing query...")
                try:
                    result = await conn.execute(text("""
                        SELECT proposals.id, proposals.ai_type, proposals.file_path, proposals.code_before, proposals.code_after, proposals.description, proposals.status, proposals.user_feedback, proposals.test_status, proposals.test_output, proposals.result, proposals.code_hash, proposals.semantic_hash, proposals.diff_score, proposals.duplicate_of, proposals.ai_reasoning, proposals.learning_context, proposals.mistake_pattern, proposals.improvement_type, proposals.confidence, proposals.user_feedback_reason, proposals.ai_learning_applied, proposals.previous_mistakes_avoided, proposals.ai_learning_summary, proposals.change_type, proposals.change_scope, proposals.affected_components, proposals.learning_sources, proposals.expected_impact, proposals.risk_assessment, proposals.application_response, proposals.application_timestamp, proposals.application_result, proposals.post_application_analysis, proposals.files_analyzed, proposals.created_at, proposals.updated_at 
                        FROM proposals 
                        WHERE proposals.status = 'pending' AND proposals.created_at < NOW()
                        LIMIT 1
                    """))
                    rows = result.fetchall()
                    print(f"✅ Query executed successfully, returned {len(rows)} rows")
                except Exception as e:
                    print(f"❌ Query failed: {e}")
            
            else:
                print("❌ Proposals table does not exist!")
                
    except Exception as e:
        print(f"❌ Error in database debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_database()) 