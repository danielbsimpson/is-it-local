"""Shared test fixtures.

These tests require a reachable PostgreSQL/PostGIS instance. Set ``TEST_DATABASE_URL``
(or ``DATABASE_URL``) to point at a disposable test database; the schema is created
and torn down around the test session.
"""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.db import get_db
from app.main import app
from app.models import Base

_RAW_URL = os.getenv(
    "TEST_DATABASE_URL",
    os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/is_it_local_test",
    ),
)
TEST_DATABASE_URL = (
    _RAW_URL.replace("postgresql://", "postgresql+psycopg://", 1)
    if _RAW_URL.startswith("postgresql://")
    else _RAW_URL
)


@pytest.fixture(scope="session")
def engine() -> Engine:
    eng = create_engine(TEST_DATABASE_URL, future=True)
    with eng.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
    Base.metadata.drop_all(eng)
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)
    eng.dispose()


@pytest.fixture
def db_session(engine: Engine) -> Session:
    connection = engine.connect()
    transaction = connection.begin()
    testing_session = sessionmaker(bind=connection, future=True)
    session = testing_session()
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_session: Session) -> TestClient:
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
