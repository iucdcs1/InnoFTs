import datetime

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import KeyboardBuilder, ReplyKeyboardBuilder


def reply_date_now_markup() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=datetime.datetime.now().strftime('%d.%m.%Y')))
    return builder.as_markup(one_time_keyboard=True)
