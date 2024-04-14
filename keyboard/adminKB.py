from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

admin_lk_kb = InlineKeyboardMarkup(row_width=1)
show_req_b = InlineKeyboardButton(text='Посмотреть заявки на регистрацию', callback_data='show_req')
show_req_a = InlineKeyboardButton(text='Редактироать пользователей', callback_data='edit_users')

admin_lk_kb.add(show_req_b,show_req_a)