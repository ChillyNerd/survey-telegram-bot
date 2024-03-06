from src.bot import Bot
from src.config import Config
import os
import logging


config = Config()
log = logging.getLogger("Main")
if config.proxy is not None:
    os.environ["http_proxy"] = config.proxy
    os.environ["https_proxy"] = config.proxy
bot = Bot(config.token)
log.debug("Bot initialized")
log.debug("Starting...")
bot.start()
log.debug("Bot stopped")
