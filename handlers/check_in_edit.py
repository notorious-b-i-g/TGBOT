from aiogram import Bot, types
from .works_check_in import *
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from states.states import *
from keybords.client_kb import *
from keybords.test import send_inline_keyboard


@dp.callback_query_handler(text='mistake', state='*')
async def check_in_edit(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text='Выберите пункт, который хотите исправить', reply_markup=edit_works_kb)
    await FSMAdmin.edit_check_in.set()

@dp.callback_query_handler(text='edit_object', state=FSMAdmin.edit_check_in)
async def object_edit(callback: types.CallbackQuery, state: FSMContext):
    test_kb = await send_inline_keyboard(1)
    await callback.message.edit_text(text='Выберите новый объект', reply_markup=test_kb)
    await FSMAdmin.object_edit.set()

@dp.callback_query_handler(lambda callback: callback.data.startswith('button'), state=FSMAdmin.object_edit)
async def object_name_callback(callback: types.CallbackQuery, state: FSMContext):
    # Получаем значение callback_data, например 'button1', 'button2' и т.д.
    button_data = callback.data

    # Вызываем функцию object_name, передавая ей значение callback_data
    button_name = await object_name(button_data)

    if button_name is not None:
        print('Нажата кнопка с названием объекта:', button_name)

        # Создаем словарь для сохранения данных и добавляем элемент 'object_name'
        async with state.proxy() as data_dict:
            #data_dict.pop('current_page')
            data_dict['object_name'] = button_name  # Сохраняем обновленное значение current_page
            print(data_dict)

            await callback.message.edit_text(text='Выберите пункт, который хотите исправить', reply_markup=edit_works_kb)
            await FSMAdmin.edit_check_in.set()



@dp.callback_query_handler(text='edit_date', state=FSMAdmin.edit_check_in)
async def today_date_edit1(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text="Введите новую дату")
    await FSMAdmin.today_date_edit.set()

@dp.message_handler(state=FSMAdmin.today_date_edit)
async def today_date_edit(message: types.Message, state: FSMContext):
    today_date = message.text
    # Получаем словарь data_dict из контекста состояния
    data_dict = await state.get_data()
    data_dict['today_date'] = today_date

    await state.update_data(data_dict)

    print(data_dict)
    await bot.send_message(message.chat.id, text='Выберите пункт, который хотите исправить', reply_markup=edit_works_kb)
    await FSMAdmin.edit_check_in.set()



#Изменить комментарий
@dp.callback_query_handler(text='edit_komment', state=FSMAdmin.edit_check_in)
async def komment_edit1(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text="Напишите, какие работы были проведены (одинм сообщеением)")
    await FSMAdmin.works_completed_edit.set()

@dp.message_handler(state=FSMAdmin.works_completed_edit)
async def works_completed_edit1(message: types.Message, state: FSMContext):
    works_completed = message.text
    # Получаем словарь data_dict из контекста состояния
    data_dict = await state.get_data()
    data_dict['works_completed'] = works_completed
    await state.update_data(data_dict)

    await bot.send_message(message.chat.id, text='Выберите пункт, который хотите исправить', reply_markup=edit_works_kb)
    await FSMAdmin.edit_check_in.set()


#Изменить реагенты
@dp.callback_query_handler(text='edit_chemical', state=FSMAdmin.edit_check_in)
async def komment_edit2(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text="Какие реагенты были привезены на объект?")
    await FSMAdmin.works_completed_edit.set()
    await FSMAdmin.chemical_edit.set()

@dp.message_handler(state=FSMAdmin.chemical_edit)
async def chemical_input(message: types.Message, state: FSMContext):
    chemical = message.text
    # Получаем словарь data_dict из контекста состояния
    data_dict = await state.get_data()
    data_dict['chemical'] = chemical
    await state.update_data(data_dict)

    await bot.send_message(message.chat.id, text='Выберите пункт, который хотите исправить', reply_markup=edit_works_kb)
    await FSMAdmin.edit_check_in.set()


#Изменить оплату
@dp.callback_query_handler(text='edit_payday', state=FSMAdmin.edit_check_in)
async def pay_day_edit1(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text="Какую сумму оплаты вы получили?")
    await FSMAdmin.works_completed_edit.set()
    await FSMAdmin.payday_edit.set()

@dp.message_handler(state=FSMAdmin.payday_edit)
async def chemical_input(message: types.Message, state: FSMContext):
    payday = message.text
    # Получаем словарь data_dict из контекста состояния
    data_dict = await state.get_data()
    data_dict['payday'] = payday
    await state.update_data(data_dict)

    await bot.send_message(message.chat.id, text='Выберите пункт, который хотите исправить', reply_markup=edit_works_kb)
    await FSMAdmin.edit_check_in.set()

