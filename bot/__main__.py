import os
import logging
from pyrogram import Client,idle
from bot import (
  API_ID,
  API_HASH,
  BOT_TOKEN,
  )



logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
LOGGER = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)



if __name__ == "__main__":
    plugins = dict(
        root="bot/plugins"
    )
    app = Client(
        "SUploadBot",
        bot_token=BOT_TOKEN,
        api_id=API_ID,
        api_hash=API_HASH,
        plugins=plugins
    )
    SESSION_STRING = os.environ.get("SESSION_STRING")
    print(os.getcwd())
    user = Client(
        SESSION_STRING,
        api_id=API_ID,
        api_hash=API_HASH,
        plugins=plugins
    )
    app.start()
    user.start()
    LOGGER.info('Starting Bot !')
    idle()
    app.stop()
    user.stop()
    LOGGER.info('Bot Stopped !')
