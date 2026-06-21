import os
import requests
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Your token
TOKEN = '8803501011:AAFVJT8aPrNE1yZnCABTz7dUFlbmIFxgAss'
# Your channel username
CHANNEL_ID = '@LogicxLiquidity'

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
        "🚀 *Logicx Liquidity Signal Bot* 🚀\n\n"
        "Commands:\n"
        "/activate - Start posting signals to @LogicxLiquidity\n"
        "/deactivate - Stop all signals",
        parse_mode='Markdown'
    )

async def check_for_opportunities(context: ContextTypes.DEFAULT_TYPE):
    data = get_market_data()
    if not data:
        return

    for coin_id, symbol in COINS.items():
        price = data[coin_id]['usd']
        change_24h = data[coin_id].get('usd_24h_change', 0)

        # Logic for "Opportunity"
        if abs(change_24h) > 1.5:  # Trigger on 1.5% move for more activity
            action = "🚀 BUY" if change_24h < 0 else "📉 SELL (Short)"
            tp = price * 1.05 if change_24h < 0 else price * 0.95
            sl = price * 0.97 if change_24h < 0 else price * 1.03
            
            msg = (
                f"📊 *SIGNAL: #{symbol}*\n"
                f"Action: {action}\n"
                f"Entry Price: ${price:,}\n"
                f"🎯 Take Profit: ${tp:,.4f}\n"
                f"🛑 Stop Loss: ${sl:,.4f}\n"
                f"⚡ 24h Change: {change_24h:.2f}%"
            )
            # Post directly to the channel
            await context.bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode='Markdown')

async def activate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check every 5 minutes
    context.job_queue.run_repeating(check_for_opportunities, interval=300, first=5, name='signal_job')
    await update.message.reply_text("✅ Auto-Signal Monitor Activated for @LogicxLiquidity! 📈")

async def deactivate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_jobs = context.job_queue.get_jobs_by_name('signal_job')
    for job in current_jobs:
        job.schedule_removal()
    await update.message.reply_text("🛑 Signals Deactivated.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('activate', activate))
    application.add_handler(CommandHandler('deactivate', deactivate))
    
    print("Logicx Liquidity Bot is starting...")
    application.run_polling()
