from src.bot import Bot
from src.config import Config
import os
import logging


if __name__ == '__main__':
    config = Config()
    log = logging.getLogger("Main")
    if config.proxy is not None:
        os.environ["http_proxy"] = config.proxy
        os.environ["https_proxy"] = config.proxy
    bot = Bot(config.token)
    log.info("Bot initialized")
    log.info("Starting...")
    bot.start()
    log.info("Bot stopped")
