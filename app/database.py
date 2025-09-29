from tortoise import Tortoise
from app import config

async def init_db():
    await Tortoise.init(
        config=config.TORTOISE_ORM
    )

async def close_db():
    await Tortoise.close_connections()