import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from brain import ask, reset

load_dotenv()
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID", "0"))


async def start(update, context):
    await update.message.reply_text("Hi! I am your AI assistant. Ask me anything, or send me a photo.")


async def reset_command(update, context):
    reset(update.effective_chat.id)
    await update.message.reply_text("Okay, I have forgotten our chat. Let's start fresh.")


async def handle_text(update, context):
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("Sorry, this is a private bot.")
        return
    answer = ask(update.effective_chat.id, update.message.text)
    await update.message.reply_text(answer)


async def handle_photo(update, context):
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("Sorry, this is a private bot.")
        return
    photo = await update.message.photo[-1].get_file()
    image_bytes = await photo.download_as_bytearray()
    question = update.message.caption or "What is in this photo?"
    answer = ask(update.effective_chat.id, question, bytes(image_bytes))
    await update.message.reply_text(answer)


app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("reset", reset_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
print("Bot is running...")
app.run_polling()
