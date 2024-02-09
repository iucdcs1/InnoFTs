import datetime

from sqlalchemy import select, insert, delete, update, and_
from APIs.DB.engine import async_session
from APIs.DB.engine import User as User_DB
from APIs.DB.engine import Route as Route_DB
from APIs.DB.engine import Place as Place_DB
from utilities.models import User, Route, Place

'''
Standard getters by id
'''


async def get_user_by_id(user_id: int) -> User:
    async with async_session() as session:
        result = await session.query(User_DB).filter(User_DB.id == user_id).one()
        parsed_result = User().parse(result)
        return parsed_result


async def get_user(telegram_id: int) -> User:
    async with async_session() as session:
        result = await session.query(User_DB).filter(User_DB.telegram_id == telegram_id).one()
        parsed_result = User().parse(result)
        return parsed_result


async def get_route(route_id: int) -> Route:
    async with async_session() as session:
        result = await session.query(Route_DB).filter(Route_DB.id == route_id).one()
        parsed_result = Route().parse(result)
        return parsed_result


async def get_place(place_id: int) -> Place:
    async with async_session() as session:
        result = await session.query(Place_DB).filter(Place_DB.id == place_id).one()
        parsed_result = Place().parse(result)
        return parsed_result


async def get_place_by_name(place_name: str) -> Place:
    async with async_session() as session:
        place = Place()
        result = await session.scalar(select(Place_DB).where(Place_DB.name == place_name))
        place.parse(result)
        return place


async def get_roads_filtered(place_from: str, place_to: str, passangers_amount: int, cost: int, date: str,
                             time: str) -> [Route]:
    async with async_session() as session:
        if len(time.split('-')) == 2:
            time_start, time_end = time.split('-')
            if int(time_start.split(':')[0]) > int(time_end.split(':')[0]):
                time_interval_1 = time_start + "-23:59"
                time_interval_2 = "00:00-" + time_end
                next_date = (datetime.datetime.strptime(date, "%d.%m.%Y") +
                             datetime.timedelta(days=1)).strftime("%d.%m.%Y")
                return (await get_roads_filtered(place_from,
                                                 place_to,
                                                 passangers_amount,
                                                 cost,
                                                 date,
                                                 time_interval_1)) + \
                    (await get_roads_filtered(place_from,
                                              place_to,
                                              passangers_amount,
                                              cost,
                                              next_date,
                                              time_interval_2))
        elif len(time.split('-')) == 1:
            time_start, time_end = time, (datetime.timedelta(minutes=30) +
                                          datetime.datetime.strptime(time, "%H:%M")).strftime("%H:%M")
            return await get_roads_filtered(place_from,
                                            place_to,
                                            passangers_amount,
                                            cost,
                                            date,
                                            time_start + "-" + time_end)
        else:
            raise ValueError('Wrong amount of intervals')

        if not (((await get_place_by_name(place_from)) is not None) & (
                (await get_place_by_name(place_to)) is not None)):
            raise ValueError('Wrong place_from or place_to. Recheck')

        req_place_from_id = (await get_place_by_name(place_from)).id
        req_place_to_id = (await get_place_by_name(place_to)).id

        time_start = datetime.time(hour=int(time_start.split(':')[0]), minute=int(time_start.split(':')[1]))
        time_end = datetime.time(hour=int(time_end.split(':')[0]), minute=int(time_end.split(':')[1]))

        query_result = await session.scalars(select(Route_DB).where((Route_DB.place_from_id == req_place_from_id),
                                                                    (Route_DB.place_to_id == req_place_to_id),
                                                                    (Route_DB.available_places >= passangers_amount),
                                                                    (Route_DB.cost <= cost),
                                                                    (Route_DB.date_field == date),
                                                                    (Route_DB.time_field >= time_start),
                                                                    (Route_DB.time_field <= time_end)
                                                                    ))

        result = []
        for route_db in query_result:
            new_obj = Route()
            new_obj.parse(route_db)
            result.append(new_obj)
        return result
