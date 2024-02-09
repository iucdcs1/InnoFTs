from aiogram import Router, F
from aiogram.types import Message

from APIs.DB.db_requests import get_roads_filtered, get_place_by_name

Message_router = Router()


@Message_router.message(F.text == 'check')
async def check(message: Message):
    await message.answer('\n\n\n'.join([str(x) for x in (await get_roads_filtered("Иннополис", "Казань", 1, 100, "10.02.2024", "10:00-12:00"))]))
