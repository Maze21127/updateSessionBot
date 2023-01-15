from loguru import logger

logger.add("logs/error.log", format="{time} {level} {message}", level="ERROR", rotation="01:00")
logger.add("logs/info.log", format="{time} {level} {message}", level="INFO", rotation="01:00")
