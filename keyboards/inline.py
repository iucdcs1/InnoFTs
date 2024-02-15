from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from APIs.DB.db_requests import get_places


async def inline_main_routs_markup(chosen: int = -1) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    destinations = await get_places()

    if chosen == -1:  # If it is the departure point
        for i, destination in enumerate(destinations):
            builder.button(text=f"{destination.name}", callback_data=f"chosen_first_destination_{destination.id}")
        return builder.adjust(2, repeat=True).row(
            InlineKeyboardButton(text='<-', callback_data=f"return_fd")).as_markup(one_time_keyboard=True)
    else:  # If it is the destination point
        for i, destination in enumerate(destinations):
            if destination.id != chosen:
                builder.button(text=f"{destination.name}", callback_data=f"chosen_second_destination_{destination.id}")
        return builder.adjust(2, repeat=True).row(
            InlineKeyboardButton(text='<-', callback_data=f"return_sd")).as_markup(one_time_keyboard=True)


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


def inline_choose_route_markup() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    return builder.button(text='<', callback_data='r_prev').button(text='>', callback_data='r_next').button(
        text='выбрать', callback_data='r_sub').adjust(2, 1).as_markup(resize_keyboard=True)
