
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from database import Base
from main import app
from fastapi.testclient import TestClient
import pytest
from models import Todos,Users
from routers.auth import bcrypt_context


SQLALCHEMY_DATABASE_URL = 'sqlite:///./test.db'

engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass= StaticPool
)

TestingSeassionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSeassionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {'user_name': 'hkm','id': 1, 'user_role':'admin'}


client = TestClient(app)

@pytest.fixture
def test_todo():
    todos = Todos(
        title='Learn the code',
        description='Need to learn every days',
        priority=3,
        complete=False,
        owner_id=1 ,
        id=1
    )
    db = TestingSeassionLocal()
    db.add(todos)
    db.commit()
    yield todos
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()
    


@pytest.fixture
def test_user():
    user = Users(
    id = 1,
    email = 'hkm@youpmail.com',
    user_name = "hkm",
    first_name = "Harsh",
    last_name = "Mistry",
    hashed_password = bcrypt_context.hash("Test@123"),
    is_active = True,
    role = "admin",
    phone_number = "1111111111"
    )

    db = TestingSeassionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()