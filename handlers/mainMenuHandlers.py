from aiogram import Router, F
from aiogram.types import Message

from filters.AdminFilter import AdminCommandFilter

MainMenu_router = Router()


@MainMenu_router.message(F.text == 'Попутчик')
async def driver_menu(message: Message):
    pass


@MainMenu_router.message(F.text == 'Водитель')
async def passenger_menu(message: Message):
    pass


@MainMenu_router.message(F.text == 'Статистика')
async def statistic_menu(message: Message):
    pass


@MainMenu_router.message(AdminCommandFilter(), F.text == 'Админ-панель')
async def admin_menu(message: Message):
    pass
