from telegram.ext import (
    ApplicationBuilder,
    ChatJoinRequestHandler,
    MessageHandler,
    filters,
)

from BotSecrets import get_secrets
from router import filter_words, send_group_link, verify_join_requests

secrets = get_secrets()

app = ApplicationBuilder().token(secrets["bot_token"]).build()

app.add_handler(
    MessageHandler(
        (filters.TEXT | filters.CAPTION) & filters.ChatType.GROUPS, filter_words
    )
)
app.add_handler(ChatJoinRequestHandler(verify_join_requests))
app.add_handler(MessageHandler(filters.ChatType.PRIVATE, send_group_link))


print("bot running!")
app.run_polling()
