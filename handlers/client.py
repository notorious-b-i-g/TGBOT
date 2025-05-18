import asyncio
from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboard.clientKB import *
import json
from db import db
from states import Form
from create_bot import bot, FSMContext, storage
from datetime import datetime, timedelta


async def get_user_state(user_id):
    # Получаем объект состояния для пользователя с использованием FSMContext
    state = FSMContext(storage, chat=user_id, user=user_id)
    user_state = await state.get_state()
    return user_state


# Обработчик команды /start
# @dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message, state: FSMContext):
    # zalupa start:
    # print(message.from_user.username, message.from_user.id)
    # zalupa end.
    query = "SELECT post_time FROM tasks"
    post_data = await db.get_data(query, ())

    await Form.main_menu.set()
    await bot.send_message(message.chat.id, 'Главное меню', reply_markup=main_menu_kb)
    # message_client_lk_id = message_client_lk.message_id
    # await state.update_data(message_client_lk=message_client_lk_id)


# @dp.callback_query_handler(text='info', state=Form.main_menu)
async def info(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer('Инфа')


# @dp.callback_query_handler(lambda callback: callback.data == 'back_1', state='*')
async def back_1(callback: types.CallbackQuery, state: FSMContext):
    # zalupa start:
    # zalupa end.
    await Form.main_menu.set()
    await callback.message.edit_text('Главное меню', reply_markup=main_menu_kb)

async def see_my_order(callback: types.CallbackQuery, state: FSMContext):
    name = callback.from_user.username
    if name is None:
        name = callback.from_user.id
    available_ids = await get_next_available_index(name)

    # message_client_lk_id = data.get('message_client_lk')
    if not available_ids:
        await callback.message.edit_text("Нет доступных заявок.", reply_markup=main_menu_kb)
        return
    first_available_id = available_ids[0]  # Берем первый ID из списка доступных
    await callback.message.delete()
    # Очищаем предыдущие данные
    await state.update_data(index=first_available_id, message_ids=[], available_ids=available_ids, current_index=0)

    media_group = await send_order_by_id(first_available_id)
    messages = await callback.bot.send_media_group(callback.message.chat.id, media_group)
    message_ids = [msg.message_id for msg in messages]
    message_1 = await callback.bot.send_message(callback.message.chat.id, "Выберите действие:",
                                                reply_markup=select_order_kb)
    message_ids.append(message_1.message_id)

    # Обновление данных в состоянии
    await state.update_data(message_ids=message_ids)
    await Form.select_order_st_client.set()  # Установка состояния, если это необходимо
    await state.update_data(come_from="see_my_available")


async def get_next_available_index(client_name_to_check: str):
    query = f"SELECT id FROM tasks WHERE client_name = '{client_name_to_check}' AND order_status != 'canceled' ORDER BY id"
    tasks = await db.get_data(query, ())
    # Assuming tasks is a list of tuples, where each tuple contains one element (id)
    return [task[0] for task in tasks]  # Extracting the first element of each tuple directly


async def change_order_see(callback: types.CallbackQuery, state: FSMContext, step: int):
    data = await state.get_data()
    available_ids = data.get('available_ids', [])
    current_index = data.get('current_index', 0)
    max_index = len(available_ids) - 1

    # Обновляем индекс, учитывая возможные границы списка
    if step == 1 and current_index < max_index:
        current_index += 1
    elif current_index == max_index and step == 1:
        current_index = 0
    elif step == -1 and current_index > 0:
        current_index -= 1
    elif current_index == 0 and step == -1:
        current_index = max_index
    order_id = available_ids[current_index]

    # Удаление старых сообщений
    message_ids = data.get('message_ids', [])
    await asyncio.gather(*(callback.bot.delete_message(callback.message.chat.id, msg_id) for msg_id in message_ids))

    # Отправка новой группы сообщений
    media_group = await send_order_by_id(order_id)
    messages = await callback.bot.send_media_group(callback.message.chat.id, media_group)

    new_message_ids = [msg.message_id for msg in messages]

    wtd = data.get('come_from')

    message_1 = await callback.bot.send_message(callback.message.chat.id, "Выберите действие:",
                                                    reply_markup=select_order_kb)
    new_message_ids.append(message_1.message_id)
    await state.update_data(index=order_id, current_index=current_index, message_ids=new_message_ids)


async def send_order_by_id(order_id):
    query = "SELECT * FROM tasks WHERE id = %s"
    tasks = await db.get_data(query, (order_id,))  # передаём order_id как параметр

    if tasks:
        task = tasks[0]  # Берём первую (и единственную) запись из результата
        specialist_name = task[1]
        problem = task[2]
        json_string = task[3]
        photos = json.loads(json_string)
        posted_time = task[6]
        end_time = task[7]
        order_status = task[8]
        if order_status == 'completed':
            json_string = task[10]
            photos = json.loads(json_string)

        media_group = types.MediaGroup()
        if photos:
            for idx, file_id in enumerate(photos):
                if idx == 0 and order_status == 'available' or order_status == 'booked':
                    media_group.attach_photo(file_id, caption=f'Специалист: {specialist_name}\nЗадача: {problem}\nВремя размещения: {posted_time}\nВремя на исполнение: {end_time}')
                elif idx == 0 and order_status == 'completed':
                    worker_name = task[4]
                    worker_comment = task[9]
                    media_group.attach_photo(file_id, caption=f'Специалист: {specialist_name}\n'
                    f'Задача: {problem}\nВремя размещения: {posted_time}\nВремя завершения: {end_time},\n'
                    f'Исполнитель: {worker_name},\nКомментарий исполнителя: {worker_comment}')

                else:
                    media_group.attach_photo(file_id)
        return media_group
    else:
        # Обработка случая, когда задача с таким ID не найдена
        print("Задача с ID {} не найдена.".format(order_id))
        return None


async def next_order_see(callback: types.CallbackQuery, state: FSMContext):

    if not (data := await state.get_data()).get('available_ids'):
        available_ids = await get_next_available_index(callback.from_user.username)
        await state.update_data(available_ids=available_ids)
    await change_order_see(callback, state, 1)


# @callback_query_handler(next_order_see, text='prev_oder', state=Form.select_order_st)
async def prev_order_see(callback: types.CallbackQuery, state: FSMContext):
    if not (data := await state.get_data()).get('available_ids'):
        available_ids = await get_next_available_index(callback.from_user.username)
        await state.update_data(available_ids=available_ids)
    await change_order_see(callback, state, -1)


async def exit_from_orders_show(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    message_ids = data.get('message_ids', [])
    if message_ids:
        await asyncio.gather(
            *(callback.bot.delete_message(callback.message.chat.id, msg_id) for msg_id in message_ids))
    await state.update_data(message_ids=[])

    await callback.message.answer('Добро пожаловать', reply_markup=main_menu_kb)
    # message_client_lk_id = message_client_lk.message_id
   #  await callback.bot.delete_message(callback.message.chat.id, message_client_lk_id)

    await Form.main_menu.set()

async def delete_order(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)
    data = await state.get_data()
    order_id = data.get('index')  # Получаем ID текущего заказа из состояния

    # SQL-запрос для удаления заказа из базы данных
    query = 'SELECT order_status FROM tasks WHERE id = %s'
    order_status_check = await db.get_data(query, (order_id,))
    if order_status_check[0][0] != 'completed':
        query = "UPDATE tasks SET order_status = 'canceled' WHERE id = %s;"
        await db.insert_data(query, order_id)
        # print(f"Заказ {order_id} удален.")
        # Обновляем список доступных заявок
        available_ids = await get_next_available_index(callback.from_user.username)
        await state.update_data(available_ids=available_ids, current_index=0)

        if available_ids:
            await change_order_see(callback, state, 1)
        else:
            await Form.main_menu.set()
            await callback.message.edit_text("Заказ удален. Нет доступных заявок.", reply_markup=main_menu_kb)
    else:
        await callback.message.edit_text(text='Заказ уже выполнен', reply_markup=select_order_kb)


async def open_order_chat(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)
    data = await state.get_data()


    available_ids = data.get('available_ids', [])
    current_index = data.get('current_index', 0)
    order_id = available_ids[current_index]
    chat_data = await db.get_data("""
        SELECT DISTINCT chat.worker_name, chat.client_name
        FROM chat
        JOIN tasks ON chat.order_id = tasks.id
        WHERE tasks.id = %s;
    """, (order_id,))
    if chat_data:
        message_ids = data.get('message_ids', [])
        if message_ids:
            await asyncio.gather(
                *(callback.bot.delete_message(callback.message.chat.id, msg_id) for msg_id in message_ids))
        message_ids = []
        await state.update_data(message_ids=message_ids)
        workers = set()
        for names in chat_data:
            workers.add(names[0])
        if len(workers) == 1:
            worker_name = chat_data[0][0]
            await state.update_data(worker_name=worker_name)
            loaded_messages = await load_chat_messages(callback, order_id, worker_name)
            await state.update_data(message_ids=loaded_messages)
            await Form.chat_with_worker.set()
        else:
            chat_kb_lot = InlineKeyboardMarkup(row_width=1)
            for worker in workers:
                button_text = f"Chat between {worker}"
                chat_kb_lot.add(InlineKeyboardButton(text=button_text, callback_data=f"open_chat:{worker}"))

            message_chat_select = await callback.message.answer(text="Выберите чат для просмотра:", reply_markup=chat_kb_lot)
            message_ids.append(message_chat_select.message_id)

            await state.update_data(message_ids=message_ids)

            await Form.order_chat.set()
    else:
        await callback.message.edit_text(text='Сообщений нет', reply_markup=select_order_kb)
        await Form.select_order_st_client.set()


async def select_chat(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)
    data = await state.get_data()
    available_ids = data.get('available_ids', [])
    current_index = data.get('current_index', 0)
    message_ids = data.get('message_ids', [])
    order_id = available_ids[current_index]
    worker_name = callback.data[10:]
    loaded_messages = await load_chat_messages(callback, order_id, worker_name)
    message_ids.extend(loaded_messages)
    await state.update_data(message_ids=message_ids, worker_name=worker_name)


async def load_chat_messages(callback: types.CallbackQuery, order_id, worker_name):
    message_chat_open = await callback.message.answer(text='Чат открыт', reply_markup=chat_kb)
    query = """
                SELECT chat.sender_id, chat.message_content
                FROM chat
                WHERE chat.order_id = %s AND chat.worker_name = %s;
            """
    chat_messages = await db.get_data(query, (order_id, worker_name))

    tasks = []
    for sender_id, message in chat_messages:
        message_text = f"{'Вы' if str(sender_id) == str(callback.from_user.id) else 'Исполнитель'}: {message}"
        tasks.append(callback.message.answer(text=message_text))

    responses = await asyncio.gather(*tasks)
    loaded_messages = [response.message_id for response in responses]
    loaded_messages.append(message_chat_open.message_id)
    await Form.chat_with_worker.set()
    return loaded_messages


async def send_message_to_worker(message: types.Message, state: FSMContext):
    data = await state.get_data()
    message_content = message.text
    available_ids = data.get('available_ids', [])
    current_index = data.get('current_index', 0)
    order_id = available_ids[current_index]
    worker_name = data.get('worker_name')
    message_ids = data.get('message_ids', [])
    message_ids.append(message.message_id)

    client_name = message.from_user.id
    other_user_state = await get_user_state(int(worker_name))
    if other_user_state != 'Form:chat_with_customer':
        await bot.send_message(chat_id=worker_name, text=f'Новое сообщение по заявке')
    else:
        await bot.send_message(chat_id=worker_name, text=message_content)
    send_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Получение текущего времени

    query = """
               INSERT INTO chat (sender_id, receiver_id, message_content, send_time, worker_name, client_name, order_id)
               VALUES (%s, %s, %s, %s, %s, %s, %s);
           """
    await db.insert_data(query, client_name, worker_name, message_content, send_time, worker_name, client_name, order_id)


async def exit_message_to_worker(message: types.Message, state: FSMContext):
    data = await state.get_data()
    message_chat_exit = message.message_id
    message_ids = data.get('message_ids', [])
    message_chat_close = await message.answer("Чат закрыт", reply_markup=types.ReplyKeyboardRemove())
    message_ids.append(message_chat_close.message_id)
    message_ids.append(message_chat_exit)
    if message_ids:
        await asyncio.gather(
            *(bot.delete_message(message.chat.id, msg_id) for msg_id in message_ids))

    await message.answer('Добро пожаловать!', reply_markup=main_menu_kb)
    await state.update_data(message_ids=[])
    await Form.main_menu.set()

def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands=['start'])
    dp.register_callback_query_handler(see_my_order, text='my_orders', state=Form.main_menu)
    dp.register_callback_query_handler(info, text='info', state=Form.main_menu)
    dp.register_callback_query_handler(back_1, lambda callback: callback.data == 'back_1', state='*')
    dp.register_callback_query_handler(exit_from_orders_show, text='exit_wrk_lk', state=Form.select_order_st_client)
    dp.register_callback_query_handler(next_order_see, text='next_oder', state=Form.select_order_st_client)
    dp.register_callback_query_handler(prev_order_see, text='prev_order', state=Form.select_order_st_client)
    dp.register_callback_query_handler(delete_order, text='delete_order', state=Form.select_order_st_client)

    # чат
    dp.register_callback_query_handler(open_order_chat, text='chat_order', state=Form.select_order_st_client)
    dp.register_message_handler(exit_message_to_worker, text='/выход', state=Form.chat_with_worker)
    dp.register_message_handler(send_message_to_worker, state=Form.chat_with_worker)
    dp.register_callback_query_handler(select_chat, lambda callback: callback.data.startswith('open_chat'), state=Form.order_chat)
