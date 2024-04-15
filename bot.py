from create_bot import dp
from handlers import client, make_order, worker, admin, finish_order
from aiogram import Bot, Dispatcher, executor, types
from handlers.make_order import AlbumMiddleware

client.register_handlers_client(dp)
make_order.register_handlers_make_order(dp)
worker.register_handlers_worker(dp)
admin.register_admin_handlers(dp)
finish_order.register_handlers_finish_order(dp)


if __name__ == '__main__':
    dp.middleware.setup(AlbumMiddleware())
    executor.start_polling(dp, skip_updates=True)