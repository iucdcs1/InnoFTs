from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    start = State()


class PassengerFindRoute(StatesGroup):
    set_route = State()
    set_date = State()
    set_time = State()
    set_value = State()
    set_seats_amount = State()
    final = State()
