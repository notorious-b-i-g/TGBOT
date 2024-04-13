import json

from aiogram import types, Dispatcher
from keyboard.workerKB import *
from keyboard.clientKB import main_menu_kb
from states import Form
from create_bot import dp, bot, FSMContext


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
    w_specialist_name = spec_names.get(w_specialist_key, 'Неизвестный специалист')  # Получаем имя или возвращаем заглушку
    await callback.answer()  # Подтверждаем обработку колбэка
    await state.update_data(specialist_name=w_specialist_name)

    await state.set_state(Form.confirm_registration)
    await callback.message.edit_text(f'Вы выбрали специализацию {w_specialist_name}, Оставить запрос на регистрацию?', reply_markup=confirm_kb)


async def confirm_yes(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    await bot.send_message(571294067,
                           f"Пользователь {user_data['username']} ({user_data['user_id']}) хочет зарегистрироваться как {user_data['specialist_name']}.")
    await Form.main_menu.set()
    await callback.message.edit_text('Запрос на регистрацию отправлен.' )

async def confirm_no(callback: types.CallbackQuery, state: FSMContext):
    await Form.main_menu.set()
    await callback.message.edit_text('Регистрация отменена.')


def register_handlers_worker(dp : Dispatcher):
    dp.register_callback_query_handler(see_my_order, text='lk_worker', state=Form.main_menu)
    dp.register_callback_query_handler(back_2, lambda callback: callback.data == 'back_2', state='*')
    dp.register_callback_query_handler(registration, lambda callback: callback.data == 'registration', state='*')
    dp.register_callback_query_handler(process_registration, lambda callback: callback.data.startswith('spec_') ,
                                       state=Form.registration)
    dp.register_callback_query_handler(confirm_yes, lambda callback: callback.data == 'yes', state=Form.confirm_registration)
    dp.register_callback_query_handler(confirm_no, lambda callback: callback.data == 'no', state=Form.confirm_registration)