# tests/conftest.py

import asyncio
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from tortoise import Tortoise
from app.database import TORTOISE_ORM
from main import app
from tortoise.contrib.test import finalizer, initializer

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def initialize_tests():
    """Initialize test database."""
    # Use test database configuration
    test_config = TORTOISE_ORM.copy()
    test_config["apps"]["models"]["models"] = [
        "aerich.models",
        "app.models.user",
        "app.models.subscription"
    ]
    test_config["apps"]["models"]["default_connection"] = "test"
    
    await Tortoise.init(config=test_config)
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()

@pytest.fixture
def client(initialize_tests):
    """Create a test client."""
    return TestClient(app)

import logging

@pytest.fixture(autouse=True)
async def clean_database():
    """Clean database after each test."""
    yield
    # Clean up all tables after each test
    conn = Tortoise.get_connection("test")
    await conn.execute_query("""
        DO $$ DECLARE
            r RECORD;
        BEGIN
            FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                EXECUTE 'TRUNCATE TABLE ' || quote_ident(r.tablename) || ' CASCADE';
            END LOOP;
        END $$;
    """)

@pytest.fixture(scope="module", autouse=True)
def initialize_tests():
    # Use the same settings as in your main app
    db_url = "postgres://user:password@localhost:5432/your_test_db"

    initializer(
        modules={"models": ["app.models.user", "app.models.subscription"]},
        db_url=db_url,
        loop=None  # Ensures it uses the same event loop
    )
    yield
    finalizer()
