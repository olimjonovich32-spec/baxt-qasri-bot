import html as H
import io
import math
import os
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import httpx
import qrcode
from PIL import Image, ImageDraw
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
PUBLIC_URL = os.getenv("PUBLIC_URL", "https://baxt-qasri-bot.onrender.com").rstrip("/")

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

# bg, bg2, matn, ramka, belgi
STYLE = {
    "romantik": ("#ffd1dc", "#ff8fab", "#5a1030", "#ff4d79", "💗"),
    "saroy": ("#2b0a0a", "#6b1d1d", "#ffe9a8", "#d4af37", "👑"),
    "kosmik": ("#05051a", "#2a1a5e", "#e8e8ff", "#7b8cff", "✨"),
    "bahor": ("#e9ffd9", "#b8f0c0", "#2d5a27", "#ff8fc7", "🌸"),
    "qish": ("#dff3ff", "#9ccfee", "#12395a", "#ffffff", "❄️"),
    "retro": ("#d9c3a0", "#a98a5c", "#3b2a14", "#6b4a1e", "🕰"),
}

MENU = ReplyKeyboardMarkup(
    [["🏰 Muzey yaratish"], ["💝 Mening muzeyim", "❓ Yordam"]],
    resize_keyboard=True,
)


# ---------- Ma'lumotlar bazasi ----------
async def db(method, path, **kw):
    async with httpx.AsyncClient(timeout=20) as c:
        r = await c.request(method, f"{SB_URL}/rest/v1/{path}", headers=HEADERS, **kw)
        r.raise_for_status()
        return r.json() if r.text else []


def sb_get(path):
    r = httpx.get(f"{SB_URL}/rest/v1/{path}", headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.json()


async def get_museum(owner_id):
    rows = await db(
        "GET", f"museums?owner_id=eq.{owner_id}&order=created_at.desc&limit=1"
    )
    return rows[0] if rows else None


# ---------- Veb sahifa ----------
PAGE = """<!doctype html><html lang="uz"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title><style>
*{box-sizing:border-box}body{margin:0;min-height:100vh;overflow-x:hidden;
font-family:Georgia,serif;color:__TXT__;text-align:center;
background:radial-gradient(circle at 50% 30%,__BG2__,__BG__ 70%)}
h1{margin:28px 16px 4px;font-size:28px}
.sub{opacity:.8;margin-bottom:10px}
.scene{perspective:1100px;height:420px;display:flex;align-items:center;justify-content:center;overflow:hidden}
.ring{position:relative;width:200px;height:280px;transform-style:preserve-3d;animation:spin 40s linear infinite}
.scene:active .ring{animation-play-state:paused}
@keyframes spin{to{transform:rotateY(-360deg)}}
.card{position:absolute;inset:0;border:6px solid __FR__;border-radius:10px;overflow:hidden;
background:#000;box-shadow:0 10px 30px rgba(0,0,0,.45);
transform:rotateY(var(--a)) translateZ(var(--r))}
.card img,.card video{width:100%;height:100%;object-fit:cover;display:block}
.msg{margin:10px auto 40px;max-width:520px;padding:18px 22px;border:2px solid __FR__;
border-radius:16px;background:rgba(255,255,255,.18);font-size:20px;line-height:1.4}
.fl{position:fixed;inset:0;pointer-events:none;overflow:hidden}
.fl span{position:absolute;bottom:-40px;font-size:22px;opacity:.7;animation:up linear infinite}
@keyframes up{to{transform:translateY(-110vh) rotate(40deg);opacity:0}}
#lb{display:none;position:fixed;inset:0;background:rgba(0,0,0,.92);z-index:9;
align-items:center;justify-content:center}
#lb img,#lb video{max-width:96vw;max-height:92vh}
</style></head><body>
<div class="fl" id="fl"></div>
<h1>__ICON__ __TITLE__ __ICON__</h1>
<div class="sub">Aylantirish uchun to'xtating, kattalashtirish uchun bosing</div>
<div class="scene"><div class="ring">__CARDS__</div></div>
__MSG__
<div id="lb" onclick="this.style.display='none';this.innerHTML=''"></div>
<script>
var fl=document.getElementById('fl');
for(var i=0;i<18;i++){var s=document.createElement('span');
s.textContent='__ICON__';s.style.left=Math.random()*100+'%';
s.style.animationDuration=(8+Math.random()*10)+'s';
s.style.animationDelay=(-Math.random()*10)+'s';fl.appendChild(s);}
function openIt(el){var lb=document.getElementById('lb');
var c=el.cloneNode(true);c.removeAttribute('style');c.controls=true;
lb.innerHTML='';lb.appendChild(c);lb.style.display='flex';}
</script></body></html>"""


def render_museum(m, items):
    bg, bg2, txt, fr, icon = STYLE.get(m.get("theme"), STYLE["romantik"])
    n = len(items)
    radius = max(230, int(n * 230 / (2 * math.pi)))
    cards = []
    for i, it in enumerate(items):
        src = f"/f/{it['file_id']}"
        if it["kind"] == "video":
            tag = f'<video src="{src}" muted loop playsinline preload="metadata" onclick="openIt(this)"></video>'
        else:
            tag = f'<img src="{src}" loading="lazy" onclick="openIt(this)">'
        a = 360 / n * i
        cards.append(f'<div class="card" style="--a:{a}deg;--r:{radius}px">{tag}</div>')
    msg = (
        f'<div class="msg">{H.escape(m["message"])}</div>' if m.get("message") else ""
    )
    out = PAGE
    for k, v in {
        "__TITLE__": H.escape(m.get("title") or "Mening muzeyim"),
        "__BG__": bg, "__BG2__": bg2, "__TXT__": txt, "__FR__": fr,
        "__ICON__": icon, "__CARDS__": "".join(cards), "__MSG__": msg,
    }.items():
        out = out.replace(k, v)
    return out


def tg_file(file_id):
    info = httpx.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/getFile",
        params={"file_id": file_id},
        timeout=20,
    ).json()
    path = info["result"]["file_path"]
    r = httpx.get(f"https://api.telegram.org/file/bot{BOT_TOKEN}/{path}", timeout=90)
    return r.content, path


