
from pyrogram import Client, filters
from pyrogram.types import Message

from mono_helper import MonoHelper
from secrets import CLIENT_SECRET, STICKER_TO_WORD, HELLO_ID, SONG_ID, SELF_ID, USER_TO_ACCOUNT_ID

app = Client(**CLIENT_SECRET)

WORD_TO_STICKER = {v: k for k, v in STICKER_TO_WORD.items()}


def handle_balance(msg: Message):
    ask = float(msg.text)
    mh = MonoHelper(msg.chat.id)
    resp = mh.reply(ask)
    msg.reply_text(resp)
    return resp


@app.on_message(filters=(filters.text | filters.sticker) & filters.private & (~ filters.user(SELF_ID)))
def reply_message(_, msg: Message):
    if msg.chat.id in USER_TO_ACCOUNT_ID:
        return handle_balance(msg)
    if not hasattr(msg, 'sticker') or msg.sticker is None or msg.sticker.file_unique_id not in STICKER_TO_WORD:
        reply_txt = "Привіт!"
        msg.reply_text(reply_txt)
        msg.reply_sticker(HELLO_ID)
        msg.reply_text("Шукаєте дівчину? Шукайте, успіхів!")
        msg.reply_audio(SONG_ID)
    else:
        msg.reply_text(STICKER_TO_WORD[msg.sticker.file_unique_id])
    return None


app.run()
