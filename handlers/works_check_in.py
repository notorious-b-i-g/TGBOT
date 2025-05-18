from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher
from create_bot import dp, bot
from aiogram.dispatcher.filters import Text
from data_base import sqlite_db
from data_base import works_db_create
import sqlite3
from keybords.test import object_name
from states.states import *
from keybords.client_kb import *
import time



@dp.callback_query_handler(lambda callback: callback.data.startswith('button'), state=FSMAdmin.check_in_state)
async def object_name_callback(callback: types.CallbackQuery, state: FSMContext):
    # Получаем значение callback_data, например 'button1', 'button2' и т.д.
    button_data = callback.data

    # Вызываем функцию object_name, передавая ей значение callback_data
    button_name = await object_name(button_data)

    if button_name is not None:
        print('Нажата кнопка с названием объекта:', button_name)

        # Создаем словарь для сохранения данных и добавляем элемент 'object_name'
        async with state.proxy() as data_dict:
            data_dict['object_name'] = button_name  # Сохраняем обновленное значение current_page
            print(data_dict)
        # Устанавливаем состояние FSMAdmin.today_date, чтобы ожидать ввод сегодняшней даты
        await FSMAdmin.today_date.set()
        await callback.message.answer("Укажите сегодняшнюю дату в формате год.месяц.день")

        # Сохраняем словарь data_dict в контекст состояния




@dp.message_handler(state=FSMAdmin.today_date)
async def today_date_input(message: types.Message, state: FSMContext):
    today_date = message.text
    # Получаем словарь data_dict из контекста состояния
    data_dict = await state.get_data()
    data_dict['today_date'] = today_date

    await state.update_data(data_dict)

    print(data_dict)
    await message.answer('Напишите, какие работы были проведены (одинм сообщеением)')

    await FSMAdmin.works_completed.set()

@dp.message_handler(state=FSMAdmin.works_completed)
async def works_completed_input(message: types.Message, state: FSMContext):
    works_completed = message.text
    # Получаем словарь data_dict из контекста состояния
    data_dict = await state.get_data()
    data_dict['works_completed'] = works_completed

    await state.update_data(data_dict)
    print(data_dict)
    await message.answer('Какие реагенты были привезены на объект')

    await FSMAdmin.chemical.set()

@dp.message_handler(state=FSMAdmin.chemical)
async def chemical_input(message: types.Message, state: FSMContext):
    chemical = message.text
    # Получаем словарь data_dict из контекста состояния
    data_dict = await state.get_data()
    data_dict['chemical'] = chemical

    await state.update_data(data_dict)

    print(data_dict)
    await message.answer('Напишите сумму оплаты, которую вы получили на руки')


    await FSMAdmin.payday.set()

@dp.message_handler(state=FSMAdmin.payday)
async def payday_input(message: types.Message, state: FSMContext):
    payday = message.text
    # Получаем словарь data_dict из контекста состояния
    data_dict = await state.get_data()
    data_dict['payday'] = payday
    await state.update_data(data_dict)
    await confirmed_enter1(message, state)

async def confirmed_enter1(message: types.Message, state: FSMContext):
    data_dict = await state.get_data()

    # Формируем строку со значениями из data_dict
    values_string = f"Объект: {data_dict['object_name']}\n"
    values_string += f"Дата: {data_dict['today_date']}\n"
    values_string += f"Работы проведены: {data_dict['works_completed']}\n"
    values_string += f"Реагенты: {data_dict['chemical']}\n"
    values_string += f"Сумма оплаты: {data_dict['payday']}"

    # Отправляем сообщение с клавиатурой
    await bot.send_message(message.chat.id, text=f"Всё верно?\n{values_string}", reply_markup=confirmed_kb)
    await FSMAdmin.confirmed.set()

async def confirmed_enter2(message: types.Message, state: FSMContext):
    data_dict = await state.get_data()

    # Формируем строку со значениями из data_dict
    values_string = f"Объект: {data_dict['object_name']}\n"
    values_string += f"Дата: {data_dict['today_date']}\n"
    values_string += f"Работы проведены: {data_dict['works_completed']}\n"
    values_string += f"Реагенты: {data_dict['chemical']}\n"
    values_string += f"Сумма оплаты: {data_dict['payday']}"

    # Отправляем сообщение с клавиатурой
    await bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=f"Всё верно?\n{values_string}", reply_markup=confirmed_kb)
    await FSMAdmin.confirmed.set()



@dp.callback_query_handler(lambda callback: callback.data == 'back3', state='*')
async def back_into_check_in_menu(callback: types.CallbackQuery, state: FSMContext):
    await FSMAdmin.edit_check_in.set()

    await confirmed_enter2(callback.message, state)


@dp.callback_query_handler(text='all_right', state=FSMAdmin.confirmed)
async def insert_data_dict(callback: types.CallbackQuery, state: FSMContext):
    data_dict = await state.get_data()
    del data_dict['current_page']


    await callback.message.edit_text(text='Спасибо, данные записаны')
    conn = sqlite3.connect('works.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO works VALUES (?, ?, ?, ?, ?, ?, ?)', tuple(data_dict.values()))
    conn.commit()
    conn.close()

    time.sleep(2)

    await FSMAdmin.lk.set()
    await callback.message.edit_text(text="Добро пожаловать в главное меню.", reply_markup=lkkb)

    #insert_data_dict(data_dict)

















