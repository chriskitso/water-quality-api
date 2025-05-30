from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from models import Base  # ✅ Import Base from models instead of redefining

# Use environment variable or fallback to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./prediction_logs.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
