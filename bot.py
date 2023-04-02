import json

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

from BotSecrets import get_secrets
from helpers import is_arabic


async def filter_words(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text or update.message.caption
    arabic_script = [0, 0]
    encountered = False
    for i, ch in enumerate(text):
        if is_arabic(ch):
            if not encountered:
                arabic_script[0] = i
                encountered = True
            else:
                arabic_script[1] = i

    if encountered:
        await update.message.reply_text("הודעה לא חוקית")


secrets = get_secrets()

app = ApplicationBuilder().token(secrets["bot_token"]).build()

app.add_handler(MessageHandler(filters.TEXT | filters.CAPTION, filter_words))

print("bot running!")
app.run_polling()