class WebHandler(BaseHTTPRequestHandler):
    def _send(self, code, ctype, body, cache=False):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        if cache:
            self.send_header("Cache-Control", "public, max-age=86400")
        self.end_headers()
        self.wfile.write(body)

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        try:
            p = urllib.parse.urlparse(self.path).path
            if p.startswith("/m/"):
                mid = p.split("/")[2]
                m = sb_get(f"museums?id=eq.{mid}")
                if not m:
                    return self._send(404, "text/plain", b"Topilmadi")
                items = sb_get(f"media?museum_id=eq.{mid}&order=created_at.asc")
                page = render_museum(m[0], items)
                return self._send(200, "text/html; charset=utf-8", page.encode())
            if p.startswith("/f/"):
                data, path = tg_file(p.split("/")[2])
                low = path.lower()
                if low.endswith(".mp4"):
                    ct = "video/mp4"
                elif low.endswith(".png"):
                    ct = "image/png"
                elif low.endswith(".webp"):
                    ct = "image/webp"
                else:
                    ct = "image/jpeg"
                return self._send(200, ct, data, cache=True)
            return self._send(200, "text/plain", b"Baxt Qasri bot ishlayapti")
        except Exception:
            return self._send(500, "text/plain", b"Xatolik")

    def log_message(self, *args):
        pass


def run_web_server():
    port = int(os.getenv("PORT", "10000"))
    ThreadingHTTPServer(("0.0.0.0", port), WebHandler).serve_forever()


# ---------- Yurak shaklidagi QR ----------
def heart_qr(url):
    size = 800
    img = Image.new("RGB", (size, size), "white")
    d = ImageDraw.Draw(img)
    pts = []
    for i in range(361):
        t = math.radians(i)
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((400 + x * 23, 340 - y * 23))
    d.polygon(pts, fill="#ff4d79")
    qr = qrcode.QRCode(border=2, box_size=10)
    qr.add_data(url)
    qr.make(fit=True)
    q = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    q = q.resize((360, 360), Image.NEAREST)
    d.rounded_rectangle((210, 150, 590, 530), radius=24, fill="white")
    img.paste(q, (220, 160))
    buf = io.BytesIO()
    img.save(buf, "PNG")
    buf.seek(0)
    return buf


# ---------- Bot ----------
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
    await db(
        "POST",
        "museums",
        json={"owner_id": q.from_user.id, "theme": key, "title": "Mening muzeyim"},
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


async def my_museum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    m = await get_museum(update.effective_user.id)
    if not m:
        await update.message.reply_text("Hozircha muzeyingiz yo'q.")
        return
    rows = await db("GET", f"media?museum_id=eq.{m['id']}&select=id")
    if not rows:
        await update.message.reply_text("Muzey bo'sh. Avval rasm yoki video yuboring 📸")
        return
    link = f"{PUBLIC_URL}/m/{m['id']}"
    await update.message.reply_text(
        f"Dizayn: {THEMES.get(m['theme'], m['theme'])}\n"
        f"Fayllar soni: {len(rows)}\n\n"
        f"Muzeyingiz havolasi 👇\n{link}"
    )
    await update.message.reply_photo(
        heart_qr(link), caption="💝 Yurakli QR-kod. Yaqinlaringizga yuboring!"
    )


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🏰 Muzey yaratish":
        await choose_theme(update, context)
    elif text == "💝 Mening muzeyim":
        await my_museum(update, context)
    elif text == "❓ Yordam":
        await update.message.reply_text(
            "1) 🏰 Muzey yaratish → dizayn tanlang\n"
            "2) Rasm/video yuboring\n"
            "3) /xabar Matn → tabrik yozing\n"
            "4) 💝 Mening muzeyim → havola va QR-kod"
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
        "POST", "media", json={"museum_id": m["id"], "file_id": file_id, "kind": kind}
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
