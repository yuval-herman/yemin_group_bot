from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    ChatJoinRequestHandler,
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
    uncensor_word,
)

secrets = get_secrets()

app = ApplicationBuilder().token(secrets["bot_token"]).build()

app.add_handler(ChatJoinRequestHandler(great_new_members))

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
app.add_handler(MessageHandler(filters.ChatType.PRIVATE, send_group_link))

print("bot running!")
app.run_polling()
