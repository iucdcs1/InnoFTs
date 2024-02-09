from datetime import datetime, time

from APIs.DB.engine import Place as Plc
from APIs.DB.engine import Route as Rt
from APIs.DB.engine import User as Usr


class User:
    id: int
    telegram_id: int
    username: str
    is_admin: bool

    def parse(self, user: Usr):
        self.id = user.id
        self.telegram_id = user.telegram_id
        self.username = user.username
        self.is_admin = user.is_admin


class Route:
    id: int
    driver_id: int
    place_from_id: int
    place_to_id: int
    available_places: int
    cost: int
    date_field: datetime
    time_field: time

    def parse(self, route: Rt):
        self.id = route.id
        self.driver_id = route.driver_id
        self.place_from_id = route.place_from_id
        self.place_to_id = route.place_to_id
        self.available_places = route.available_places
        self.cost = route.cost
        self.date_field = datetime.strptime(route.date_field, "%d.%m.%Y")
        self.time_field = route.time_field

    def __str__(self):
        return f'ID: {self.id}\n' \
               f'Driver_ID: {self.driver_id}\n' \
               f'Place_from_ID: {self.place_from_id}\n' \
               f'Place_to_ID: {self.place_to_id}\n' \
               f'Available places: {self.available_places}\n' \
               f'Cost: {self.cost}\n' \
               f'Date: {self.date_field.strftime("%d.%m.%Y")}\n' \
               f'Time: {self.time_field.strftime("%H:%M")}'


class Place:
    id: int
    name: str

    def parse(self, place: Plc):
        self.id = place.id
        self.name = place.name
