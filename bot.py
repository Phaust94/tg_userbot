
from pyrogram import Client, filters
from pyrogram.types import Message, Sticker

from secrets import CLIENT_SECRET

app = Client(**CLIENT_SECRET)


@app.on_message()
def reply_message(_, msg: Message):
    msg.reply_text("Привіт!")
    msg.reply_sticker('CAACAgIAAxkBAAOLYoK4i1VTbrB32xLm8556nTA7uB4AAt4cAALyzRlIIYbPY7VRnWUeBA')
    msg.reply_text("Шукаєте дівчину? Шукайте, успіхів!")
    return None


app.run()
