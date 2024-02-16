import datetime

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram_calendar import SimpleCalendarCallback, SimpleCalendar

from APIs.DB.db_requests import get_routes_filtered
from keyboards.inline import inline_choose_route_markup, inline_main_routs_markup, return_back_markup
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


@Passenger_router.callback_query(F.data.startswith('return_'))
async def return_passenger_back(callback: CallbackQuery, state: FSMContext):
    phase = callback.data.split('_')[1]
    if phase == 'fd':
        await callback.message.delete()
        await callback.message.answer('Открыто меню попутчика', reply_markup=passenger_main_kb)
    elif phase == 'sd':
        await callback.message.edit_text(text='Выберите место отправления:',
                                         reply_markup=await inline_main_routs_markup())
    elif phase == 'time':
        await callback.message.delete()
        await change_state(state, PassengerFindRoute.set_date)
        await callback.message.answer(
            text='Выберите дату поездки:'
            , reply_markup=await SimpleCalendar().start_calendar())

    elif phase == 'cost':
        await change_state(state, PassengerFindRoute.set_time)
        await callback.message.delete()
        msg_id = (await callback.message.answer(text='Укажите время поездки в формате HH:MM-HH:MM или HH:MM',
                                                reply_markup=return_back_markup("time"))).message_id
        return await state.update_data(message_to_delete_time=msg_id)
    elif phase == 'seats':
        await callback.message.delete()
        await change_state(state, PassengerFindRoute.set_value)
        msg_id = (await callback.message.answer(text='Сколько вы готовы заплатить за поездку?',
                                                reply_markup=return_back_markup("cost"))).message_id
        return await state.update_data(message_to_delete_cost=msg_id)
    else:
        raise ValueError(f'Bad return callback: {callback.data}')


@Passenger_router.callback_query(F.data.startswith('chosen_first_destination'))
async def end_point_passanger_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    place_id = int(callback.data.split('_')[3])
    await state.update_data(route_start=place_id)
    await callback.message.answer(text='Выберите место назначения:',
                                  reply_markup=await inline_main_routs_markup(chosen=place_id))


@Passenger_router.callback_query(F.data.startswith('chosen_second_destination'))
async def end_point_passanger_handler(callback: CallbackQuery, state: FSMContext):
    place_id = int(callback.data.split('_')[3])
    await state.update_data(route_end=place_id)
    await change_state(state, PassengerFindRoute.set_date)
    await callback.message.delete()
    await callback.message.answer(
        text='Выберите дату поездки:'
        , reply_markup=await SimpleCalendar().start_calendar())


@Passenger_router.callback_query(PassengerFindRoute.set_date, SimpleCalendarCallback.filter())
async def get_passenger_date(callback: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    calendar = SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime.datetime.now() - datetime.timedelta(days=1),
                             datetime.datetime.now() + datetime.timedelta(days=30))
    selected, date = await calendar.process_selection(callback, callback_data)
    if not date and isinstance(date, bool):
        return await callback.message.answer(text='Выберите место назначения:',
                                             reply_markup=await inline_main_routs_markup(
                                                 chosen=(await state.get_data())['route_start'])
                                             )
    if selected:
        if is_valid_date(date.strftime('%d.%m.%Y')):
            await state.update_data(date=date.strftime('%d.%m.%Y'))
            await change_state(state, PassengerFindRoute.set_time)

            await callback.message.delete()

            msg_id = (await callback.message.answer(text='Укажите время поездки в формате HH:MM-HH:MM или HH:MM',
                                                    reply_markup=return_back_markup("time"))).message_id

            await state.update_data(message_to_delete_time=msg_id)
        else:
            return await callback.message.answer('Неверно выбрана дата. Выберите ещё раз :)',
                                                 reply_markup=await SimpleCalendar().start_calendar())


@Passenger_router.message(PassengerFindRoute.set_time)
async def get_passenger_time(message: Message, state: FSMContext, bot: Bot):
    await message.delete()
    # TODO: Rewrite. Too much of supplementary checks in handler
    correct_interval = time_pattern_interval_first.fullmatch(
        message.text) is not None or time_pattern_interval_second.fullmatch(
        message.text) is not None or time_pattern_interval_third.fullmatch(message.text) is not None
    correct_single = time_pattern_single_first.fullmatch(
        message.text) is not None or time_pattern_single_second.fullmatch(
        message.text) is not None or time_pattern_interval_fourth.fullmatch(message.text) is not None

    if not correct_interval and not correct_single:
        return await bot.edit_message_text(chat_id=message.chat.id,
                                           message_id=(await state.get_data())["message_to_delete_time"],
                                           text='Некорректный временной интервал, попробуйте ещё раз.\n'
                                                'Пример: 10:00-10:45',
                                           reply_markup=return_back_markup("time"))

    await bot.delete_message(chat_id=message.chat.id, message_id=(await state.get_data())["message_to_delete_time"])
    await state.update_data(time=message.text)
    await change_state(state, PassengerFindRoute.set_value)

    msg_id = (await message.answer(text='Сколько вы готовы заплатить за поездку?',
                                   reply_markup=return_back_markup("cost"))).message_id

    await state.update_data(message_to_delete_cost=msg_id)


@Passenger_router.message(PassengerFindRoute.set_value)
async def get_passenger_value(message: Message, state: FSMContext, bot: Bot):
    if message.text.isdigit():
        await state.update_data(cost=message.text)
        await change_state(state, PassengerFindRoute.set_seats_amount)

        await message.delete()
        await bot.delete_message(chat_id=message.chat.id, message_id=(await state.get_data())["message_to_delete_cost"])

        msg_id = (await message.answer(text='Сколько мест в салоне Вам потребуется?',
                                       reply_markup=return_back_markup("seats"))).message_id
        await state.update_data(message_to_delete_seats=msg_id)

    else:
        await message.delete()

        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=(await state.get_data())["message_to_delete_cost"],
                                    text='Введите число. Сколько вы готовы заплатить за поездку?',
                                    reply_markup=return_back_markup("cost"))


@Passenger_router.message(PassengerFindRoute.set_seats_amount)
async def get_passenger_seats_amount(message: Message, state: FSMContext, bot: Bot):
    await message.delete()

    if message.text.isdigit():
        await bot.delete_message(chat_id=message.chat.id,
                                 message_id=(await state.get_data())["message_to_delete_seats"])

        await message.answer(text='Ищем подходящие маршруты...')

        await state.update_data(required_places=message.text)

        data = await state.get_data()
        await state.clear()
        await state.update_data(required_places=int(data['required_places']))

        place_from = data['route_start']
        place_to = data['route_end']
        seats_amount = int(data['required_places'])
        cost = int(data['cost'])
        date = str(data['date'])
        time = str(data['time'])
        routes = await get_routes_filtered(place_from, place_to, seats_amount, cost, date, time)
        routes_ids = [x.id for x in routes]

        if not routes_ids:
            return await message.answer('Подходящих маршрутов не найдено, попробуйте позже')

        await change_state(state, PassengerFindRoute.final)
        await state.update_data(route_ids=routes_ids)
        await state.update_data(current_index=0)

        await message.answer(text=f'Найдёно {len(routes_ids)} подходящих маршрутов!')
        await message.answer(text=write_route_info(routes[0]), reply_markup=inline_choose_route_markup())

    else:
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=(await state.get_data())["message_to_delete_seats"],
                                    text='Введите число. Сколько мест в салоне Вам потребуется?',
                                    reply_markup=return_back_markup("seats"))
