from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram_calendar import SimpleCalendarCallback, SimpleCalendar

from APIs.DB.db_requests import get_routes_filtered
from keyboards.inline import inline_choose_route_markup, inline_main_routs_markup
from keyboards.mainKB import passenger_main_kb
from keyboards.reply import reply_date_now_markup
from states import PassengerFindRoute
from utilities.changeState import change_state
from utilities.checkValidDate import is_valid_date
from utilities.regex import time_pattern_interval_first, time_pattern_interval_second, time_pattern_interval_third, \
    time_pattern_single_first, time_pattern_single_second, time_pattern_interval_fourth
from utilities.writeRouteInfo import write_route_info

Passenger_router = Router()


@Passenger_router.message(F.text == 'Найти попутку')
async def start_passenger_handle(message: Message):
    await message.answer(text='Выберите место отправления:',
                         reply_markup=await inline_main_routs_markup())


@Passenger_router.callback_query(F.data.startswith('return_fd'))
async def return_to_passenger_menu(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer('Открыто меню попутчика', reply_markup=passenger_main_kb)


@Passenger_router.callback_query(F.data.startswith('chosen_first_destination'))
async def end_point_passanger_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    place_id = int(callback.data.split('_')[3])
    await state.update_data(route_start=place_id)
    await callback.message.answer(text='Выберите место назначения:',
                                  reply_markup=await inline_main_routs_markup(chosen=place_id))


@Passenger_router.callback_query(F.data.startswith('return_sd'))
async def return_to_passenger_menu(callback: CallbackQuery):
    await callback.message.edit_text(text='Выберите место отправления:', reply_markup=await inline_main_routs_markup())


@Passenger_router.callback_query(F.data.startswith('chosen_second_destination'))
async def end_point_passanger_handler(callback: CallbackQuery, state: FSMContext):
    place_id = int(callback.data.split('_')[3])
    await state.update_data(route_end=place_id)
    await change_state(state, PassengerFindRoute.set_date)
    await callback.message.answer(
        text='отлично, мне надо знать когда вы планируете поездку.'
        , reply_markup=reply_date_now_markup())


@Passenger_router.message(PassengerFindRoute.set_date)
async def get_passenger_date(message: Message, state: FSMContext):
    if not is_valid_date(message.text.replace(' ', '')):
        return await message.answer('я вас не понял, введите дату формата DD.MM.YYYY',
                                    reply_markup=reply_date_now_markup())
    await state.update_data(date=message.text)
    await change_state(state, PassengerFindRoute.set_time)
    await message.answer(
        text='теперь yажите пожалуста время.\nВ ведите интервал времени в формате HH:MM - HH:MM или HH:MM если ищете водителей на конкретное время.')


@Passenger_router.message(PassengerFindRoute.set_time)
async def get_passenger_time(message: Message, state: FSMContext):
    correct_interval = time_pattern_interval_first.fullmatch(
        message.text) is not None or time_pattern_interval_second.fullmatch(
        message.text) is not None or time_pattern_interval_third.fullmatch(message.text) is not None
    correct_single = time_pattern_single_first.fullmatch(
        message.text) is not None or time_pattern_single_second.fullmatch(
        message.text) is not None or time_pattern_interval_fourth.fullmatch(message.text) is not None
    if not correct_interval and not correct_single:
        return await message.answer(text='я вас не понял, введите ещё раз.')
    await state.update_data(time=message.text)
    await change_state(state, PassengerFindRoute.set_value)
    await message.answer(text='супер, введите пожалуйста сколько вы готовы заплатить за поездку.')


@Passenger_router.message(PassengerFindRoute.set_value, F.text.isdigit())
async def get_passenger_value(message: Message, state: FSMContext):
    await state.update_data(cost=message.text)
    await change_state(state, PassengerFindRoute.set_seats_amount)
    await message.answer(text='ура, остался последний шаг, сколько мест в салоне вам потребуеться?')


@Passenger_router.message(PassengerFindRoute.set_value)
async def get_passenger_value_is_not_digit(message: Message):
    await message.answer(text='пожалуйста введите число.')


@Passenger_router.message(PassengerFindRoute.set_seats_amount, F.text.isdigit())
async def get_passenger_seats_amount(message: Message, state: FSMContext):
    await state.update_data(required_places=message.text)
    await message.answer(text='ищем подходящих водителей...')
    await change_state(state, PassengerFindRoute.final)
    data = await state.get_data()
    place_from = data['route_start']
    place_to = data['route_end']
    seats_amount = int(data['required_places'])
    cost = int(data['cost'])
    date = str(data['date'])
    time = str(data['time'])
    routes = await get_routes_filtered(place_from, place_to, seats_amount, cost, date, time)
    routes_ids = list(map(lambda x: x.id, routes))
    if not routes_ids:
        await state.clear()
        return await message.answer('к сожалению подходящих поездок не найдено, попробуйте позже')
    await state.update_data(route_ids=routes_ids)
    await state.update_data(current_index=0)
    await message.answer(text='нашёл кое-что для вас')
    await message.answer(text=write_route_info(routes[0]), reply_markup=inline_choose_route_markup())


@Passenger_router.message(PassengerFindRoute.set_seats_amount)
async def get_passenger_seats_amount_is_not_digit(message: Message):
    await message.answer(text='пожалуйста введите число.')
