#!/usr/bin/env python3
"""
Create Proposals Table Script
=============================
Creates the proposals table with all required columns
"""

import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def create_proposals_table():
    """Create the proposals table with all required columns"""
    
    logger.info("🔧 Creating proposals table...")
    
    # SQL to create the proposals table with all required columns
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS proposals (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        ai_type VARCHAR(50) NOT NULL,
        file_path TEXT,
        code_before TEXT,
        code_after TEXT,
        description TEXT,
        status VARCHAR(50) DEFAULT 'pending',
        user_feedback TEXT,
        test_status VARCHAR(50),
        test_output TEXT,
        result TEXT,
        code_hash VARCHAR(255),
        semantic_hash VARCHAR(255),
        diff_score FLOAT,
        duplicate_of UUID REFERENCES proposals(id),
        ai_reasoning TEXT,
        learning_context TEXT,
        mistake_pattern TEXT,
        improvement_type VARCHAR(50),
        confidence FLOAT,
        user_feedback_reason TEXT,
        ai_learning_applied BOOLEAN DEFAULT FALSE,
        previous_mistakes_avoided JSONB DEFAULT '[]',
        ai_learning_summary TEXT,
        learning_proposal_id UUID,
        change_type VARCHAR(50),
        change_scope VARCHAR(50),
        affected_components TEXT,
        learning_sources TEXT,
        expected_impact TEXT,
        risk_assessment TEXT,
        application_response TEXT,
        application_timestamp TIMESTAMP,
        application_result TEXT,
        post_application_analysis TEXT,
        files_analyzed TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    try:
        # Create the table
        result = subprocess.run([
            "sudo", "-u", "postgres", "psql", "-d", "ai_backend", "-c", create_table_sql
        ], capture_output=True, text=True, check=True)
        
        logger.info("✅ Proposals table created successfully")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create table: {e.stderr}")
        return False
    
    # Create indexes for better performance
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_proposals_ai_type_status ON proposals(ai_type, status);",
        "CREATE INDEX IF NOT EXISTS idx_proposals_file_path_ai_type ON proposals(file_path, ai_type);",
        "CREATE INDEX IF NOT EXISTS idx_proposals_created_at ON proposals(created_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_proposals_code_hash_ai_type ON proposals(code_hash, ai_type);",
        "CREATE INDEX IF NOT EXISTS idx_proposals_semantic_hash_ai_type ON proposals(semantic_hash, ai_type);",
        "CREATE INDEX IF NOT EXISTS idx_proposals_status_created_at ON proposals(status, created_at DESC);"
    ]
    
    for index_sql in indexes:
        try:
            subprocess.run([
                "sudo", "-u", "postgres", "psql", "-d", "ai_backend", "-c", index_sql
            ], capture_output=True, text=True, check=True)
            logger.info("✅ Index created")
        except subprocess.CalledProcessError as e:
            logger.warning(f"Could not create index: {e.stderr}")
    
    # Verify the table was created
    try:
        result = subprocess.run([
            "sudo", "-u", "postgres", "psql", "-d", "ai_backend", 
            "-c", "SELECT COUNT(*) FROM proposals;"
        ], capture_output=True, text=True, check=True)
        
        logger.info("✅ Table verification successful")
        logger.info(f"Current row count: {result.stdout.strip()}")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to verify table: {e.stderr}")
        return False
    
    # Show the table schema
    try:
        result = subprocess.run([
            "sudo", "-u", "postgres", "psql", "-d", "ai_backend", 
            "-c", "\\d proposals"
        ], capture_output=True, text=True, check=True)
        
        logger.info("📋 Proposals table schema:")
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to show schema: {e}")
    
    logger.info("✅ Proposals table creation completed successfully")
    return True

if __name__ == "__main__":
    create_proposals_table() 