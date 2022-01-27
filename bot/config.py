from bot import AUTH_USERS,OWNER_ID
from pyrogram import filters

class CustomFilters:
    auth_users = filters.create(
        lambda _, __, message: str(message.from_user.id) in AUTH_USERS
        or str(message.chat.id) in AUTH_USERS
    )
    owner = filters.create(
        lambda _, __, message: str(message.from_user.id) in OWNER_ID)

class Messages:
  START_MSG = "**📌MAIN MENU**\n\nHi ! This is Simple File Upload Bot \n\n__Check Below for commands/features__"
  HELP_MSG = "**⁉HELP MENU**:\n\n/start : Check Alive Status \n/upload : Upload DIrect Links \n/unzip : Unzip zip/rar files from direct Links\n/thumb : Reply to photo to save as custom thumb \n/clrthumb : Clear Custom ThumbNail \n/toggle : Upload videos as streamable/document\n/speedtest: Check DL and UL Speed"
  TOGGLE_MSG = "**⚙TOGGLE MENU:**\n[__Click to change__]\n\nVideo File Will be Uploaded as "

class messageobj:
    def __init__(self, message, unzip=False):
        self.message = message
        self.unzip = unzip


class Var(object):
    tdict = dict()
    upload_as_doc = dict()
    q_link = dict()
    cancel = dict()
    return_msg = dict()
    proc_cancel = False