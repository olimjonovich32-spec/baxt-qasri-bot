import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

MENU = ReplyKeyboardMarkup(
    [["🏰 Muzey yaratish"], ["💝 Mening muzeyim", "❓ Yordam"]],
    resize_keyboard=True,
)


class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Baxt Qasri bot ishlayapti")

    def log_message(self, *args):
        pass


def run_web_server():
    port = int(os.getenv("PORT", "10000"))
    HTTPServer(("0.0.0.0", port), PingHandler).serve_forever()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Baxt Qasri'ga xush kelibsiz! 💝\n"
        "Rasm va videolaringizdan kichkina 3D muzey yarating.",
        reply_markup=MENU,
    )


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🏰 Muzey yaratish":
        await update.message.reply_text(
            "Rasm yoki videolaringizni yuboring. 📸"
        )
    elif text == "💝 Mening muzeyim":
        await update.message.reply_text("Hozircha muzeyingiz yo'q.")
    elif text == "❓ Yordam":
        await update.message.reply_text(
            "Rasm yoki video yuboring, men ularni muzeyga qo'shaman."
        )
    else:
        await update.message.reply_text("Menyudan tanlang 👇", reply_markup=MENU)


async def media_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Qabul qilindi! ✅ Muzeyga qo'shiladi.")


def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN topilmadi")

    threading.Thread(target=run_web_server, daemon=True).start()

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, media_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.run_polling()


if __name__ == "__main__":
    main()
