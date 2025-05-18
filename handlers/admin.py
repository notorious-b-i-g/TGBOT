# admin.py

from aiogram import types, Dispatcher
from create_bot import bot, FSMContext
from states import Form
import json
from config import admins
from keyboard.adminKB import *
from config import API_TOKEN
from db import db
from utils.google_sheets import *

async def get_usernames():
    query = "SELECT username FROM registered_users"
    result = await db.get_data(query, ())
    return [row[0] for row in result]

async def admin_lk_show(message: types.Message):
    user_id = message.from_user.username
    specialists = await get_usernames()
    print(user_id)
    if user_id in admins:
        await bot.send_message(message.chat.id, 'Какой важный', reply_markup=admin_lk_kb)
        await Form.admin_lk_st.set()
    else:
        await bot.send_message(message.chat.id, 'У вас нет прав доступа')

async def edit_registred_users(call: types.CallbackQuery):
    await bot.answer_callback_query(call.id)
    query = "SELECT * FROM registered_users"
    users = await db.get_data(query, ())
    for i, user in enumerate(users):
        remove_button = InlineKeyboardButton("Убрать", callback_data=f"remove_user_{user[1]}")
        keyboard = InlineKeyboardMarkup().add(remove_button)
        formatted_user = f"Пользователь {i + 1}: [@{user[0]}] - Специализация: {user[2]}"
        await bot.send_message(call.message.chat.id, formatted_user, reply_markup=keyboard)

async def remove_registered_user(call: types.CallbackQuery):
    user_id = call.data.split("_")[2]
    query = "DELETE FROM registered_users WHERE userid = %s"
    await db.insert_data(query, (user_id,))
    await bot.delete_message(call.message.chat.id, call.message.message_id)

async def view_requests(call: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(call.id)
    query = "SELECT * FROM users"
    requests = await db.get_data(query, ())
    for i, request in enumerate(requests):
        accept_button = InlineKeyboardButton("Принять", callback_data=f"accept_{request[1]}")
        remove_button = InlineKeyboardButton("Убрать", callback_data=f"remove_{request[1]}")
        keyboard = InlineKeyboardMarkup().add(accept_button, remove_button)
        formatted_request = f"Заявка {i + 1}: [@{request[0]}] - Специализация: {request[2]}"
        await bot.send_message(call.message.chat.id, formatted_request, reply_markup=keyboard)

async def accept_request(call: types.CallbackQuery):
    user_id = call.data.split("_")[1]
    query = "SELECT * FROM users WHERE userid = %s"
    user_data = await db.get_data(query, (user_id,))
    query = "INSERT INTO registered_users (username, userid, specialist_name) VALUES (%s, %s, %s)"
    await db.insert_data(query, user_data[0][0], user_data[0][1], user_data[0][2])
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    query = "DELETE FROM users WHERE userid = %s"
    await db.insert_data(query, (user_id,))

async def remove_request(call: types.CallbackQuery):
    user_id = call.data.split("_")[1]
    query = "DELETE FROM users WHERE userid = %s"
    await db.insert_data(query, (user_id,))
    await bot.delete_message(call.message.chat.id, call.message.message_id)

async def load_to_excel(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Укажите срок выгрузки или введите свой в днях', reply_markup=excel_load_kb)
    await Form.admin_excel_load.set()

def row_exists(sheet, order_id, current_order_status):
    existing_rows = sheet.get_all_values()
    for row_index, row in enumerate(existing_rows):
        if str(row[0]) == str(order_id):
            if row[8] == current_order_status:
                return True
            else:
                sheet.update_cell(row_index + 1, 9, current_order_status)
                return True
    return False

async def get_time_interval(callback: types.CallbackQuery, state: FSMContext):
    start_date, end_date = get_time_range(callback.data)
    await load_to_excel_data(start_date, end_date)
    await callback.message.edit_text('Данные успешно загружены', reply_markup=admin_lk_kb)
    await Form.admin_lk_st.set()

async def input_time_interval(message: types.Message, state: FSMContext):
    time_input = message.text
    start_date, end_date = input_time_range(time_input)
    await load_to_excel_data(start_date, end_date)
    await message.answer('Данные успешно загружены', reply_markup=admin_lk_kb)
    await Form.admin_lk_st.set()

async def get_photo_url(photo_id):
    file_info = await bot.get_file(photo_id)
    file_path = file_info.file_path
    url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file_path}"
    return url


async def load_to_excel_data(start_date, end_date):
    client = authenticate_google_docs()
    sheet = client.open('telegaGTb').sheet1
    query = "SELECT specialist_name, problem_description, post_time, end_time, order_status, worker_name, client_name, comment_description, photo_ids, finish_photo_ids, id FROM tasks WHERE post_time BETWEEN %s AND %s"
    tasks = await db.get_data(query, (start_date, end_date))

    for task in tasks:
        spec_name = task[0]
        prob_dsc = task[1]
        post_time = task[2]
        end_time = task[3]
        order_status = task[4]
        worker_name = task[5]
        client_name = task[6]
        worker_comment = task[7]
        photo_ids = json.loads(task[8]) if task[8] else []
        finish_photo_ids = json.loads(task[9]) if task[9] else []
        order_id = task[10]

        # Обработка фотографий
        if photo_ids:
            photo_urls = [await get_photo_url(photo_id) for photo_id in photo_ids]
            photo_urls_str = ', '.join(photo_urls)
        else:
            photo_urls_str = ''

        if finish_photo_ids:
            finish_photo_urls = [await get_photo_url(photo_id) for photo_id in finish_photo_ids]
            finish_photo_urls_str = ', '.join(finish_photo_urls)
        else:
            finish_photo_urls_str = ''

        # Формирование строки для вставки в таблицу
        row = [order_id, client_name, spec_name, prob_dsc, worker_name, worker_comment, post_time, end_time,
               order_status, photo_urls_str, finish_photo_urls_str]

        # Проверка на существование строки
        if not row_exists(sheet, order_id, order_status):
            sheet.append_row(row)

def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(admin_lk_show, commands=['admin'], state='*')
    dp.register_callback_query_handler(view_requests, text='show_req', state=Form.admin_lk_st)
    dp.register_callback_query_handler(edit_registred_users, text='edit_users', state=Form.admin_lk_st)
    dp.register_callback_query_handler(remove_registered_user, lambda call: call.data.startswith('remove_user_'), state=Form.admin_lk_st)
    dp.register_callback_query_handler(accept_request, lambda call: call.data.startswith('accept_'), state=Form.admin_lk_st)
    dp.register_callback_query_handler(remove_request, lambda call: call.data.startswith('remove_'), state=Form.admin_lk_st)
    dp.register_callback_query_handler(load_to_excel, text='excel_load', state=Form.admin_lk_st)
    dp.register_callback_query_handler(get_time_interval, lambda call: call.data.startswith('month_'), state=Form.admin_excel_load)
    dp.register_message_handler(input_time_interval, state=Form.admin_excel_load)

# Make sure to import this module and call register_admin_handlers with your Dispatcher instance.
