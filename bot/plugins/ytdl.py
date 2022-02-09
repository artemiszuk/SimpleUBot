import os
import shutil
from pathlib import Path
import time
import wget
import datetime
from pytube import YouTube, Playlist
from bot.config import Var
from bot.helpers.utils import progress
import ffmpeg
from __main__ import user, app
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
from bot.helpers.progress import humanbytes, progress_for_pyrogram , _progress_for_pyrogram
from bot.helpers.uploadtools import upload
from bot.config import Var, CustomFilters

@user.on_message(filters.command(["ytdl"],["."]) & CustomFilters.auth_users & filters.outgoing)
def ytdl_user(client, message):
    mypytube(client, message)

class var:
    def __init__(self,_time):
        self._time = _time
    def htime(self):
        return self._time


@Client.on_message(filters.command(["ytlist"]) & CustomFilters.auth_users & filters.incoming)
def mypytubelist(client,message):
    user_id = message.from_user.id
    msglist = message.text.split()
    if len(msglist) < 3:
        return message.reply("YtdlPlaylist Takes 2 Parameters\n e.g./ytdl quality youtube_link")
    p = Playlist(msglist[-1])
    count = len(p)
    if count == 0:
        return message.reply("InValid Playlist URL")
    else:
        status = message.reply(f"Found {len(p)} videos in playlist")
    Var.cancel[user_id] = False
    c_time = time.time()
    i = 0
    start_t = var(int(time.time()))
    time.sleep(2)
    bot_msg = status.reply(f"Downloading Playlist... 📥")
    for url in p:
        ct = var(int(time.time()))
        ytdl_path = f"ytlist/{message.from_user.id}/{message.message_id}"
        def progress_func(stream,data_chunk,remaining):
            curr = int(time.time())
            if curr - start_t.htime() >= 5:
                start_t._time = int(time.time())
                downloaded = stream.filesize-remaining
                percent = (downloaded/stream.filesize)*100
                #print(percent)
                if Var.cancel[user_id]:
                    raise Exception("Cancelled")
                    #stream = None
                    #return
                prg = progress(int(percent),100)
                text = f"**Filename 📝 **: __{stream.title}__"+f"\n\n**Progress 📊 : **{prg}"+"\n**Downloaded 📥 **:"+humanbytes(downloaded)+"\n**Total Size 📀 **: "+humanbytes(stream.filesize) +f"**\nPlaylist** : {i}/{count}"+ f"\n**Elapsed ⏳ **: {str(datetime.timedelta(seconds = curr - int(c_time)))}"
                bot_msg.edit(
                    text,
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("Cancel ❌", callback_data="cancel")]]
                    )
                )
        def complete_func(stream,filepath):
            base, ext = os.path.splitext(filepath)
            if quality == "audio": 
                os.rename(filepath,base+".mp3")
                filepath = base + ".mp3"
            filename = os.path.splitext(filepath)[0]
            wget.download(url = yt.thumbnail_url,out=f'{ytdl_path}/{os.path.basename(filename)}.jpg')
            #end of for
        yt = YouTube(
            url,
            on_progress_callback=progress_func,
            on_complete_callback=complete_func
        )
        i = i + 1
        quality = msglist[1]
        if quality == "audio":
            video = yt.streams.filter(only_audio=True).last()
        #elif quality in ("144","240","360","480"):
        else:
            quality += "p"
            video = yt.streams.filter(resolution=quality).first()
            print(video)
        try:
            video.download(ytdl_path)  
        except Exception as e:
            print(e)
            if str(e) == "Cancelled":
                shutil.rmtree(ytdl_path)
                return message.reply("#cancel\n\nDownload Cancelled By User")
            else:
                return bot_msg.edit(f"ERROR : {e}\n\n__Maybe Requested Video or Quality not available.__")
    bot_msg.delete()
    status.edit(f"#ytplaylist\n\nPlayList Downloaded\nTotal Files :{count}")
    filelist = []
    paths = sorted(Path(ytdl_path).iterdir(), key=os.path.getmtime)
    for file in paths:filelist.append(file.name)
    print(filelist)
    to_upload = []
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
    quality = msglist[1]
    return_msg = f"**🎴 UPLOADED MENU:** \n__Sender__ : {message.from_user.mention()}\n"
    for filepath in to_upload:
        if Var.cancel[user_id]:
            shutil.rmtree(ytdl_path)
            message.reply("#cancel\n\nUpload Cancelled By User")
            return
        filename = os.path.basename(filepath)
        bot_msg = message.reply(f"__Uploading {filename}📤__...")
        jpg_thumb = os.path.splitext(filepath)[0] + ".jpg"
        if quality == "audio":
            probe = ffmpeg.probe(filepath)
            media_msg = status.reply_audio(
                filepath,
                thumb=jpg_thumb,
                duration=round(float(probe["format"]["duration"])),
                caption=filename,
                progress=_progress_for_pyrogram,
                progress_args=(
                    "Upload Status: \n",
                    bot_msg,
                    c_time,
                    message.from_user.id,
                    client
                )
            )
        else:
            probe = ffmpeg.probe(filepath)
            media_msg = status.reply_video(
                filepath,
                duration = round(float(probe["format"]["duration"])),
                height = int(msglist[1]),
                caption = os.path.basename(filename),
                thumb = jpg_thumb,
                progress=_progress_for_pyrogram,
                progress_args=(
                    "Upload Status: \n",
                    bot_msg,
                    c_time,
                    message.from_user.id,
                    client
                )
            )
        time.sleep(1)
        bot_msg.delete()
        time.sleep(3)
        chatid_string = str(message.chat.id)
        mediaid_string = str(media_msg.message_id)
        link = f"https://t.me/c/{chatid_string[4:]}/{mediaid_string}"
        return_msg += f"\n⚈ [{os.path.splitext(filename)[0]}]({link})"
    if message.chat.type == "supergroup" : message.reply(return_msg)
    shutil.rmtree(ytdl_path)






