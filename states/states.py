from aiogram.dispatcher.filters.state import StatesGroup, State


class UpdateAccount(StatesGroup):
    api_id = State()
    api_hash = State()
    phone = State()
    tg_code = State()
