from aiogram import types

from loader import dp, bot
from settings import DOMAIN, ADMINS
from utils import api
from utils.messages import MESSAGES


@dp.message_handler(commands=['start'], state="*")
async def start_handler(message: types.Message):
    if message.from_user.id not in ADMINS:
        return
    state = dp.current_state()
    await state.finish()
    return await message.answer(MESSAGES['start'])


@dp.message_handler(commands=['help'], state="*")
async def help_handler(message: types.Message):
    if message.from_user.id not in ADMINS:
        return
    state = dp.current_state()
    await state.finish()
    return await message.answer(MESSAGES['help'])


@dp.message_handler(commands=['rename'], state="*")
async def rename_handler(message: types.Message):
    if message.from_user.id not in ADMINS:
        return
    await message.answer(f"Запущена смена ссылок у каналов, через несколько минут вы получите отчёт.")
    state = dp.current_state()
    await state.finish()
    result = await api.rename()
    print(result)
    await message.answer("Переименование завершено")


@dp.message_handler(commands=['update'], state="*")
async def update_handler(message: types.Message):
    if message.from_user.id not in ADMINS:
        return
    state = dp.current_state()
    await state.finish()
    return await message.answer(f"Обновление аккуанта происходит здесь\nhttp://{DOMAIN}/account")



@dp.message_handler(commands=['status'])
async def status_handler(message: types.Message):
    if message.from_user.id not in ADMINS:
        return
    responce = await api.account_status()
    account = responce.get('account', None)
    error = responce.get('error', None)
    groups = responce.get('groups', None)
    if error:
        return await message.answer(error['message'])
    result_message = f"""
ID: {account['id']}
First name: {account['first_name']}
Last name: {account['last_name']}
Phone: {account['phone']}
Api ID: {account['api_id']}
Api Hash: {account['api_hash']}
"""
    await message.answer(result_message)
    if isinstance(groups, str):
        return await message.answer("На аккаунте нет созданных каналов, где можно менять название.")
    if groups:
        for group in groups:
            group_message = f"""
ID: {group['id']}
Название группы: {group['name']}
Ссылка: https://t.me/{group['username']}
Количество участников: {group['participants_count']}
"""
            await message.answer(group_message)

