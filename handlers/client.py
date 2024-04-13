from aiogram import types, Dispatcher
from keyboard.clientKB import *
from states import Form
from create_bot import bot, FSMContext


# Обработчик команды /start
# @dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    # zalupa start:

    # zalupa end.
    await Form.main_menu.set()
    await bot.send_message(message.chat.id, 'Главное меню', reply_markup=main_menu_kb)


# @dp.callback_query_handler(text='my_orders', state=Form.main_menu)
async def see_my_order(call: types.CallbackQuery, state: FSMContext):
    pass


# @dp.callback_query_handler(text='info', state=Form.main_menu)
async def info(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer('Инфа')


# @dp.callback_query_handler(lambda callback: callback.data == 'back_1', state='*')
async def back_1(callback: types.CallbackQuery, state: FSMContext):
    # zalupa start:
    # zalupa end.
    await Form.main_menu.set()
    await callback.message.edit_text('Главное меню', reply_markup=main_menu_kb)


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands=['start'])
    dp.register_callback_query_handler(see_my_order, text='my_orders', state=Form.main_menu)
    dp.register_callback_query_handler(info, text='info', state=Form.main_menu)
    dp.register_callback_query_handler(back_1, lambda callback: callback.data == 'back_1', state='*')
