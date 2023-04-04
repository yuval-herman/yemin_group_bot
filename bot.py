from telegram.ext import (
    ApplicationBuilder,
    ChatJoinRequestHandler,
    MessageHandler,
    CommandHandler,
    filters,
)

from BotSecrets import get_secrets
from router import (
    uncensor_word,
    filter_words,
    send_group_link,
    verify_join_requests,
    censor_word,
)

secrets = get_secrets()

app = ApplicationBuilder().token(secrets["bot_token"]).build()

app.add_handler(MessageHandler(filters.ChatType.PRIVATE, send_group_link))
app.add_handler(CommandHandler("censor", censor_word))
app.add_handler(CommandHandler("uncensor", uncensor_word))
app.add_handler(
    MessageHandler(
        (filters.TEXT | filters.CAPTION) & filters.ChatType.GROUPS, filter_words
    )
)
app.add_handler(ChatJoinRequestHandler(verify_join_requests))


print("bot running!")
app.run_polling()
