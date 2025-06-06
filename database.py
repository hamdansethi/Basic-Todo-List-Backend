from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite connection URL (file-based database)
SQLALCHEMY_DATABASE_URL = "sqlite:///./todos.db"

# Create SQLAlchemy engine with SQLite-specific arg
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Needed for SQLite with multiple threads (like FastAPI)
)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models to inherit from
Base = declarative_base()

# Dependency to get DB session for each request; closes session after use
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
