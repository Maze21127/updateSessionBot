from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import dp, bot
from logger import logger
from renamer import start, update_session, login, sign_in
from settings import ADMINS
from states.states import UpdateAccount
from utils.messages import MESSAGES


@dp.message_handler(commands=['start'], state="*")
async def start_handler(message: types.Message):
    if message.from_user.id not in ADMINS:
        return
    state = dp.current_state()
    await state.finish()
    return await message.answer("Для того, чтобы изменить аккаунт, введи /update")


@dp.message_handler(commands=['update'], state="*")
async def update_handlers(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        return
    state = dp.current_state()
    await state.finish()
    keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton("Отмена", callback_data='cancel'))
    await UpdateAccount.api_id.set()
    return await message.answer("Введите api_id", reply_markup=keyboard)


@dp.message_handler(state=UpdateAccount.api_id)
async def waiting_api_id(message: types.Message, state: FSMContext):
    api_id = message.text
    await state.update_data(api_id=api_id)
    await UpdateAccount.api_hash.set()
    keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton("Отмена", callback_data='cancel'))
    return await message.answer("Введите api_hash", reply_markup=keyboard)


@dp.message_handler(state=UpdateAccount.api_hash)
async def waiting_api_hash(message: types.Message, state: FSMContext):
    api_hash = message.text
    await state.update_data(api_hash=api_hash)
    await UpdateAccount.phone.set()
    keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton("Отмена", callback_data='cancel'))
    return await message.answer("Введите номер телефона", reply_markup=keyboard)


@dp.message_handler(state=UpdateAccount.phone)
async def waiting_api_phone(message: types.Message, state: FSMContext):
    phone = message.text
    await state.update_data(phone=phone)
    data = await state.get_data()
    api_id = data['api_id']
    api_hash = data['api_hash']

    result = await login(api_id, api_hash, phone)
    if result == "Пользователь уже авторизован":
        await state.finish()
        return await message.answer("Аккаунт уже авторизован")

    await state.update_data(phone_code_hash=result.phone_code_hash)
    keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton("Код не пришел", callback_data='send_code'))
    keyboard.add(InlineKeyboardButton("Отмена", callback_data='cancel'))
    await message.answer("Введите код", reply_markup=keyboard)
    return await UpdateAccount.tg_code.set()


@dp.message_handler(state=UpdateAccount.tg_code)
async def waiting_tg_code(message: types.Message, state: FSMContext):
    tg_code = message.text
    data = await state.get_data()
    api_id = data['api_id']
    api_hash = data['api_hash']
    phone = data['phone']
    phone_code_hash = data['phone_code_hash']

    print(f"{tg_code} получен, попытаемся войти...")
    result = await sign_in(api_id, api_hash, phone, tg_code, phone_code_hash)
    await state.finish()
    return await message.answer(result)


@dp.callback_query_handler(lambda cb: cb.data == 'send_code', state=UpdateAccount.tg_code)
async def resend_code(callback_query: types.CallbackQuery, state: FSMContext):
    print("Код не пришел, отправляем еще раз")
    data = await state.get_data()
    api_id = data['api_id']
    api_hash = data['api_hash']
    phone = data['phone']

    result = await login(api_id, api_hash, phone)
    return await state.update_data(phone_code_hash=result.phone_code_hash)


@dp.callback_query_handler(lambda cb: cb.data == 'cancel', state=UpdateAccount)
async def cancel(callback_query: types.CallbackQuery, state: FSMContext):
    state = dp.current_state()
    await state.finish()

    await callback_query.message.answer("Действие отменено")


@dp.message_handler(commands=['result'], state="*")
async def update_handlers(message: types.Message):
    if message.from_user.id not in ADMINS:
        return
    state = dp.current_state()
    await state.finish()
    result = " ".join(message.text.split()[1:])
    return await bot.send_message(1214900768, result)

