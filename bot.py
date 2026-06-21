import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Replace with your token from BotFather
TOKEN = 'YOUR_BOT_TOKEN_HERE'

def get_crypto_price(coin_id='bitcoin'):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
        response = requests.get(url)
        data = response.json()
        return data[coin_id]['usd']
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Market Alert Bot is active! 📊\nUse /price to get the latest Bitcoin price.")

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    btc_price = get_crypto_price('bitcoin')
    if btc_price:
        await update.message.reply_text(f"🚀 Current Bitcoin Price: ${btc_price:,}")
    else:
        await update.message.reply_text("Could not fetch price at the moment. Try again later.")

async def market_update(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    btc_price = get_crypto_price('bitcoin')
    if btc_price:
        message = f"🔔 [Market Update]: Bitcoin is currently at ${btc_price:,}"
        await context.bot.send_message(job.chat_id, text=message)

async def set_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_message.chat_id
    # Sends a market update every 4 hours (14400 seconds)
    context.job_queue.run_repeating(market_update, interval=14400, first=10, chat_id=chat_id)
    await update.message.reply_text("Alerts set! You'll get a market update every 4 hours. ✅")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('price', price))
    application.add_handler(CommandHandler('alerts', set_alerts))
    
    print("Market Alert Bot is starting...")
    application.run_polling()
