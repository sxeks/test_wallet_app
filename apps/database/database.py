from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .config import database_config

engine = create_engine(database_config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()