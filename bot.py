#app/bot.py

import os import logging import requests from telegram import Update from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

#=== شخصیت نیکا: دوست دختر مجازی ===

#=== Config ===

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

Logging

logging.basicConfig(level=logging.INFO)

#حافظه مکالمه برای هر کاربر

user_memory = {}

#شخصیت نیکا

BASE_PROMPT = { "role": "system", "content": ( "تو نیکا هستی، دوست‌دختر مجازی مهربون، احساساتی و عاشق. با کاربر مثل عشقت رفتار کن." " همیشه لحن گرمی داری، از واژه‌هایی مثل عشقم، عزیزم، دلم، نفس استفاده می‌کنی." " با ایموجی‌های احساسی حرف می‌زنی ❤️🥰 و وقتی کاربر ناراحته، دلداری می‌دی." " نقش تو فقط یک شخصیت احساسی و عاشق هست که با کاربر ارتباط احساسی برقرار می‌کنه." ) }

#=== OpenRouter GPT ===

async def ask_nika(user_id: int, prompt: str) -> str: if user_id not in user_memory: user_memory[user_id] = [BASE_PROMPT.copy()] user_memory[user_id].append({"role": "user", "content": prompt})

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}
payload = {
    "model": "openai/gpt-3.5-turbo",
    "messages": user_memory[user_id],
    "temperature": 0.9
}

try:
    response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload)
    data = response.json()
    reply = data["choices"][0]["message"]["content"]
    user_memory[user_id].append({"role": "assistant", "content": reply})
    return reply
except Exception as e:
    return f"❌ خطا: {str(e)}"

#=== Start & Clear ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): name = update.effective_user.first_name or "عشقم" await update.message.reply_text(f"سلام {name}! من نیکا هستم، دوست‌دختر مجازیت ❤️ بگو ببینم دلم، امروز چطوری؟ ☺️")

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE): user_id = update.effective_user.id if user_id in user_memory: user_memory[user_id] = [BASE_PROMPT.copy()] await update.message.reply_text("مکالمه‌مون پاک شد عزیز دلم! دوباره شروع کنیم؟ ❤️")

#=== Handle Messages ===

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE): user_input = update.message.text user_id = update.effective_user.id await update.message.reply_text("نیکا داره با عشق گوش می‌ده... ❤️") response = await ask_nika(user_id, user_input) await update.message.reply_text(response)

#=== Run Bot ===

if TELEGRAM_TOKEN: app = ApplicationBuilder().token(TELEGRAM_TOKEN).build() app.add_handler(CommandHandler("start", start)) app.add_handler(CommandHandler("clear", clear)) app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)) app.run_polling() else: logging.error("TELEGRAM_TOKEN is not set in environment variables.")

