from telegram import Update
from telegram.error import TelegramError
from telegram.ext import (
    ApplicationBuilder,
    ChatJoinRequestHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from BotSecrets import get_secrets
from helpers import get_group_rules, increment_user_warnings_or_delete, is_valid_text


async def filter_words(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text or update.message.caption
    isValid, reason = is_valid_text(text)
    if isValid:
        return

    await update.effective_chat.send_message(
        "נמחקה הודעה לא חוקית של המשתמש "
        + update.effective_user.full_name
        + f"\nההודעה הכילה {reason}"
    )
    try:
        await update.message.delete()
    except TelegramError as e:
        await update.effective_chat.send_message("כשל במחיקת הודעה: " + e.message)
    try:
        shouldBan, warningsAmount = increment_user_warnings_or_delete(
            update.effective_user.id
        )
        if shouldBan:
            if update.effective_user.id != 227093322:
                await update.effective_chat.ban_member(update.effective_user.id)
            await update.effective_chat.send_message(
                f"המשתמש {update.effective_user.full_name} הועף מהקבוצה לאחר הפרת הכללים 3 פעמים..."
            )
        else:
            await update.effective_chat.send_message(
                f"{update.effective_user.full_name} זאת ההזהרה {'הראשונה' if warningsAmount==1 else 'השנייה' } שלך, בפעם השלישית שתפר את חוקי הקבוצה תזרק מהקבוצה!"
            )
    except TelegramError as e:
        await update.effective_chat.send_message("כשל בזריקת משתמש: " + e.message)


async def verify_join_requests(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    request = update.chat_join_request
    isValid, reason = is_valid_text(request.from_user.full_name + (request.bio or ""))
    if isValid:
        await request.approve()
        await update.effective_chat.send_message(
            get_group_rules(request.from_user.full_name)
        )
    else:
        await request.decline()
        await update.effective_chat.send_message(
            f"המשתמש {update.effective_user.full_name} נחסם מכניסה לקבוצה\n{reason}"
        )


secrets = get_secrets()

app = ApplicationBuilder().token(secrets["bot_token"]).build()

app.add_handler(MessageHandler(filters.TEXT | filters.CAPTION, filter_words))
app.add_handler(ChatJoinRequestHandler(verify_join_requests))


print("bot running!")
app.run_polling()
