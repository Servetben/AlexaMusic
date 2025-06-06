# Copyright (C) 2025 by Alexa_Help @ Github, < https://github.com/TheTeamAlexa >
# Subscribe On YT < Jankari Ki Duniya >. All rights reserved. © Alexa © Yukki.

"""
TheTeamAlexa is a project of Telegram bots with variety of purposes.
Copyright (c) 2021 ~ Present Team Alexa <https://github.com/TheTeamAlexa>

This program is free software: you can redistribute it and can modify
as you want or you can collabe if you have new ideas.
"""

import asyncio
import time

from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from config import BANNED_USERS
from strings import get_command
from AlexaMusic import app
from AlexaMusic.misc import SUDOERS
from AlexaMusic.utils import get_readable_time
from AlexaMusic.utils.database import (
    add_banned_user,
    get_banned_count,
    get_banned_users,
    get_served_chats,
    is_banned_user,
    remove_banned_user,
)
from AlexaMusic.utils.decorators.language import language

# Command
GBAN_COMMAND = get_command("GBAN_COMMAND")
UNGBAN_COMMAND = get_command("UNGBAN_COMMAND")
GBANNED_COMMAND = get_command("GBANNED_COMMAND")


@app.on_message(filters.command(GBAN_COMMAND) & SUDOERS)
@language
async def gbanuser(client, message: Message, _):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(_["general_1"])
        user = message.text.split(None, 1)[1]
        user = await app.get_users(user)
        user_id = user.id
        mention = user.mention
    else:
        user_id = message.reply_to_message.from_user.id
        mention = message.reply_to_message.from_user.mention
    if user_id == message.from_user.id:
        return await message.reply_text(_["gban_1"])
    elif user_id == app.id:
        return await message.reply_text(_["gban_2"])
    elif user_id in SUDOERS:
        return await message.reply_text(_["gban_3"])
    is_gbanned = await is_banned_user(user_id)
    if is_gbanned:
        return await message.reply_text(_["gban_4"].format(mention))
    if user_id not in BANNED_USERS:
        BANNED_USERS.add(user_id)
    chats = await get_served_chats()
    served_chats = [int(chat["chat_id"]) for chat in chats]
    time_expected = len(served_chats)
    time_expected = get_readable_time(time_expected)
    mystic = await message.reply_text(
        _["gban_5"].format(mention, time_expected, user.id)
    )
    number_of_chats = 0
    for chat_id in served_chats:
        try:
            await app.ban_chat_member(chat_id, user_id)
            number_of_chats += 1
        except FloodWait as e:
            await asyncio.sleep(int(e.x))
        except Exception:
            pass
    await add_banned_user(user_id)
    await message.reply_text(_["gban_6"].format(mention, number_of_chats))
    await mystic.delete()


@app.on_message(filters.command(UNGBAN_COMMAND) & SUDOERS)
@language
async def gungabn(client, message: Message, _):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(_["general_1"])
        user = message.text.split(None, 1)[1]
        user = await app.get_users(user)
        user_id = user.id
        mention = user.mention
    else:
        user_id = message.reply_to_message.from_user.id
        mention = message.reply_to_message.from_user.mention
    is_gbanned = await is_banned_user(user_id)
    if not is_gbanned:
        return await message.reply_text(_["gban_7"].format(mention))
    if user_id in BANNED_USERS:
        BANNED_USERS.remove(user_id)
    chats = await get_served_chats()
    served_chats = [int(chat["chat_id"]) for chat in chats]
    time_expected = len(served_chats)
    time_expected = get_readable_time(time_expected)
    mystic = await message.reply_text(_["gban_8"].format(mention, time_expected))
    number_of_chats = 0
    for chat_id in served_chats:
        try:
            await app.unban_chat_member(chat_id, user_id)
            number_of_chats += 1
        except FloodWait as e:
            await asyncio.sleep(int(e.x))
        except Exception:
            pass
    await remove_banned_user(user_id)
    await message.reply_text(_["gban_9"].format(mention, number_of_chats))
    await mystic.delete()


@app.on_message(filters.command(GBANNED_COMMAND) & SUDOERS)
@language
async def gbanned_list(client, message: Message, _):
    counts = await get_banned_count()
    if counts == 0:
        return await message.reply_text(_["gban_10"])
    mystic = await message.reply_text(_["gban_11"])
    msg = "ɢʙᴀɴɴᴇᴅ ᴜsᴇʀ:\n\n"
    count = 0
    users = await get_banned_users()
    for user_id in users:
        count += 1
        try:
            user = await app.get_users(user_id)
            user = user.mention or user.first_name
            msg += f"{count}➤ {user}\n"
        except Exception:
            msg += f"{count}➤ [Unfetched User]{user_id}\n"
            continue
    if count == 0:
        return await mystic.edit_text(_["gban_10"])
    else:
        return await mystic.edit_text(msg)
