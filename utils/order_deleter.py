from db import db
import asyncio
from datetime import datetime, timedelta


async def order_clean():
    while True:
        query = "SELECT post_time FROM tasks WHERE order_status = 'available'"
        post_data = await db.get_data(query, ())
        today = datetime.now()

        for date in post_data:
            # print(date[0])
            post_time = datetime.strptime(date[0], "%Y-%m-%d %H:%M:%S")
            pass_time = today - post_time

            if pass_time > timedelta(days=7):
                query = "UPDATE tasks SET order_status = 'overtime' WHERE post_time = %s;"
                # print(f"Прошло более 3 дней с момента {post_time}")
                await db.insert_data(query, date[0])
        await asyncio.sleep(10800)
