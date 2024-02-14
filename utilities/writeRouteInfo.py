from aiogram import Bot

from utilities.models import Route


def write_route_info(route: Route) -> str:
    return f"""
    дата: {route.date_field}\n
    время: {route.time_field}\n
    ценна за место: {route.cost}₽\n
    """