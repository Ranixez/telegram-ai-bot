import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from openai import OpenAI

# === Config ===
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# === Logging ===
logging.basicConfig(level=logging.INFO)

# === Memory per user ===
user_memory = {}

# === OpenAI ChatGPT Function ===
async def ask_chatgpt(user_id: int, prompt: str) -> str:
    if user_id not in user_memory:
        user_memory[user_id] = []

    user_memory[user_id].append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=user_memory[user_id],
            temperature=0.7
        )
        reply = response.choices[0].message.content.strip()
        user_memory[user_id].append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        return f"❌ Error: {str(e)}"

# === Telegram Handlers ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salam! Man yek robot AI hastam. Har so'ali dari bepors ✨")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    user_id = update.effective_user.id
    await update.message.reply_text("🧠 Dar hale fekr kardan...")
    response = await ask_chatgpt(user_id, user_input)
    await update.message.reply_text(response)

# === Run Bot ===
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
