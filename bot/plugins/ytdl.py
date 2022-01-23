import os
import shutil
import time
from pyrogram import Client, filters
import asyncio
from bot.helpers.progress import humanbytes, progress_for_pyrogram
from bot.helpers.uploadtools import upload
from bot.config import Var, CustomFilters

@Client.on_message(filters.command(["ytdl"]) & CustomFilters.auth_users)
async def ytdl(client, message):
    c_time = time.time()
    msglist = message.text.split()
    bot_msg = await message.reply("Trying to download..")
    if(len(msglist) < 3 ):
      await bot_msg.edit("Ytdl Takes 2 Parameters\n e.g./ytdl quality youtube_link")
      return
    
    ytdl_path = f"ytdl/{message.from_user.id}/{message.message_id}"
    if not os.path.isdir(ytdl_path):
      os.makedirs(ytdl_path)


    format = msglist[1]
    if format in ("mp3","m4a"):
      youtube_dl_format = 'bestaudio[ext=m4a]'
    else:
      youtube_dl_format = f"bestvideo[height<={format}]+bestaudio/best[height<={format}]"
    youtube_dl_url = msglist[-1]
    command_to_exec = [
        "youtube-dl",
        "-f",
        youtube_dl_format,
        youtube_dl_url,
        "-o",
        f"{ytdl_path}/%(title)s.%(ext)s"
    ]
    proc = await asyncio.create_subprocess_exec(
        *command_to_exec,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    try:
      while proc.returncode is None:
        prg = ""
        try:
          print("In ytdl process")
          filelist = os.listdir(ytdl_path)
          filename = os.path.basename(f"{ytdl_path}/{filelist[-1]}")
          file_size = os.path.getsize(f"{ytdl_path}/{filelist[-1]}")
          prg = f"**Filename 📝** : __{filename}__\n" +f"\n**Downloaded 📊** :{humanbytes(file_size)}"
          #line = await proc.stdout.reade
        except IndexError:
          pass
        line = await proc.stdout.readexactly(100)
        line = line.decode('utf-8')
        print(line)
        textlist = line.split()
        if "of" in textlist: 
          total_size = textlist[textlist.index("of")+1] 
        else : total_size = 0
        if "at" in textlist: 
          speed = textlist[textlist.index("at")+1]
        else: speed = 0
        prg += f" of {total_size}\n**Speed 🚀 ** : {speed}"
        print(prg)
        await bot_msg.edit(prg)
        await asyncio.sleep(5)
    except Exception as e:
      await bot_msg.edit(str(e))
    else:
      await bot_msg.edit("Trying To Upload...")
      filelist = os.listdir(ytdl_path)
      filepath = f"{ytdl_path}/{filelist[-1]}"
      if format in ("mp3","m4a"):
        await message.reply_audio(
                filepath,
                caption=filelist[-1],
                progress=progress_for_pyrogram,
                progress_args=("Upload Status: \n", message, c_time, message.from_user.id, client),
            )
      else:
        user_id = message.from_user.id
        if user_id not in Var.upload_as_doc or Var.upload_as_doc[user_id]:
          Var.upload_as_doc[user_id] = False
        await upload(client, bot_msg, filepath, user_id, message)
        Var.upload_as_doc[user_id] = True
        shutil.rmtree(ytdl_path)

      
