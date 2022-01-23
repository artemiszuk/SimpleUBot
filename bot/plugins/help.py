from pyrogram import Client, filters
from bot.config import CustomFilters, Messages, Var
from pyrogram.types import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

@Client.on_message(filters.command(["start"]) & CustomFilters.auth_users)
async def start(client, message):
    await message.reply(
        Messages.START_MSG,
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


@Client.on_message(filters.command(["help"]) & CustomFilters.auth_users)
async def help(client, message):
    await start(client, message)

@Client.on_callback_query()
async def button(client, cmd: CallbackQuery):
    cb_data = cmd.data
    if "help" in cb_data:
        await cmd.message.edit(
            Messages.HELP_MSG,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Back ◀", callback_data="start")]]
            ),
        )
    elif "start" in cb_data:
        await cmd.message.edit(
            Messages.START_MSG,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Help ❓", callback_data="help"),
                        InlineKeyboardButton(
                            "Developer 🧑‍💻", url="https://t.me/SorceryBhai"
                        ),
                    ],
                    [
                        InlineKeyboardButton("Close ❌", callback_data="close"),
                        InlineKeyboardButton(
                            "Source Code 📝",
                            url="https://github.com/artemiszuk/upload_Z",
                        ),
                    ],
                ]
            ),
        )
    elif "close" in cb_data:
        current_user_id = cmd.message.reply_to_message.from_user.id
        current_touched_user_id = cmd.from_user.id
        if current_user_id != current_touched_user_id:
          await client.answer_callback_query(
              callback_query_id=cmd.id,
              text="not your msg 🤔🤔",
              show_alert=True,
              cache_time=0,
          )
          return
        await cmd.message.delete()
    elif "cancel" in cb_data:
        Var.cancel[cmd.from_user.id] = True
    elif "toggle" in cb_data:
        current_user_id = cmd.message.reply_to_message.from_user.id
        current_touched_user_id = cmd.from_user.id
        if current_user_id != current_touched_user_id:
          await client.answer_callback_query(
              callback_query_id=cmd.id,
              text="not your msg 🤔🤔",
              show_alert=True,
              cache_time=0,
          )
          return
        user_id = cmd.from_user.id
        print(user_id)
        Var.upload_as_doc[user_id] = not Var.upload_as_doc[user_id]
        text = "**⚙TOGGLE MENU:**\n[__Click to change__]\n\nVideo File Will be Uploaded as "
        if Var.upload_as_doc[user_id]:
            text_append = "Document 📁"
        else:
            text_append = "Streamable 🎬"
        await cmd.message.edit(
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
