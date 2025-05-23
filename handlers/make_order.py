import states
import json
import asyncio
import datetime
from aiogram import types, Dispatcher
from keyboard.clientKB import *
from states import Form
from create_bot import bot, FSMContext
from db import db
from support.support_class import List





# @dp.callback_query_handler(text='make_order', state=Form.main_menu)
async def make_order(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.make_order)
    await call.message.edit_text('Выберите специласита', reply_markup=spec_keyboard)


# @dp.callback_query_handler(lambda callback: callback.data.startswith('spec_'), state='*')
async def process_spec_selection(callback: types.CallbackQuery, state: FSMContext):
    # Загрузка списка специалистов из JSON-файла
    with open('spec_names.json', 'r', encoding='utf-8') as f:
        spec_names = json.load(f)
    await bot.answer_callback_query(callback.id)

    # Получаем callback.data и преобразуем в имя специалиста
    specialist_key = callback.data
    specialist_name = spec_names.get(specialist_key, 'Неизвестный специалист')

    await callback.message.answer(f'Вы выбрали специалиста {specialist_name}. Теперь опишите свою задачу.')

    async with state.proxy() as data_dict:
        data_dict['specialist'] = specialist_key  # Сохраняем ключ выбранного специалиста в словаре состояния
        data_dict['specialist_name'] = specialist_name  # Опционально сохраняем и имя специалиста

    await state.set_state(Form.problem_description)


# @dp.message_handler(state=Form.problem_description)
async def what_to_do(message: types.Message, state: FSMContext):
    problem = message.text
    async with state.proxy() as data_dict:
        data_dict['problem_description'] = problem
        data_dict['photos'] = []

    await message.answer('Прикрепите фотографии работы')
    # Далее вы можете выполнить любые необходимые действия с данными о специалисте и описанием проблемы
    await Form.wait_foto.set()



# @dp.message_handler(state=Form.wait_foto)
async def work_foto(message: types.Message, album: List[types.Message], state: FSMContext):
    media_group = types.MediaGroup()
    async with state.proxy() as data_dict:
        specialist_name = data_dict.get('specialist_name', '')
        problem = data_dict.get('problem_description', '')
        photos = data_dict.get('photos')

        # Формируем медиа группу из полученного альбома
        for idx, obj in enumerate(album):
            if obj.photo:
                photo = obj.photo[-1]  # Берем самое большое изображение
                photos.append(photo.file_id)
                if idx == 0:
                    # Для первой фотографии добавляем подпись
                    media_group.attach_photo(photo.file_id, caption=f'Специалист: {specialist_name}\nЗадача: {problem}')
                else:
                    media_group.attach_photo(photo.file_id)
            else:
                # Пропускаем, если в альбоме не фото (или обработать другие типы медиа)
                continue
        # Отправляем медиа группу

        await message.answer_media_group(media=media_group)
        await message.answer(text='Всё верно?', reply_markup=confirm_order)
        await Form.order_confirming.set()  # Переводим состояние в подтверждение заказа


# @message_handler(add_one_foto, content_types=['photo'], state=Form.wait_foto)
async def add_one_foto(message: types.Message, state: FSMContext):
    photo = message.photo[-1]  # Берем последний элемент списка, который является самым большим по размеру
    async with state.proxy() as data_dict:
        specialist_name = data_dict.get('specialist_name', '')  # Получение значения по ключу specialist_name
        problem = data_dict.get('problem_description', '')
        photos = data_dict.get('photos')
        photos.append(photo.file_id)  # Добавление нового фото в список

    media_group = types.MediaGroup()
    for file_id in photos:
        if photos.index(file_id) == 0:
            # Для первой фотографии добавляем подпись
            media_group.attach_photo(file_id, caption=f'Специалист: {specialist_name}\nЗадача: {problem}')
        else:
            media_group.attach_photo(file_id)

    await message.answer_media_group(media=media_group)
    await message.answer(text='Всё верно?', reply_markup=confirm_order)
    await Form.order_confirming.set()


# @callback_query_handler(confirm_of_order, text='edit_order', state=Form.order_confirming)
async def confirm_of_order(callback: types.CallbackQuery, state: FSMContext):
    # SQL query updated to include user_id field
    query = '''
    INSERT INTO tasks (specialist_name, problem_description, photo_ids, client_name, post_time, order_status, chat_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    '''
    chat_id = callback.message.chat.id  # Получаем ID пользователя из объекта callback
    async with state.proxy() as data_dict:
        specialist_name = data_dict.get('specialist_name', '')
        problem = data_dict.get('problem_description', '')
        photos = data_dict.get('photos', [])  # Ensure photos are saved in state

    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
    json_file_ids = json.dumps(photos)

    name = callback.from_user.username
    if name is None:
        name = callback.from_user.id
    params = (specialist_name, problem, json_file_ids, name, formatted_datetime, 'available', chat_id)
    await db.insert_task_with_photos(query, params)
    await callback.message.edit_text(text='Главное меню', reply_markup=main_menu_kb)
    await Form.main_menu.set()


# @callback_query_handler(edit_spec_in_order, text='edit_spec', state=Form.order_confirming)
async def edit_sth_in_order(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text='Редактировать:', reply_markup=edit_order_kb)
    await Form.edit_order_st.set()


