import os
import requests
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Your token
TOKEN = '8803501011:AAFVJT8aPrNE1yZnCABTz7dUFlbmIFxgAss'

def get_crypto_price(coin_id='bitcoin'):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
        response = requests.get(url)
        data = response.json()
        return data[coin_id]['usd']
    except Exception as e:
        print(f"Error fetching price: {e}")
        return none

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Signal Service Active!\nUse /signals to start receiving 1-minute market signals.")

async def send_signal(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    btc_price = get_crypto_price('bitcoin')
    
    if btc_price:
        # Simple logic: random "signal" based on real price
        # In a real app, you'd use Technical Analysis here
        action = random.choice(["🚀 BUY", "📉 SELL", "⚡️ HOLD"])
        target = btc_price * (1.05 if action == "🚀 BUY" else 0.95)
        
        message = (
            f"{action} #BTC at ${btc_price:,}\n"
            f"🎯 Target: ${target:,.2f}\n"
            f"🕒 Time: 1-minute update"
        )
        await context.bot.send_message(job.chat_id, text=message)

async def signals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_message.chat_id
    # Set to 60 seconds (1 minute) for testing
    context.job_queue.run_repeating(send_signal, interval=60, first=10, chat_id=chat_id)
    await update.message.reply_text("✅ 1-Minute Signals Started! Stay tuned...")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('signals', signals))
    
    print("Signal Bot is starting...")
    application.run_polling()
