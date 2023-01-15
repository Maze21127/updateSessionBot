from aiogram import executor, Dispatcher, types
from logger import logger
from loader import dp
import handlers
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from renamer import start


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
    #scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    #scheduler.add_job(start, trigger='interval', seconds=10)
    #scheduler.start()
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)

