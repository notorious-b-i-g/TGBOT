import json

from aiogram import types, Dispatcher
from keyboard.workerKB import *
from keyboard.clientKB import main_menu_kb
from states import Form
from create_bot import dp, bot, FSMContext
from db import insert_data, get_data, insert_task_with_photos
from config import specialists
import asyncio


# @dp.callback_query_handler(text='lk_worker', state=Form.main_menu)
async def see_my_order(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.worker_lk)
    await call.message.edit_text('Добро пожаловать', reply_markup=worker_lk_kb)


async def back_2(callback: types.CallbackQuery, state: FSMContext):
    # zalupa start:
    # zalupa end.
    await Form.main_menu.set()
    await callback.message.edit_text('Главное меню', reply_markup=main_menu_kb)


async def registration(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(user_id=callback.from_user.id, username=callback.from_user.username)
    await Form.registration.set()
    await callback.message.edit_text('Укажите вашу специальность', reply_markup=worker_spec_select_kb)
    print(callback.from_user.id)


async def process_registration(callback: types.CallbackQuery, state: FSMContext):
    # Загрузка списка специалистов из JSON-файла
    with open('spec_names.json', 'r', encoding='utf-8') as f:
        spec_names = json.load(f)

    w_specialist_key = callback.data
    w_specialist_name = spec_names.get(w_specialist_key,
                                       'Неизвестный специалист')  # Получаем имя или возвращаем заглушку
    await callback.answer()  # Подтверждаем обработку колбэка
    await state.update_data(specialist_name=w_specialist_name)

    await state.set_state(Form.confirm_registration)
    await callback.message.edit_text(f'Вы выбрали специализацию {w_specialist_name}, Оставить запрос на регистрацию?',
                                     reply_markup=confirm_kb)


# @callback_query_handler(confirm_yes, lambda callback: callback.data == 'yes', state=Form.confirm_registration)
async def confirm_yes(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    #await bot.send_message(571294067,
    #                       f"Пользователь {user_data['username']} ({user_data['user_id']}) хочет зарегистрироваться как {user_data['specialist_name']}.")
    query = "INSERT INTO Users (username, userid, specialist_name) VALUES (%s, %s, %s)"
    await insert_data(query, user_data['username'], str(user_data['user_id']), user_data['specialist_name'])
    await Form.main_menu.set()
    await callback.message.edit_text('Запрос на регистрацию отправлен.')


# @callback_query_handler(confirm_no, lambda callback: callback.data == 'no', state=Form.confirm_registration)
async def confirm_no(callback: types.CallbackQuery, state: FSMContext):
    await Form.main_menu.set()
    await callback.message.edit_text('Регистрация отменена.')


async def send_order_by_id(id):
    print(id)
    id -= 1
    query = "SELECT * FROM tasks"
    tasks = await get_data(query, ())
    specialist_name = tasks[id][1]
    problem = tasks[id][2]
    json_string = tasks[id][3]
    photos = json.loads(json_string)
    posted_time = tasks[id][6]
    end_time = tasks[id][7]

    media_group = types.MediaGroup()
    if photos:
        for idx, file_id in enumerate(photos):
            if idx == 0:
                media_group.attach_photo(file_id,
                                         caption=f'Специалист: {specialist_name}\nЗадача: {problem}\nВремя размещения: {posted_time}\nВремя на исполнение: {end_time}')
            else:
                media_group.attach_photo(file_id)
    return media_group


# @callback_query_handler(enter_worker_lk, text='enter', state=Form.worker_lk)
async def enter_worker_lk(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.username in specialists:
        available_ids = await get_next_available_index()
        if not available_ids:
            await callback.bot.send_message(callback.message.chat.id, "Нет доступных заявок.")
            return
        first_available_id = available_ids[0]  # Берем первый ID из списка доступных

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
        await Form.select_order_st.set()  # Установка состояния, если это необходимо
    else:
        await bot.answer_callback_query(callback.id)
        await callback.message.edit_text('Вы не в списке исполнителей', reply_markup=worker_lk_kb)


async def get_next_available_index():
    query = "SELECT id FROM tasks WHERE order_status = 'available' ORDER BY id"
    tasks = await get_data(query, ())
    print([task[0] for task in tasks], "tasks")
    # Assuming tasks is a list of tuples, where each tuple contains one element (id)
    return [task[0] for task in tasks]  # Extracting the first element of each tuple directly


async def get_next_booked_index():
    query = "SELECT id FROM tasks WHERE order_status = 'booked' ORDER BY id"
    tasks = await get_data(query, ())
    # Assuming tasks is a list of tuples, where each tuple contains one element (id)
    return [task[0] for task in tasks]  # Extracting the first element of each tuple directly


async def change_order_see(callback: types.CallbackQuery, state: FSMContext, step: int):
    data = await state.get_data()
    print(data)
    available_ids = data.get('available_ids', [])
    print(available_ids, "available_ids")
    current_index = data.get('current_index', 0)
    max_index = len(available_ids) - 1

    # Обновляем индекс, учитывая возможные границы списка
    if step == 1 and current_index < max_index:
        current_index += 1
    elif step == -1 and current_index > 0:
        current_index -= 1
    order_id = available_ids[current_index]

    # Удаление старых сообщений
    message_ids = data.get('message_ids', [])
    await asyncio.gather(*(callback.bot.delete_message(callback.message.chat.id, msg_id) for msg_id in message_ids))

    # Отправка новой группы сообщений
    media_group = await send_order_by_id(order_id)
    messages = await callback.bot.send_media_group(callback.message.chat.id, media_group)
    new_message_ids = [msg.message_id for msg in messages]
    message_1 = await callback.bot.send_message(callback.message.chat.id, "Выберите действие:",
                                                reply_markup=select_order_kb)
    new_message_ids.append(message_1.message_id)
    await state.update_data(index=order_id, current_index=current_index, message_ids=new_message_ids)


# @callback_query_handler(next_order_see, text='next_oder', state=Form.select_order_st)
async def next_order_see(callback: types.CallbackQuery, state: FSMContext):
    if not (data := await state.get_data()).get('available_ids'):
        available_ids = await get_next_available_index()
        print(available_ids)
        await state.update_data(available_ids=available_ids)
    await change_order_see(callback, state, 1)


# @callback_query_handler(next_order_see, text='prev_oder', state=Form.select_order_st)
async def prev_order_see(callback: types.CallbackQuery, state: FSMContext):
    if not (data := await state.get_data()).get('available_ids'):
        available_ids = await get_next_available_index()
        await state.update_data(available_ids=available_ids)
    await change_order_see(callback, state, -1)


async def accept_order(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    order_id = data.get('index')  # Предположим, что ID текущего заказа хранится в состоянии
    print(order_id, "data")

    worker_name = callback.from_user.username  # Получаем имя пользователя, который нажал на кнопку
    query = "UPDATE tasks SET order_status = 'booked', worker_name = %s WHERE id = %s;"
    await insert_data(query, worker_name, order_id)
    await callback.message.edit_text("Заказ подтверждён и забронирован.", reply_markup=select_order_kb)


# @callback_query_handler(exit_from_orders_show, text='exit_wrk_lk', state=Form.select_order_st)
async def exit_from_orders_show(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Добро пожаловать', reply_markup=main_menu_kb)
    await Form.main_menu.set()


async def see_my_booked_orders(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.username in specialists:
        available_ids = await get_next_booked_index()
        if not available_ids:
            await callback.bot.send_message(callback.message.chat.id, "Нет доступных заявок.")
            return
        first_available_id = available_ids[0]  # Берем первый ID из списка доступных

        # Очищаем предыдущие данные
        await state.update_data(index=0, message_ids=[], available_ids=available_ids, current_index=0)

        media_group = await send_order_by_id(first_available_id)
        messages = await callback.bot.send_media_group(callback.message.chat.id, media_group)
        message_ids = [msg.message_id for msg in messages]
        message_1 = await callback.bot.send_message(callback.message.chat.id, "Выберите действие:",
                                                    reply_markup=select_order_kb)
        message_ids.append(message_1.message_id)

        # Обновление данных в состоянии
        await state.update_data(message_ids=message_ids)
        await Form.select_order_st.set()  # Установка состояния, если это необходимо
    else:
        await bot.answer_callback_query(callback.id)
        await callback.message.edit_text('Вы не в списке исполнителей', reply_markup=worker_lk_kb)


# @callback_query_handler(next_order_see, text='next_oder', state=Form.select_order_st)


# @callback_query_handler(next_order_see, text='next_oder', state=Form.select_order_st)
async def next_order_see_booked(callback: types.CallbackQuery, state: FSMContext):
    if not (data := await state.get_data()).get('booked_ids'):
        available_ids = await get_next_booked_index()
        await state.update_data(available_ids=available_ids)
    await change_order_see(callback, state, 1)


async def prev_order_see_booked(callback: types.CallbackQuery, state: FSMContext):
    if not (data := await state.get_data()).get('booked_ids'):
        available_ids = await get_next_booked_index()
        await state.update_data(available_ids=available_ids)
    await change_order_see(callback, state, -1)


def register_handlers_worker(dp: Dispatcher):
    dp.register_callback_query_handler(see_my_order, text='lk_worker', state=Form.main_menu)
    dp.register_callback_query_handler(back_2, lambda callback: callback.data == 'back_2', state='*')
    dp.register_callback_query_handler(registration, lambda callback: callback.data == 'registration',
                                       state=Form.main_menu)
    dp.register_callback_query_handler(process_registration, lambda callback: callback.data.startswith('spec_'),
                                       state=Form.registration)
    dp.register_callback_query_handler(confirm_yes, lambda callback: callback.data == 'yes',
                                       state=Form.confirm_registration)
    dp.register_callback_query_handler(confirm_no, lambda callback: callback.data == 'no',
                                       state=Form.confirm_registration)
    dp.register_callback_query_handler(enter_worker_lk, text='enter', state=Form.worker_lk)
    dp.register_callback_query_handler(exit_from_orders_show, text='exit_wrk_lk', state=Form.select_order_st)
    dp.register_callback_query_handler(next_order_see, text='next_oder', state=Form.select_order_st)
    dp.register_callback_query_handler(prev_order_see, text='prev_order', state=Form.select_order_st)
    dp.register_callback_query_handler(accept_order, text='accept_order', state=Form.select_order_st)
    dp.register_callback_query_handler(see_my_booked_orders, text='worker_orders', state=Form.worker_lk)
    dp.register_callback_query_handler(next_order_see_booked, text='next_oder_booked',
                                       state=Form.select_order_st_booked)
    dp.register_callback_query_handler(prev_order_see_booked, text='prev_oder_booked',
                                       state=Form.select_order_st_booked)
