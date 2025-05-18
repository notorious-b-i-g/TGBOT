from aiogram import Bot, types
from .client import *
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from keybords.client_kb import *
import sqlite3

@dp.callback_query_handler(text='edit_menu', state='*')
async def edit_menu(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text='Выберите пункт, который хотите изменить', reply_markup=edit_menu_kb)


@dp.callback_query_handler(text='edit_name', state='*')
async def edit_name(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Введите новое имя')
    await FSMAdmin.edit_name_state.set()
    await callback.answer()

@dp.callback_query_handler(text='edit_number', state='*')
async def edit_name(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Введите новый номер')
    await FSMAdmin.edit_number_state.set()
    await callback.answer()
@dp.callback_query_handler(text='edit_tabel', state='*')
async def edit_name(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Введите новый табельный номер')
    await FSMAdmin.edit_tabel_state.set()
    await callback.answer()
@dp.callback_query_handler(text='edit_post', state='*')
async def edit_name(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Введите новую должность')
    await FSMAdmin.edit_post_state.set()
    await callback.answer()
@dp.message_handler(state=FSMAdmin.edit_name_state)
async def new_name_enter(message: types.Message, state: FSMContext):
    data = await state.get_data()
    password = data.get('password')
    new_name = message.text
    print(new_name)
    print(password)

    with sqlite3.connect('works.db') as conn:
        cur = conn.cursor()
        # Обновите значение в базе данных
        cur.execute('UPDATE users SET name = ? WHERE password = ?', (new_name, password))
        conn.commit()
        await message.answer("Имя изменено")
        await FSMAdmin.lk.set()
        await message.answer('Выберите пункт, который хотите изменить', reply_markup=edit_menu_kb)


@dp.message_handler(state=FSMAdmin.edit_number_state)
async def new_name_enter(message: types.Message, state: FSMContext):
    data = await state.get_data()
    password = data.get('password')
    new_number = message.text
    print(new_number)
    print(password)

    with sqlite3.connect('works.db') as conn:
        cur = conn.cursor()
        # Обновите значение в базе данных
        cur.execute('UPDATE users SET number = ? WHERE password = ?', (new_number, password))
        conn.commit()
        await message.answer("Номер изменён")
        await FSMAdmin.lk.set()
        await message.answer('Выберите пункт, который хотите изменить', reply_markup=edit_menu_kb)

@dp.message_handler(state=FSMAdmin.edit_tabel_state)
async def new_name_enter(message: types.Message, state: FSMContext):
    data = await state.get_data()
    password = data.get('password')
    new_tabel = message.text
    print(new_tabel)
    print(password)

    with sqlite3.connect('works.db') as conn:
        cur = conn.cursor()
        # Обновите значение в базе данных
        cur.execute('UPDATE users SET tabel = ? WHERE password = ?', (new_tabel, password))
        conn.commit()
        await message.answer("Табельный номер изменён")
        await FSMAdmin.lk.set()
        await message.answer('Выберите пункт, который хотите изменить', reply_markup=edit_menu_kb)

@dp.message_handler(state=FSMAdmin.edit_post_state)
async def new_name_enter(message: types.Message, state: FSMContext):
    data = await state.get_data()
    password = data.get('password')
    new_post = message.text
    print(new_post)
    print(password)

    with sqlite3.connect('works.db') as conn:
        cur = conn.cursor()
        # Обновите значение в базе данных
        cur.execute('UPDATE users SET post = ? WHERE password = ?', (new_post, password))
        conn.commit()
        await message.answer("Должность изменена")
        await FSMAdmin.lk.set()
        await message.answer('Выберите пункт, который хотите изменить', reply_markup=edit_menu_kb)