import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# === Config ===
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# === Logging ===
logging.basicConfig(level=logging.INFO)

# === Memory per user ===
user_memory = {}

# === OpenRouter ChatGPT-compatible request ===
async def ask_openrouter(user_id: int, prompt: str) -> str:
    if user_id not in user_memory:
        user_memory[user_id] = []

    user_memory[user_id].append({"role": "user", "content": prompt})

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": user_memory[user_id],
    }

    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload)
        data = response.json()
        reply = data["choices"][0]["message"]["content"]
        user_memory[user_id].append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        return f"❌ Error: {str(e)}"

# === Telegram Handlers ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! من چت جی بی تی هستم 🤖\nسوالتو بپرس!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    user_id = update.effective_user.id
    intro = "چت جی بی تی 🤖:\n"
    await update.message.reply_text("🧠 در حال فکر کردن...")
    response = await ask_openrouter(user_id, user_input)
    await update.message.reply_text(intro + response)

# === Run Bot ===
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
