import datetime
import re

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from states import PassengerFindRoute
from keyboards.reply import reply_date_now_markup, reply_main_routs_markup
from utilities.checkValidDate import is_valid_date
from utilities.regex import time_pattern_interval_first, time_pattern_interval_second, time_pattern_interval_third, \
    time_pattern_single_first, time_pattern_single_second, time_pattern_interval_fourth
from utilities.changeState import change_state

passenger_router = Router()


@passenger_router.message(Command(commands=['test_passenger']))
async def test_passenger(message: Message, state: FSMContext):
    await state.set_state(PassengerFindRoute.set_route)
    await message.answer(text='Привет для того чтобы найти машину, вам надо выбрать маршрут',
                         reply_markup=reply_main_routs_markup())


@passenger_router.message(PassengerFindRoute.set_route)
async def get_passenger_route(message: Message, state: FSMContext):
    await state.update_data(route=message.text)
    await change_state(state, PassengerFindRoute.set_date)
    await message.answer(
        text='отлично, мне надо знать когда вы планируете поездку.'
        , reply_markup=reply_date_now_markup())


@passenger_router.message(PassengerFindRoute.set_date)
async def get_passenger_date(message: Message, state: FSMContext):
    if not is_valid_date(message.text.replace(' ', '')):
        return await message.answer('я вас не понял, введите дату формата DD.MM.YYYY',
                                    reply_markup=reply_date_now_markup())
    await state.update_data(date=message.text)
    await change_state(state, PassengerFindRoute.set_time)
    await message.answer(
        text='теперь yажите пожалуста время.\nВ ведите интервал времени в формате HH:MM - HH:MM или HH:MM если ищете водителей на конкретное время.')


@passenger_router.message(PassengerFindRoute.set_time)
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


@passenger_router.message(PassengerFindRoute.set_value, F.text.isdigit())
async def get_passenger_value(message: Message, state: FSMContext):
    await state.update_data(value=message.text)
    await change_state(state, PassengerFindRoute.set_seats_amount)
    await message.answer(text='ура, остался последний шаг, сколько мест в салоне вам потребуеться?')


@passenger_router.message(PassengerFindRoute.set_value)
async def get_passenger_value_is_not_digit(message: Message):
    await message.answer(text='пожалуйста введите число.')


@passenger_router.message(PassengerFindRoute.set_seats_amount, F.text.isdigit())
async def get_passenger_seats_amount(message: Message, state: FSMContext):
    await state.update_data(seats_amount=message.text)
    await message.answer(text='ищем подходящих водителей...')
    # ТУТ ДОЛЖНО БЫТЬ ОБРАЩЕНИЕ В DB API


@passenger_router.message(PassengerFindRoute.set_seats_amount)
async def get_passenger_seats_amount_is_not_digit(message: Message):
    await message.answer(text='пожалуйста введите число.')
