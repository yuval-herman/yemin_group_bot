from functools import wraps
from telegram.ext import ContextTypes
from telegram import ReplyKeyboardRemove, Update

from botFunctions import is_admin, is_private_chat


def only_admins(func):
    @wraps(func)
    async def allow_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if (
            update.effective_chat is None
            or update.effective_user is None
            or update.message is None
        ):
            return

        if await is_admin(update):
            return await func(update, context)
        await update.message.reply_text("פקודה זה מיועדת למנהלים בלבד")

    return allow_admin


def only_private(func):
    @wraps(func)
    async def allow_private(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat is None or update.message is None:
            return

        if await is_private_chat(update.effective_chat):
            return await func(update, context)
        await update.message.reply_text("פקודה זה פועלת בצ'אט פרטי בלבד")

    return allow_private


def removes_custom_keyboard(func):
    @wraps(func)
    async def remove_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat is None:
            return
        await func(update, context)

        message = await update.effective_chat.send_message(
            "ignore this", reply_markup=ReplyKeyboardRemove()
        )
        await message.delete()

    return remove_keyboard
