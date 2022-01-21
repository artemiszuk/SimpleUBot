import os
import shutil
import asyncio
from pyrogram import Client, filters, errors
from bot.config import Var
from bot.helpers.utils import extension,get_details
from bot.helpers.progress import progress_for_pyrogram, humanbytes
import time

async def upload_folder(client,path, bot_msg, user_id):
    if os.path.isdir(path) and len(os.listdir(path)) > 0:
        allfiles = os.listdir(path)
        allfiles.sort()
        await asyncio.sleep(3)
        info = await bot_msg.reply(
            f"Currently in Folder : __{os.path.basename(path)}__\nTotal Files : {len(allfiles)}",
        )
        await asyncio.sleep(3)
        # print("Total files",len(allfiles),"allfiles = ",allfiles)
        for flist in allfiles:
            npath = os.path.join(path, flist)
            await upload_folder(client,npath, bot_msg, user_id)
    else:
        await asyncio.sleep(3)
        bot_msg = await bot_msg.reply("Trying to Upload...")
        await asyncio.sleep(3)
        await upload(client,bot_msg, path, user_id)


async def upload(client, message, filepath, user_id):
    c_time = time.time()
    if user_id not in Var.upload_as_doc:
        Var.upload_as_doc[user_id] = True
    filename = os.path.basename(filepath)
    exten = extension(filepath)
    await message.edit(f"__Uploading {filename}__ ... 📤")
    if user_id in Var.tdict:
        if Var.upload_as_doc[user_id] == False and (exten == ".mp4" or exten == ".mkv"):
            mydict = await get_details(filepath)
            print("Uploading as Video")
            media_msg = await client.send_video(
                message.chat.id,
                filepath,
                supports_streaming=True,
                caption=filename,
                thumb=str(Var.tdict[user_id]),
                duration=int(float(mydict["duration"])),
                width=int(mydict["width"]),
                height=int(mydict["height"]),
                progress=progress_for_pyrogram,
                progress_args=("Upload Status: \n", message, c_time, user_id, client),
            )
        else:
            print("Uploading as Document")
            media_msg = await client.send_document(
                message.chat.id,
                filepath,
                caption=filename,
                thumb=str(Var.tdict[user_id]),
                progress=progress_for_pyrogram,
                progress_args=("Upload Status: \n", message, c_time, user_id, client),
            )
    else:
        if Var.upload_as_doc[user_id] == False and (exten == ".mp4" or exten == ".mkv"):
            print("Uploading as Video")
            mydict = await get_details(filepath)
            media_msg = await client.send_video(
                message.chat.id,
                filepath,
                supports_streaming=True,
                caption=filename,
                thumb=mydict["tname"],
                duration=int(float(mydict["duration"])),
                width=int(mydict["width"]),
                height=int(mydict["height"]),
                progress=progress_for_pyrogram,
                progress_args=("Upload Status: \n", message, c_time, user_id, client),
            )
            os.remove(mydict["tname"])
        elif exten == ".mp4" or exten == ".mkv":
            print("Uploading as Documetn")
            print(Var.upload_as_doc[user_id])
            mydict = await get_details(filepath)
            media_msg = await client.send_document(
                message.chat.id,
                filepath,
                caption=filename,
                thumb=mydict["tname"],
                progress=progress_for_pyrogram,
                progress_args=("Upload Status: \n", message, c_time, user_id, client),
            )
            os.remove(mydict["tname"])
        else:
            print("Uploading as Docuemnt")
            media_msg = await client.send_document(
                message.chat.id,
                filepath,
                caption=filename,
                progress=progress_for_pyrogram,
                progress_args=("Upload Status: \n", message, c_time, user_id, client),
            )
    if not media_msg:
        return
    chatid_string = str(message.chat.id)
    mediaid_string = str(media_msg.message_id)
    link = f"https://t.me/c/{chatid_string[4:]}/{mediaid_string}"
    Var.return_msg[user_id] += f"⚈ [{filename}]({link})" + "\n\n"
    await message.delete()