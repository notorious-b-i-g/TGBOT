from aiogram import types, Dispatcher
from create_bot import bot, FSMContext
from states import Form
import json

from keyboard.adminKB import *
from config import specialists
from db import insert_data,get_data,insert_task_with_photos


async def admin_lk_show(message: types.Message):
    user_id = message.from_user.username
    print(user_id)
    if user_id in specialists:
        await bot.send_message(message.chat.id, 'Какой важный', reply_markup=admin_lk_kb)
        await Form.admin_lk_st.set()
    else:
        await bot.send_message(message.chat.id, 'Пошёл нахуй')

async def edit_registred_users(call: types.CallbackQuery):
    query = "SELECT * FROM registered_users"
    users = await get_data(query, ())
    for i, user in enumerate(users):
        # Создаем кнопки для каждого пользователя
        remove_button = InlineKeyboardButton("Убрать", callback_data=f"remove_user_{user[1]}")

        # Добавляем кнопки в клавиатуру
        keyboard = InlineKeyboardMarkup().add(remove_button)

        # Форматируем данные и отправляем сообщение с кнопками
        formatted_user = f"Пользователь {i + 1}: [@{user[0]}] - Специализация: {user[2]}"
        await bot.send_message(call.message.chat.id, formatted_user, reply_markup=keyboard)


async def remove_registered_user(call: types.CallbackQuery):
    # Извлекаем user_id из callback_data
    user_id = call.data.split("_")[2]

    # Удаляем данные пользователя из таблицы registered_users
    query = "DELETE FROM registered_users WHERE userid = %s"
    await insert_data(query, (user_id,))
    await bot.delete_message(call.message.chat.id, call.message.message_id)

async def view_requests(call: types.CallbackQuery, state: FSMContext):
    # Получаем заявки из базы данных
    query = "SELECT * FROM users"
    requests = await get_data(query, ())
    await call.answer()
    for i, request in enumerate(requests):
        # Создаем кнопки для каждой заявки
        accept_button = InlineKeyboardButton("Принять", callback_data=f"accept_{request[1]}")
        remove_button = InlineKeyboardButton("Убрать", callback_data=f"remove_{request[1]}")

        # Добавляем кнопки в клавиатуру
        keyboard = InlineKeyboardMarkup().add(accept_button, remove_button)

        # Форматируем данные и отправляем сообщение с кнопками
        formatted_request = f"Заявка {i + 1}: [@{request[0]}] - Специализация: {request[2]}"
        await bot.send_message(call.message.chat.id, formatted_request, reply_markup=keyboard)

async def accept_request(call: types.CallbackQuery):
    # Извлекаем user_id из callback_data
    user_id = call.data.split("_")[1]

    # Получаем данные пользователя
    query = "SELECT * FROM users WHERE userid = %s"
    user_data = await get_data(query, (user_id,))
    print(user_data)
    # Добавляем данные пользователя в таблицу registered_users
    query = "INSERT INTO registered_users (username, userid, specialist_name) VALUES (%s, %s, %s)"
    await insert_data(query, user_data[0][0], user_data[0][1], user_data[0][2])
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    query = "DELETE FROM users WHERE userid = %s"
    await insert_data(query, (user_id,))

async def remove_request(call: types.CallbackQuery):
    # Извлекаем user_id из callback_data
    user_id = call.data.split("_")[1]

    # Удаляем данные пользователя из таблицы users
    query = "DELETE FROM users WHERE userid = %s"
    await insert_data(query, (user_id,))


def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(admin_lk_show, commands=['admin'])
    dp.register_callback_query_handler(view_requests, text='show_req', state=Form.admin_lk_st)
    dp.register_callback_query_handler(edit_registred_users, text='edit_users', state=Form.admin_lk_st)
    dp.register_callback_query_handler(remove_registered_user, lambda call: call.data.startswith('remove_user_'),
                                       state=Form.admin_lk_st)
    dp.register_callback_query_handler(accept_request, lambda call: call.data.startswith('accept_'),
                                       state=Form.admin_lk_st)
    dp.register_callback_query_handler(remove_request, lambda call: call.data.startswith('remove_'),
                                       state=Form.admin_lk_st)