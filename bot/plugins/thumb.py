import os
import shutil
from __main__ import user
from pyrogram import Client, filters
from bot.config import CustomFilters, Messages, Var
from pyrogram.types import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

@user.on_message(filters.command(["thumb"],["."]) & filters.outgoing)
async def user_thumb(client,message):
  await thumb(client, message)

@user.on_message(filters.command(["clrthumb"],["."]) & filters.outgoing)
async def user_clrthumb(client, message):
  await clrthumb(client, message)

@Client.on_message(filters.command(["thumb"]) & CustomFilters.auth_users & filters.incoming)
async def thumb(client, message):
    photo_msg = message.reply_to_message
    if photo_msg is not None and photo_msg.photo is not None:
        photo_dl_path = f"bot/downloads/{message.from_user.id}.jpg"
        await photo_msg.download(file_name=f"{message.from_user.id}.jpg")
        Var.tdict[message.from_user.id] = photo_dl_path
        await message.reply_text(
            f"Custom Thumb Saved", reply_to_message_id=photo_msg.message_id, quote=True
        )
    else:
        await message.reply_text(f"Not a Photo", quote=True)


@Client.on_message(filters.command(["clrthumb"]) & CustomFilters.auth_users & filters.incoming)
async def clrthumb(client, message):
    user_id = message.from_user.id
    if user_id in Var.tdict:
        Var.tdict.pop(user_id)
        os.remove(f"bot/downloads/{user_id}.jpg")
        await message.reply_text("Thumbnail Cleared")
    else:
        await message.reply_text("No Custom Thumbnail Found")

@Client.on_message(filters.command(["toggle"]) & CustomFilters.auth_users & filters.incoming)
async def toggle(client, message):
    user_id = message.from_user.id
    if user_id not in Var.upload_as_doc:
        Var.upload_as_doc[user_id] = True
    text = "**⚙TOGGLE MENU:**\n[__Click to change__]\n\nVideo File Will be Uploaded as "
    if Var.upload_as_doc[user_id]:
        text_append = "Document 📁"
    else:
        text_append = "Streamable 🎬"
    await message.reply(
        text,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text_append, callback_data="toggle"),
                    InlineKeyboardButton("Close ❌", callback_data="close"),
                ]
            ]
        ),
    )
