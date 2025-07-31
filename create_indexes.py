#!/usr/bin/env python3
"""
Create indexes for the new tables
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def create_indexes():
    """Create indexes for the new tables"""
    try:
        from app.core.database import init_database
        from sqlalchemy import text
        
        print("🔧 Creating indexes for new tables...")
        
        # Initialize database
        await init_database()
        
        from app.core.database import engine
        
        async with engine.begin() as conn:
            # Create indexes one by one
            indexes_to_create = [
                ("idx_internet_knowledge_source", "CREATE INDEX idx_internet_knowledge_source ON internet_knowledge(source)"),
                ("idx_internet_knowledge_content_type", "CREATE INDEX idx_internet_knowledge_content_type ON internet_knowledge(content_type)"),
                ("idx_internet_knowledge_created_at", "CREATE INDEX idx_internet_knowledge_created_at ON internet_knowledge(created_at DESC)"),
                ("idx_test_scenarios_type", "CREATE INDEX idx_test_scenarios_type ON test_scenarios(scenario_type)"),
                ("idx_test_scenarios_difficulty", "CREATE INDEX idx_test_scenarios_difficulty ON test_scenarios(difficulty)"),
                ("idx_test_scenarios_created_at", "CREATE INDEX idx_test_scenarios_created_at ON test_scenarios(created_at DESC)"),
                ("idx_ai_communications_test_id", "CREATE INDEX idx_ai_communications_test_id ON ai_communications(test_id)"),
                ("idx_ai_communications_ai_type", "CREATE INDEX idx_ai_communications_ai_type ON ai_communications(ai_type)"),
                ("idx_ai_communications_timestamp", "CREATE INDEX idx_ai_communications_timestamp ON ai_communications(timestamp DESC)"),
                ("idx_ai_responses_test_id", "CREATE INDEX idx_ai_responses_test_id ON ai_responses(test_id)"),
                ("idx_ai_responses_ai_type", "CREATE INDEX idx_ai_responses_ai_type ON ai_responses(ai_type)"),
                ("idx_ai_responses_created_at", "CREATE INDEX idx_ai_responses_created_at ON ai_responses(created_at DESC)"),
                ("idx_learning_entries_ai_type", "CREATE INDEX idx_learning_entries_ai_type ON learning_entries(ai_type)"),
                ("idx_learning_entries_learning_type", "CREATE INDEX idx_learning_entries_learning_type ON learning_entries(learning_type)"),
                ("idx_learning_entries_created_at", "CREATE INDEX idx_learning_entries_created_at ON learning_entries(created_at DESC)")
            ]
            
            created_indexes = []
            for index_name, create_sql in indexes_to_create:
                try:
                    print(f"📝 Creating {index_name}...")
                    await conn.execute(text(create_sql))
                    created_indexes.append(index_name)
                    print(f"✅ Created {index_name}")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        print(f"✅ {index_name} already exists")
                    else:
                        print(f"❌ Error creating {index_name}: {e}")
            
            print(f"\n✅ Successfully created {len(created_indexes)} indexes")
            
    except Exception as e:
        print(f"❌ Error creating indexes: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_indexes()) 