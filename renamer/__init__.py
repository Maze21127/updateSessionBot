import asyncio
import random
import time

from loguru import logger
from telethon import TelegramClient, functions, types
from telethon.errors import rpcerrorlist, UsernameOccupiedError, UsernameInvalidError
from telethon.tl.types import InputChannel

from renamer.config import get_data


def get_usernames(filename):
    with open(filename, 'r') as f:
        return [i.strip() for i in f.readlines()]


async def main(client: TelegramClient):
    global RESULT
    channel_ids = [1762984368, 1716502839, 1510767968]
    random.shuffle(channel_ids)
    names = get_usernames('renamer/names.txt')
    RESULT = names
    #await client.send_message()
    return
    for channel_id in channel_ids:
        logger.info(f"Going to channel_id {channel_id}")
        while True:
            username = random.choice(names)
            try:
                result = await client(functions.channels.UpdateUsernameRequest(channel_id, username))
                if result:
                    logger.info(f"Username changed to {username}")
                    break
            except rpcerrorlist.UsernameNotModifiedError:
                logger.debug(f"Username is not different from current username")
            except UsernameOccupiedError:
                logger.debug(f"Channel name '{username}' already exists")
            except UsernameInvalidError:
                logger.debug(f"Channel name '{username}' is invalid")
            except Exception as ex:
                logger.warning(ex)
                break
            await asyncio.sleep(60)


async def start():
    global result
    API_ID, API_HASH, SESSION = get_data()
    client = TelegramClient(SESSION, API_ID, API_HASH)
    logger.info(f"start script")
    loop = asyncio.get_event_loop()
    result = await loop.create_task(main(client))
    return RESULT
    #async with client:
        #await client.loop.run_until_complete(main(client))


async def login(api_id, api_hash, phone):
    API_ID, API_HASH, SESSION = get_data()
    client = TelegramClient('test_session', api_id, api_hash)
    await client.connect()
    if not await client.is_user_authorized():
        print("Отправляем код")
        result = await client.send_code_request(phone)
        print(result)
        print(result.phone_code_hash)
        await client.disconnect()
        print("Отключение...")
        return result
    else:
        return "Пользователь уже авторизован"


async def sign_in(api_id, api_hash, phone, code, phone_code_hash):
    API_ID, API_HASH, SESSION = get_data()
    client = TelegramClient('test_session', api_id, api_hash)
    await client.connect()
    print(code)
    print(phone_code_hash)
    result = await client.sign_in(phone, code, phone_code_hash=phone_code_hash)
    print(result)
    return result


async def update_session(api_id: int, api_hash: str):
    with open('.env2', 'r') as file:
        data = [i.strip() for i in file.readlines()]
    with open('.env2', 'w') as file:
        file.writelines([
            f"{data[0]}\n",
            f"{data[1]}\n",
            f"{data[2]}\n",
            f"API_ID={api_id}\n",
            f"API_hash={api_hash}\n",
            f"{data[5]}\n",
        ])
    return "Успех"
