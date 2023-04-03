from botFunctions import ban_user, delete_message
from helpers import get_group_rules, increment_user_warnings_or_delete, is_valid_text


from telegram import Update
from telegram.ext import ContextTypes


async def filter_words(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # analyze text from caption or normal message
    text = update.message.text or update.message.caption

    isValid, reason = is_valid_text(text)
    if isValid:
        return

    await delete_message(update, reason)

    shouldBan, warningsAmount = increment_user_warnings_or_delete(
        update.effective_user.id
    )
    if shouldBan:
        await ban_user(update)
    else:
        await update.effective_chat.send_message(
            f"{update.effective_user.full_name} זאת ההזהרה {'הראשונה' if warningsAmount==1 else 'השנייה' } שלך, בפעם השלישית שתפר את חוקי הקבוצה תזרק מהקבוצה!"
        )


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