@Client.on_message(filters.command(["ytdl"]) & CustomFilters.auth_users & filters.incoming)
def mypytube(client,message):
    user_id = message.from_user.id
    msglist = message.text.split()
    bot_msg = message.reply("Trying to download 📥...")
    if len(msglist) < 3:
        bot_msg.edit("Ytdl Takes 2 Parameters\n e.g./ytdl quality youtube_link")
        return
    Var.cancel[user_id] = False
    start_t = var(int(time.time()))
    ct = var(int(time.time()))
    ytdl_path = f"ytdl/{message.from_user.id}/{message.message_id}"
    c_time = time.time()
    def progress_func(stream,data_chunk,remaining):
        curr = int(time.time())
        if curr - start_t.htime() >= 3:
            start_t._time = int(time.time())
            downloaded = stream.filesize-remaining
            percent = (downloaded/stream.filesize)*100
            #print(percent)
            if Var.cancel[user_id]:
                print(stream)
                raise Exception("Cancelled")
                #stream = None
                #return
            prg = progress(int(percent),100)
            text = f"**Filename 📝 **: __{stream.title}__"+f"\n\n**Progress 📊 : **{prg}"+"\n**Downloaded 📥 **:"+humanbytes(downloaded)+"\n**Total Size 📀 **: "+humanbytes(stream.filesize) + f"\n**Elapsed ⏳ **: {str(datetime.timedelta(seconds = curr - ct.htime()))}"
            bot_msg.edit(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Cancel ❌", callback_data="cancel")]]
                )
            )
    
    def complete_func(stream,filepath):
        return_msg = f"**🎴 UPLOADED MENU:** \n__Sender__ : {message.from_user.mention()}\n\n"
        base, ext = os.path.splitext(filepath)
        if quality == "audio": 
            os.rename(filepath,base+".mp3")
            filepath = base + ".mp3"
        bot_msg.edit("Downloaded")
        bot_msg.edit(f"__Uploading {os.path.basename(filepath)}📤__...")
        filename = os.path.splitext(filepath)[0]
        wget.download(url = yt.thumbnail_url,out=f'{ytdl_path}/{os.path.basename(filename)}.jpg')
        if not quality == "audio":
            media_msg = message.reply_video(
                filepath,
                duration = yt.length,
                height = int(msglist[1]),
                caption = os.path.basename(filename),
                thumb = filename + ".jpg",
                progress=_progress_for_pyrogram,
                progress_args=(
                    "Upload Status: \n",
                    bot_msg,
                    c_time,
                    message.from_user.id,
                    client
                )
            )
        else :
            media_msg = message.reply_audio(
                    filepath,
                    thumb=filename + ".jpg",
                    duration=yt.length,
                    caption=os.path.basename(filename),
                    progress = _progress_for_pyrogram,
                    progress_args=(
                        "Upload Status: \n",
                        bot_msg,
                        c_time,
                        message.from_user.id,
                        client
                    )
                )
        bot_msg.delete()

        filename = os.path.basename(filepath)
        chatid_string = str(message.chat.id)
        mediaid_string = str(media_msg.message_id)
        link = f"https://t.me/c/{chatid_string[4:]}/{mediaid_string}"
        return_msg += f"⚈ [{os.path.splitext(filename)[0]}]({link})"
        time.sleep(1)
        if message.chat.type == "supergroup" : message.reply(return_msg)
        shutil.rmtree(ytdl_path)
        


    yt = YouTube(
            msglist[-1],
            on_progress_callback=progress_func,
            on_complete_callback=complete_func
        )
    quality = msglist[1]
    if quality == "audio":
        video = yt.streams.filter(only_audio=True).last()
    #elif quality in ("144","240","360","480"):
    else:
        quality += "p"
        video = yt.streams.filter(resolution=quality).first()
    try:
        
        video.download(ytdl_path)  
    except Exception as e:
        print(e)
        if str(e) == "Cancelled":
            bot_msg.edit("Cancelled")
        else:
            bot_msg.edit(f"ERROR : {e}\n\n__Maybe Requested Video or Quality not available.__")




'''@Client.on_message(filters.command(["ytdl"]) & CustomFilters.auth_users & filters.incoming)
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
'''
      
