from pyrogram import Client, filters
import asyncio
from bot.config import CustomFilters

@Client.on_message(filters.command(["exec"]) & CustomFilters.owner)
async def exec_cmd(client, message):
  msglist = message.text.split()
  if len(msglist) == 1:
    await message.reply("No Command Found")
    return
  
  command_to_exec = list(msglist[1:])
  print(command_to_exec)
  proc = await asyncio.create_subprocess_exec(
        *command_to_exec,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
  try:
    await proc.wait()
    text = await proc.stdout.read()
    text = text.decode('utf-8')
    await message.reply(text)
  except Exception as e:
    await message.reply(str(e))
