from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from create_bot import dp

#@dp.message_handler()
async def echo_send(message : types.Message):
    if message.text == "Привет":
        await message.answer(message.text)
        #await message.reply(message.text)
        #await bot.send message(message.from_user.id, message.txt)

def register_handlers_other(dp : Dispatcher):
    dp.register_message_handler(echo_send)