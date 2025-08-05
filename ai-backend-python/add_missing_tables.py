#!/usr/bin/env python3
"""
Add missing tables to existing Neon database
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def add_missing_tables():
    """Add missing tables to the database"""
    try:
        from app.core.database import init_database
        from sqlalchemy import text
        
        print("🔧 Adding missing tables to database...")
        
        # Initialize database
        await init_database()
        
        from app.core.database import engine
        
        async with engine.begin() as conn:
            # Check which tables exist
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            
            existing_tables = {row[0] for row in result.fetchall()}
            
            # Define missing tables to create
            tables_to_create = {
                'internet_knowledge': """
                    CREATE TABLE internet_knowledge (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        source VARCHAR(255) NOT NULL,
                        content_type VARCHAR(100) NOT NULL,
                        content TEXT NOT NULL,
                        url VARCHAR(500),
                        tags TEXT[],
                        relevance_score FLOAT DEFAULT 0.0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """,
                
                'test_scenarios': """
                    CREATE TABLE test_scenarios (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        scenario_type VARCHAR(50) NOT NULL,
                        title VARCHAR(255) NOT NULL,
                        description TEXT NOT NULL,
                        requirements JSONB NOT NULL,
                        difficulty VARCHAR(20) NOT NULL,
                        complexity VARCHAR(10) NOT NULL,
                        ai_knowledge_based BOOLEAN DEFAULT FALSE,
                        internet_knowledge_based BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """,
                
                'ai_communications': """
                    CREATE TABLE ai_communications (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        test_id UUID NOT NULL,
                        ai_type VARCHAR(50) NOT NULL,
                        message_type VARCHAR(50) NOT NULL,
                        content TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata JSONB
                    )
                """,
                
                'ai_responses': """
                    CREATE TABLE ai_responses (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        test_id UUID NOT NULL,
                        ai_type VARCHAR(50) NOT NULL,
                        response_type VARCHAR(50) NOT NULL,
                        generated_code TEXT,
                        architecture_design TEXT,
                        documentation TEXT,
                        testing_strategy TEXT,
                        deployment_strategy TEXT,
                        security_measures TEXT,
                        performance_optimization TEXT,
                        metadata JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """,
                
                'learning_entries': """
                    CREATE TABLE learning_entries (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        ai_type VARCHAR(50) NOT NULL,
                        learning_type VARCHAR(50) NOT NULL,
                        content TEXT NOT NULL,
                        source VARCHAR(255),
                        confidence_score FLOAT DEFAULT 0.0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
            }
            
            # Create missing tables
            created_tables = []
            for table_name, create_sql in tables_to_create.items():
                if table_name not in existing_tables:
                    print(f"📝 Creating {table_name} table...")
                    await conn.execute(text(create_sql))
                    created_tables.append(table_name)
                    print(f"✅ Created {table_name} table")
                else:
                    print(f"✅ {table_name} table already exists")
            
            # Create indexes for better performance
            if 'internet_knowledge' in created_tables:
                print("📝 Creating indexes for internet_knowledge...")
                await conn.execute(text("""
                    CREATE INDEX idx_internet_knowledge_source ON internet_knowledge(source);
                    CREATE INDEX idx_internet_knowledge_content_type ON internet_knowledge(content_type);
                    CREATE INDEX idx_internet_knowledge_created_at ON internet_knowledge(created_at DESC);
                """))
            
            if 'test_scenarios' in created_tables:
                print("📝 Creating indexes for test_scenarios...")
                await conn.execute(text("""
                    CREATE INDEX idx_test_scenarios_type ON test_scenarios(scenario_type);
                    CREATE INDEX idx_test_scenarios_difficulty ON test_scenarios(difficulty);
                    CREATE INDEX idx_test_scenarios_created_at ON test_scenarios(created_at DESC);
                """))
            
            if 'ai_communications' in created_tables:
                print("📝 Creating indexes for ai_communications...")
                await conn.execute(text("""
                    CREATE INDEX idx_ai_communications_test_id ON ai_communications(test_id);
                    CREATE INDEX idx_ai_communications_ai_type ON ai_communications(ai_type);
                    CREATE INDEX idx_ai_communications_timestamp ON ai_communications(timestamp DESC);
                """))
            
            if 'ai_responses' in created_tables:
                print("📝 Creating indexes for ai_responses...")
                await conn.execute(text("""
                    CREATE INDEX idx_ai_responses_test_id ON ai_responses(test_id);
                    CREATE INDEX idx_ai_responses_ai_type ON ai_responses(ai_type);
                    CREATE INDEX idx_ai_responses_created_at ON ai_responses(created_at DESC);
                """))
            
            if 'learning_entries' in created_tables:
                print("📝 Creating indexes for learning_entries...")
                await conn.execute(text("""
                    CREATE INDEX idx_learning_entries_ai_type ON learning_entries(ai_type);
                    CREATE INDEX idx_learning_entries_learning_type ON learning_entries(learning_type);
                    CREATE INDEX idx_learning_entries_created_at ON learning_entries(created_at DESC);
                """))
            
            print(f"\n✅ Successfully created {len(created_tables)} tables: {created_tables}")
            
    except Exception as e:
        print(f"❌ Error adding tables: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(add_missing_tables()) 