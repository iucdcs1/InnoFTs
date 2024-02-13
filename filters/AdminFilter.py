from aiogram.filters import BaseFilter
from aiogram.types import Message

from APIs.DB.db_requests import get_user


class AdminCommandFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        user = await get_user(message.from_user.id)
        if user:
            return user.is_admin
        else:
            return False
