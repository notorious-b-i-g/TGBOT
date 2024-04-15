import asyncio
from config import specialists
from aiogram import types, Dispatcher
from keyboard.clientKB import *
import json
from db import get_data,insert_data
from states import Form
from create_bot import bot, FSMContext

# Обработчик команды /start
# @dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message, state: FSMContext):
    # zalupa start:

    # zalupa end.
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
    available_ids = await get_next_available_index(callback.from_user.username)
    print(available_ids, 'available_ids232')

    data = await state.get_data()
    # message_client_lk_id = data.get('message_client_lk')
    print(available_ids, 'available_ids')
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



async def get_next_available_index(client_name_to_check):
    query = f"SELECT id FROM tasks WHERE client_name = '{client_name_to_check}' AND order_status != 'canceled' ORDER BY id"
    tasks = await get_data(query, ())
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
    tasks = await get_data(query, (order_id,))  # передаём order_id как параметр

    if tasks:
        task = tasks[0]  # Берём первую (и единственную) запись из результата
        specialist_name = task[1]
        problem = task[2]
        json_string = task[3]
        photos = json.loads(json_string)
        posted_time = task[6]
        end_time = task[7]

        media_group = types.MediaGroup()
        if photos:
            for idx, file_id in enumerate(photos):
                if idx == 0:
                    media_group.attach_photo(file_id, caption=f'Специалист: {specialist_name}\nЗадача: {problem}\nВремя размещения: {posted_time}\nВремя на исполнение: {end_time}')
                else:
                    media_group.attach_photo(file_id)
        return media_group
    else:
        # Обработка случая, когда задача с таким ID не найдена
        print("Задача с ID {} не найдена.".format(order_id))
        return None

async def next_order_see(callback: types.CallbackQuery, state: FSMContext):

    if not (data := await state.get_data()).get('available_ids'):
        available_ids = await get_next_available_index()
        await state.update_data(available_ids=available_ids)
    await change_order_see(callback, state, 1)


# @callback_query_handler(next_order_see, text='prev_oder', state=Form.select_order_st)
async def prev_order_see(callback: types.CallbackQuery, state: FSMContext):
    print(state)
    if not (data := await state.get_data()).get('available_ids'):
        available_ids = await get_next_available_index()
        await state.update_data(available_ids=available_ids)
    await change_order_see(callback, state, -1 )

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
    data = await state.get_data()
    order_id = data.get('index')  # Получаем ID текущего заказа из состояния

    # SQL-запрос для удаления заказа из базы данных
    query = "UPDATE tasks SET order_status = 'canceled' WHERE id = %s;"
    await insert_data(query, order_id)
    print(f"Заказ {order_id} удален.")
    # Обновляем список доступных заявок
    available_ids = await get_next_available_index(callback.from_user.username)
    print(available_ids, 'available_ids')
    await state.update_data(available_ids=available_ids)

    if available_ids:
        await change_order_see(callback, state, 1)
    else:
        await Form.main_menu.set()
        await callback.message.edit_text("Заказ удален. Нет доступных заявок.", reply_markup=main_menu_kb)

def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands=['start'])
    dp.register_callback_query_handler(see_my_order, text='my_orders', state=Form.main_menu)
    dp.register_callback_query_handler(info, text='info', state=Form.main_menu)
    dp.register_callback_query_handler(back_1, lambda callback: callback.data == 'back_1', state='*')
    dp.register_callback_query_handler(exit_from_orders_show, text='exit_wrk_lk', state=Form.select_order_st_client)
    dp.register_callback_query_handler(next_order_see, text='next_oder', state=Form.select_order_st_client)
    dp.register_callback_query_handler(prev_order_see, text='prev_order', state=Form.select_order_st_client)
    dp.register_callback_query_handler(delete_order, text='delete_order', state=Form.select_order_st_client)
