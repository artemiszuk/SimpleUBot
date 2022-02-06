import os
import shutil
import time
import ffmpeg
from __main__ import user
from pyrogram import Client, filters
from pyrogram.types import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
import subprocess
from bot.helpers.utils import get_details
import asyncio
from bot.helpers.progress import humanbytes, progress_for_pyrogram
from bot.helpers.uploadtools import upload
from bot.config import Var, CustomFilters

@user.on_message(filters.command(["ytdl"],["."]) & CustomFilters.auth_users & filters.outgoing)
async def ytdl_user(client, message):
  await ytdl(client, message)

@Client.on_message(filters.command(["ytdl"]) & CustomFilters.auth_users & filters.incoming)
async def ytdl(client, message):
    user_id = message.from_user.id
    c_time = time.time()
    msglist = message.text.split()
    bot_msg = await message.reply("Trying to download..")
    if len(msglist) < 3:
        await bot_msg.edit("Ytdl Takes 2 Parameters\n e.g./ytdl quality youtube_link")
        return

    if user_id not in Var.return_msg:
          Var.return_msg[user_id] = f"**🎴 UPLOADED MENU:** \n__Sender__ : {message.from_user.mention()}\n\n"

    ytdl_path = f"ytdl/{message.from_user.id}/{message.message_id}"
    if not os.path.isdir(ytdl_path):
        os.makedirs(ytdl_path)

    format = msglist[1]
    youtube_dl_url = msglist[-1]
    if format in ("mp3", "m4a", "wav", "flac"):
        command_to_exec = [
        "yt-dlp",
        "-x",
        "--audio-format",
        format,
        youtube_dl_url,
        "-o",
        f"{ytdl_path}/%(title)s.%(ext)s",
        "--write-thumbnail"
        ]
    else:
        youtube_dl_format = (
            f"bestvideo[height<={format}]+bestaudio/best[height<={format}]"
        )
        command_to_exec = [
        "yt-dlp",
        "-f",
        youtube_dl_format,
        youtube_dl_url,
        "-o",
        f"{ytdl_path}/%(title)s.%(ext)s",
        "--write-thumbnail"
        ]

    proc = await asyncio.create_subprocess_exec(
        *command_to_exec, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    user_id = message.from_user.id
    if user_id not in Var.cancel or Var.cancel[user_id]:
        Var.cancel[user_id] = False

    try:
        while proc.returncode is None:
            # on cancel CAllback
            if Var.cancel[user_id]:
                proc.terminate()
                Var.cancel[user_id] = False
                await bot_msg.edit("Download Cancelled")
                shutil.rmtree(ytdl_path)
                return

            prg = ""
            filename = ""
            file_size = ""
            try:
                print("In ytdl process")
                filelist = os.listdir(ytdl_path)
                filename = os.path.basename(f"{ytdl_path}/{filelist[-1]}")
                file_size = os.path.getsize(f"{ytdl_path}/{filelist[-1]}")
                # line = await proc.stdout.reade
            except IndexError:
                pass
            line = await proc.stdout.readexactly(200)
            line = line.decode("utf-8")
            textlist = line.split()
            if "of" in textlist:
                total_size = textlist[textlist.index("of") + 1]
            else:
                total_size = 0
            if "at" in textlist:
                speed = textlist[textlist.index("at") + 1]
            else:
                speed = 0
            # Wait message until download starts
            if len(filename) == 0:
                prg = "__Downloading From Youtube 📺...__"
            else:
                prg = (
                    f"**Filename 📝** : __{filename}__\n"
                    + f"\n**Downloaded 📊** :{humanbytes(file_size)} of {total_size}\n**Speed 🚀 ** : {speed}"
                )
            await bot_msg.edit(
                prg,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Cancel ❌", callback_data="cancel")]]
                ),
            )
            await asyncio.sleep(5)
    except Exception as e:
        await bot_msg.edit(
            f"**ERROR** : {str(e)}\n\n**Maybe Requested Quality not available.**"
        )
    else:
        filelist = sorted(os.listdir(ytdl_path))
        print(filelist)
        to_upload = []
        thumb_list = []
        for file in filelist:
            if os.path.splitext(file)[1] in (
                ".webm",
                ".mp4",
                ".mp3",
                ".m4a",
                ".opus",
                ".flac",
                ".mkv",
            ):
                filepath = os.path.join(ytdl_path, file)
                to_upload.append(filepath)
        await bot_msg.delete()

        for filepath in to_upload:
            if Var.cancel[user_id]:
                shutil.rmtree(ytdl_path)
                return
            bot_msg = await message.reply(f"__Uploading {os.path.basename(filepath)}📤__...")
            thumbpath = os.path.splitext(filepath)[0] + ".webp"
            jpg_thumb = os.path.splitext(filepath)[0] + ".jpg"
            print(jpg_thumb)
            p = subprocess.Popen(["ffmpeg", "-i", thumbpath, jpg_thumb])
            p.wait()
            # os.system(cmd)
            print(thumbpath)
            if format in ("mp3", "m4a", "wav", "flac"):
                probe = ffmpeg.probe(filepath)
                media_msg = await message.reply_audio(
                    filepath,
                    thumb=jpg_thumb,
                    duration=round(float(probe["format"]["duration"])),
                    caption=os.path.splitext(filelist[0])[0],
                    progress=progress_for_pyrogram,
                    progress_args=(
                        "Upload Status: \n",
                        bot_msg,
                        c_time,
                        message.from_user.id,
                        client,
                    ),
                )
            else:
                mydict = await get_details(filepath)
                media_msg = await message.reply_video(
                    filepath,
                    supports_streaming=True,
                    caption=os.path.splitext(filelist[0])[0],
                    thumb=jpg_thumb,
                    duration=int(float(mydict["duration"])),
                    width=int(mydict["width"]),
                    height=int(mydict["height"]),
                    progress=progress_for_pyrogram,
                    progress_args=("Upload Status: \n", bot_msg, c_time, user_id, client),
                )
                os.remove(mydict["tname"])
            filename = os.path.basename(filepath)
            chatid_string = str(message.chat.id)
            mediaid_string = str(media_msg.message_id)
            link = f"https://t.me/c/{chatid_string[4:]}/{mediaid_string}"
            Var.return_msg[user_id] += f"⚈ [{os.path.splitext(filename)[0]}]({link})" + "\n\n"
            await bot_msg.delete()
        if message.chat.type == "supergroup" : await message.reply(Var.return_msg[user_id])
        print(ytdl_path)
        shutil.rmtree(ytdl_path)

      
