import typing

from pyrogram import Client, filters
from pyrogram.types import Message, InputMediaPhoto

from mono_helper import MonoHelper
import pause_game_helper
from bot_secrets import (
    CLIENT_SECRET,
    STICKER_TO_WORD,
    HELLO_ID,
    SONG_ID,
    SELF_ID,
    USER_TO_ACCOUNT_ID,
)

app = Client(**CLIENT_SECRET)

WORD_TO_STICKER = {v: k for k, v in STICKER_TO_WORD.items()}

VERSION = "2.2.0"


async def handle_balance(msg: Message):
    ask = float(msg.text)
    mh = MonoHelper(msg.chat.id)
    resp = mh.reply(ask)
    await msg.reply_text(resp)
    return resp


def is_version(msg: str) -> bool:
    return msg == "/ver"


async def handle_reply_frames(frames_paths: typing.List[str], msg: Message):
    if not frames_paths:
        await msg.reply_text("Failed to detect pause game frames :(")
        return None
    media_group = [InputMediaPhoto(x) for x in frames_paths]
    await msg.reply_media_group(media_group)
    pause_game_helper.cleanup(frames_paths)
    return None


@app.on_message(filters=filters.video & filters.private & (~filters.user(SELF_ID)))
async def reply_message_video(_, msg: Message):
    video_path = await msg.download()
    frames_paths = pause_game_helper.guess_pause_frame(video_path)
    await handle_reply_frames(frames_paths, msg)
    return None


@app.on_message(
    filters=(filters.text | filters.sticker)
    & filters.private
    & (~filters.user(SELF_ID))
)
async def reply_message(_, msg: Message):
    if is_version(msg.text):
        await msg.reply_text(VERSION)
        return None
    elif msg.chat.id in USER_TO_ACCOUNT_ID:
        return await handle_balance(msg)
    elif (
        not hasattr(msg, "sticker")
        or msg.sticker is None
        or msg.sticker.file_unique_id not in STICKER_TO_WORD
    ):
        reply_txt = "Привіт!"
        await msg.reply_text(reply_txt)
        await msg.reply_sticker(HELLO_ID)
        await msg.reply_text("Шукаєте дівчину? Шукайте, успіхів!")
        await msg.reply_audio(SONG_ID)
    else:
        await msg.reply_text(STICKER_TO_WORD[msg.sticker.file_unique_id])
    return None


app.run()
