from tortoise import Tortoise
from app import config

async def init_db():
    # await Tortoise.init(
    #     db_url=config.TORTOISE_ORM,
    #     modules={"models": ["app.models"]}
    # )
    # await Tortoise.generate_schemas()

    await Tortoise.init(
        config=config.TORTOISE_ORM
    )

async def close_db():
    await Tortoise.close_connections()