from telegram import ChatJoinRequest, Update
from telegram.ext import ContextTypes

from botFunctions import ban_user, delete_message, is_admin
from dataStructures import BotActions, InvalidActions
from helpers import (
    add_runtime_censor_word,
    get_group_rules,
    increment_user_warnings_or_delete,
    is_valid_text,
)


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


async def send_group_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat is None or update.effective_user is None:
        return
    await update.effective_chat.send_message(
        f"""שלום {update.effective_user.full_name},
הבוט הזה הוא בוט לניהול קבוצת הימין בטלגרם, ניתן להצטרף לקבוצה בקישור: https://t.me/+SHMn122vwFdlM2Jk
מעבר לשליחת הודעה זאת אין לבוט כל יכולת לדבר בצ'אט פרטי."""
    )


async def censor_word(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if (
        update.effective_chat is None
        or update.effective_user is None
        or update.message is None
    ):
        return

    if not await is_admin(update):
        return
    if context.args is None or len(context.args) == 0:
        await update.message.reply_text(
            "שלח לי את הפקודה ואחריה את המילה שתרצה לחסום, לדוגמא\n/censor@yemin_group_bot חלול"
        )
    elif len(context.args) > 1:
        await update.message.reply_text(
            "אני יכול לחסום רק מילים יחידות, אם תרצה לחסום משפט, מצא את המילה הפוגענית ורשום לי רק אותה, לדוגמא\n"
            + "/censor@yemin_group_bot אני שונא אותך! -> /censor@yemin_group_bot שונא"
        )
    else:
        await update.effective_chat.send_message("המילה ששלחת תחסם")
        add_runtime_censor_word(context.args[0])
    try:
        await update.message.delete()
    except:
        pass
