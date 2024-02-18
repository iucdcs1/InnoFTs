import datetime

from aiogram import Router, Bot, F
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback

from APIs.DB.db_requests import get_route, subscribe_route
from keyboards.Passenger.inline import inline_choose_route_markup, return_back_markup, inline_main_routs_markup, \
    inline_choose_selected_route_markup
from keyboards.mainKB import passenger_main_kb
from states import PassengerFindRoute, PassengerSubscription
from utilities.changeState import change_state
from utilities.checkValidDate import is_valid_date
from utilities.validateRoute import validate_route
from utilities.writeRouteInfo import write_route_info

Passenger_Callback_router = Router()


@Passenger_Callback_router.callback_query(F.data.startswith('return_'))
async def return_passenger_back(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Handle the 'return_' callback query for the passenger.

    Args:
        callback (CallbackQuery): The callback query received.
        state (FSMContext): The current FSM context.
        bot (Bot): Aiogram bot object.

    Raises:
        ValueError: If the callback data is invalid.
    """

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
    elif phase == 'main':
        await bot.delete_message(chat_id=callback.message.chat.id,
                                 message_id=(await state.get_data())['message_to_delete'])
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
        await state.clear()
    else:
        raise ValueError(f'Bad return callback: {callback.data}')


@Passenger_Callback_router.callback_query(
    F.data.startswith('chosen_first_destination') | F.data.startswith('chosen_second_destination'))
async def end_point_passanger_handler(callback: CallbackQuery, state: FSMContext):
    """
    Handle the 'chosen_first_destination' and 'chosen_second_destination' callback queries for the passenger.

    Args:
        callback (CallbackQuery): The callback query received.
        state (FSMContext): The current FSM context.
    """

    await callback.message.delete()
    place_id = int(callback.data.split('_')[3])
    if callback.data.startswith('chosen_first_destination'):
        await state.update_data(route_start=place_id)
        await callback.message.answer(text='Выберите место назначения:',
                                      reply_markup=await inline_main_routs_markup(chosen=place_id))
    elif callback.data.startswith('chosen_second_destination'):
        await state.update_data(route_end=place_id)
        await change_state(state, PassengerFindRoute.set_date)
        await callback.message.answer(text='Выберите дату поездки:',
                                      reply_markup=await SimpleCalendar().start_calendar())


@Passenger_Callback_router.callback_query(PassengerFindRoute.set_date, SimpleCalendarCallback.filter())
async def get_passenger_date(callback: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    """
    Handle the callback query for selecting a date for the passenger.

    Args:
        callback (CallbackQuery): The callback query received.
        callback_data (CallbackData): The callback data.
        state (FSMContext): The current FSM context.
    """

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


@Passenger_Callback_router.callback_query(PassengerFindRoute.final)
async def get_callback_when_choose_route(call: CallbackQuery, bot: Bot, state: FSMContext):
    """
    Handle the callback query when choosing a route for the passenger.

    Args:
        call (CallbackQuery): The callback query received.
        bot (Bot): The bot instance.
        state (FSMContext): The current FSM context.
    """

    data = await state.get_data()
    current_index = int(data['current_index'])
    cb = call.data.split('_')
    if cb[1] == 'prev':
        if current_index == 0:
            current_index = len(data['route_ids']) - 1
        else:
            current_index -= 1
    elif cb[1] == 'next':
        if current_index == len(data['route_ids']) - 1:
            current_index = 0
        else:
            current_index += 1

    await state.update_data(current_index=current_index)

    route_ids = data['route_ids']

    route = await get_route(route_ids[current_index])

    if cb[1] == 'sub':
        if validate_route(route, data['required_places']):
            await subscribe_route(route_ids[current_index], call.from_user.id, data['required_places'])
            return await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                               text=write_route_info(
                                                   route) + f'[водитель](tg://user?id{route.driver_id})',
                                               parse_mode='Markdown')
    #           TODO: notification for driver?

    required_places: int = int(data['required_places'])
    if validate_route(route, required_places):
        return await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                           text=write_route_info(route), reply_markup=inline_choose_route_markup())
    await get_callback_when_choose_route(call, bot, state)


@Passenger_Callback_router.callback_query(PassengerSubscription.selected_routes)
async def get_callback_when_choose_route(call: CallbackQuery, bot: Bot, state: FSMContext):
    """
    Handle the callback query when describing a route for the passenger.

    Args:
        call (CallbackQuery): The callback query received.
        bot (Bot): The bot instance.
        state (FSMContext): The current FSM context.
    """

    data = await state.get_data()
    current_index = int(data['current_index'])
    cb = call.data.split('_')

    if cb[1] == 'prev':
        if current_index == 0:
            current_index = len(data['route_ids']) - 1
        else:
            current_index -= 1
    elif cb[1] == 'next':
        if current_index == len(data['route_ids']) - 1:
            current_index = 0
        else:
            current_index += 1

    await state.update_data(current_index=current_index)

    route_ids = data['route_ids']

    route = await get_route(route_ids[current_index])

    return await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                       text=write_route_info(route), reply_markup=inline_choose_selected_route_markup())
