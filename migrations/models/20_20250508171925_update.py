from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "usersubscription" ADD "subscription_frequency" VARCHAR(7) NOT NULL;
        ALTER TABLE "usersubscription" ALTER COLUMN "subscription_plan" TYPE VARCHAR(10) USING "subscription_plan"::VARCHAR(10);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "usersubscription" DROP COLUMN "subscription_frequency";
        ALTER TABLE "usersubscription" ALTER COLUMN "subscription_plan" TYPE VARCHAR(255) USING "subscription_plan"::VARCHAR(255);"""
