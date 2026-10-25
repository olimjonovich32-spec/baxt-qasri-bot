import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import httpx
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
SB_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SB_KEY = os.getenv("SUPABASE_KEY", "")

HEADERS = {
    "apikey": SB_KEY,
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

THEMES = {
    "romantik": "💝 Romantik",
    "saroy": "🏰 Qirollik saroyi",
    "kosmik": "🌌 Kosmik",
    "bahor": "🌸 Bahor bog'i",
    "qish": "❄️ Qishki ertak",
    "retro": "🕰 Retro galereya",
}

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


async def db(method, path, **kw):
    async with httpx.AsyncClient(timeout=20) as c:
        r = await c.request(method, f"{SB_URL}/rest/v1/{path}", headers=HEADERS, **kw)
        r.raise_for_status()
        return r.json() if r.text else []


async def get_museum(owner_id):
    rows = await db(
        "GET",
        f"museums?owner_id=eq.{owner_id}&order=created_at.desc&limit=1",
    )
    return rows[0] if rows else None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Baxt Qasri'ga xush kelibsiz! 💝\n"
        "Rasm va videolaringizdan kichkina 3D muzey yarating.",
        reply_markup=MENU,
    )


async def choose_theme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton(name, callback_data=f"theme:{key}")]
        for key, name in THEMES.items()
    ]
    await update.message.reply_text(
        "Muzey dizaynini tanlang 👇", reply_markup=InlineKeyboardMarkup(buttons)
    )


async def theme_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    key = q.data.split(":", 1)[1]
    uid = q.from_user.id
    await db(
        "POST",
        "museums",
        json={"owner_id": uid, "theme": key, "title": "Mening muzeyim"},
    )
    await q.edit_message_text(
        f"Tanlandi: {THEMES[key]} ✅\n\n"
        "Endi rasm yoki videolaringizni yuboring 📸\n"
        "Tabrik matni qo'shish uchun: /xabar Matningiz"
    )


async def set_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    m = await get_museum(update.effective_user.id)
    if not m:
        await update.message.reply_text("Avval muzey yarating 🏰")
        return
    text = " ".join(context.args).strip()
    if not text:
        await update.message.reply_text("Misol: /xabar Tug'ilgan kuning bilan, onajon!")
        return
    await db("PATCH", f"museums?id=eq.{m['id']}", json={"message": text})
    await update.message.reply_text("Tabrik matni saqlandi 💌")


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🏰 Muzey yaratish":
        await choose_theme(update, context)
    elif text == "💝 Mening muzeyim":
        m = await get_museum(update.effective_user.id)
        if not m:
            await update.message.reply_text("Hozircha muzeyingiz yo'q.")
            return
        rows = await db("GET", f"media?museum_id=eq.{m['id']}&select=id")
        await update.message.reply_text(
            f"Dizayn: {THEMES.get(m['theme'], m['theme'])}\n"
            f"Fayllar soni: {len(rows)}\n"
            "Havola va QR-kod tez orada qo'shiladi 🔜"
        )
    elif text == "❓ Yordam":
        await update.message.reply_text(
            "1) 🏰 Muzey yaratish → dizayn tanlang\n"
            "2) Rasm/video yuboring\n"
            "3) /xabar Matn → tabrik yozing"
        )
    else:
        await update.message.reply_text("Menyudan tanlang 👇", reply_markup=MENU)


async def media_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    m = await get_museum(update.effective_user.id)
    if not m:
        await update.message.reply_text("Avval 🏰 Muzey yaratish tugmasini bosing.")
        return
    msg = update.message
    if msg.photo:
        file_id, kind = msg.photo[-1].file_id, "photo"
    else:
        file_id, kind = msg.video.file_id, "video"
    await db(
        "POST",
        "media",
        json={"museum_id": m["id"], "file_id": file_id, "kind": kind},
    )
    await msg.reply_text("Saqlandi! ✅ Muzeyga qo'shildi.")


def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN topilmadi")
    threading.Thread(target=run_web_server, daemon=True).start()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("xabar", set_message))
    app.add_handler(CallbackQueryHandler(theme_chosen, pattern="^theme:"))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, media_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.run_polling()


if __name__ == "__main__":
    main()
