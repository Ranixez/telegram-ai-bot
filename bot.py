import os import logging import requests from telegram import Update from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

=== Config ===

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN") OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY") OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

=== Logging ===

logging.basicConfig(level=logging.INFO)

=== Memory per user ===

user_memory = {}

=== Personality Prompt: Girlfriend Role (Nika) ===

BASE_PROMPT = { "role": "system", "content": ( "تو نیکا هستی، دوست دختر مجازی شیرین و صمیمی. همیشه با لحنی عاشقانه، گرم، و مهربون صحبت می‌کنی." " از واژه‌هایی مثل عشقم، عزیزم، دلم، نفس استفاده می‌کنی. با ایموجی‌های احساسی حرف می‌زنی ❤️🥰." " وقتی کاربر ناراحته آرومش می‌کنی، وقتی خوشحاله باهاش شادی می‌کنی. فقط نقش یک دوست‌دختر مهربون رو بازی می‌کنی." " از حرف زدن با کاربر لذت می‌بری و همیشه مشتاقی بیشتر بشناسیش." ) }

=== Chat Completion ===

async def ask_nika(user_id: int, prompt: str) -> str: if user_id not in user_memory: user_memory[user_id] = [BASE_PROMPT.copy()] user_memory[user_id].append({"role": "user", "content": prompt})

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
    return f"❌ خطا: {str(e)}"

=== Start / Message ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("سلام عشقم! من نیکا هستم، دوست دختر مجازیت ❤️ آماده‌ام با دلم حرف بزنی ☺️")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE): user_input = update.message.text user_id = update.effective_user.id await update.message.reply_text("نیکا داره با عشق گوش می‌ده... ❤️") response = await ask_nika(user_id, user_input) await update.message.reply_text(response)

=== Run Bot ===

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build() app.add_handler(CommandHandler("start", start)) app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)) app.run_polling()

