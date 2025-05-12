import os
from pathlib import Path
from dotenv import load_dotenv
from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise
import ssl

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / 'app/.env'
load_dotenv(dotenv_path=env_path)

# Database configuration components
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "summit_db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_SSL_MODE = os.getenv("DB_SSL_MODE", "require")

# Test database configuration
TEST_DB_NAME = os.getenv("TEST_DB_NAME", "summit_test_db")
TEST_DB_HOST = os.getenv("TEST_DB_HOST", "localhost")
TEST_DB_PORT = os.getenv("TEST_DB_PORT", "5432")
TEST_DB_USER = os.getenv("TEST_DB_USER", "postgres")
TEST_DB_PASSWORD = os.getenv("TEST_DB_PASSWORD", "postgres")
TEST_DB_SSL_MODE = os.getenv("TEST_DB_SSL_MODE", "disable")

print('DB_USER:', DB_USER)

# Create SSL context
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Database URL for Tortoise ORM
TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": DB_HOST,
                "port": int(DB_PORT),
                "user": DB_USER,
                "password": DB_PASSWORD,
                "database": DB_NAME,
                "ssl": ssl_context if DB_SSL_MODE == "require" else None
            }
        },
        "test": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": TEST_DB_HOST,
                "port": int(TEST_DB_PORT),
                "user": TEST_DB_USER,
                "password": TEST_DB_PASSWORD,
                "database": TEST_DB_NAME,
                "ssl": ssl_context if TEST_DB_SSL_MODE == "require" else None
            }
        }
    },
    "apps": {
        "models": {
            "models": ["aerich.models", "app.models.user", "app.models.subscription"],
            "default_connection": "default",
        },
    },
}

async def init_db():
    """Initialize database connection"""
    await Tortoise.init(config=TORTOISE_ORM)
    # Create tables if they don't exist
    await Tortoise.generate_schemas()

async def close_db():
    """Close database connection"""
    await Tortoise.close_connections()

# Function to register Tortoise ORM with FastAPI
def register_db(app):
    register_tortoise(
        app,
        config=TORTOISE_ORM,
        generate_schemas=True,
        add_exception_handlers=True,
    ) 