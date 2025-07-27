import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables if using .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set in environment")

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# 1. Set xp = GREATEST(xp, custody_xp) for all rows
session.execute(text("""
    UPDATE agent_metrics SET xp = GREATEST(COALESCE(xp, 0), COALESCE(custody_xp, 0));
"""))

# 2. Merge duplicate agent rows (sandbox_agent with sandbox, imperium_agent with imperium)
# Define pairs to merge
merge_pairs = [
    ("sandbox_agent", "sandbox"),
    ("imperium_agent", "imperium")
]

for agent_id_1, agent_id_2 in merge_pairs:
    # Find both rows
    rows = session.execute(text("""
        SELECT * FROM agent_metrics WHERE agent_id IN (:id1, :id2)
    """), {"id1": agent_id_1, "id2": agent_id_2}).fetchall()
    if len(rows) < 2:
        continue  # Nothing to merge
    # Pick canonical (prefer non _agent)
    canonical_id = agent_id_2
    duplicate_id = agent_id_1
    # Sum test counts and XP
    session.execute(text("""
        UPDATE agent_metrics SET
            total_tests_given = COALESCE((SELECT total_tests_given FROM agent_metrics WHERE agent_id=:id1),0) + COALESCE((SELECT total_tests_given FROM agent_metrics WHERE agent_id=:id2),0),
            total_tests_passed = COALESCE((SELECT total_tests_passed FROM agent_metrics WHERE agent_id=:id1),0) + COALESCE((SELECT total_tests_passed FROM agent_metrics WHERE agent_id=:id2),0),
            total_tests_failed = COALESCE((SELECT total_tests_failed FROM agent_metrics WHERE agent_id=:id1),0) + COALESCE((SELECT total_tests_failed FROM agent_metrics WHERE agent_id=:id2),0),
            xp = COALESCE((SELECT xp FROM agent_metrics WHERE agent_id=:id1),0) + COALESCE((SELECT xp FROM agent_metrics WHERE agent_id=:id2),0),
            custody_xp = COALESCE((SELECT custody_xp FROM agent_metrics WHERE agent_id=:id1),0) + COALESCE((SELECT custody_xp FROM agent_metrics WHERE agent_id=:id2),0),
            updated_at = GREATEST(COALESCE((SELECT updated_at FROM agent_metrics WHERE agent_id=:id1), '1970-01-01'), COALESCE((SELECT updated_at FROM agent_metrics WHERE agent_id=:id2), '1970-01-01'))
        WHERE agent_id = :canonical_id
    """), {"id1": duplicate_id, "id2": canonical_id, "canonical_id": canonical_id})
    # Delete duplicate
    session.execute(text("DELETE FROM agent_metrics WHERE agent_id = :dup_id"), {"dup_id": duplicate_id})

session.commit()
session.close()
print("XP updated and duplicate agent rows merged.") 