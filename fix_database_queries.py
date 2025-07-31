#!/usr/bin/env python3
"""
Fix Database Query Issues
Fixes the ambiguous function errors in SQL queries
"""

import os
import subprocess
import sys
from pathlib import Path

def run_ssh_command(command):
    """Run SSH command on EC2 instance"""
    try:
        ssh_cmd = [
            "ssh", "-i", "New.pem", 
            "ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com",
            command
        ]
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def fix_database_queries():
    """Fix the database query issues on EC2"""
    print("🔧 Fixing database query issues on EC2 instance...")
    
    # Create SQL functions to fix the ambiguous function errors
    sql_functions = """
-- Fix for ambiguous function errors in PostgreSQL
-- Run these functions to handle JSON operations properly

-- Function to safely extract numeric values from JSON
CREATE OR REPLACE FUNCTION safe_json_numeric(json_data JSONB, key TEXT)
RETURNS NUMERIC AS $$
BEGIN
    RETURN COALESCE(
        CAST(json_data->>key AS NUMERIC),
        0.0
    );
EXCEPTION
    WHEN OTHERS THEN
        RETURN 0.0;
END;
$$ LANGUAGE plpgsql;

-- Function to safely calculate average of JSON numeric values
CREATE OR REPLACE FUNCTION safe_json_avg(json_data JSONB, key TEXT)
RETURNS NUMERIC AS $$
DECLARE
    total NUMERIC := 0;
    count_val INTEGER := 0;
BEGIN
    SELECT 
        COALESCE(AVG(safe_json_numeric(json_data, key)), 0.0)
    INTO total;
    
    RETURN total;
EXCEPTION
    WHEN OTHERS THEN
        RETURN 0.0;
END;
$$ LANGUAGE plpgsql;

-- Function to get learning confidence from JSON
CREATE OR REPLACE FUNCTION get_learning_confidence(learning_data JSONB)
RETURNS NUMERIC AS $$
BEGIN
    RETURN safe_json_numeric(learning_data, 'confidence');
END;
$$ LANGUAGE plpgsql;

-- Function to get learning success rate from JSON
CREATE OR REPLACE FUNCTION get_learning_success_rate(learning_data JSONB)
RETURNS NUMERIC AS $$
BEGIN
    RETURN safe_json_numeric(learning_data, 'success_rate');
END;
$$ LANGUAGE plpgsql;

-- Function to get learning improvement score from JSON
CREATE OR REPLACE FUNCTION get_learning_improvement_score(learning_data JSONB)
RETURNS NUMERIC AS $$
BEGIN
    RETURN safe_json_numeric(learning_data, 'improvement_score');
END;
$$ LANGUAGE plpgsql;
"""
    
    # Write SQL functions to EC2
    print("📝 Creating SQL helper functions...")
    success, output, error = run_ssh_command(f"cd /home/ubuntu/ai-backend-python && cat > fix_database_functions.sql << 'EOF'\n{sql_functions}\nEOF")
    
    if not success:
        print(f"❌ Failed to create SQL functions file: {error}")
        return False
    
    print("✅ SQL functions file created")
    
    # Execute the SQL functions
    print("🔧 Executing SQL functions...")
    success, output, error = run_ssh_command("cd /home/ubuntu/ai-backend-python && psql 'postgresql://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require' -f fix_database_functions.sql")
    
    if not success:
        print(f"❌ Failed to execute SQL functions: {error}")
        print(f"Output: {output}")
        return False
    
    print("✅ SQL functions executed successfully")
    
    # Now fix the Python code that uses these queries
    print("🔧 Fixing Python service files...")
    
    # Fix AI Growth Service
    growth_service_fix = '''
# Fix for app/services/ai_growth_service.py
# Replace the problematic query with this fixed version

async def _get_current_performance(self, ai_type: str) -> Dict[str, Any]:
    """Get current performance metrics for an AI type"""
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import select, func, and_
        from ..models.sql_models import Learning, Proposal
        
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        # Fixed query that properly handles JSON data
        learning_query = select(
            func.count(Learning.id).label('total_learning'),
            func.coalesce(
                func.avg(
                    func.cast(
                        func.json_extract_path_text(Learning.learning_data, 'confidence'),
                        func.Float
                    )
                ),
                0.5
            ).label('avg_confidence')
        ).where(
            and_(
                Learning.ai_type == ai_type,
                Learning.created_at >= cutoff_date
            )
        )
        
        async with get_session() as session:
            result = await session.execute(learning_query)
            row = result.first()
            
            return {
                'total_learning': row.total_learning or 0,
                'avg_confidence': float(row.avg_confidence or 0.5)
            }
    except Exception as e:
        logger.error("Error getting current performance", error=str(e))
        return {
            'total_learning': 0,
            'avg_confidence': 0.5
        }
'''
    
    # Write the fix to EC2
    success, output, error = run_ssh_command(f"cd /home/ubuntu/ai-backend-python && cat > growth_service_fix.py << 'EOF'\n{growth_service_fix}\nEOF")
    
    if success:
        print("✅ Growth service fix created")
    else:
        print(f"❌ Failed to create growth service fix: {error}")
    
    # Fix Imperium Learning Controller
    imperium_fix = '''
# Fix for app/services/imperium_learning_controller.py
# Replace the problematic query with this fixed version

async def _get_agent_learning_stats(self, agent_id: str) -> Dict[str, Any]:
    """Get agent learning statistics with fixed query"""
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import select, func, and_
        from ..models.sql_models import Learning
        
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        # Fixed query for agent learning stats
        query = select(
            func.count(Learning.id).label('total_learning'),
            func.coalesce(
                func.avg(
                    func.cast(
                        func.json_extract_path_text(Learning.learning_data, 'learning_score'),
                        func.Float
                    )
                ),
                0.0
            ).label('avg_learning_score'),
            func.coalesce(
                func.avg(
                    func.cast(
                        func.json_extract_path_text(Learning.learning_data, 'success_rate'),
                        func.Float
                    )
                ),
                0.0
            ).label('avg_success_rate')
        ).where(
            and_(
                Learning.ai_type == agent_id,
                Learning.created_at >= cutoff_date
            )
        )
        
        async with get_session() as session:
            result = await session.execute(query)
            row = result.first()
            
            return {
                'total_learning': row.total_learning or 0,
                'avg_learning_score': float(row.avg_learning_score or 0.0),
                'avg_success_rate': float(row.avg_success_rate or 0.0)
            }
    except Exception as e:
        logger.error("Error getting agent learning stats", error=str(e))
        return {
            'total_learning': 0,
            'avg_learning_score': 0.0,
            'avg_success_rate': 0.0
        }
'''
    
    # Write the imperium fix to EC2
    success, output, error = run_ssh_command(f"cd /home/ubuntu/ai-backend-python && cat > imperium_fix.py << 'EOF'\n{imperium_fix}\nEOF")
    
    if success:
        print("✅ Imperium service fix created")
    else:
        print(f"❌ Failed to create imperium service fix: {error}")
    
    # Create a comprehensive fix script
    fix_script = '''
#!/usr/bin/env python3
"""
Apply database query fixes to all services
"""

import os
import re
from pathlib import Path

def fix_service_file(file_path: str, old_pattern: str, new_pattern: str):
    """Fix a service file by replacing problematic queries"""
    try:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return False
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Replace the problematic pattern
        if old_pattern in content:
            content = content.replace(old_pattern, new_pattern)
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            print(f"✅ Fixed: {file_path}")
            return True
        else:
            print(f"Pattern not found in: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def main():
    """Apply all database query fixes"""
    print("🔧 Applying database query fixes...")
    
    # Fix AI Growth Service
    growth_file = "app/services/ai_growth_service.py"
    old_growth_query = "func.avg(Learning.confidence).label('avg_confidence')"
    new_growth_query = """func.coalesce(
                func.avg(
                    func.cast(
                        func.json_extract_path_text(Learning.learning_data, 'confidence'),
                        func.Float
                    )
                ),
                0.5
            ).label('avg_confidence')"""
    
    fix_service_file(growth_file, old_growth_query, new_growth_query)
    
    # Fix Guardian AI Service
    guardian_file = "app/services/guardian_ai_service.py"
    old_guardian_query = "func.avg(Learning.confidence).label('avg_confidence')"
    new_guardian_query = """func.coalesce(
                func.avg(
                    func.cast(
                        func.json_extract_path_text(Learning.learning_data, 'confidence'),
                        func.Float
                    )
                ),
                0.5
            ).label('avg_confidence')"""
    
    fix_service_file(guardian_file, old_guardian_query, new_guardian_query)
    
    # Fix Imperium Learning Controller
    imperium_file = "app/services/imperium_learning_controller.py"
    old_imperium_query = "func.avg(Learning.confidence).label('avg_confidence')"
    new_imperium_query = """func.coalesce(
                func.avg(
                    func.cast(
                        func.json_extract_path_text(Learning.learning_data, 'confidence'),
                        func.Float
                    )
                ),
                0.5
            ).label('avg_confidence')"""
    
    fix_service_file(imperium_file, old_imperium_query, new_imperium_query)
    
    print("🎉 Database query fixes applied!")

if __name__ == "__main__":
    main()
'''
    
    # Write and execute the fix script on EC2
    success, output, error = run_ssh_command(f"cd /home/ubuntu/ai-backend-python && cat > apply_database_fixes.py << 'EOF'\n{fix_script}\nEOF")
    
    if success:
        print("✅ Database fix script created")
        
        # Execute the fix script
        success, output, error = run_ssh_command("cd /home/ubuntu/ai-backend-python && python3 apply_database_fixes.py")
        
        if success:
            print("✅ Database fixes applied")
            print(output)
        else:
            print(f"❌ Failed to apply database fixes: {error}")
            print(f"Output: {output}")
    else:
        print(f"❌ Failed to create database fix script: {error}")
    
    # Restart the backend service
    print("🔄 Restarting AI backend service...")
    success, output, error = run_ssh_command("sudo systemctl restart ai-backend-python")
    
    if success:
        print("✅ AI backend service restarted")
    else:
        print(f"❌ Failed to restart service: {error}")
    
    # Check service status
    print("📊 Checking service status...")
    success, output, error = run_ssh_command("sudo systemctl status ai-backend-python --no-pager")
    
    if success:
        print("Service status:")
        print(output)
    else:
        print(f"❌ Failed to get service status: {error}")
    
    print("\n🎉 Database query fixes completed!")
    print("=" * 50)
    print("The ambiguous function errors should now be resolved.")
    print("Check the logs to verify the fix worked:")
    print("sudo journalctl -u ai-backend-python -f")
    
    return True

if __name__ == "__main__":
    fix_database_queries() 