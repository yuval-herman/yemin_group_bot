from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

from BotSecrets import get_secrets
from helpers import is_arabic, is_banned, load_word_dict


async def filter_words(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text or update.message.caption

    encountered = False
    for word in text.split():
        if is_banned(word):
            encountered = True
            break
        for ch in word:
            if is_arabic(ch):
                encountered = True
                break

    if encountered:
        await update.effective_chat.send_message(
            "נמחקה הודעה לא חוקית של המשתמש " + update.effective_user.full_name
        )
        await update.message.delete()


secrets = get_secrets()

app = ApplicationBuilder().token(secrets["bot_token"]).build()

app.add_handler(MessageHandler(filters.TEXT | filters.CAPTION, filter_words))

print(is_banned("זונה"))
print("bot running!")
app.run_polling()
