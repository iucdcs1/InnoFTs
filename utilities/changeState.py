from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State


async def change_state(state: FSMContext, new_state: State):
    data = await state.get_data()
    await state.set_state(new_state)
    await state.set_data(data)
