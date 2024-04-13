from aiogram import types, Dispatcher
from create_bot import bot, FSMContext
from states import Form
import json

from keyboard.adminKB import *
from config import specialists


async def admin_lk_show(message: types.Message):
    user_id = message.from_user.username
    print(user_id)
    if user_id in specialists:
        await bot.send_message(message.chat.id, 'Какой важный', reply_markup=admin_lk_kb)
        await Form.admin_lk_st.set()
    else:
        await bot.send_message(message.chat.id, 'Пошёл нахуй')

def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(admin_lk_show, commands=['admin'])