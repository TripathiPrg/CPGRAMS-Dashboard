"""
Database setup for CPGRAMS Personal Workbench
Using SQLite with SQLAlchemy ORM
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite in FastAPI
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency that provides a database session and safely closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Create all tables in the SQLite database and ensure schema migrations."""
    from backend import models  # Ensure models are loaded
    from sqlalchemy import inspect, text
    Base.metadata.create_all(bind=engine)

    # Auto-migration for SQLite columns added in upgrades
    with engine.connect() as conn:
        inspector = inspect(engine)
        if "grievances" in inspector.get_table_names():
            columns = [c["name"] for c in inspector.get_columns("grievances")]
            new_cols = [
                ("workflow_state", "VARCHAR(50) DEFAULT 'Retrieved'"),
                ("portal_action_timestamp", "DATETIME"),
                ("portal_confirmation_id", "VARCHAR(100)"),
                ("verification_status", "VARCHAR(50) DEFAULT 'unverified'"),
                ("portal_reply_recorded", "TEXT"),
                ("disposal_category", "VARCHAR(100)"),
                ("disposal_remarks", "TEXT"),
            ]
            for col_name, col_type in new_cols:
                if col_name not in columns:
                    conn.execute(text(f"ALTER TABLE grievances ADD COLUMN {col_name} {col_type}"))
            conn.commit()
