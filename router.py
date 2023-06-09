import json
from typing import Optional, Union

from telegram import (
    Chat,
    ChatJoinRequest,
    ChatPermissions,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    User,
)
from telegram.ext import ContextTypes

from botFunctions import ban_user, delete_message, is_admin
from dataStructures import BotActions, ReferralSource, kick_messages
from db import add_poll_answer, aggregate_poll_answers
from decorators import only_admins, only_private, removes_custom_keyboard
from helpers import (
    add_runtime_censor_word,
    get_group_rules,
    get_join_poll,
    get_runtime_banned_words,
    increment_user_warnings_or_delete,
    is_banned,
    is_valid_text,
    remove_runtime_censor_word,
)


async def filter_words(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if (
        update.message is None
        or update.effective_user is None
        or update.effective_chat is None
    ):
        return
    for entity in update.message.entities + update.message.caption_entities:
        if entity.type in [entity.TEXT_LINK, entity.URL] and not await is_admin(update):
            await update.message.delete()
            await update.effective_chat.send_message(
                f"{update.effective_user.full_name} שים לב כי אסור לשלוח לינקים בקבוצה."
                + " אם ברצונך לפרסם לינק ששאר חברי הקבוצה צריכים לראות פנה למנהלי הקבוצה והם יפרסמו את הלינק בשמך"
            )
            break
    text = " ".join([update.message.text or "", update.message.caption or ""])

    info = is_valid_text(text)
    if not info["is_invalid"]:
        return

    await delete_message(update, info["msg"])

    info = increment_user_warnings_or_delete(update.effective_user.id, info)
    if info["action"] == BotActions.ban:
        await ban_user(
            update.effective_chat,
            update.effective_user,
            kick_messages[info["invalid_action"]],
        )
    else:
        await update.effective_chat.send_message(
            f"{update.effective_user.full_name} זאת האזהרה {'הראשונה' if info['warnings_amount']==1 else 'השנייה' } שלך, בפעם השלישית שתפר את חוקי הקבוצה תזרק מהקבוצה!"
        )


async def new_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if (
        update.message is None
        or update.message.new_chat_members is None
        or update.effective_chat is None
    ):
        return

    for user in update.message.new_chat_members:
        await filter_new_members(user, update.effective_chat, update.message.from_user)


async def great_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.chat_join_request is None or update.effective_chat is None:
        return
    await filter_new_members(update.chat_join_request, update.effective_chat)


async def filter_new_members(
    request: Union[ChatJoinRequest, User], chat: Chat, from_user: Optional[User] = None
):
    user = request if isinstance(request, User) else request.from_user
    bio = request.bio or "" if isinstance(request, ChatJoinRequest) else ""

    info = is_valid_text(user.full_name + bio)
    if not info["is_invalid"]:
        if isinstance(request, ChatJoinRequest):
            await request.approve()
        await chat.restrict_member(
            user.id,
            ChatPermissions.no_permissions(),
        )
        await chat.send_message(get_group_rules(user.full_name))
        pollText, replyMarkup = get_join_poll(user.full_name, user.id)
        await chat.send_message(pollText, reply_markup=replyMarkup)
    else:
        ban_message = f"עקב {info['msg']}"
        if isinstance(request, ChatJoinRequest):
            await request.decline()
            await chat.send_message(ban_message)
        else:
            await ban_user(chat, user, ban_message)
        if from_user and info["action"] == BotActions.ban:
            await ban_user(
                chat,
                from_user,
                f"עקב נסיון להכניס משתמש ערבי.",
            )


@removes_custom_keyboard
async def send_group_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat is None or update.effective_user is None:
        return
    await update.effective_chat.send_message(
        f"""שלום {update.effective_user.full_name},
הבוט הזה הוא בוט לניהול קבוצת הימין בטלגרם, ניתן להצטרף לקבוצה בקישור: https://t.me/+SHMn122vwFdlM2Jk
מעבר לשליחת הודעה זאת אין לבוט כל יכולת לדבר בצ'אט פרטי."""
    )


@removes_custom_keyboard
@only_admins
async def censor_word(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if (
        update.effective_chat is None
        or update.effective_user is None
        or update.message is None
    ):
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


@only_admins
async def uncensor_word(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if (
        update.effective_chat is None
        or update.effective_user is None
        or update.message is None
    ):
        return

    if context.args is None or len(context.args) == 0:
        keyboard = [
            [f"/uncensor@yemin_group_bot {word}"] for word in get_runtime_banned_words()
        ]
        await update.message.reply_text(
            "שלח לי את הפקודה ואחריה את המילה שתרצה להוריד ממאגר החסימות, לדוגמא\n/uncensor@yemin_group_bot חלול",
            reply_markup=ReplyKeyboardMarkup(keyboard),
        )
    elif len(context.args) > 1:
        await update.message.reply_text(
            "אני יכול לחסום רק מילים יחידות, כך שלא יכול להיות שיש משפט חסום במאגר"
        )
    elif not is_banned(context.args[0]):
        await update.message.reply_text(
            "המילה ששלחת לא חסומה כרגע, כדי לחסום אותה, נסה את הפקודה הזאת:\n"
            + f"/censor@yemin_group_bot {context.args[0]}"
        )
    else:
        await update.message.reply_text(
            "המילה ששלחת תורד ממאגר החסימות", reply_markup=ReplyKeyboardRemove()
        )
        remove_runtime_censor_word(context.args[0])


@removes_custom_keyboard
@only_private
async def poll_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return

    pollAnswers = aggregate_poll_answers()
    totalAnswersCount = sum([c["count"] for c in pollAnswers])
    await update.message.reply_text(
        f"עד כה {totalAnswersCount} אנשים הגיבו לשאלון\n"
        + "\n".join(
            [
                f"{answer[0]} -> {(answer[1]/totalAnswersCount)*100}%, {answer[1]}"
                for answer in pollAnswers
            ]
        )
    )


@removes_custom_keyboard
@only_private
async def get_censored_words(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if update.message is None:
        return

    await update.message.reply_text(
        "אלו המילים החסומות כרגע:\n" + "\n".join(get_runtime_banned_words())
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""

    query = update.callback_query
    if query is None:
        return

    if query.data is None:
        return
    callbackData = json.loads(query.data)
    if callbackData[0] not in (x.value for x in ReferralSource):
        return
    if callbackData[1] != query.from_user.id:
        await query.answer("ההודעה מיודעת למשתמש אחר")
        return

    add_poll_answer(callbackData[0])
    await query.answer("תודה על ההיענות!")
    await query.delete_message()
    if update.effective_chat is None or update.effective_user is None:
        return
    await update.effective_chat.restrict_member(
        update.effective_user.id,
        ChatPermissions.all_permissions(),
    )
