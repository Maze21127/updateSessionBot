import random

import telethon.types
from telethon import TelegramClient, functions
from telethon.errors.rpcerrorlist import ChannelsAdminPublicTooMuchError, ChannelInvalidError, ChatAdminRequiredError, \
    UsernameInvalidError, UsernameOccupiedError, PhoneNumberInvalidError

from app.models import *
from logger import logger
from telethon.sessions import StringSession


async def send_code(api_id, api_hash, phone_number):
    client = TelegramClient("tg", api_id, api_hash)
    await client.connect()

    if await client.is_user_authorized():
        result = await client.get_me()
        return f"""
Аккаунт:
<h3>id: {result.id}</h3>
<h3>first_name: {result.first_name}</h3>
<h3>last_name: {result.last_name}</h3>
<h3>phone: {result.phone}</h3>
<h1>Вход уже выполнен</h1>
"""
    try:
        result = await client.send_code_request(phone_number)
        logger.info(f"Отправлен код на {phone_number}")
    except PhoneNumberInvalidError:
        await client.disconnect()
        return "Неверный номер телефона"
    code_hash = result.phone_code_hash
    code = CodeRequest(api_id=api_id, api_hash=api_hash, phone_number=phone_number, code_hash=code_hash)
    db.session.add(code)
    db.session.commit()
    await client.disconnect()
    return code


async def sign_in(code, code_hash):
    code_from_db = CodeRequest.query.filter_by(code_hash=code_hash).first()

    client = TelegramClient("tg", code_from_db.api_id, code_from_db.api_hash)
    await client.connect()

    result = await client.sign_in(code_from_db.phone_number, code, phone_code_hash=code_hash)
    try:
        status = "Вход успешно выполнен"
    except Exception as ex:
        return f"Ошибка {ex}"
    old_account = Account.query.filter_by(is_active=True).first()
    if old_account is not None:
        old_account.is_active = False
    string = StringSession.save(client.session)
    account = Account(phone_number=code_from_db.phone_number,
                      api_id=code_from_db.api_id,
                      api_hash=code_from_db.api_hash,
                      session=string)
    db.session.add(account)
    db.session.commit()
    await client.disconnect()
    return status


async def get_me():
    account = Account.query.filter_by(is_active=True).first()
    if account is None:
        return "Вход не выполнен"
    client = TelegramClient(StringSession(account.session), account.api_id, account.api_hash)
    await client.connect()
    result = await client.get_me()
    acc_dict = {
        "id": result.id,
        "first_name": result.first_name,
        "last_name": result.last_name,
        "phone": result.phone,
        "api_id": account.api_id,
        "api_hash": account.api_hash
    }
    await client.disconnect()
    return acc_dict


def channel_filter(dialog):
    if isinstance(dialog.entity, telethon.types.Channel):
        if dialog.entity.creator:
            return True
    return False


async def _get_client():
    account = Account.query.filter_by(is_active=True).first()
    if account is None:
        return "Вход не выполнен"
    client = TelegramClient(StringSession(account.session), account.api_id, account.api_hash)
    await client.connect()
    logger.info("Connected")
    return client


async def get_groups(tg_client: TelegramClient = None):
    if tg_client is None:
        client = await _get_client()
        if isinstance(client, str):
            return "Вход не выполнен"
    else:
        client = tg_client

    groups = await client.get_dialogs()
    groups = filter(channel_filter, groups)
    for i in groups:
        print(i)
    result = [{
        "name": i.name,
        "id": i.entity.id,
        "username": i.entity.username,
        "participants_count": i.entity.participants_count
    } for i in groups]

    if tg_client is None:
        await client.disconnect()
    if not result:
        result = "На аккаунте нет созданных каналов, где можно менять название."
    return result


def _get_new_name(names: list, old_name) -> str:
    while True:
        new_name = random.choice(names)
        if new_name != old_name:
            return new_name


async def rename_channels():
    client = await _get_client()
    logger.info("Connected")
    groups = await get_groups(client)
    if isinstance(groups, str):
        await client.disconnect()
        return {"status": "400",
                "message": "На аккаунте нет созданных каналов, где можно менять название.",
                }
    with open('app/static/files/names.txt', 'r') as file:
        names = [i.strip() for i in file.readlines()]

    result_list = []
    for channel in groups:
        new_name = _get_new_name(names, channel['username'])
        while True:
            try:
                entity = await client.get_entity(new_name)
                new_name = _get_new_name(names, channel['username'])
            except ValueError:
                break
        try:
            result = await client(functions.channels.UpdateUsernameRequest(channel['id'], new_name))
            if result:
                result_list.append({"status": "200",
                                    "message": f"Название канала {channel['username']}({channel['id']}) изменен на {new_name}",
                                    "channel_id": channel['id']})
                logger.info(f"Username {channel['username']} changed to {new_name}")
        except ChannelsAdminPublicTooMuchError as ex:
            result_list.append({"status": "400",
                                "message": "Вы является администратором слишком большого количества публичных каналов, сделайте некоторых каналы приватными, чтобы изменить имя этого",
                                "channel_id": channel['id']})
            logger.exception(ex)
        except ChannelInvalidError as ex:
            result_list.append({"status": "400",
                                "message": "ChannelInvalidError",
                               "channel_id": channel['id']})
            logger.exception(ex)
        except ChatAdminRequiredError as ex:
            result_list.append({"status": "400",
                                "message": "Необходимы привелегии администратора (нет прав на изменение имени канала)",
                                "channel_id": channel['id']})
            logger.exception(ex)
        except UsernameInvalidError as ex:
            result_list.append({"status": "400",
                                "message": f"Неверное имя для смены {new_name}",
                                "channel_id": channel['id']})
            logger.exception(ex)
        except UsernameOccupiedError as ex:
            result_list.append({"status": "400",
                                "message": f"Неверное имя для смены {new_name}",
                                "channel_id": channel['id']})
            logger.exception(ex)
    await client.disconnect()
    return result_list

