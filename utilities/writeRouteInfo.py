from aiogram import Bot

from utilities.models import Route


def write_route_info(route: Route) -> str:
    return f'дата: {route.date_field.date()}\n' \
           f'время: {route.time_field}\n' \
           f'цена за место: {route.cost}₽\n'


