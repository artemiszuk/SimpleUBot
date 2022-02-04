import os
import speedtest
import wget
from pyrogram import Client, filters
from bot.config import CustomFilters
from __main__ import user


@user.on_message(filters.command(["speedtest"],["."]) & filters.outgoing)
async def user_speedtst(client, message):
  await speedtst(client, message)
@Client.on_message(filters.command(["speedtest"]) & CustomFilters.auth_users & filters.incoming)
async def speedtst(client, message):
    bot_msg = await message.reply(f"__Performing Speedtest__ ...")
    try:
        test = speedtest.Speedtest()
        test.get_best_server()
        await bot_msg.edit("__Performing download test ...__")
        test.download()
        await bot_msg.edit("__Performing upload test ...__")
        test.upload()
        test.results.share()
        result = test.results.dict()
    except Exception as e:
        await message.edit_text(f"{str(e)}")
    path = wget.download((result["share"]))
    await message.reply_photo(photo=path)
    await bot_msg.delete()
    os.remove(path)