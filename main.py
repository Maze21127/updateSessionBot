from aiogram import executor, Dispatcher, types
from aiogram.utils.exceptions import ChatNotFound

import utils.api
from logger import logger
from loader import dp, bot
import handlers
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from settings import ADMINS


async def rename_channels():
    result = await utils.api.rename()
    for obj in result['data']:
        if obj['status'] != "200":
            for i in ADMINS:
                try:
                    await bot.send_message(i, f"{obj['channel_id']}\n{obj['message']}")
                except ChatNotFound:
                    continue


async def on_startup(dispatcher: Dispatcher):
    await dispatcher.bot.set_my_commands([
        types.BotCommand('start', 'Запустить бота'),
        types.BotCommand('help', 'Помощь'),
        types.BotCommand('status', 'Статус'),
        types.BotCommand('update', 'Изменить аккаут'),
    ])
    logger.info("Commands added")


async def on_shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()
    logger.info("Shutdown completed")


if __name__ == "__main__":
    logger.info("Start bot")
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(rename_channels, trigger='interval', hours=4)
    scheduler.start()
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)

