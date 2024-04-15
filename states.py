from aiogram.dispatcher.filters.state import StatesGroup, State


class Form(StatesGroup):
    # Состояния в главном меню
    main_menu = State()
    make_order = State()
    my_orders = State()
    bot_info = State()
    settings = State()
    worker_lk = State()

    # Состояния составления задачи
    problem_description = State()
    wait_foto = State()  # Новое состояние для отправления заявки
    is_add_more_photo = State()
    order_confirming = State()
    send_order = State()
    edit_order_st = State()
    registration = State()
    process_registration = State()
    confirm_registration = State()

    # Состояние редактирование задачи
    edit_photo_st = State()
    edit_spec_st = State()
    edit_prob_st = State()

    # Состояния админа
    admin_lk_st = State()
    admin_show_req = State()

    # Состояния работяги
    select_order_st = State()
    select_order_st_booked = State()
    select_order_st_client = State()

    comment_description = State()
    wait_foto_finish = State()
    order_confirming_finish = State()
    edit_order_st_finish = State()
    edit_photo_st_finish = State()
    problem_description_finish = State()
    edit_prob_st_finish = State()
