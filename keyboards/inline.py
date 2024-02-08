from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def date_selection_markup(dates) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for date in dates:
        builder.button(text=f'{date}', callback_data=f'd_{date}')


def inline_num_keyboard_markup(data: str, final=False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for i in range(9):
        builder.button(text=f'{i}', callback_data=f'i_{data}{i}_nok')
    builder.button(text='clear', callback_data=f'i_{data[:-1]}_nok')
    if not final:
        builder.adjust(3, 3, 3, 1)
        return builder.as_markup(resize_keyboard=True)
    builder.button(text='ok', callback_data=f'i_{data}_ok')
    builder.adjust(3, 3, 3, 1, 1)
    return builder.as_markup(resize_keyboard=True)
