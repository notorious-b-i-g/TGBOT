from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

worker_lk_kb = InlineKeyboardMarkup(row_wide=2)
w_b1 = InlineKeyboardButton(text='Регистрация', callback_data='registration')
w_b2 = InlineKeyboardButton(text='Активные заявки', callback_data='enter')
w_b3 = InlineKeyboardButton(text='Мои заявки', callback_data='worker_orders')
w_b4 = InlineKeyboardButton(text='Назад', callback_data='back_2')

confirm_kb = InlineKeyboardMarkup(row_wide=2)
yes_button = InlineKeyboardButton(text='Да', callback_data='yes')
no_button = InlineKeyboardButton(text='Нет', callback_data='no')
confirm_kb.add(yes_button, no_button)
worker_lk_kb.add(w_b1, w_b2)
worker_lk_kb.add(w_b3)
worker_lk_kb.add(w_b4)

worker_spec_select_kb = InlineKeyboardMarkup(row_width=2)
w_spec_1 = InlineKeyboardButton(text="Электрик", callback_data='spec_electric')
w_spec_2 = InlineKeyboardButton(text="Трубочист", callback_data='spec_master')
w_spec_3 = InlineKeyboardButton(text="Глиномес", callback_data='spec_dark_holm')
w_spec_back = InlineKeyboardButton(text='Выход', callback_data='back_1')

worker_spec_select_kb.add(w_spec_1, w_spec_2)
worker_spec_select_kb.add(w_spec_3)

select_order_kb = InlineKeyboardMarkup(row_width=2)
accept_order_b = InlineKeyboardButton(text='Принять заявку', callback_data='accept_order')
submit_order_b = InlineKeyboardButton(text='Сдать заявку', callback_data='submit_order')
decline_order_b = InlineKeyboardButton(text='Отклонить заявку', callback_data='decline_order')
next_order_b = InlineKeyboardButton(text='Следующая заявка', callback_data='next_oder')
prev_order_b = InlineKeyboardButton(text='Предыдущая заявка', callback_data='prev_order')
exit_wrk_lk_b = InlineKeyboardButton(text='Выход', callback_data='exit_wrk_lk')

select_order_kb.add(accept_order_b)
select_order_kb.add(prev_order_b, next_order_b)
select_order_kb.add(exit_wrk_lk_b)

select_order_kb_booked = InlineKeyboardMarkup(row_width=2)

select_order_kb_booked.add(decline_order_b , submit_order_b)
select_order_kb_booked.add(prev_order_b, next_order_b)
select_order_kb_booked.add(exit_wrk_lk_b)