# @callback_query_handler(edit_photo, text='edit_photo', state=Form.edit_order_st)
async def edit_photo(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text='Добавить ещё фото или добавить заново', reply_markup=edit_photo_kb)
    await bot.answer_callback_query(callback.id)
    await Form.edit_photo_st.set()


# @callback_query_handler(wait_one_more_photo, text='add_more_photo', state=Form.edit_photo_st)
async def wait_one_more_photo(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Прикрепите фотографии работы')
    await bot.answer_callback_query(callback.id)
    await Form.wait_foto.set()


# @callback_query_handler(reset_photos, text='reset_photo', state=Form.edit_photo_st)
async def reset_photos(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Добавьте фотографии заново')
    await bot.answer_callback_query(callback.id)
    async with state.proxy() as data_dict:
        data_dict['photos'] = []

    await Form.wait_foto.set()


# @callback_query_handler(edit_comment_start, text='edit_prob', state=Form.edit_order_st)
async def edit_comment_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Ввидите новое описание задачи')
    await bot.answer_callback_query(callback.id)
    await Form.edit_prob_st.set()


# @message_handler(edit_comment, state=Form.edit_prob_st)
async def edit_comment(message: types.Message, state: FSMContext):
    problem = message.text
    async with state.proxy() as data_dict:
        specialist_name = data_dict.get('specialist_name', '')
        data_dict['problem_description'] = problem
        photos = data_dict.get('photos')

    media_group = types.MediaGroup()
    for file_id in photos:
        if photos.index(file_id) == 0:
            # Для первой фотографии добавляем подпись
            media_group.attach_photo(file_id, caption=f'Специалист: {specialist_name}\nЗадача: {problem}')
        else:
            media_group.attach_photo(file_id)

    await message.answer_media_group(media=media_group)
    await message.answer(text='Всё верно?', reply_markup=confirm_order)
    await Form.order_confirming.set()


async def edit_spec_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(text='Выберите специалиста', reply_markup=spec_keyboard)
    await Form.edit_spec_st.set()


async def edit_spec(callback: types.CallbackQuery, state: FSMContext):
    # Загрузка списка специалистов из JSON-файла
    with open('spec_names.json', 'r', encoding='utf-8') as f:
        spec_names = json.load(f)
    # Получаем callback.data и преобразуем в имя специалиста
    specialist_key = callback.data
    specialist_name = spec_names.get(specialist_key, 'Неизвестный специалист')

    await callback.answer()
    async with state.proxy() as data_dict:
        data_dict['specialist'] = specialist_key  # Сохраняем ключ выбранного специалиста в словаре состояния
        data_dict['specialist_name'] = specialist_name  # Опционально сохраняем и имя специалиста
        specialist_name = data_dict.get('specialist_name', '')
        problem = data_dict.get('problem_description')
        photos = data_dict.get('photos')

    media_group = types.MediaGroup()
    for file_id in photos:
        if photos.index(file_id) == 0:
            # Для первой фотографии добавляем подпись
            media_group.attach_photo(file_id, caption=f'Специалист: {specialist_name}\nЗадача: {problem}')
        else:
            media_group.attach_photo(file_id)

    await callback.message.answer_media_group(media=media_group)
    await callback.message.answer(text='Всё верно?', reply_markup=confirm_order)
    await Form.order_confirming.set()


# @message_handler(reset_state, commands=['reset'], state='*')
async def reset_state(message: types.Message, state: FSMContext):
    await state.finish()
    #await Form.main_menu.set()


def register_handlers_make_order(dp: Dispatcher):
    dp.register_callback_query_handler(make_order, text='make_order', state=Form.main_menu)
    dp.register_callback_query_handler(process_spec_selection, lambda callback: callback.data.startswith('spec_'), state=Form.make_order)
    dp.register_message_handler(what_to_do, state=Form.problem_description)
    dp.register_message_handler(work_foto, is_media_group=True, content_types=types.ContentType.ANY, state=Form.wait_foto)
    dp.register_message_handler(add_one_foto, content_types=['photo'], state=Form.wait_foto)

    # Редактирование заявки
    dp.register_callback_query_handler(confirm_of_order, text='all_right', state=Form.order_confirming)
    dp.register_callback_query_handler(edit_sth_in_order, text='edit_order', state=Form.order_confirming)
    dp.register_callback_query_handler(edit_spec_start, text='edit_spec', state=Form.edit_order_st)
    dp.register_callback_query_handler(edit_spec, lambda callback: callback.data.startswith('spec_'), state=Form.edit_spec_st)
    dp.register_callback_query_handler(edit_comment_start, text='edit_prob', state=Form.edit_order_st)
    dp.register_message_handler(edit_comment, state=Form.edit_prob_st)
    dp.register_callback_query_handler(edit_photo, text='edit_photo', state=Form.edit_order_st)
    dp.register_callback_query_handler(wait_one_more_photo, text='add_more_photo', state=Form.edit_photo_st)
    dp.register_callback_query_handler(reset_photos, text='reset_photo', state=Form.edit_photo_st)

    # Reset
    dp.register_message_handler(reset_state, commands=['reset'], state='*')
