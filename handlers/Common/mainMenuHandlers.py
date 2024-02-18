from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from filters.AdminFilter import AdminCommandFilter
from keyboards.mainKB import passenger_main_kb, main_kb, driver_main_kb, admin_main_kb, statistics_main_kb

MainMenu_router = Router()


@MainMenu_router.message(Command(commands=['start']))
async def start_menu(message: Message):
    await message.delete()
    await message.answer('Охайо', reply_markup=main_kb)


@MainMenu_router.message(F.text == 'Попутчик')
async def driver_menu(message: Message):
    await message.delete()
    await message.answer('Открыто меню попутчика. Выберите один из вариантов ниже:', reply_markup=passenger_main_kb)


@MainMenu_router.message(F.text == 'Водитель')
async def passenger_menu(message: Message):
    await message.delete()
    await message.answer('Открыто меню водителя. Выберите один из вариантов ниже:', reply_markup=driver_main_kb)


@MainMenu_router.message(F.text == 'Статистика')
async def statistic_menu(message: Message):
    await message.delete()
    await message.answer('Открыто меню статистики. Выберите один из вариантов ниже:', reply_markup=statistics_main_kb)


@MainMenu_router.message(AdminCommandFilter(), F.text == 'Админ-панель')
async def admin_menu(message: Message):
    await message.delete()
    await message.answer('Открыта админ-панель.', reply_markup=admin_main_kb)


@MainMenu_router.message(F.text == 'Вернуться')
async def get_back(message: Message, state: FSMContext):
    await state.clear()
    await message.delete()
    await message.answer('Возврат в главное меню...', reply_markup=main_kb)
