import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models.user import User, UserRole
from app.core.security import get_password_hash

# Test database URL (separate from main database)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create test database engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create session for tests
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create database session
    database = TestingSessionLocal()
    
    try:
        yield database
    finally:
        database.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    # Override the database dependency
    app.dependency_overrides[get_db] = override_get_db
    
    # Create test client
    with TestClient(app) as test_client:
        yield test_client
    
    # Clear overrides
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_student(db):
    student = User(
        email="teststudent@test.com",
        name="Test Student",
        hashed_password=get_password_hash("password123"),
        role=UserRole.STUDENT,
        is_active=True
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@pytest.fixture(scope="function")
def test_admin(db):
    admin = User(
        email="testadmin@test.com",
        name="Test Admin",
        hashed_password=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        is_active=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture(scope="function")
def student_token(client, test_student):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "teststudent@test.com",
            "password": "password123"
        }
    )
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def admin_token(client, test_admin):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "testadmin@test.com",
            "password": "admin123"
        }
    )
    return response.json()["access_token"]