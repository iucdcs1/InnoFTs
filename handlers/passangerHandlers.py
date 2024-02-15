from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from APIs.DB.db_requests import get_routes_filtered, get_route
from states import PassengerFindRoute
from keyboards.reply import reply_date_now_markup, reply_main_routs_markup
from keyboards.inline import inline_choose_route_markup
from utilities.checkValidDate import is_valid_date
from utilities.regex import time_pattern_interval_first, time_pattern_interval_second, time_pattern_interval_third, \
    time_pattern_single_first, time_pattern_single_second, time_pattern_interval_fourth
from utilities.changeState import change_state
from utilities.writeRouteInfo import write_route_info

Passenger_router = Router()


@Passenger_router.message(F.text == 'Найти попутку')
async def start_passenger_handle(message: Message, bot: Bot, state: FSMContext):
    await bot.delete_message(message.chat.id, message.message_id)
    await state.set_state(PassengerFindRoute.set_route)
    await message.answer(text='Вам надо выбрать маршрут',
                         reply_markup=reply_main_routs_markup())


@Passenger_router.message(Command(commands=['test_passenger']))
async def test_passenger(message: Message, bot: Bot, state: FSMContext):
    await bot.delete_message(message.chat.id, message.message_id)
    await state.set_state(PassengerFindRoute.set_route)
    await message.answer(text='Привет для того чтобы найти машину, вам надо выбрать маршрут',
                         reply_markup=reply_main_routs_markup())


@Passenger_router.message(PassengerFindRoute.set_route)
async def get_passenger_route(message: Message, bot: Bot, state: FSMContext):
    await bot.delete_message(message.chat.id, message.message_id)
    await state.update_data(route=message.text)
    await change_state(state, PassengerFindRoute.set_date)
    await message.answer(
        text='отлично, мне надо знать когда вы планируете поездку.'
        , reply_markup=reply_date_now_markup())


@Passenger_router.message(PassengerFindRoute.set_date)
async def get_passenger_date(message: Message, bot: Bot, state: FSMContext):
    await bot.delete_message(message.chat.id, message.message_id)
    if not is_valid_date(message.text.replace(' ', '')):
        return await message.answer('я вас не понял, введите дату формата DD.MM.YYYY',
                                    reply_markup=reply_date_now_markup())
    await state.update_data(date=message.text)
    await change_state(state, PassengerFindRoute.set_time)
    await message.answer(
        text='теперь yажите пожалуста время.\nВ ведите интервал времени в формате HH:MM - HH:MM или HH:MM если ищете водителей на конкретное время.')


@Passenger_router.message(PassengerFindRoute.set_time)
async def get_passenger_time(message: Message, bot: Bot, state: FSMContext):
    await bot.delete_message(message.chat.id, message.message_id)
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
async def get_passenger_value(message: Message, bot: Bot, state: FSMContext):
    await bot.delete_message(message.chat.id, message.message_id)
    await state.update_data(cost=message.text)
    await change_state(state, PassengerFindRoute.set_seats_amount)
    await message.answer(text='ура, остался последний шаг, сколько мест в салоне вам потребуеться?')


@Passenger_router.message(PassengerFindRoute.set_value)
async def get_passenger_value_is_not_digit(message: Message, bot: Bot):
    await bot.delete_message(message.chat.id, message.message_id)
    await message.answer(text='пожалуйста введите число.')


@Passenger_router.message(PassengerFindRoute.set_seats_amount, F.text.isdigit())
async def get_passenger_seats_amount(message: Message, bot: Bot, state: FSMContext):
    await bot.delete_message(message.chat.id, message.message_id)
    await state.update_data(required_places=message.text)
    await message.answer(text='ищем подходящих водителей...')
    await change_state(state, PassengerFindRoute.final)
    data = await state.get_data()
    place_from = str(data['route']).split('-')[0]
    place_to = str(data['route']).split('-')[1]
    seats_amount = int(data['required_places'])
    cost = int(data['cost'])
    date = str(data['date'])
    time = str(data['time'])
    routes = await get_routes_filtered(place_from, place_to, seats_amount, cost, date, time)
    routes_ids = map(lambda x: x.id, routes)
    if not routes_ids:
        await state.clear()
        return await message.answer('к сожалению подходящих поездок не найдено, попробуйте позже')
    await state.update_data(route_ids=routes_ids)
    await state.update_data(current_index=0)
    await message.answer(text='нашёл кое-что для вас')
    await message.answer(text=write_route_info(routes[0]), reply_markup=inline_choose_route_markup())


@Passenger_router.message(PassengerFindRoute.set_seats_amount)
async def get_passenger_seats_amount_is_not_digit(message: Message, bot: Bot):
    await bot.delete_message(message.chat.id, message.message_id)
    await message.answer(text='пожалуйста введите число.')
