"""
Fix json_extract_path_text function for PostgreSQL
"""

# revision identifiers, used by Alembic.
revision = 'fix_json_extract_function_001'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

def upgrade():
    # Add the json_extract_path_text function
    op.execute("""
        CREATE OR REPLACE FUNCTION json_extract_path_text(json_data jsonb, path text)
        RETURNS text AS $$
        BEGIN
            RETURN json_data #>> string_to_array(path, '.');
        EXCEPTION
            WHEN OTHERS THEN
                RETURN NULL;
        END;
        $$ LANGUAGE plpgsql IMMUTABLE;
    """)
    
    # Grant execute permission
    op.execute("GRANT EXECUTE ON FUNCTION json_extract_path_text(jsonb, text) TO PUBLIC;")

def downgrade():
    # Remove the function
    op.execute("DROP FUNCTION IF EXISTS json_extract_path_text(jsonb, text);")
