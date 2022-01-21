from pyrogram import Client, filters
from bot.config import CustomFilters, Messages
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@app.on_message(filters.command(["start"]) & CustomFilters.auth_users)
async def start(client, message):
    text = "**📌MAIN MENU**\n\nHi ! This is Simple File Upload Bot \n\n__Check Below for commands/features__"
    await message.reply(
        text,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Help ❓", callback_data="help"),
                    InlineKeyboardButton("Developer 🧑‍💻", url="https://google.com"),
                ],
                [
                    InlineKeyboardButton("Close ❌", callback_data="close"),
                    InlineKeyboardButton(
                        "Source Code 📝", url="https://github.com/artemiszuk/upload_Z"
                    ),
                ],
            ]
        ),
    )  # sends above messsage


@app.on_message(filters.command(["help"]))
async def help(client, message):
    await start(client, message)
