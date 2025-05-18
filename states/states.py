from aiogram.dispatcher.filters.state import State, StatesGroup


# Перечисление состояний для машины состояний
class FSMAdmin(StatesGroup):
    add_new_object_state = State()
    remove_object_state = State()

    number_add = State()
    password_add = State()
    admin_rule = State()
    #ExportStates = State()

    password_enter = State()
    number = State()
    lk = State()

    edit_menu_state = State()
    edit_name_state = State()
    edit_number_state = State()
    edit_tabel_state = State()
    edit_post_state = State()

    check_in_state = State()

    today_date = State()
    works_completed = State()
    chemical = State()
    payday = State()
    confirmed = State()

    edit_check_in = State()

    today_date_edit = State()
    object_edit = State()
    works_completed_edit = State()
    chemical_edit = State()
    payday_edit = State()
    confirmed_edit = State()