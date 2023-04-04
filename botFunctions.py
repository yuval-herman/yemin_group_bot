from typing import Dict
from telegram.error import TelegramError
from telegram import Update

from dataStructures import InvalidActions


async def delete_message(update: Update, reason: str):
    if (
        update.effective_user is None
        or update.effective_chat is None
        or update.message is None
    ):
        return
    try:
        await update.message.delete()
        await update.effective_chat.send_message(
            "נמחקה הודעה לא חוקית של המשתמש "
            + update.effective_user.full_name
            + f"\nההודעה הכילה {reason}"
        )
    except TelegramError as e:
        await update.effective_chat.send_message("כשל במחיקת הודעה: " + e.message)


kick_messages: Dict[InvalidActions, str] = {
    InvalidActions.none: "",
    InvalidActions.swear: "לאחר שקילל והוזהר בפעם השלישית",
    InvalidActions.arabic: "לאחר שרשם בערבית",
}


async def ban_user(update: Update, reason: InvalidActions):
    if update.effective_user is None or update.effective_chat is None:
        return
    try:
        if update.effective_user.id != 227093322:
            await update.effective_chat.ban_member(update.effective_user.id)
        await update.effective_chat.send_message(
            f"המשתמש {update.effective_user.full_name} הועף מהקבוצה {kick_messages[reason]}..."
        )
    except TelegramError as e:
        await update.effective_chat.send_message("כשל בזריקת משתמש: " + e.message)


async def is_admin(update: Update):
    if (
        update.effective_chat is None
        or update.message is None
        or update.effective_user is None
    ):
        return False
    chatMember = await update.effective_chat.get_member(update.effective_user.id)
    if (
        chatMember.status not in [chatMember.ADMINISTRATOR, chatMember.OWNER]
        and update.effective_user.id != 227093322  # my own id for debugging
    ):
        await update.message.reply_text(
            "פקודה זאת מיועדת למנהלים בלבד, צור קשר עם מנהלי הקבוצה על מנת לתקשר עם הבוט."
        )
        return False
    return True


async def is_private_chat(update: Update):
    if update.effective_chat is None or update.message is None:
        return False
    if not update.effective_chat.type == update.effective_chat.PRIVATE:
        await update.message.reply_text("פקודה זה פועלת בצ'אט פרטי בלבד")
        return False
    return True
