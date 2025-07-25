# Copyright (C) 2025 by Alexa_Help @ Github, < https://github.com/TheTeamAlexa >
# Subscribe On YT < Jankari Ki Duniya >. All rights reserved. © Alexa © Yukki.

"""
TheTeamAlexa is a project of Telegram bots with variety of purposes.
Copyright (c) 2021 ~ Present Team Alexa <https://github.com/TheTeamAlexa>

This program is free software: you can redistribute it and can modify
as you want or you can collabe if you have new ideas.
"""

import os
from random import randint

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from AlexaMusic import Carbon, YouTube, app
from AlexaMusic.utils.database import (
    delete_playlist,
    get_playlist,
    get_playlist_names,
    save_playlist,
)
from AlexaMusic.utils.decorators.language import language, languageCB
from AlexaMusic.utils.inline.playlist import (
    botplaylist_markup,
    get_playlist_markup,
    warning_markup,
)
from AlexaMusic.utils.pastebin import Alexabin
from AlexaMusic.utils.stream.stream import stream
from config import BANNED_USERS, SERVER_PLAYLIST_LIMIT
from strings import get_command

# Command
PLAYLIST_COMMAND = get_command("PLAYLIST_COMMAND")
DELETEPLAYLIST_COMMAND = get_command("DELETEPLAYLIST_COMMAND")


@app.on_message(filters.command(PLAYLIST_COMMAND) & ~BANNED_USERS)
@language
async def check_playlist(client, message: Message, _):
    _playlist = await get_playlist_names(message.from_user.id)
    if _playlist:
        get = await message.reply_text(_["playlist_2"])
    else:
        return await message.reply_text(_["playlist_3"])
    msg = _["playlist_4"]
    count = 0
    for shikhar in _playlist:
        _note = await get_playlist(message.from_user.id, shikhar)
        title = _note["title"]
        title = title.title()
        duration = _note["duration"]
        count += 1
        msg += f"\n\n{count}- {title[:70]}\n"
        msg += _["playlist_5"].format(duration)
    link = await Alexabin(msg)
    lines = msg.count("\n")
    car = os.linesep.join(msg.split(os.linesep)[:17]) if lines >= 17 else msg
    carbon = await Carbon.generate(car, randint(100, 10000000000))
    await get.delete()
    await message.reply_photo(carbon, caption=_["playlist_15"].format(link))


@app.on_message(filters.command(DELETEPLAYLIST_COMMAND) & filters.group & ~BANNED_USERS)
@language
async def del_group_message(client, message: Message, _):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["PL_B_6"],
                    url=f"https://t.me/{app.username}?start=delplaylists",
                ),
            ]
        ]
    )
    await message.reply_text(_["playlist_6"], reply_markup=upl)


async def get_keyboard(_, user_id):
    _playlist = await get_playlist_names(user_id)
    count = len(_playlist)
    buttons = []
    for x in _playlist:
        _note = await get_playlist(user_id, x)
        title = _note["title"]
        title = title.title()
        buttons.append(
            [
                InlineKeyboardButton(
                    text=title,
                    callback_data=f"del_playlist {x}",
                )
            ]
        )
    buttons.append(
        [
            InlineKeyboardButton(text=_["PL_B_5"], callback_data="delete_warning"),
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close"),
        ]
    )
    keyboard = InlineKeyboardMarkup(buttons)
    return keyboard, count


@app.on_message(
    filters.command(DELETEPLAYLIST_COMMAND) & filters.private & ~BANNED_USERS
)
@language
async def del_plist_msg(client, message: Message, _):
    _playlist = await get_playlist_names(message.from_user.id)
    if _playlist:
        get = await message.reply_text(_["playlist_2"])
    else:
        return await message.reply_text(_["playlist_3"])
    keyboard, count = await get_keyboard(_, message.from_user.id)
    await get.edit_text(_["playlist_7"].format(count), reply_markup=keyboard)


