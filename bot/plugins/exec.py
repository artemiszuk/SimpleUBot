from pyrogram import Client, filters, errors
from pathlib import Path
import shutil
import asyncio
import os
from __main__ import app,user
from io import StringIO
from contextlib import redirect_stdout
import traceback
from bot.config import CustomFilters, Var
from pyrogram.types import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

@Client.on_message(filters.command(["shell"]) & CustomFilters.owner & filters.incoming)
async def shell_cmd(client, message):
    msglist = message.text.split()
    if len(msglist) == 1:
        await message.reply("No Shell Command Found")
        return
    try:
        command_to_exec = list(msglist[1:])
        print(command_to_exec)
        proc = await asyncio.create_subprocess_exec(
            *command_to_exec,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await proc.wait()
        text = await proc.stdout.read()
        text = text.decode("utf-8")
        await message.reply(text)
    except Exception as e:
        await message.reply(str(e))

@user.on_message(filters.command(["exec"],["."]) & filters.outgoing)
def exec_cmd_user(client, message):
  exec_cmd(client, message)

@Client.on_message(filters.command(["exec"]) & CustomFilters.owner & filters.incoming)
def exec_cmd(client, message):
  msglist = message.text.split()
  if len(msglist) == 1:
    message.reply("No Python Command Found")
    return
  try:
    command_to_exec = message.text[6:]
    print(command_to_exec)
    f = StringIO()  
    with redirect_stdout(f):
      help(command_to_exec)
    s = f.getvalue()
    print(s)
    message.reply(s)
  except errors.MessageEmpty:
    message.reply("`None`")
  except Exception :
    message.reply(traceback.format_exc())

def help(code):
  exec(code)
