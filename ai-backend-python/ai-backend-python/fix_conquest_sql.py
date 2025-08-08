#!/usr/bin/env python3
"""
Fix SQL Query Issues in Conquest AI Service
"""

import os

def fix_conquest_sql_queries():
    """Fix the SQL query issues in conquest_ai_service.py"""
    print("🔧 Fixing SQL query issues in conquest_ai_service.py...")
    
    file_path = "app/services/conquest_ai_service.py"
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix the update_deployment_status method
    old_update_query = '''                # Update deployment record
                query = """
                    UPDATE conquest_deployments 
                    SET status = $1, updated_at = $2, error_message = $3, build_logs = $4
                    WHERE app_id = $5
                """
                await session.execute(
                    query, 
                    status, 
                    datetime.utcnow(), 
                    error_message or "", 
                    build_logs or "", 
                    app_id
                )'''
    
    new_update_query = '''                # Update deployment record
                from sqlalchemy import text
                query = text("""
                    UPDATE conquest_deployments 
                    SET status = :status, updated_at = :updated_at, error_message = :error_message, build_logs = :build_logs
                    WHERE id = :app_id
                """)
                await session.execute(
                    query, 
                    {
                        "status": status,
                        "updated_at": datetime.utcnow(),
                        "error_message": error_message or "",
                        "build_logs": build_logs or "",
                        "app_id": app_id
                    }
                )'''
    
    content = content.replace(old_update_query, new_update_query)
    
    # Fix the get_progress_logs method
    old_progress_query = '''                query = """
                    SELECT 
                        app_id,
                        app_name,
                        status,
                        created_at,
                        updated_at,
                        error_message,
                        build_logs
                    FROM conquest_deployments 
                    ORDER BY created_at DESC 
                    LIMIT 50
                """
                result = await session.execute(query)'''
    
    new_progress_query = '''                from sqlalchemy import text
                query = text("""
                    SELECT 
                        id as app_id,
                        app_name,
                        status,
                        created_at,
                        updated_at,
                        error_message,
                        build_logs
                    FROM conquest_deployments 
                    ORDER BY created_at DESC 
                    LIMIT 50
                """)
                result = await session.execute(query)'''
    
    content = content.replace(old_progress_query, new_progress_query)
    
    # Fix the get_error_learnings method
    old_error_query = '''                query = """
                    SELECT 
                        app_id,
                        app_name,
                        error_message,
                        build_logs,
                        created_at
                    FROM conquest_deployments 
                    WHERE status = 'failed' AND error_message IS NOT NULL
                    ORDER BY created_at DESC 
                    LIMIT 20
                """
                result = await session.execute(query)'''
    
    new_error_query = '''                from sqlalchemy import text
                query = text("""
                    SELECT 
                        id as app_id,
                        app_name,
                        error_message,
                        build_logs,
                        created_at
                    FROM conquest_deployments 
                    WHERE status = 'failed' AND error_message IS NOT NULL
                    ORDER BY created_at DESC 
                    LIMIT 20
                """)
                result = await session.execute(query)'''
    
    content = content.replace(old_error_query, new_error_query)
    
    # Write the fixed content back
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ SQL query issues fixed successfully")
    return True

if __name__ == "__main__":
    fix_conquest_sql_queries() 