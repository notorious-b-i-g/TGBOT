from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
import json
b1 = KeyboardButton('/start')


main_menu_kb = InlineKeyboardMarkup(row_width=2)
mmb1 = InlineKeyboardButton(text="Составить заявку 📝", callback_data='make_order')
mmb2 = InlineKeyboardButton(text='Мои заявки 📗', callback_data='my_orders')
mmb3 = InlineKeyboardButton(text='Информация ℹ️', callback_data='info')
mmb4 = InlineKeyboardButton(text='Настройки 🛠', callback_data='settings')
mmb5 = InlineKeyboardButton(text='Для работников 👷‍♂️', callback_data='lk_worker')

main_menu_kb.row(mmb2, mmb1)
main_menu_kb.row(mmb3, mmb4)
main_menu_kb.row(mmb5)

# Кнопки в выборе спеца
with open('spec_names.json', 'r', encoding='utf-8') as f:
    spec_names = json.load(f)
buttons = []

for i, spec_name in enumerate(list(spec_names.values())):
    button = InlineKeyboardButton(text=f'{spec_name}', callback_data=f'spec_name_{i}')
    buttons.append(button)
spec_keyboard = InlineKeyboardMarkup(row_width=2)

# Разбиваем кнопки на строки по две кнопки в каждой
for i in range(0, len(buttons), 2):
    spec_keyboard.row(*buttons[i:i+2])

spec_back = InlineKeyboardButton(text='Назад', callback_data='back_1')
spec_keyboard.add(spec_back)

# Кнопки выбора проблемы
# prob_keyboard = InlineKeyboardButton(row_width=3)
# prob_ = InlineKeyboardButton(text=)



# Подтвержение заявки

confirm_order = InlineKeyboardMarkup(row_width=1)
confirm_all = InlineKeyboardButton(text='Да, верно ✅', callback_data='all_right')
edit_someth = InlineKeyboardButton(text='Нет, редактировать ✏️', callback_data='edit_order')
confirm_order.add(confirm_all).add(edit_someth)

# Что редактировать
edit_order_kb = InlineKeyboardMarkup(row_width=2)
b_edit_spec = InlineKeyboardButton(text='Специалиста', callback_data='edit_spec')
b_edit_photo = InlineKeyboardButton(text='Фото', callback_data='edit_photo')
b_edit_prob = InlineKeyboardButton(text='Задачу', callback_data='edit_prob')
edit_order_kb.add(b_edit_spec, b_edit_prob)
edit_order_kb.add(b_edit_photo)

# Для ректирование фото
edit_photo_kb = InlineKeyboardMarkup(row_width=1)
b_add_photo = InlineKeyboardButton(text='Добавить ещё📎', callback_data='add_more_photo')
b_reset_photo = InlineKeyboardButton(text='Доабавить заново🖇', callback_data='reset_photo')
edit_photo_kb.add(b_add_photo)
edit_photo_kb.add(b_reset_photo)

select_order_kb = InlineKeyboardMarkup(row_width=2)
decline_order_b = InlineKeyboardButton(text='❌ Удалить заявку', callback_data='delete_order')
next_order_b = InlineKeyboardButton(text='Следующая заявка ➡️', callback_data='next_oder')
prev_order_b = InlineKeyboardButton(text='⬅️ Предыдущая заявка', callback_data='prev_order')
chat_order_b = InlineKeyboardButton(text='Чат по заявке📱', callback_data='chat_order')
exit_wrk_lk_b = InlineKeyboardButton(text='Выход', callback_data='exit_wrk_lk')

select_order_kb.add(decline_order_b, chat_order_b)
select_order_kb.add(prev_order_b, next_order_b)
select_order_kb.add(exit_wrk_lk_b)

exit_from_chat_b = KeyboardButton(text='/выход')
chat_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

chat_kb.add(exit_from_chat_b)