import logging
from sys import argv

from telegram import constants
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    ChatJoinRequestHandler,
    ChatMemberHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from BotSecrets import get_secrets
from router import (
    button,
    censor_word,
    filter_words,
    get_censored_words,
    great_new_members,
    poll_stats,
    send_group_link,
    new_chat_members,
    uncensor_word,
)

secrets = get_secrets()
is_dev_mode = len(argv) >= 2 and argv[1].lower() == "dev"
token = secrets["test_bot_token"] if is_dev_mode else secrets["bot_token"]

app = ApplicationBuilder().token(token).build()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG if is_dev_mode else logging.INFO,
)
app.add_handler(ChatJoinRequestHandler(great_new_members))
app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_chat_members))


app.add_handler(CommandHandler("censor", censor_word))
app.add_handler(CommandHandler("uncensor", uncensor_word))
app.add_handler(CommandHandler("poll_stats", poll_stats))
app.add_handler(CommandHandler("get_censored_words", get_censored_words))

app.add_handler(CallbackQueryHandler(button))
app.add_handler(
    MessageHandler(
        (filters.TEXT | filters.CAPTION) & filters.ChatType.GROUPS, filter_words
    )
)
app.run_polling()
