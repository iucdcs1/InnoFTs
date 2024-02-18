from aiogram import Router, F
from aiogram.types import Message

# from APIs.DB.db_requests import *

Test_router = Router()


@Test_router.message(F.text == 'check')
async def check(message: Message):
    pass
    '''
    await message.answer((await get_user(1)).username)
    await message.answer((await get_user_by_id(1)).username)

    await message.answer(str((await get_route(1))))

    await message.answer(str((await get_place_by_name('Казань')).id))
    await message.answer((await get_place(1)).name)

    await message.answer('\n\n'.join([str(x) for x in (await get_driver_routes(1))]))

    await message.answer('\n\n'.join([str(x) for x in (await get_routes_filtered('Иннополис', 'Казань', 1, 120, '10.02.2024', '10:45'))]))

    await message.answer('\n\n'.join([str(x) for x in (await get_passenger_routes(1))]))

    await subscribe_route(1, 1)

    await message.answer('\n\n'.join([str(x) for x in (await get_passenger_routes(1))]))
    '''