@app.on_callback_query(filters.regex("play_playlist") & ~BANNED_USERS)
@languageCB
async def play_playlist(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    mode = callback_data.split(None, 1)[1]
    user_id = CallbackQuery.from_user.id
    _playlist = await get_playlist_names(user_id)
    if not _playlist:
        try:
            return await CallbackQuery.answer(
                _["playlist_3"],
                show_alert=True,
            )
        except Exception:
            return
    chat_id = CallbackQuery.message.chat.id
    user_name = CallbackQuery.from_user.first_name
    await CallbackQuery.message.delete()
    try:
        await CallbackQuery.answer()
    except Exception:
        pass
    video = True if mode == "v" else None
    mystic = await CallbackQuery.message.reply_text(_["play_1"])
    result = list(_playlist)
    try:
        await stream(
            _,
            mystic,
            user_id,
            result,
            chat_id,
            user_name,
            CallbackQuery.message.chat.id,
            video,
            streamtype="playlist",
        )
    except Exception as e:
        ex_type = type(e).__name__
        err = e if ex_type == "AssistantErr" else _["general_3"].format(ex_type)
        return await mystic.edit_text(err)
    return await mystic.delete()


@app.on_callback_query(filters.regex("add_playlist") & ~BANNED_USERS)
@languageCB
async def add_playlist(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    videoid = callback_data.split(None, 1)[1]
    user_id = CallbackQuery.from_user.id
    _check = await get_playlist(user_id, videoid)
    if _check:
        try:
            return await CallbackQuery.answer(_["playlist_8"], show_alert=True)
        except Exception:
            return
    _count = await get_playlist_names(user_id)
    count = len(_count)
    if count == SERVER_PLAYLIST_LIMIT:
        try:
            return await CallbackQuery.answer(
                _["playlist_9"].format(SERVER_PLAYLIST_LIMIT),
                show_alert=True,
            )
        except Exception:
            return
    (
        title,
        duration_min,
        duration_sec,
        thumbnail,
        vidid,
    ) = await YouTube.details(videoid, True)
    title = (title[:50]).title()
    plist = {
        "videoid": vidid,
        "title": title,
        "duration": duration_min,
    }
    await save_playlist(user_id, videoid, plist)
    try:
        title = (title[:30]).title()
        return await CallbackQuery.answer(
            _["playlist_10"].format(title), show_alert=True
        )
    except Exception:
        return


@app.on_callback_query(filters.regex("del_playlist") & ~BANNED_USERS)
@languageCB
async def del_plist(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    videoid = callback_data.split(None, 1)[1]
    user_id = CallbackQuery.from_user.id
    deleted = await delete_playlist(CallbackQuery.from_user.id, videoid)
    if deleted:
        try:
            await CallbackQuery.answer(_["playlist_11"], show_alert=True)
        except Exception:
            pass
    else:
        try:
            return await CallbackQuery.answer(_["playlist_12"], show_alert=True)
        except Exception:
            return
    keyboard, count = await get_keyboard(_, user_id)
    return await CallbackQuery.edit_message_reply_markup(reply_markup=keyboard)


@app.on_callback_query(filters.regex("delete_whole_playlist") & ~BANNED_USERS)
@languageCB
async def del_whole_playlist(client, CallbackQuery, _):
    _playlist = await get_playlist_names(CallbackQuery.from_user.id)
    for x in _playlist:
        await delete_playlist(CallbackQuery.from_user.id, x)
    return await CallbackQuery.edit_message_text(_["playlist_13"])


@app.on_callback_query(filters.regex("get_playlist_playmode") & ~BANNED_USERS)
@languageCB
async def get_playlist_playmode_(client, CallbackQuery, _):
    try:
        await CallbackQuery.answer()
    except Exception:
        pass
    buttons = get_playlist_markup(_)
    return await CallbackQuery.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@app.on_callback_query(filters.regex("delete_warning") & ~BANNED_USERS)
@languageCB
async def delete_warning_message(client, CallbackQuery, _):
    try:
        await CallbackQuery.answer()
    except Exception:
        pass
    upl = warning_markup(_)
    return await CallbackQuery.edit_message_text(_["playlist_14"], reply_markup=upl)


@app.on_callback_query(filters.regex("home_play") & ~BANNED_USERS)
@languageCB
async def home_play_(client, CallbackQuery, _):
    try:
        await CallbackQuery.answer()
    except Exception:
        pass
    buttons = botplaylist_markup(_)
    return await CallbackQuery.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@app.on_callback_query(filters.regex("del_back_playlist") & ~BANNED_USERS)
@languageCB
async def del_back_playlist(client, CallbackQuery, _):
    user_id = CallbackQuery.from_user.id
    _playlist = await get_playlist_names(user_id)
    if _playlist:
        try:
            await CallbackQuery.answer(_["playlist_2"], show_alert=True)
        except Exception:
            pass
    else:
        try:
            return await CallbackQuery.answer(_["playlist_3"], show_alert=True)
        except Exception:
            return
    keyboard, count = await get_keyboard(_, user_id)
    return await CallbackQuery.edit_message_text(
        _["playlist_7"].format(count), reply_markup=keyboard
    )
