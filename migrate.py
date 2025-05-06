import os
import sys
import asyncio
import shutil
from pathlib import Path
from tortoise import Tortoise
from app.database import TORTOISE_ORM
from aerich import Command

def clean_migrations():
    """Clean up existing migrations directory"""
    migrations_dir = Path("migrations")
    if migrations_dir.exists():
        shutil.rmtree(migrations_dir)
        print("✅ Cleaned up existing migrations directory")

async def init_tortoise():
    await Tortoise.init(config=TORTOISE_ORM)

async def close_tortoise():
    await Tortoise.close_connections()

async def run_migration(command: str):
    await init_tortoise()
    try:
        aerich = Command(tortoise_config=TORTOISE_ORM, app="models")
        
        if command == "init":
            clean_migrations()
            await aerich.init()
        elif command == "init-db":
            await aerich.init_db(safe=True)
        elif command == "migrate":
            await aerich.migrate()
        elif command == "upgrade":
            await aerich.upgrade()
        elif command == "history":
            await aerich.history()
        elif command == "downgrade":
            await aerich.downgrade()
    finally:
        await close_tortoise()


async def main():
    if len(sys.argv) < 2:
        print("Usage: python migrate.py [init|migrate|upgrade|history|downgrade]")
        sys.exit(1)

    command = sys.argv[1].lower()
    valid_commands = {"init", "init-db", "migrate", "upgrade", "history", "downgrade"}

    if command not in valid_commands:
        print(f"❌ Unknown command: {command}")
        print("Available commands: init, migrate, upgrade, history, downgrade")
        sys.exit(1)

    await run_migration(command)

if __name__ == "__main__":
    asyncio.run(main())
