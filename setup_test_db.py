import os
import asyncio
import asyncpg
from app.database import (
    TEST_DB_HOST,
    TEST_DB_PORT,
    TEST_DB_USER,
    TEST_DB_PASSWORD,
    TEST_DB_NAME
)

async def create_test_database():
    """Create test database if it doesn't exist"""
    # Connect to default postgres database
    sys_conn = await asyncpg.connect(
        host=TEST_DB_HOST,
        port=int(TEST_DB_PORT),
        user=TEST_DB_USER,
        password=TEST_DB_PASSWORD,
        database='postgres'
    )
    
    try:
        # Check if database exists
        exists = await sys_conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1",
            TEST_DB_NAME
        )
        
        if not exists:
            print(f"Creating test database: {TEST_DB_NAME}")
            await sys_conn.execute(f'CREATE DATABASE {TEST_DB_NAME}')
            print("Test database created successfully!")
        else:
            print(f"Test database {TEST_DB_NAME} already exists")
            
    except Exception as e:
        print(f"Error creating test database: {e}")
        raise
    finally:
        await sys_conn.close()

async def main():
    try:
        await create_test_database()
    except Exception as e:
        print(f"Failed to set up test database: {e}")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 