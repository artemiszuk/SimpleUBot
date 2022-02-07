import os
import time
import datetime
import shutil
from pyrogram.types import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from urllib.request import urlopen
from patoolib import extract_archive
from pyrogram import Client, filters, errors
from bot.helpers.utils import progress
from bot.config import Var
from pySmartDL import SmartDL
import asyncio
from urllib.parse import unquote
from bot.helpers.utils import extension
from bot.helpers.progress import humanbytes
from bot.helpers.uploadtools import upload_folder

async def unzip_and_upload(client,bot_msg, filepath, user_id,reply_to):
    new_dir = filepath[0 : filepath.index(extension(filepath))] + "/"
    os.makedirs(new_dir)
    try:
        extract_archive(filepath, outdir=new_dir)
    except Exception as e:
        e_text = str(e)
        await bot_msg.edit_text(e_text)
        return
    else:
        await upload_folder(client,new_dir, bot_msg, user_id,reply_to)

def geturl(url):
  newurl=""
  try:
    newurl = urlopen(url,timeout=3).geturl()
  except Exception as e:
    print(e)
    return False
  else:
    return newurl

async def dl_link(client, message):
    user_id = message.from_user.id
    # if user_id not exists then store cancel flag
    #if user_id not in Var.cancel or Var.cancel[user_id]:
    Var.cancel[user_id] = False
      # seperate link from message
    text = f"__Checking Redirects__..."
    bot_msg = await message.reply(
        text, disable_web_page_preview=True
    )  # displays user input
    url = geturl(message.text.split()[-1])
    if not url : url = message.text.split()[-1]
    print(url)
    path = f"download/{user_id}/{message.message_id}"
    start_time = int(time.time())
    if os.path.isdir(f"download/{user_id}") == False:
        try:
            await bot_msg.edit("File Downloading")
            os.makedirs(path)
            downloader = SmartDL(url, path, progress_bar=False)
            downloader.start(blocking=False)
            file_name = os.path.basename(url)
            while not downloader.isFinished():
                total_length = downloader.filesize if downloader.filesize else 0
                if Var.cancel[user_id] or (total_length > 2097152000 and os.path.splitext(file_name)[1] not in (".zip",".rar")):
                    downloader.stop()
                    if Var.cancel[user_id]:
                        append = ""
                    else:
                        append = (
                            f"\nFile Size: {humanbytes(total_length)}\nLimit : 2 GB"
                        )
                    await bot_msg.edit(f"Download Cancelled ‼{append}")
                    shutil.rmtree(f"download/{user_id}/")
                    Var.cancel[user_id] = False
                    return "", bot_msg
                downloaded = downloader.get_dl_size()
                percentage = downloader.get_progress() * 100
                prg = progress(int(percentage), 100)
                speed = downloader.get_speed(human=True)
                eta_time = downloader.get_eta(human=True)
                curr_time = int(time.time())
                progress_str = (
                    f"**File Name** 📝: {unquote(file_name)} \n"
                    + f"**Progress** 📊: {prg}\n"
                    + f"{humanbytes(downloaded)} of {humanbytes(total_length)}\n"
                    + "**Completed **: "
                    + str(int(percentage))
                    + "%\n"
                    + f"**Speed **🚀: {speed}\n"
                    + f"**ETA **⏳: {eta_time}\n"
                    + f"**Elapsed Time ⏰**: {str(datetime.timedelta(seconds = curr_time - start_time))}"
                )
                await bot_msg.edit(
                    progress_str,
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("Cancel ❌", callback_data="cancel")]]
                    ),
                )
                await asyncio.sleep(5)
            await bot_msg.edit("File Downloaded")
            f = os.listdir(path)
            filepath = f"{path}/{f[0]}"
            return filepath, bot_msg
        except Exception as e:
            e_text = str(e)
            shutil.rmtree(f"download/{user_id}/")
            print(e_text)
            await bot_msg.edit_text("Some Error Occcured,Can't Download\nPlease Check the URL you entered  ‼")
            return "",bot_msg