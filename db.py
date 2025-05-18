import aiomysql
import asyncio
from sshtunnel import SSHTunnelForwarder
from config import DB_CONFIG, SSH_CONFIG

class Database:
    def __init__(self):
        self.server = None
        self.pool = None

    async def start_tunnel(self):
        self.server = SSHTunnelForwarder(
            (SSH_CONFIG['ssh_host'], SSH_CONFIG['ssh_port']),
            ssh_username=SSH_CONFIG['ssh_user'],
            ssh_password=SSH_CONFIG['ssh_password'],
            remote_bind_address=SSH_CONFIG['remote_bind_address']
        )
        self.server.start()

    async def create_pool(self):
        await self.start_tunnel()
        self.pool = await aiomysql.create_pool(
            host=DB_CONFIG['host'],
            port=self.server.local_bind_port,
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            db=DB_CONFIG['db'],
            minsize=1,
            maxsize=10
        )

    async def close_pool(self):
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
        if self.server:
            self.server.stop()

    async def get_data(self, query, params):
        if not self.pool:
            await self.create_pool()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params)
                result = await cur.fetchall()
                return result

    async def insert_data(self, query, *params):
        if not self.pool:
            await self.create_pool()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params)
                await conn.commit()

    async def insert_task_with_photos(self, query, params):
        if not self.pool:
            await self.create_pool()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params)
                await conn.commit()

    async def test_connection(self):
        if not self.pool:
            await self.create_pool()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT VERSION()")
                result = await cur.fetchone()
                print(f"MySQL version: {result[0]}")

db = Database()

async def main():
    await db.create_pool()
    await db.test_connection()
    await db.close_pool()

if __name__ == '__main__':
    asyncio.run(main())
