import os
import logging

logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.FileHandler('log.txt'), logging.StreamHandler()],
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
LOGGER = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


try:
  BOT_TOKEN = os.environ.get('BOT_TOKEN')
  API_ID = int(os.environ.get('API_ID'))
  API_HASH = os.environ.get('API_HASH')
  AUTH_USERS = os.environ.get("AUTH_USERS").split()
  OWNER_ID = os.environ.get("OWNER_ID").split()
except KeyError:
  LOGGER.error('One or more configuration values are missing exiting now.')
  exit(1)