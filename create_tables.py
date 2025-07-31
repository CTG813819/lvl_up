#!/usr/bin/env python3
"""
Script to create all database tables
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import init_database, create_tables, create_indexes
from app.models.sql_models import Base, TokenUsage, TokenUsageLog
from sqlalchemy import text
import structlog

logger = structlog.get_logger()

async def create_all_tables():
    """Create all database tables"""
    try:
        # Initialize database connection
        await init_database()
        
        # Create tables
        await create_tables()
        
        # Create indexes
        await create_indexes()
        
        # Create oath_papers table if it doesn't exist
        from app.core.database import engine
        async with engine.begin() as conn:
            # Check if oath_papers table exists
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'oath_papers'
                );
            """))
            table_exists = result.scalar()
            
            if not table_exists:
                logger.info("Creating oath_papers table...")
                await conn.execute(text("""
                    CREATE TABLE oath_papers (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        title VARCHAR(200) NOT NULL,
                        content TEXT NOT NULL,
                        category VARCHAR(50) NOT NULL,
                        ai_insights JSONB,
                        learning_value FLOAT DEFAULT 0.0,
                        status VARCHAR(20) DEFAULT 'pending',
                        ai_responses JSONB DEFAULT '{}',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """))
                
                # Create indexes for oath_papers
                await conn.execute(text("""
                    CREATE INDEX idx_oath_papers_category ON oath_papers(category);
                    CREATE INDEX idx_oath_papers_created_at ON oath_papers(created_at DESC);
                    CREATE INDEX idx_oath_papers_status ON oath_papers(status);
                """))
                
                logger.info("oath_papers table created successfully")
            else:
                logger.info("oath_papers table already exists")
            
            # Check if token_usage tables exist
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'token_usage'
                );
            """))
            token_usage_exists = result.scalar()
            
            if not token_usage_exists:
                logger.info("Creating token_usage tables...")
                # Create token_usage table
                await conn.execute(text("""
                    CREATE TABLE token_usage (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        ai_type VARCHAR(50) NOT NULL,
                        month_year VARCHAR(7) NOT NULL,
                        tokens_in INTEGER DEFAULT 0,
                        tokens_out INTEGER DEFAULT 0,
                        total_tokens INTEGER DEFAULT 0,
                        request_count INTEGER DEFAULT 0,
                        monthly_limit INTEGER DEFAULT 500000,
                        usage_percentage FLOAT DEFAULT 0.0,
                        last_request_at TIMESTAMP,
                        status VARCHAR(20) DEFAULT 'active',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """))
                
                # Create token_usage_logs table
                await conn.execute(text("""
                    CREATE TABLE token_usage_logs (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        ai_type VARCHAR(50) NOT NULL,
                        month_year VARCHAR(7) NOT NULL,
                        request_id VARCHAR(100),
                        tokens_in INTEGER DEFAULT 0,
                        tokens_out INTEGER DEFAULT 0,
                        total_tokens INTEGER DEFAULT 0,
                        model_used VARCHAR(50),
                        request_type VARCHAR(50),
                        success BOOLEAN DEFAULT TRUE,
                        error_message TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """))
                
                # Create indexes for token usage tables
                await conn.execute(text("""
                    CREATE INDEX idx_token_usage_ai_month ON token_usage(ai_type, month_year);
                    CREATE INDEX idx_token_usage_ai_type ON token_usage(ai_type);
                    CREATE INDEX idx_token_usage_month_year ON token_usage(month_year);
                    CREATE INDEX idx_token_usage_status ON token_usage(status);
                    CREATE INDEX idx_token_usage_updated_at ON token_usage(updated_at DESC);
                    CREATE INDEX idx_token_usage_logs_ai_type ON token_usage_logs(ai_type);
                    CREATE INDEX idx_token_usage_logs_month_year ON token_usage_logs(month_year);
                    CREATE INDEX idx_token_usage_logs_created_at ON token_usage_logs(created_at DESC);
                    CREATE INDEX idx_token_usage_logs_request_id ON token_usage_logs(request_id);
                """))
                
                logger.info("token_usage tables created successfully")
            else:
                logger.info("token_usage tables already exist")
            
            # Check if internet_knowledge table exists
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'internet_knowledge'
                );
            """))
            internet_knowledge_exists = result.scalar()
            
            if not internet_knowledge_exists:
                logger.info("Creating internet_knowledge table...")
                await conn.execute(text("""
                    CREATE TABLE internet_knowledge (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        source VARCHAR(500) NOT NULL,
                        source_type VARCHAR(50) NOT NULL,
                        topic VARCHAR(100) NOT NULL,
                        content TEXT NOT NULL,
                        extracted_knowledge JSONB,
                        relevance_score FLOAT DEFAULT 0.8,
                        last_fetched TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """))
                
                # Create indexes for internet_knowledge
                await conn.execute(text("""
                    CREATE INDEX idx_internet_knowledge_source_type ON internet_knowledge(source_type);
                    CREATE INDEX idx_internet_knowledge_topic ON internet_knowledge(topic);
                    CREATE INDEX idx_internet_knowledge_relevance ON internet_knowledge(relevance_score DESC);
                    CREATE INDEX idx_internet_knowledge_created_at ON internet_knowledge(created_at DESC);
                """))
                
                logger.info("internet_knowledge table created successfully")
            else:
                logger.info("internet_knowledge table already exists")
            
            # Check if test_scenarios table exists
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'test_scenarios'
                );
            """))
            test_scenarios_exists = result.scalar()
            
            if not test_scenarios_exists:
                logger.info("Creating test_scenarios table...")
                await conn.execute(text("""
                    CREATE TABLE test_scenarios (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        scenario_type VARCHAR(50) NOT NULL,
                        difficulty VARCHAR(20) NOT NULL,
                        complexity VARCHAR(10) NOT NULL,
                        description TEXT NOT NULL,
                        requirements JSONB,
                        success_criteria JSONB,
                        ai_types JSONB,
                        docker_config JSONB,
                        time_limit INTEGER DEFAULT 3600,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """))
                
                # Create indexes for test_scenarios
                await conn.execute(text("""
                    CREATE INDEX idx_test_scenarios_type ON test_scenarios(scenario_type);
                    CREATE INDEX idx_test_scenarios_difficulty ON test_scenarios(difficulty);
                    CREATE INDEX idx_test_scenarios_complexity ON test_scenarios(complexity);
                    CREATE INDEX idx_test_scenarios_created_at ON test_scenarios(created_at DESC);
                """))
                
                logger.info("test_scenarios table created successfully")
            else:
                logger.info("test_scenarios table already exists")
            
            # Check if ai_communications table exists
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'ai_communications'
                );
            """))
            ai_communications_exists = result.scalar()
            
            if not ai_communications_exists:
                logger.info("Creating ai_communications table...")
                await conn.execute(text("""
                    CREATE TABLE ai_communications (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        scenario_id UUID REFERENCES test_scenarios(id),
                        ai_types JSONB NOT NULL,
                        communication_rounds JSONB,
                        collaboration_rules JSONB,
                        expected_outcome JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """))
                
                # Create indexes for ai_communications
                await conn.execute(text("""
                    CREATE INDEX idx_ai_communications_scenario_id ON ai_communications(scenario_id);
                    CREATE INDEX idx_ai_communications_created_at ON ai_communications(created_at DESC);
                """))
                
                logger.info("ai_communications table created successfully")
            else:
                logger.info("ai_communications table already exists")
            
            # Check if ai_responses table exists
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'ai_responses'
                );
            """))
            ai_responses_exists = result.scalar()
            
            if not ai_responses_exists:
                logger.info("Creating ai_responses table...")
                await conn.execute(text("""
                    CREATE TABLE ai_responses (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        ai_type VARCHAR(50) NOT NULL,
                        scenario_id UUID REFERENCES test_scenarios(id),
                        response_types JSONB NOT NULL,
                        generated_content JSONB NOT NULL,
                        languages_used JSONB,
                        architecture_components JSONB,
                        code_snippets JSONB,
                        documentation TEXT,
                        testing_approach TEXT,
                        performance_considerations TEXT,
                        security_measures TEXT,
                        deployment_strategy TEXT,
                        quality_score FLOAT DEFAULT 0.0,
                        complexity_level VARCHAR(10),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """))
                
                # Create indexes for ai_responses
                await conn.execute(text("""
                    CREATE INDEX idx_ai_responses_ai_type ON ai_responses(ai_type);
                    CREATE INDEX idx_ai_responses_scenario_id ON ai_responses(scenario_id);
                    CREATE INDEX idx_ai_responses_created_at ON ai_responses(created_at DESC);
                    CREATE INDEX idx_ai_responses_quality_score ON ai_responses(quality_score DESC);
                """))
                
                logger.info("ai_responses table created successfully")
            else:
                logger.info("ai_responses table already exists")
        
        logger.info("All database tables created successfully")
        
    except Exception as e:
        logger.error("Error creating tables", error=str(e))
        raise

if __name__ == "__main__":
    asyncio.run(create_all_tables()) 