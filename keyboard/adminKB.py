from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

admin_lk_kb = InlineKeyboardMarkup(row_width=1)
show_req_b = InlineKeyboardButton(text='Посмотреть заявки на регистрацию', callback_data='show_req')
show_req_a = InlineKeyboardButton(text='Редактироать пользователей', callback_data='edit_users')
load_to_excel_b = InlineKeyboardButton(text='Выгрузить данные заявок в excel', callback_data='excel_load')
admin_lk_kb.add(show_req_b, show_req_a)
admin_lk_kb.add(load_to_excel_b)

excel_load_kb = InlineKeyboardMarkup(row_width=3)
time_b_1 = InlineKeyboardButton(text='1 месяц', callback_data='month_one')
time_b_2 = InlineKeyboardButton(text='2 месяца', callback_data='month_two')
time_b_3 = InlineKeyboardButton(text='3 месяца', callback_data='month_three')
excel_load_kb.add(time_b_1, time_b_2, time_b_3)
