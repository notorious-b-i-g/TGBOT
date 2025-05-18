from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
import json

worker_lk_kb = InlineKeyboardMarkup(row_wide=2)
w_b1 = InlineKeyboardButton(text='Регистрация👨‍💻', callback_data='registration')
w_b2 = InlineKeyboardButton(text='Доступные заявки📙', callback_data='enter')
w_b3 = InlineKeyboardButton(text='Мои заявки📘', callback_data='worker_orders')
w_b4 = InlineKeyboardButton(text='Назад', callback_data='back_2')

confirm_kb = InlineKeyboardMarkup(row_wide=2)
yes_button = InlineKeyboardButton(text='Да', callback_data='yes')
no_button = InlineKeyboardButton(text='Нет', callback_data='no')
confirm_kb.add(yes_button, no_button)
worker_lk_kb.add(w_b4)


with open('spec_names.json', 'r', encoding='utf-8') as f:
    spec_names = json.load(f)
buttons = []

for i, spec_name in enumerate(list(spec_names.values())):
    button = InlineKeyboardButton(text=f'{spec_name}', callback_data=f'spec_name_{i}')
    buttons.append(button)
worker_spec_select_kb = InlineKeyboardMarkup(row_width=2)

# Разбиваем кнопки на строки по две кнопки в каждой
for i in range(0, len(buttons), 2):
    worker_spec_select_kb.row(*buttons[i:i+2])

w_spec_back = InlineKeyboardButton(text='Выход', callback_data='back_1')
worker_spec_select_kb.add(w_spec_back)

select_order_kb = InlineKeyboardMarkup(row_width=2)
accept_order_b = InlineKeyboardButton(text='Принять заявку ✅', callback_data='accept_order')
submit_order_b = InlineKeyboardButton(text='Сдать заявку 📌', callback_data='submit_order')
decline_order_b = InlineKeyboardButton(text='❌ Отклонить заявку', callback_data='decline_order')
next_order_b = InlineKeyboardButton(text='Следующая заявка ➡️', callback_data='next_oder')
prev_order_b = InlineKeyboardButton(text='⬅️ Предыдущая заявка', callback_data='prev_order')
exit_wrk_lk_b = InlineKeyboardButton(text='Выход', callback_data='exit_wrk_lk')
communicate_customer_b = InlineKeyboardButton(text='Связь с заказчиком📱', callback_data='comm_cust')

select_order_kb.add(accept_order_b)
select_order_kb.add(communicate_customer_b)
select_order_kb.add(prev_order_b, next_order_b)
select_order_kb.add(exit_wrk_lk_b)

select_order_kb_booked = InlineKeyboardMarkup(row_width=2)

select_order_kb_booked.add(decline_order_b , submit_order_b)
select_order_kb_booked.add(prev_order_b, next_order_b)
select_order_kb_booked.add(communicate_customer_b)
select_order_kb_booked.add(exit_wrk_lk_b)

edit_order_kb_finish = InlineKeyboardMarkup(row_width=1)
b_edit_photo_f = InlineKeyboardButton(text='Фото', callback_data='edit_photo_finish')
b_edit_prob_f = InlineKeyboardButton(text='Комментарий', callback_data='edit_prob_finish')
edit_order_kb_finish.add(b_edit_prob_f)
edit_order_kb_finish.add(b_edit_photo_f)

exit_from_chat_b = KeyboardButton(text='/выход')
chat_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

chat_kb.add(exit_from_chat_b)