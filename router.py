from botFunctions import ban_user, delete_message
from dataStructures import BotActions, InvalidActions
from helpers import get_group_rules, increment_user_warnings_or_delete, is_valid_text


from telegram import ChatJoinRequest, Update
from telegram.ext import ContextTypes


async def filter_words(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # analyze text from caption or normal message
    if (
        update.message is None
        or update.effective_user is None
        or update.effective_chat is None
    ):
        return
    text = update.message.text or update.message.caption or ""

    info = is_valid_text(text)
    if not info["is_invalid"]:
        return

    await delete_message(update, info["msg"])

    info = increment_user_warnings_or_delete(update.effective_user.id, info)
    if info["action"] == BotActions.ban:
        await ban_user(update, info["invalid_action"])
    else:
        await update.effective_chat.send_message(
            f"{update.effective_user.full_name} זאת האזהרה {'הראשונה' if info['warnings_amount']==1 else 'השנייה' } שלך, בפעם השלישית שתפר את חוקי הקבוצה תזרק מהקבוצה!"
        )


async def verify_join_requests(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if update.effective_user is None or update.effective_chat is None:
        return
    request: ChatJoinRequest = update.chat_join_request  # type: ignore
    info = is_valid_text(request.from_user.full_name + (request.bio or ""))
    if not info["is_invalid"]:
        await request.approve()
        await update.effective_chat.send_message(
            get_group_rules(request.from_user.full_name)
        )
    else:
        await request.decline()
        await update.effective_chat.send_message(
            f"המשתמש {update.effective_user.full_name} נחסם מכניסה לקבוצה\n{info['msg']}"
        )
