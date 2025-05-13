from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "usersubscription" ADD "is_active" BOOL NOT NULL  DEFAULT True;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "usersubscription" DROP COLUMN "is_active";"""
