
from pyrogram import Client, filters
from pyrogram.types import Message, InputMediaPhoto

from mono_helper import MonoHelper
import pause_game_helper
from bot_secrets import CLIENT_SECRET, STICKER_TO_WORD, HELLO_ID, SONG_ID, SELF_ID, USER_TO_ACCOUNT_ID

app = Client(**CLIENT_SECRET)

WORD_TO_STICKER = {v: k for k, v in STICKER_TO_WORD.items()}

VERSION = "2.0.0"


def handle_balance(msg: Message):
    ask = float(msg.text)
    mh = MonoHelper(msg.chat.id)
    resp = mh.reply(ask)
    msg.reply_text(resp)
    return resp


def is_version(msg: str) -> bool:
    return msg == '/ver'


@app.on_message(filters=(filters.text | filters.sticker) & filters.private & (~ filters.user(SELF_ID)))
def reply_message(_, msg: Message):
    if is_version(msg.text):
        msg.reply_text(VERSION)
        return None
    elif pause_game_helper.is_reel(msg.text):
        frames_paths = pause_game_helper.pause_game_full(msg.text)
        if not frames_paths:
            msg.reply_text("Failed to detect pause game frames :(")
            return None
        media_group = [
            InputMediaPhoto(x)
            for x in frames_paths
        ]
        msg.reply_media_group(media_group)
        pause_game_helper.cleanup(frames_paths)
    elif msg.chat.id in USER_TO_ACCOUNT_ID:
        return handle_balance(msg)
    elif not hasattr(msg, 'sticker') or msg.sticker is None or msg.sticker.file_unique_id not in STICKER_TO_WORD:
        reply_txt = "Привіт!"
        msg.reply_text(reply_txt)
        msg.reply_sticker(HELLO_ID)
        msg.reply_text("Шукаєте дівчину? Шукайте, успіхів!")
        msg.reply_audio(SONG_ID)
    else:
        msg.reply_text(STICKER_TO_WORD[msg.sticker.file_unique_id])
    return None


app.run()
