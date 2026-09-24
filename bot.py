import logging
import os
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import yfinance as yf

# -------------------------------------------------------------
# ১. Render-এর ফ্রি সার্ভার পোর্টের জন্য ওয়েব সার্ভার কোড
# -------------------------------------------------------------
app = Flask('')


@app.route('/')
def home():
    return 'Bot is active and running 24/7!'


def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)


def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()


# ওয়েব সার্ভার ব্যাকগ্রাউন্ডে চালু করা হলো
keep_alive()

# -------------------------------------------------------------
# ২. টেলিগ্রাম বোট ও সিগন্যাল লজিক
# -------------------------------------------------------------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)

# আপনার টেলিগ্রাম বোট টোকেন
TOKEN = '8139589998:AAFDp6E-Hia_vL52oP0v5i3v27fV_M_Toxw'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'হ্যালো! XAUUSD (Gold) সিগন্যাল বোটে আপনাকে স্বাগতম।\n\n'
        'লাইভ এনালাইসিস পেতে পাঠাতেন: /signal'
    )


async def get_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('XAUUSD মার্কেট ডাটা এনালাইসিস করা হচ্ছে...')
    try:
        gold = yf.Ticker('GC=F')
        df = gold.history(period='1d', interval='5m')

        if df.empty:
            await update.message.reply_text(
                'মার্কেট ডাটা পাওয়া যায়নি। মার্কেট বন্ধ থাকতে পারে।'
            )
            return

        last_price = round(df['Close'].iloc[-1], 2)

        # সাধারণ উদাহরণ সিগন্যাল মেসেজ
        message = (
            f'📊 **XAUUSD / GOLD SIGNAL**\n\n'
            f'🔹 **Current Price:** ${last_price}\n'
            f'🔹 **Status:** Market Active\n\n'
            f'⚠️ *Note: Always use proper Risk Management.*'
        )

        await update.message.reply_text(message, parse_mode='Markdown')

    except Exception as e:
        await update.message.reply_text(f'ডাটা আনতে সমস্যা হয়েছে: {str(e)}')


def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('signal', get_signal))

    print('Bot is running...')
    application.run_polling()


if __name__ == '__main__':
    main()
