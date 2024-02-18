from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from APIs.DB.db_requests import get_routes_filtered, get_passenger_routes, get_route
from keyboards.Passenger.inline import inline_choose_route_markup, inline_main_routs_markup, return_back_markup, \
    inline_choose_selected_route_markup
from states import PassengerFindRoute, PassengerSubscription
from utilities.changeState import change_state
from utilities.regex import time_pattern_interval_first, time_pattern_interval_second, time_pattern_interval_third, \
    time_pattern_single_first, time_pattern_single_second, time_pattern_interval_fourth
from utilities.writeRouteInfo import write_route_info

Passenger_Message_router = Router()


@Passenger_Message_router.message(F.text == 'Найти попутку')
async def start_passenger_handle(message: Message):
    """
    Starting FT`s finding process

    :param message: message object, written by user
    """

    await message.delete()
    await message.answer(text='Выберите место отправления:',
                         reply_markup=await inline_main_routs_markup())


@Passenger_Message_router.message(PassengerFindRoute.set_time)
async def get_passenger_time(message: Message, state: FSMContext, bot: Bot):
    """
    Get user`s value (time segment) and update the state

    :param message: message object, written by user
    :param state: current state
    :param bot: Aiogram bot variable
    :return: nothing
    """

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


@Passenger_Message_router.message(PassengerFindRoute.set_value)
async def get_passenger_value(message: Message, state: FSMContext, bot: Bot):
    """
    Get user`s value (cost) and update the state

    :param message: message object, written by user
    :param state: current state
    :param bot: Aiogram bot variable
    :return: nothing
    """

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


@Passenger_Message_router.message(PassengerFindRoute.set_seats_amount)
async def get_passenger_seats_amount(message: Message, state: FSMContext, bot: Bot):
    """
    Get passenger seats amount and update the state.
    Using API retrieve suitable routes.

    :param message: message object, written by user
    :param state: current state
    :param bot: Aiogram bot variable
    :return: nothing
    """

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


# TODO: Unsubscribe
@Passenger_Message_router.message(F.text == 'Мои подписки')
async def get_subscriptions(message: Message, state: FSMContext):
    await message.delete()
    routes_id = [x.id for x in (await get_passenger_routes(message.from_user.id))]
    if routes_id:
        msg_id = (await message.answer(text=f'Вы подписались на {len(routes_id)} поездок!')).message_id
        await state.set_state(PassengerSubscription.selected_routes)
        await state.update_data(current_index=0, route_ids=routes_id, message_to_delete=msg_id)
        await message.answer(text=write_route_info((await get_route(routes_id[0]))),
                             reply_markup=inline_choose_selected_route_markup())
    else:
        await message.answer(text='Подписок не найдено.')
