import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os
import sys
from time import sleep

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from main import app
from apps.database.database import get_db
from apps.wallets.models import Base

TEST_DATABASE_URL = "postgresql://test_user:test_password@test_db:5432/test_wallets"

# postgres не успевает инициализироваться, поэтому оставляем
# несколько попыток с задержкой в секунду

counter = 10
while True:
    counter -= 1
    try:
        engine = create_engine(TEST_DATABASE_URL)
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        break
    except:
        sleep(1)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def db_session():
    # Создаю таблицы для каждой тестовой функции
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()
        # Очищаю таблицы после теста
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()