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
    if chatMember.status not in [chatMember.ADMINISTRATOR, chatMember.OWNER]:
        await update.message.reply_text(
            "פקודה זאת מיועדת למנהלים בלבד, אם נתקלת במילה שלדעתך צריך לחסום, צור קשר עם מנהלי הקבוצה והם יחסמו אותה."
        )
        return False
    return True
