import asyncio
import logging
import os
import sys

from aiogram import Dispatcher, Bot

from dotenv import load_dotenv

from APIs.DB.engine import db_engine_start

from handlers.Passenger.callbackHandlers import Passenger_Callback_router
from handlers.Passenger.messageHandlers import Passenger_Message_router
from handlers.Common.dbTestHandlers import Test_router
from handlers.Common.mainMenuHandlers import MainMenu_router

from utilities.scheduler import setup_scheduler

load_dotenv(".env")
token = os.getenv("TOKEN_API")
bot = Bot(token, parse_mode="HTML")
dp = Dispatcher()


async def main() -> None:
    await db_engine_start()
    scheduler = await setup_scheduler()

    dp.include_routers(Passenger_Callback_router, Passenger_Message_router, Test_router, MainMenu_router)
    await bot.delete_webhook(drop_pending_updates=True)

    try:
        scheduler.start()
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    logging.basicConfig(format='\n%(asctime)s,%(msecs)d n%(name)s, %(levelname)s:\n%(message)s', level=logging.INFO,
                        stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
