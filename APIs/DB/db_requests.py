import datetime

from sqlalchemy import select, update

from APIs.DB.engine import Place as Place_DB
from APIs.DB.engine import Route as Route_DB
from APIs.DB.engine import User as User_DB
from APIs.DB.engine import async_session
from APIs.DB.engine import passenger_routes
from utilities.models import User, Route, Place


async def get_user_by_id(user_id: int) -> User:
    async with async_session() as session:
        result = await session.scalar(select(User_DB).where(User_DB.id == user_id))

        return result


async def get_user(telegram_id: int) -> User:
    async with async_session() as session:
        result = await session.scalar(select(User_DB).where(User_DB.telegram_id == telegram_id))

        return result


async def get_route(route_id: int) -> Route:
    async with async_session() as session:
        query_result = await session.scalar(select(Route_DB).where(Route_DB.id == route_id))

        result_route = Route()
        result_route.parse(query_result)

        return result_route


async def get_place(place_id: int) -> Place:
    async with async_session() as session:
        result = await session.scalar(select(Place_DB).where(Place_DB.id == place_id))

        return result


async def get_place_by_name(place_name: str) -> Place:
    async with async_session() as session:
        result = await session.scalar(select(Place_DB).where(Place_DB.name == place_name))

        return result


async def get_passanger_routes(telegram_id: int) -> [Route]:
    async with async_session() as session:
        user = await get_user(telegram_id)

        if user:
            user_id = user.id
            routes_id = [x.route_id for x in
                         (await session.execute(passenger_routes.select().where(passenger_routes.c.user_id == user_id)))
                         ]

            return [(await get_route(route_id)) for route_id in routes_id]
        else:
            raise ValueError(f'Passanger with telegram_id ({telegram_id}) not found')


async def get_driver_routes(telegram_id: int) -> [Route]:
    async with async_session() as session:
        user = await get_user(telegram_id)

        if user:
            user_id = user.id
            result_query = await session.scalars(select(Route_DB).where(Route_DB.driver_id == user_id))

            result_routes = []

            for route in result_query:
                temp_route = Route()
                temp_route.parse(route)

                result_routes.append(temp_route)

            return result_routes
        else:
            raise ValueError(f'Driver with telegram_id ({telegram_id}) not found')


async def get_routes_filtered(place_from: str, place_to: str, passangers_amount: int, cost: int, date: str,
                              time: str) -> [Route]:
    async with async_session() as session:
        if len(time.split('-')) == 2:
            time_start, time_end = time.split('-')
            if int(time_start.split(':')[0]) > int(time_end.split(':')[0]):
                time_interval_1 = time_start + "-23:59"
                time_interval_2 = "00:00-" + time_end
                next_date = (datetime.datetime.strptime(date, "%d.%m.%Y") +
                             datetime.timedelta(days=1)).strftime("%d.%m.%Y")
                return (await get_routes_filtered(place_from,
                                                  place_to,
                                                  passangers_amount,
                                                  cost,
                                                  date,
                                                  time_interval_1)) + \
                    (await get_routes_filtered(place_from,
                                               place_to,
                                               passangers_amount,
                                               cost,
                                               next_date,
                                               time_interval_2))
        elif len(time.split('-')) == 1:
            time_start, time_end = time, (datetime.timedelta(minutes=30) +
                                          datetime.datetime.strptime(time, "%H:%M")).strftime("%H:%M")
            return await get_routes_filtered(place_from,
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

        result_routes = []

        for route in query_result:
            temp_route = Route()
            temp_route.parse(route)

            result_routes.append(temp_route)

        return result_routes


async def subscribe_route(telegram_id: int, chosen_route_id: int) -> None:
    async with async_session() as session:
        passanger_id = (await get_user(telegram_id)).id

        await session.execute(
            update(Route_DB).values(available_places=Route_DB.available_places - 1).where(
                Route_DB.id == chosen_route_id)
        )

        await session.execute(passenger_routes.insert().values(
            user_id=passanger_id,
            route_id=chosen_route_id
        ))

        await session.commit()
