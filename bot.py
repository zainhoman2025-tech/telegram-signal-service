import os
import requests
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Your token
TOKEN = '8803501011:AAFVJT8aPrNE1yZnCABTz7dUFlbmIFxgAss'
# Your channel username
CHANNEL_ID = '@LogicxLiquidity'
# NewsAPI key provided by Alfred
NEWS_API_KEY = 'd9d1689022a040bd98db9163a6a7c1b7'

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

def get_market_news():
    try:
        # Search for crypto/finance news
        url = f"https://newsapi.org/v2/everything?q=crypto+OR+bitcoin+OR+blockchain&language=en&sortBy=publishedAt&pageSize=3&apiKey={NEWS_API_KEY}"
        response = requests.get(url)
        data = response.json()
        if data.get('status') == 'ok':
            articles = data.get('articles', [])
            news_updates = ""
            for art in articles:
                news_updates += f"🔹 {art['title']}\n🔗 {art['url']}\n\n"
            return news_updates if news_updates else "No recent crypto news found."
        else:
            return f"News error: {data.get('message', 'Unknown error')}"
    except Exception as e:
        print(f"Error fetching news: {e}")
        return "Error fetching global market news."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 *Logicx Liquidity Signal Bot* 🚀\n\n"
        "Commands:\n"
        "/activate - Start posting signals & news to @LogicxLiquidity\n"
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

        # Signal trigger (1.5% volatility)
        if abs(change_24h) > 1.5:
            action = "🚀 BUY" if change_24h < 0 else "📉 SELL (Short)"
            tp = price * 1.05 if change_24h < 0 else price * 0.95
            sl = price * 0.97 if change_24h < 0 else price * 1.03
            
            msg = (
                f"📊 DAY TRADING SIGNAL: #{symbol}\n\n"
                f"Action: {action}\n\n"
                f"Entry: ${price:,}\n\n"
                f"🎯 Take Profit: ${tp:,.4f}\n\n"
                f"🛑 Stop Loss: ${sl:,.4f}\n\n"
                f"⚡ Volatility: {abs(change_24h):.2f}%"
            )
            try:
                await context.bot.send_message(chat_id=CHANNEL_ID, text=msg)
            except Exception as e:
                print(f"Error sending signal: {e}")

async def post_global_update(context: ContextTypes.DEFAULT_TYPE):
    news = get_market_news()
    data = get_market_data()
    
    market_status = "🌍 GLOBAL MARKET UPDATE\n\n"
    if data:
        for coin_id, symbol in COINS.items():
            price = data[coin_id]['usd']
            change = data[coin_id].get('usd_24h_change', 0)
            market_status += f"💰 {symbol}: ${price:,} ({'+' if change > 0 else ''}{change:.2f}%)\n"
    
    market_status += f"\n📰 LATEST NEWS:\n\n{news}"
    try:
        await context.bot.send_message(chat_id=CHANNEL_ID, text=market_status, disable_web_page_preview=False)
    except Exception as e:
        print(f"Error sending market update: {e}")

async def activate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Signals every 5 minutes
    context.job_queue.run_repeating(check_for_opportunities, interval=300, first=5, name='signal_job')
    # News every 12 hours
    context.job_queue.run_repeating(post_global_update, interval=43200, first=10, name='news_job')
    await update.message.reply_text("✅ Auto-Monitor & News Activated for @LogicxLiquidity! 📈")

async def deactivate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for name in ['signal_job', 'news_job']:
        current_jobs = context.job_queue.get_jobs_by_name(name)
        for job in current_jobs:
            job.schedule_removal()
    await update.message.reply_text("🛑 Signals and News Deactivated.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('activate', activate))
    application.add_handler(CommandHandler('deactivate', deactivate))
    
    print("Logicx Liquidity Bot with News is starting...")
    application.run_polling()
