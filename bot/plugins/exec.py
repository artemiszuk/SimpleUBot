from pyrogram import Client, filters
from pathlib import Path
import shutil
import asyncio
import os
from bot.config import CustomFilters, Var
from pyrogram.types import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

@Client.on_message(filters.command(["exec"]) & CustomFilters.owner)
async def exec_cmd(client, message):
    msglist = message.text.split()
    if len(msglist) == 1:
        await message.reply("No Command Found")
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


