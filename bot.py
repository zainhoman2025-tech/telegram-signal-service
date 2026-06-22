import os
import requests
import random
import pandas as pd
import pandas_ta as ta  # Technical analysis library
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Configurations (Highly recommend moving these to environment variables later!)
TOKEN = '8803501011:AAFVJT8aPrNE1yZnCABTz7dUFlbmIFxgAss'
CHANNEL_ID = '@LogicxLiquidity'
NEWS_API_KEY = 'd9d1689022a040bd98db9163a6a7c1b7'

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

def get_historical_rsi(coin_id):
    """Fetches historical data and calculates the 14-period RSI"""
    try:
        # Fetch 15 days of hourly data to safely compute a 14-period RSI
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=15&interval=hourly"
        response = requests.get(url).json()
        prices = [candle[1] for candle in response['prices']]
        
        # Load into a Pandas DataFrame
        df = pd.DataFrame(prices, columns=['close'])
        # Calculate RSI using pandas-ta
        df.ta.rsi(close='close', length=14, append=True)
        
        # Return the latest RSI value
        return df['RSI_14'].iloc[-1]
    except Exception as e:
        print(f"Error calculating RSI for {coin_id}: {e}")
        return None

# --- TELEGRAM USER INTERFACE (Feature 2) ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Creating an interactive dashboard using Inline Buttons
    keyboard = [
        [
            InlineKeyboardButton("📊 Activate System", callback_data="btn_activate"),
            InlineKeyboardButton("🛑 Deactivate", callback_data="btn_deactivate")
        ],
        [
            InlineKeyboardButton("💰 Instant Price Check", callback_data="btn_prices")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🚀 *Welcome to Logicx Liquidity Control Panel* 🚀\n\n"
        "Use the dashboard below to control your automated channel signals or fetch instant analytical data.",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles clicks from the inline dashboard buttons"""
    query = update.callback_query
    await query.answer()  # Acknowledge the click immediately

    if query.data == "btn_activate":
        # Check if already running to prevent duplicates
        jobs = context.job_queue.get_jobs_by_name('signal_job')
        if jobs:
            await query.edit_message_text("⚠️ Automation is already running actively!")
            return
        
        context.job_queue.run_repeating(check_for_opportunities, interval=300, first=5, name='signal_job')
        await query.edit_message_text("✅ *Auto-Monitor & Intelligent Strategy Activated!* 📈", parse_mode='Markdown')

    elif query.data == "btn_deactivate":
        current_jobs = context.job_queue.get_jobs_by_name('signal_job')
        for job in current_jobs:
            job.schedule_removal()
        await query.edit_message_text("🛑 *System Standby:* Signals have been deactivated.", parse_mode='Markdown')

    elif query.data == "btn_prices":
        # Instant on-demand prices fetched right inside the chat
        data = get_market_data()
        if not data:
            await query.edit_message_text("❌ Error reading market data. Try again.")
            return

        msg = "🎯 *Current Market Snapshot:*\n\n"
        for coin_id, symbol in COINS.items():
            price = data[coin_id]['usd']
            rsi = get_historical_rsi(coin_id)
            rsi_str = f"{rsi:.1f}" if rsi else "N/A"
            msg += f"• *{symbol}*: ${price:,} | 🕒 RSI(14): {rsi_str}\n"
        
        await query.message.reply_text(msg, parse_mode='Markdown')

# --- UPGRADED STRATEGY (Feature 1) ---

async def check_for_opportunities(context: ContextTypes.DEFAULT_TYPE):
    data = get_market_data()
    if not data:
        return

    for coin_id, symbol in COINS.items():
        price = data[coin_id]['usd']
        rsi = get_historical_rsi(coin_id)
        
        if not rsi:
            continue

        # Advanced Strategy Rules
        triggered = False
        if rsi < 30:  # Oversold condition -> Expect market bounce
            action = "🚀 STRATEGIC BUY (Oversold)"
            tp = price * 1.04  # 4% Target profit
            sl = price * 0.98  # Tight 2% Stop loss
            triggered = True
        elif rsi > 70:  # Overbought condition -> Expect drop
            action = "📉 STRATEGIC SHORT (Overbought)"
            tp = price * 0.96
            sl = price * 1.02
            triggered = True

        if triggered:
            msg = (
                f"🚨 *ALGORITHMIC SIGNAL: #{symbol}* 🚨\n\n"
                f"🔥 *Action:* {action}\n"
                f"💵 *Entry Price:* ${price:,}\n\n"
                f"🎯 *Take Profit:* ${tp:,.2f}\n"
                f"🛑 *Stop Loss:* ${sl:,.2f}\n\n"
                f"📈 *RSI (14-period):* {rsi:.2f}\n"
                f"💡 _Ensure your leverage matches your risk management rules._"
            )
            try:
                await context.bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode='Markdown')
            except Exception as e:
                print(f"Error sending signal: {e}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_handler))  # Catches button inputs
    
    print("Upgraded Logicx Liquidity Bot is running smoothly...")
    application.run_polling()
