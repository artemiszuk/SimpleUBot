import os
import shutil
from pyrogram import Client, filters
from bot.helpers.utils import extension
from __main__ import user
from bot.config import CustomFilters, Messages, Var, messageobj
from bot.helpers.uploadtools import upload
from bot.helpers.downloadtools import dl_link, unzip_and_upload
from pyrogram.types import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

@user.on_message(filters.command(["upload"],["."]) & filters.outgoing)
async def user_link(client, message, unzipflag=False):
  await link(client, message, unzipflag)

@user.on_message(filters.command(["unzip"],["."]) & filters.outgoing)
async def user_unzip(client, message):
  await unzip_cmd(client, message)

@Client.on_message(filters.command(["upload"]) & CustomFilters.auth_users & filters.incoming)
async def link(client, message, unzipflag=False):
    user_id = message.from_user.id
    if user_id not in Var.q_link:
        Var.q_link[user_id] = []
    Var.q_link[user_id].append(messageobj(message))
    Var.q_link[user_id][-1].unzip = unzipflag
    if os.path.isdir(f"download/{user_id}") and len(Var.q_link[user_id]) > 1:
        queue_msg = await message.reply(
            f"Queue Added\nPENDING TASKS :{str(len(Var.q_link[user_id])-1)}"
        )
        await asyncio.sleep(5)
        await queue_msg.delete()
        return
    while len(Var.q_link[user_id][:]) > 0:
        if user_id not in Var.return_msg:
          Var.return_msg[user_id] = f"**🎴 UPLOADED MENU:** \n__Sender__ : @{message.from_user.username}\n\n"
        obj = Var.q_link[user_id][0]
        print("Download task is started ,size of Queue= ", len(Var.q_link[user_id]))
        try:
          filepath, bot_msg = await dl_link(client, obj.message)
        except Exception as e:
          Var.q_link[user_id].pop(0)
          print(e)
          return
        if len(filepath) != 0:
            if obj.unzip:
                await unzip_and_upload(client,bot_msg, filepath, user_id,message)
                if(not filters.private): await message.reply(Var.return_msg[user_id])
            else:
                await upload(client,bot_msg, filepath, obj.message.from_user.id,message)
                if(not filters.private): await message.reply(Var.return_msg[user_id])
            shutil.rmtree(f"download/{obj.message.from_user.id}/")
        Var.return_msg.pop(user_id)
        Var.q_link[user_id].pop(0)
        print("Download Task is Done ,size of Queue = ", len(Var.q_link[user_id]))


@Client.on_message(filters.command(["unzip"]) & CustomFilters.auth_users & filters.incoming)
async def unzip_cmd(client, message):
    archives = [".zip", ".rar"]
    if extension(message.text) not in archives:
        await message.reply("Not A Zip/Rar Link")
        return
    await link(client, message, True)