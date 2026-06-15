from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .config import database_config
from time import sleep

# postgres не успевает инициализироваться, поэтому оставляем
# несколько попыток с задержкой в секунду

counter = 10
while True:
    counter -= 1
    try:
        engine = create_engine(database_config.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        break
    except:
        sleep(1)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()