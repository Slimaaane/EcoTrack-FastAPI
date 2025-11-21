"""Pytest configuration and fixtures."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.db.models.user import User
from app.db.models.zone import Zone
from app.db.models.source import Source
from app.db.models.indicator import Indicator
from app.core.security import get_password_hash


# Base de données de test en mémoire
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with test database."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db_session):
    """Create an admin user for testing."""
    user = User(
        email="admin@test.com",
        username="admin",
        hashed_password=get_password_hash("admin123"),
        role="admin",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def normal_user(db_session):
    """Create a normal user for testing."""
    user = User(
        email="user@test.com",
        username="testuser",
        hashed_password=get_password_hash("user123"),
        role="user",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_token(client, admin_user):
    """Get JWT token for admin user."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@test.com", "password": "admin123"}
    )
    return response.json()["access_token"]


@pytest.fixture
def user_token(client, normal_user):
    """Get JWT token for normal user."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "user@test.com", "password": "user123"}
    )
    return response.json()["access_token"]


@pytest.fixture
def sample_zone(db_session, admin_user):
    """Create a sample zone for testing."""
    zone = Zone(
        name="Zone Test",
        postal_code="75001",
        description="Zone de test"
    )
    db_session.add(zone)
    db_session.commit()
    db_session.refresh(zone)
    return zone


@pytest.fixture
def sample_source(db_session):
    """Create a sample source for testing."""
    source = Source(
        name="Source Test",
        url="https://test.com",
        format="CSV",
        frequency="daily",
        description="Source de test"
    )
    db_session.add(source)
    db_session.commit()
    db_session.refresh(source)
    return source


@pytest.fixture
def sample_indicator(db_session, admin_user, sample_zone, sample_source):
    """Create a sample indicator for testing."""
    from datetime import datetime
    indicator = Indicator(
        type="air_quality_no2",
        name="NO2 Test",
        value=45.5,
        unit="µg/m³",
        timestamp=datetime.utcnow(),
        zone_id=sample_zone.id,
        source_id=sample_source.id,
        owner_id=admin_user.id
    )
    db_session.add(indicator)
    db_session.commit()
    db_session.refresh(indicator)
    return indicator
