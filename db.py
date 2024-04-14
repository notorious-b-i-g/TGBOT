import aiomysql
import json

from config import DB_CONFIG

async def create_pool():
    return await aiomysql.create_pool(**DB_CONFIG)

async def get_data(query,params):
    pool = await create_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query, params)
            result = await cur.fetchall()
            return result


async def insert_data(query, *params):
    pool = await create_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query, params)
            await conn.commit()


async def insert_task_with_photos(query, params):
    pool = await create_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query, params)
            await conn.commit()
