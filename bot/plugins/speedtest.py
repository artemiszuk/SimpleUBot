import os
import speedtest
import wget
from pyrogram import Client, filters

@Client.on_message(filters.command(["speedtest"]))
async def speedtst(client, message):
    message = await message.reply(f"Performing Speedtest ...")
    try:
        test = speedtest.Speedtest()
        test.get_best_server()
        await message.edit("`Performing download test . . .`")
        test.download()
        await message.edit("`Performing upload test . . .`")
        test.upload()
        test.results.share()
        result = test.results.dict()
    except Exception as e:
        await message.edit_text(f"{str(e)}")
    path = wget.download((result["share"]))
    await message.reply_photo(photo=path)
    await message.delete()
    os.remove(path)