from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from APIs.DB.db_requests import get_route, subscribe_route
from keyboards.inline import inline_choose_route_markup
from states import PassengerFindRoute
from utilities.validateRoute import validate_route
from utilities.writeRouteInfo import write_route_info

Callback_router = Router()


@Callback_router.callback_query(PassengerFindRoute.final)
async def get_callback_when_choose_route(call: CallbackQuery, bot: Bot, state: FSMContext):
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
    route_ids = data['route_ids']
    route = await get_route(route_ids[current_index])
    required_places: int = int(data['required_places'])
    if validate_route(route, required_places):
        return await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                           text=write_route_info(route), reply_markup=inline_choose_route_markup())
    await get_callback_when_choose_route(call, bot, state)
