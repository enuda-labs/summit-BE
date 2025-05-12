from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "subscription" RENAME COLUMN "subscription_type" TO "subscription_plan";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "subscription" RENAME COLUMN "subscription_plan" TO "subscription_type";"""
