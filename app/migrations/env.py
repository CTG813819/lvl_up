from __future__ import with_statement
import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# --- BEGIN USER EDIT SECTION ---
# Add your app directory to sys.path so imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import your SQLAlchemy Base
from app.core.database import Base

# Import all model modules so their tables are registered with Base.metadata
import app.models.sql_models
import app.models.terra_extension
import app.models.imperium_graph_node
import app.models.training_data

target_metadata = Base.metadata
# --- END USER EDIT SECTION ---

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Get your database URL from environment or config
# You can set it in alembic.ini or use an env var

def get_url():
    url = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
    if not url:
        raise RuntimeError("No database URL provided in environment or alembic.ini")
    # Remove +asyncpg and any ssl=... parameter (psycopg2 does not accept 'ssl')
    url = url.replace('+asyncpg', '')
    if 'ssl=' in url:
        # Remove ssl=... from query string
        import re
        url = re.sub(r'([&?])ssl=[^&]*&?', r'\1', url)
        # Clean up any trailing ? or &
        url = url.rstrip('?&')
    return url

config.set_main_option('sqlalchemy.url', get_url())

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, compare_type=True
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata, compare_type=True
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online() 