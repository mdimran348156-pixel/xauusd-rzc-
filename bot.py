import asyncio
from datetime import datetime
import yfinance as yf
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from telegram import Bot

# ================= Configuration =================
TELEGRAM_BOT_TOKEN = "8767813972:AAG4RJ_lFNUVZEdbNUx-vqafFN7leXpICkA"
# প্রাইভেট চ্যানেলের জন্য ইনভাইট লিংক সাপোর্ট করবে
CHANNEL_LINK = "https://t.me/+FqUn8zT9b4MyM2Rl"
MAX_DAILY_SIGNALS = 5
# =================================================

bot = Bot(token=TELEGRAM_BOT_TOKEN)

daily_signal_count = 0
last_signal_date = datetime.now().date()
last_signal_type = None
target_chat_id = None

async def get_channel_id():
    """বোটের কাছে আসা আপডেট থেকে প্রাইভেট চ্যানেলের ID বের করবে"""
    global target_chat_id
    try:
        updates = await bot.get_updates()
        for update in updates:
            if update.channel_post:
                target_chat_id = update.channel_post.chat.id
                print(f"Detected Channel ID: {target_chat_id}")
                return target_chat_id
    except Exception as e:
        print(f"Error getting Chat ID: {e}")
    return None

def get_xauusd_signal():
    try:
        data = yf.download(tickers="GC=F", period="1d", interval="15m", progress=False)
        if data.empty or len(data) < 20:
            return None
        
        close_prices = data['Close'].squeeze()
        rsi = RSIIndicator(close=close_prices, window=14).rsi().iloc[-1]
        ema20 = EMAIndicator(close=close_prices, window=20).ema_indicator().iloc[-1]
        current_price = float(close_prices.iloc[-1])
        
        signal = None
        if rsi < 35 and current_price > ema20:
            sl = current_price - 3.0
            tp = current_price + 6.0
            signal = ("BUY", f"🚨 **XAUUSD BUY SIGNAL** 🚨\n\n"
                             f"📈 Entry Price: ${current_price:.2f}\n"
                             f"🎯 Take Profit: ${tp:.2f}\n"
                             f"🛑 Stop Loss: ${sl:.2f}\n"
                             f"📊 RSI: {rsi:.1f} | TF: 15m")
                             
        elif rsi > 65 and current_price < ema20:
            sl = current_price + 3.0
            tp = current_price - 6.0
            signal = ("SELL", f"🚨 **XAUUSD SELL SIGNAL** 🚨\n\n"
                              f"📉 Entry Price: ${current_price:.2f}\n"
                              f"🎯 Take Profit: ${tp:.2f}\n"
                              f"🛑 Stop Loss: ${sl:.2f}\n"
                              f"📊 RSI: {rsi:.1f} | TF: 15m")
            
        return signal
    except Exception as e:
        print(f"Data Fetch Error: {e}")
        return None

async def main():
    global daily_signal_count, last_signal_date, last_signal_type, target_chat_id
    print("Bot is starting...")
    
    while True:
        try:
            current_date = datetime.now().date()
            
            if current_date != last_signal_date:
                daily_signal_count = 0
                last_signal_date = current_date
                last_signal_type = None
            
            if daily_signal_count < MAX_DAILY_SIGNALS:
                result = get_xauusd_signal()
                
                if result:
                    sig_type, sig_message = result
                    
                    if sig_type != last_signal_type:
                        daily_signal_count += 1
                        formatted_message = f"{sig_message}\n\n📌 Today's Signal: {daily_signal_count}/{MAX_DAILY_SIGNALS}"
                        
                        # প্রথমে যেকোনো মেসেজ পাঠিয়ে চ্যানেলে কানেক্ট করার চেষ্টা করবে
                        try:
                            await bot.send_message(chat_id=CHANNEL_LINK, text=formatted_message, parse_mode="Markdown")
                        except:
                            if not target_chat_id:
                                target_chat_id = await get_channel_id()
                            if target_chat_id:
                                await bot.send_message(chat_id=target_chat_id, text=formatted_message, parse_mode="Markdown")
                        
                        last_signal_type = sig_type
            
        except Exception as e:
            print(f"Loop Error: {e}")
            
        await asyncio.sleep(300)

if __name__ == "__main__":
    asyncio.run(main())
