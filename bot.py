import itertools
import random
import typing

import tqdm
from pyrogram import Client, filters
from pyrogram.types import Message

from secrets import CLIENT_SECRET

app = Client(**CLIENT_SECRET)




@app.on_message(filters.text & (~filters.me))
def reply_message(_, msg: Message):
    msg.reply_text(f"Вбийте в поле відповіді 42!")
    return None


app.run()
