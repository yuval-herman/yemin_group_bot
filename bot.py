import json

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

from BotSecrets import get_secrets


async def filter_words(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text or update.message.caption
    arabic_script = [0, 0]
    encountered = False
    for i, ch in enumerate(text):
        if (
            "\u0600" <= ch <= "\u06FF"
            or "\u0750" <= ch <= "\u077F"
            or "\u08A0" <= ch <= "\u08FF"
            or "\uFB50" <= ch <= "\uFDFF"
            or "\uFE70" <= ch <= "\uFEFF"
            or "\U00010E60" <= ch <= "\U00010E7F"
            or "\U0001EE00" <= ch <= "\U0001EEFF"
        ):
            if not encountered:
                arabic_script[0] = i
                encountered = True
            else:
                arabic_script[1] = i

    if arabic_script:
        await update.message.reply_text(arabic_script or text)


secrets = get_secrets()

app = ApplicationBuilder().token(secrets["bot_token"]).build()

app.add_handler(MessageHandler(filters.TEXT | filters.CAPTION, filter_words))

print("bot running!")
app.run_polling()
