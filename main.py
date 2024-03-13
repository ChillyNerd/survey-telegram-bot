import logging
import os

from src.bot import Bot
from src.config import Config

QUESTIONS = ['First question', 'Second question', 'Third question']
PRIVILEGED_USERS = None

if __name__ == '__main__':
    config = Config()
    log = logging.getLogger("Main")
    if config.proxy is not None:
        os.environ["http_proxy"] = config.proxy
        os.environ["https_proxy"] = config.proxy
    bot = Bot(
        token=config.token,
        questions=QUESTIONS,
        privileged_users=PRIVILEGED_USERS
    )
    log.info("Bot initialized")
    log.info("Starting...")
    bot.start()
    log.info("Bot stopped")
