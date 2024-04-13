from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

b1 = KeyboardButton('/start')


main_menu_kb = InlineKeyboardMarkup(row_width=2)
mmb1 = InlineKeyboardButton(text="Составить заявку", callback_data='make_order')
mmb2 = InlineKeyboardButton(text='Мои заявки', callback_data='my_orders')
mmb3 = InlineKeyboardButton(text='Информация', callback_data='info')
mmb4 = InlineKeyboardButton(text='Настройки', callback_data='settings')
mmb5 = InlineKeyboardButton(text='Для работников', callback_data='lk_worker')

main_menu_kb.row(mmb1, mmb2)
main_menu_kb.row(mmb3, mmb4)
main_menu_kb.row(mmb5)

# Кнопки в выборе спеца
spec_keyboard = InlineKeyboardMarkup(row_width=2)
spec_1 = InlineKeyboardButton(text="Электрик", callback_data='spec_electric')
spec_2 = InlineKeyboardButton(text="Трубочист", callback_data='spec_master')
spec_3 = InlineKeyboardButton(text="Глиномес", callback_data='spec_dark_holm')
spec_back = InlineKeyboardButton(text='Назад', callback_data='back_1')

spec_keyboard.add(spec_1, spec_2)
spec_keyboard.add(spec_3)
spec_keyboard.add(spec_back)

# Кнопки выбора проблемы
# prob_keyboard = InlineKeyboardButton(row_width=3)
# prob_ = InlineKeyboardButton(text=)

# Добавление фото
photo_kb = InlineKeyboardMarkup(row_width=1)
add_photo = InlineKeyboardButton(text='Добавить фото', callback_data='add_photo')
cont_order = InlineKeyboardButton(text='Закончить добавление', callback_data='end_add')
photo_kb.add(add_photo)
photo_kb.add(cont_order)

# Подтвержение заявки
confirm_order = InlineKeyboardMarkup(row_width=1)
confirm_all = InlineKeyboardButton(text='Да, верно', callback_data='all_right')
edit_someth = InlineKeyboardButton(text='Нет, редактировать', callback_data='edit_order')
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
b_add_photo = InlineKeyboardButton(text='Добавить ещё', callback_data='add_more_photo')
b_remove_photo = InlineKeyboardButton(text='Удлалить фото', callback_data='remove_photo')
b_reset_photo = InlineKeyboardButton(text='Доабавить заново', callback_data='reset_photo')
edit_photo_kb.add(b_add_photo)
edit_photo_kb.add(b_remove_photo)
edit_photo_kb.add(b_reset_photo)