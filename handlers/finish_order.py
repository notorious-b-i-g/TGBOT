import states
from aiogram import types, Dispatcher
from keyboard.clientKB import *
from states import Form
from create_bot import bot, FSMContext
import json
import asyncio
import datetime

from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from typing import List, Union
from db import insert_data, get_data, insert_task_with_photos


class AlbumMiddleware(BaseMiddleware):
    """This middleware is for capturing media groups."""

    album_data: dict = {}

    def __init__(self, latency: Union[int, float] = 0.01):
        """
        You can provide custom latency to make sure
        albums are handled properly in highload.
        """
        self.latency = latency
        super().__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        if not message.media_group_id:
            return

        try:
            self.album_data[message.media_group_id].append(message)
            raise CancelHandler()  # Tell aiogram to cancel handler for this group element
        except KeyError:
            self.album_data[message.media_group_id] = [message]
            await asyncio.sleep(self.latency)

            message.conf["is_last"] = True
            data["album"] = self.album_data[message.media_group_id]

    async def on_post_process_message(self, message: types.Message, result: dict, data: dict):
        """Clean up after handling our album."""
        if message.media_group_id and message.conf.get("is_last"):
            del self.album_data[message.media_group_id]


# @dp.callback_query_handler(text='make_order', state=Form.main_menu)
async def make_order(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer("Напишите комментарий к работе")
    await state.set_state(Form.problem_description)


# @dp.callback_query_handler(lambda callback: callback.data.startswith('spec_'), state='*')
# @dp.message_handler(state=Form.problem_description)
async def comment(message: types.Message, state: FSMContext):
    problem = message.text
    photos = []
    async with state.proxy() as data_dict:
        data_dict['comment_description'] = problem  # Сохраняем описание проблемы в словаре состояния
        data_dict['photos'] = photos

    await message.answer('Прикрепите фотографии работы')
    # Далее вы можете выполнить любые необходимые действия с данными о специалисте и описанием проблемы
    await Form.wait_foto_finish.set()



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
        await Form.order_confirming_finish.set()  # Переводим состояние в подтверждение заказа


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
    print(12345 , 'add_one_foto')
    await Form.order_confirming_finish.set()


# @callback_query_handler(confirm_of_order, text='edit_order', state=Form.order_confirming)
async def confirm_of_order_finish(callback: types.CallbackQuery, state: FSMContext):

    query = '''
    INSERT INTO tasks (comment_description, finish_photo_ids, end_time)
    VALUES (%s, %s, %s)
    '''
    user_id = callback.from_user.id  # Получаем ID пользователя из объекта callback
    async with state.proxy() as data_dict:
        problem = data_dict.get('comment_description', '')
        photos = data_dict.get('photos', [])  # Убедитесь, что 'photos' сохраняются в состоянии

    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')

    json_file_ids = json.dumps(photos)
    print(problem, json_file_ids, formatted_datetime)

    params = (problem, json_file_ids, formatted_datetime)
    await insert_task_with_photos(query, params)  # Передача параметров корректно
    await callback.message.edit_text(text='Главное меню', reply_markup=main_menu_kb)
    await Form.main_menu.set()


# @callback_query_handler(edit_spec_in_order, text='edit_spec', state=Form.order_confirming)
async def edit_sth_in_order(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text='Редактировать:', reply_markup=edit_order_kb)
    await Form.edit_order_st_finish.set()


# @callback_query_handler(edit_photo, text='edit_photo', state=Form.edit_order_st)
async def edit_photo(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text='Добавить ещё фото или добавить заново', reply_markup=edit_photo_kb)
    await bot.answer_callback_query(callback.id)
    await Form.edit_photo_st_finish.set()


# @callback_query_handler(wait_one_more_photo, text='add_more_photo', state=Form.edit_photo_st)
async def wait_one_more_photo(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Прикрепите фотографии работы')
    await bot.answer_callback_query(callback.id)
    await Form.wait_foto_finish.set()


async def reset_photos(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Добавьте фотографии заново')
    await bot.answer_callback_query(callback.id)
    async with state.proxy() as data_dict:
        data_dict['photos'] = []

    await Form.wait_foto_finish.set()


# @message_handler(reset_state, commands=['reset'], state='*')
async def reset_state(message: types.Message, state: FSMContext):
    print(12345)
    await state.finish()
    #await Form.main_menu.set()


def register_handlers_finish_order(dp: Dispatcher):
    dp.register_callback_query_handler(make_order, text='submit_order', state=Form.select_order_st)
    dp.register_message_handler(comment, state=Form.problem_description)

    dp.register_message_handler(work_foto, is_media_group=True, content_types=types.ContentType.ANY, state=Form.wait_foto_finish)
    dp.register_message_handler(add_one_foto, content_types=['photo'], state=Form.wait_foto_finish)

    # Редактирование заявки
    dp.register_callback_query_handler(confirm_of_order_finish, text='all_right', state=Form.order_confirming_finish)
    dp.register_callback_query_handler(edit_sth_in_order, text='edit_order', state=Form.order_confirming_finish)
    dp.register_callback_query_handler(edit_photo, text='edit_photo', state=Form.edit_order_st_finish)
    dp.register_callback_query_handler(wait_one_more_photo, text='add_more_photo', state=Form.edit_photo_st_finish)
    dp.register_callback_query_handler(reset_photos, text='reset_photo', state=Form.edit_photo_st_finish)

    # Reset
    dp.register_message_handler(reset_state, commands=['reset'], state='*')
