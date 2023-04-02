from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ChatJoinRequestHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

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
        await update.effective_chat.ban_member(update.effective_user.id)
        await update.effective_chat.send_message(
            f"המשתמש {update.effective_user.full_name} הועף מהקבוצה לאחר הפרת הכללים"
        )


async def verify_join_requests(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    disallow = False
    request = update.chat_join_request
    for ch in request.from_user.full_name + (request.bio or ""):
        if is_arabic(ch):
            disallow = True
    if disallow:
        await request.decline()
        await update.effective_chat.send_message(
            f"המשתמש {update.effective_user.full_name} נחסם מכניסה לקבוצה"
        )
    else:
        await request.approve()


secrets = get_secrets()

app = ApplicationBuilder().token(secrets["bot_token"]).build()

app.add_handler(MessageHandler(filters.TEXT | filters.CAPTION, filter_words))
app.add_handler(ChatJoinRequestHandler(verify_join_requests))


print("bot running!")
app.run_polling()
