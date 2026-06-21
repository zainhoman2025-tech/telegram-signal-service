import os
import requests
import random
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Your token
TOKEN = '8803501011:AAFVJT8aPrNE1yZnCABTz7dUFlbmIFxgAss'

# List of coins to monitor
COINS = {
    'bitcoin': 'BTC',
    'ethereum': 'ETH',
    'ripple': 'XRP',
    'solana': 'SOL',
    'cardano': 'ADA'
}

def get_market_data():
    try:
        ids = ",".join(COINS.keys())
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd&include_24hr_change=true"
        response = requests.get(url)
        return response.json()
    except Exception as e:
        print(f"Error fetching market data: {e}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 *Zapia Professional Signal Service* 🚀\n\n"
        "I am now monitoring BTC, ETH, XRP, SOL, and ADA.\n"
        "I will post signals automatically when I detect market movement.\n\n"
        "Commands:\n"
        "/activate - Start the auto-signal monitor\n"
        "/price - Get instant market snapshot",
        parse_mode='Markdown'
    )

async def check_for_opportunities(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    data = get_market_data()
    if not data:
        return

    for coin_id, symbol in COINS.items():
        price = data[coin_id]['usd']
        change_24h = data[coin_id].get('usd_24h_change', 0)

        # Logic for "Opportunity"
        # 1. Day Trading Signal (based on volatility)
        if abs(change_24h) > 2.0:  # If moves more than 2%
            action = "🚀 BUY" if change_24h < 0 else "📉 SELL (Short)"
            tp = price * 1.05 if change_24h < 0 else price * 0.95
            sl = price * 0.97 if change_24h < 0 else price * 1.03
            
            msg = (
                f"📊 *DAY TRADING SIGNAL: #{symbol}*\n"
                f"Action: {action}\n"
                f"Entry: ${price:,}\n"
                f"🎯 Take Profit: ${tp:,.4f}\n"
                f"🛑 Stop Loss: ${sl:,.4f}\n"
                f"⚡ Volatility: {change_24h:.2f}%"
            )
            await context.bot.send_message(job.chat_id, text=msg, parse_mode='Markdown')

        # 2. Long Term/Early Gem Signal
        elif change_24h < -10.0: # Huge dip = Long term entry
            msg = (
                f"💎 *LONG TERM OPPORTUNITY: #{symbol}*\n"
                f"The market is down {change_24h:.2f}%. This is a great zone for long-term accumulation (Hold for 6-12 months).\n"
                f"Current Price: ${price:,}"
            )
            await context.bot.send_message(job.chat_id, text=msg, parse_mode='Markdown')

async def activate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_message.chat_id
    # Check every 5 minutes (300 seconds) for real opportunities
    # This prevents spamming and only posts when things move
    context.job_queue.run_repeating(check_for_opportunities, interval=300, first=5, chat_id=chat_id)
    await update.message.reply_text("✅ Auto-Monitor Activated. I will post signals when I find opportunities! 📈")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('activate', activate))
    
    print("Professional Signal Bot is starting...")
    application.run_polling()
