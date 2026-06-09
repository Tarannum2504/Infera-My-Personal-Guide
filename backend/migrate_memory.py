import os
from sqlalchemy import create_engine
from sqlalchemy.sql import text

# Use DATABASE_URL from environment variable (provided by Render), fallback to local postgres
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://infera_user:infera_pass@localhost:5432/infera")

# If the URL starts with postgres:// (which Render sometimes does), sqlalchemy requires postgresql://
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

def migrate():
    print(f"Connecting to database to add memory_notes column...")
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            # Check if using SQLite (local) or Postgres (Render)
            if "sqlite" in SQLALCHEMY_DATABASE_URL:
                print("Running SQLite migration...")
                # SQLite doesn't natively support JSON types in older versions, but accepts TEXT for JSON
                conn.execute(text("ALTER TABLE user_profiles ADD COLUMN memory_notes JSON DEFAULT '[]'"))
            else:
                print("Running PostgreSQL migration...")
                # Postgres requires explicit casting to JSON
                conn.execute(text("ALTER TABLE user_profiles ADD COLUMN memory_notes JSON DEFAULT '[]'::json"))
            
            conn.commit()
            print("Successfully added memory_notes column to user_profiles table!")
        except Exception as e:
            print(f"Migration error (column might already exist): {e}")

if __name__ == "__main__":
    migrate()
