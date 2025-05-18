import asyncio
from create_bot import dp
from handlers import client, make_order, worker, admin, finish_order
from utils import order_deleter
from aiogram import Bot, Dispatcher, executor, types
from support.support_class import AlbumMiddleware
from db import db

# Регистрация обработчиков
client.register_handlers_client(dp)
make_order.register_handlers_make_order(dp)
worker.register_handlers_worker(dp)
admin.register_admin_handlers(dp)
finish_order.register_handlers_finish_order(dp)

async def on_startup(dp):
    await db.create_pool()
    asyncio.create_task(order_deleter.order_clean())

async def on_shutdown(dp):
    await db.close_pool()

if __name__ == '__main__':
    dp.middleware.setup(AlbumMiddleware())
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
