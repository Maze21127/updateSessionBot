from aiogram import executor, Dispatcher, types

import utils.api
from logger import logger
from loader import dp, bot
import handlers
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from settings import ADMINS


async def rename_channels():
    result = await utils.api.rename()
    for obj in result['data']:
        if obj['status'] != "MUTEX":
            for i in ADMINS:
                await bot.send_message(i, f"{obj['channel_id']}\n{obj['message']}")


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
    scheduler.add_job(rename_channels, trigger='interval', hours=2)
    scheduler.start()
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)

