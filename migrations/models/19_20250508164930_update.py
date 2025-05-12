from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "usersubscription" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "user" VARCHAR(255) NOT NULL,
    "subscription_plan" VARCHAR(255) NOT NULL,
    "start_date" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "end_date" TIMESTAMPTZ
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "usersubscription";"""
