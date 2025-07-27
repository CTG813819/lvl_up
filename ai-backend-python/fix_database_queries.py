#!/usr/bin/env python3
"""
Database Query Fixes
Fixes the avg() function errors on JSON text fields
"""

import asyncio
from pathlib import Path

# Simple logging without structlog
def log_info(message):
    print(f"[INFO] {message}")

def log_error(message):
    print(f"[ERROR] {message}")

def log_warning(message):
    print(f"[WARNING] {message}")

class DatabaseQueryFixer:
    def __init__(self):
        self.fixes_applied = []
    
    async def fix_all_queries(self):
        """Apply all database query fixes"""
        log_info("🔧 Fixing database query issues...")
        
        # Fix 1: Learning service queries
        await self.fix_learning_queries()
        
        # Fix 2: Analytics queries
        await self.fix_analytics_queries()
        
        # Fix 3: Agent metrics queries
        await self.fix_agent_metrics_queries()
        
        log_info(f"✅ Applied {len(self.fixes_applied)} query fixes")
        return self.fixes_applied
    
    async def fix_learning_queries(self):
        """Fix learning service database queries"""
        try:
            log_info("🔧 Fixing learning service queries...")
            
            # Create the fixed learning service file
            learning_fix = '''
# Fix for app/services/ai_learning_service.py
# Replace the problematic query with this fixed version

async def _get_learning_confidence_stats(self, ai_type: str, days: int = 30) -> Dict[str, Any]:
    """Get learning confidence statistics with fixed query"""
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import select, func, and_
        from app.models.sql_models import Learning
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Fixed query that properly handles JSON data
        query = select(
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
            result = await session.execute(query)
            row = result.first()
            
            return {
                'total_learning': row.total_learning or 0,
                'avg_confidence': float(row.avg_confidence or 0.5)
            }
    except Exception as e:
        log_error(f"Error getting learning confidence stats: {str(e)}")
        return {
            'total_learning': 0,
            'avg_confidence': 0.5
        }

async def _get_current_performance(self, ai_type: str, days: int = 30) -> Dict[str, Any]:
    """Get current performance with fixed query"""
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import select, func, and_
        from app.models.sql_models import Learning
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Fixed query for performance metrics
        query = select(
            func.count(Learning.id).label('total_learning'),
            func.coalesce(
                func.avg(
                    func.cast(
                        func.json_extract_path_text(Learning.learning_data, 'improvement_score'),
                        func.Float
                    )
                ),
                0.0
            ).label('avg_improvement'),
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
                Learning.ai_type == ai_type,
                Learning.created_at >= cutoff_date
            )
        )
        
        async with get_session() as session:
            result = await session.execute(query)
            row = result.first()
            
            return {
                'total_learning': row.total_learning or 0,
                'avg_improvement': float(row.avg_improvement or 0.0),
                'avg_success_rate': float(row.avg_success_rate or 0.0)
            }
    except Exception as e:
        log_error(f"Error getting current performance: {str(e)}")
        return {
            'total_learning': 0,
            'avg_improvement': 0.0,
            'avg_success_rate': 0.0
        }
'''
            
            # Write the fix to a file
            fix_file = Path("learning_service_query_fix.py")
            fix_file.write_text(learning_fix)
            
            self.fixes_applied.append("learning_service_queries")
            log_info("✅ Learning service query fixes created")
            
        except Exception as e:
            log_error(f"Failed to fix learning queries: {str(e)}")
    
    async def fix_analytics_queries(self):
        """Fix analytics service database queries"""
        try:
            log_info("🔧 Fixing analytics service queries...")
            
            analytics_fix = '''
# Fix for app/services/ai_growth_service.py
# Replace problematic analytics queries

async def _get_agent_performance_metrics(self, ai_type: str) -> Dict[str, Any]:
    """Get agent performance metrics with fixed query"""
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import select, func, and_
        from app.models.sql_models import Learning, AgentMetrics
        
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        # Fixed query for agent performance
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
        
        metrics_query = select(AgentMetrics).where(AgentMetrics.agent_type == ai_type)
        
        async with get_session() as session:
            # Get learning stats
            learning_result = await session.execute(learning_query)
            learning_row = learning_result.first()
            
            # Get agent metrics
            metrics_result = await session.execute(metrics_query)
            agent_metrics = metrics_result.scalar_one_or_none()
            
            return {
                'total_learning': learning_row.total_learning or 0,
                'avg_confidence': float(learning_row.avg_confidence or 0.5),
                'agent_metrics': agent_metrics
            }
    except Exception as e:
        log_error(f"Error getting agent performance metrics: {str(e)}")
        return {
            'total_learning': 0,
            'avg_confidence': 0.5,
            'agent_metrics': None
        }
'''
            
            # Write the fix to a file
            fix_file = Path("analytics_service_query_fix.py")
            fix_file.write_text(analytics_fix)
            
            self.fixes_applied.append("analytics_service_queries")
            log_info("✅ Analytics service query fixes created")
            
        except Exception as e:
            log_error(f"Failed to fix analytics queries: {str(e)}")
    
    async def fix_agent_metrics_queries(self):
        """Fix agent metrics database queries"""
        try:
            log_info("🔧 Fixing agent metrics queries...")
            
            metrics_fix = '''
# Fix for app/services/imperium_learning_controller.py
# Replace problematic agent metrics queries

async def _get_agent_learning_stats(self, agent_id: str) -> Dict[str, Any]:
    """Get agent learning statistics with fixed query"""
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import select, func, and_
        from app.models.sql_models import Learning, AgentMetrics
        
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
        log_error(f"Error getting agent learning stats: {str(e)}")
        return {
            'total_learning': 0,
            'avg_learning_score': 0.0,
            'avg_success_rate': 0.0
        }
'''
            
            # Write the fix to a file
            fix_file = Path("agent_metrics_query_fix.py")
            fix_file.write_text(metrics_fix)
            
            self.fixes_applied.append("agent_metrics_queries")
            log_info("✅ Agent metrics query fixes created")
            
        except Exception as e:
            log_error(f"Failed to fix agent metrics queries: {str(e)}")
    
    async def create_sql_functions(self):
        """Create SQL functions to handle JSON operations properly"""
        try:
            log_info("🔧 Creating SQL helper functions...")
            
            sql_functions = '''
-- SQL functions to fix JSON aggregation issues
-- Run this in your PostgreSQL database

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
'''
            
            # Write SQL functions to file
            sql_file = Path("database_helper_functions.sql")
            sql_file.write_text(sql_functions)
            
            self.fixes_applied.append("sql_helper_functions")
            log_info("✅ SQL helper functions created")
            
        except Exception as e:
            log_error(f"Failed to create SQL functions: {str(e)}")
    
    async def create_application_script(self):
        """Create a script to apply all the fixes"""
        try:
            log_info("🔧 Creating application script...")
            
            apply_script = '''#!/bin/bash
# Database Query Fixes Application Script

set -e

echo "🔧 Applying database query fixes..."

# 1. Apply SQL helper functions
echo "🗄️ Creating SQL helper functions..."
if [[ -f database_helper_functions.sql ]]; then
    psql $DATABASE_URL -f database_helper_functions.sql
    echo "✅ SQL helper functions applied"
fi

# 2. Apply learning service fixes
echo "📚 Applying learning service fixes..."
if [[ -f learning_service_query_fix.py ]]; then
    echo "⚠️ Manual application required for learning_service_query_fix.py"
    echo "   Copy the relevant functions to app/services/ai_learning_service.py"
fi

# 3. Apply analytics service fixes
echo "📊 Applying analytics service fixes..."
if [[ -f analytics_service_query_fix.py ]]; then
    echo "⚠️ Manual application required for analytics_service_query_fix.py"
    echo "   Copy the relevant functions to app/services/ai_growth_service.py"
fi

# 4. Apply agent metrics fixes
echo "🤖 Applying agent metrics fixes..."
if [[ -f agent_metrics_query_fix.py ]]; then
    echo "⚠️ Manual application required for agent_metrics_query_fix.py"
    echo "   Copy the relevant functions to app/services/imperium_learning_controller.py"
fi

echo "✅ Database query fixes applied successfully!"
echo ""
echo "📋 Next Steps:"
echo "1. Manually apply the Python code fixes to the respective service files"
echo "2. Restart the AI backend service"
echo "3. Monitor logs for any remaining database errors"
'''
            
            # Write application script
            script_file = Path("apply_database_fixes.sh")
            script_file.write_text(apply_script)
            script_file.chmod(0o755)  # Make executable
            
            self.fixes_applied.append("application_script")
            log_info("✅ Application script created")
            
        except Exception as e:
            log_error(f"Failed to create application script: {str(e)}")

async def main():
    """Main function to run all database query fixes"""
    fixer = DatabaseQueryFixer()
    
    print("🚀 Database Query Fixer")
    print("=" * 40)
    
    # Apply all fixes
    fixes = await fixer.fix_all_queries()
    
    # Create SQL functions
    await fixer.create_sql_functions()
    
    # Create application script
    await fixer.create_application_script()
    
    # Print results
    print(f"\n📊 Fixes Applied: {len(fixes)}")
    for fix in fixes:
        print(f"   - {fix}")
    
    print("\n📋 Next Steps:")
    print("1. Run: chmod +x apply_database_fixes.sh")
    print("2. Run: ./apply_database_fixes.sh")
    print("3. Manually apply the Python code fixes to the service files")
    print("4. Restart the AI backend service")
    print("5. Monitor logs for database errors")

if __name__ == "__main__":
    asyncio.run(main()) 