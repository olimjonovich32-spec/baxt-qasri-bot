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
    "qish": ("#dff3ff", "#9ccfee", "#12395a", "#8fb8d8", "❄️"),
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


# ---------- Veb sahifa: 3D muzey ----------
PAGE = """<!doctype html><html lang="uz"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no">
<title>__TITLE__</title><style>
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent;user-select:none;-webkit-user-select:none}
html,body{margin:0;height:100%;overflow:hidden;background:#000;font-family:Georgia,serif}
#stage{position:fixed;inset:0;perspective:500px;touch-action:none;overflow:hidden;background:#000}
#world{position:absolute;left:50%;top:50%;width:0;height:0;transform-style:preserve-3d}
.wall{position:absolute;top:-210px;height:420px;transform-style:preserve-3d;
background:linear-gradient(90deg,__BG2__,__BG__ 50%,__BG2__);
box-shadow:inset 0 0 60px rgba(0,0,0,.45)}
.wall:before{content:"";position:absolute;inset:0;opacity:.12;
background:repeating-linear-gradient(0deg,#fff 0 1px,transparent 1px 22px)}
.base{position:absolute;left:0;right:0;bottom:0;height:26px;
background:linear-gradient(#f4efe6,#cfc6b4);border-top:2px solid rgba(0,0,0,.25)}
.crown{position:absolute;left:0;right:0;top:0;height:18px;
background:linear-gradient(#e9e2d2,#b9ae96)}
.slot{position:absolute;left:50%;top:50%;width:170px;height:230px;margin:-125px 0 0 -85px}
.spot{position:absolute;left:50%;top:-95px;width:300px;height:360px;margin-left:-150px;
background:radial-gradient(ellipse at 50% 0,rgba(255,244,200,.5),rgba(255,244,200,.1) 55%,transparent 72%);
clip-path:polygon(44% 0,56% 0,100% 100%,0 100%);pointer-events:none}
.lamp{position:absolute;left:50%;top:-100px;width:34px;height:14px;margin-left:-17px;
background:#222;border-radius:0 0 18px 18px;box-shadow:0 0 18px 6px rgba(255,236,170,.8)}
.frame{position:absolute;inset:0;border:9px solid __FR__;border-radius:4px;background:#000;
box-shadow:0 14px 28px rgba(0,0,0,.65),inset 0 0 0 2px rgba(0,0,0,.5);overflow:hidden}
.frame img,.frame video{width:100%;height:100%;object-fit:cover;display:block}
.plate{position:absolute;left:50%;bottom:-34px;width:60px;margin-left:-30px;height:18px;
border-radius:3px;background:linear-gradient(#e7c873,#a8842c);color:#3a2a00;
font-size:12px;line-height:18px;text-align:center}
.deco{position:absolute;left:50%;top:50%;font-size:46px;margin:-30px 0 0 -23px;opacity:.55}
.floor,.ceil{position:absolute;left:__FL__px;top:__FL__px;width:__FS__px;height:__FS__px}
.floor{transform:translateY(210px) rotateX(90deg);
background:repeating-linear-gradient(0deg,rgba(255,255,255,.16) 0 2px,transparent 2px 70px),
repeating-linear-gradient(90deg,rgba(255,255,255,.16) 0 2px,transparent 2px 70px),__BG2__;
box-shadow:inset 0 0 0 9999px rgba(0,0,0,.3)}
.ceil{transform:translateY(-210px) rotateX(90deg);background:#0b0b0b}
#vig{position:fixed;inset:0;pointer-events:none;
background:radial-gradient(ellipse at center,transparent 50%,rgba(0,0,0,.6) 100%)}
#top{position:fixed;left:0;right:0;top:0;padding:12px 14px;text-align:center;
color:#fff;text-shadow:0 2px 8px #000;pointer-events:none;font-size:20px}
#top small{display:block;font-size:12px;opacity:.8;margin-top:2px}
#sw{position:fixed;right:10px;top:60px;z-index:8;display:flex;gap:6px}
#sw button{width:42px;height:42px;border-radius:50%;border:2px solid #fff8;
background:#0007;font-size:22px;color:#fff}
#msg{position:fixed;left:12px;right:12px;top:92px;max-width:520px;margin:auto;
padding:10px 14px;border:2px solid __FR__;border-radius:14px;
background:rgba(20,20,20,.55);font-size:16px;line-height:1.35;text-align:center;
pointer-events:none;color:#fff}
#pad{position:fixed;left:0;right:0;bottom:12px;z-index:8;display:flex;
justify-content:space-between;padding:0 16px;pointer-events:none}
#pad .g{display:flex;gap:10px;pointer-events:auto}
#pad button{width:60px;height:60px;border-radius:50%;border:2px solid #fff9;
background:#0008;color:#fff;font-size:24px}
#pad button:active{background:#fff5}
.av{position:fixed;left:50%;bottom:92px;width:100px;height:140px;margin-left:-50px;
pointer-events:none;z-index:5;display:none}
.av.on{display:block}
.fig{position:absolute;inset:0;transform-origin:50% 100%}
.av.walking .fig{animation:bob .5s infinite}
@keyframes bob{50%{transform:translateY(-6px) rotate(1.5deg)}}
@keyframes step{50%{transform:translateY(-10px)}}
.av.walking .l{animation:step .5s infinite}
.av.walking .r{animation:step .5s infinite .25s}
.av i{position:absolute;display:block}
.pg .body{left:18px;top:42px;width:64px;height:84px;background:#1b2230;border-radius:50% 50% 46% 46%}
.pg .head{left:28px;top:8px;width:44px;height:44px;background:#222b3c;border-radius:50%}
.pg .scarf{left:25px;top:44px;width:50px;height:11px;background:__FR__;border-radius:6px}
.pg .wl{left:6px;top:58px;width:16px;height:52px;background:#141a25;border-radius:50%;transform:rotate(10deg)}
.pg .wr{left:78px;top:58px;width:16px;height:52px;background:#141a25;border-radius:50%;transform:rotate(-10deg)}
.pg .fl{left:20px;top:122px;width:28px;height:13px;background:#ff9f1c;border-radius:50%}
.pg .fr{left:52px;top:122px;width:28px;height:13px;background:#ff9f1c;border-radius:50%}
.pp .head{left:32px;top:6px;width:36px;height:40px;background:#3b2a1f;border-radius:50%}
.pp .torso{left:22px;top:46px;width:56px;height:50px;background:__FR__;border-radius:14px 14px 6px 6px;border:2px solid rgba(0,0,0,.25)}
.pp .al{left:8px;top:48px;width:14px;height:44px;background:__FR__;border-radius:8px;border:2px solid rgba(0,0,0,.25)}
.pp .ar{left:78px;top:48px;width:14px;height:44px;background:__FR__;border-radius:8px;border:2px solid rgba(0,0,0,.25)}
.pp .ll{left:28px;top:94px;width:20px;height:34px;background:#2a2f4a;border-radius:6px}
.pp .lr{left:52px;top:94px;width:20px;height:34px;background:#2a2f4a;border-radius:6px}
.pp .sl{left:26px;top:126px;width:24px;height:11px;background:#111;border-radius:6px}
.pp .sr{left:50px;top:126px;width:24px;height:11px;background:#111;border-radius:6px}
#lb{display:none;position:fixed;inset:0;background:rgba(0,0,0,.94);z-index:20;
align-items:center;justify-content:center}
#lb img,#lb video{max-width:96vw;max-height:92vh}
</style></head><body>
<div id="stage"><div id="world">
<div class="ceil"></div><div class="floor"></div>
__WALLS__
</div></div>
<div id="vig"></div>
<div id="top">__ICON__ __TITLE__ __ICON__<small>Yurish: tugmalar yoki ekranni suring. Rasmni bosing: kattalashadi</small></div>
__MSG__
<div id="sw"><button id="b1">🐧</button><button id="b2">🧍</button></div>

<div class="av pg on" id="pg"><div class="fig"><i class="body"></i><i class="head"></i><i class="scarf"></i>
<i class="wl l"></i><i class="wr r"></i><i class="fl l"></i><i class="fr r"></i></div></div>
<div class="av pp" id="pp"><div class="fig"><i class="head"></i><i class="al l"></i><i class="ar r"></i>
<i class="torso"></i><i class="ll l"></i><i class="lr r"></i><i class="sl l"></i><i class="sr r"></i></div></div>

<div id="pad">
<div class="g"><button id="bl">◀</button><button id="br">▶</button></div>
<div class="g"><button id="bf">▲</button><button id="bb">▼</button></div>
</div>
<div id="lb" onclick="this.style.display='none';this.innerHTML=''"></div>
<script>
var R=__R__,w=document.getElementById('world'),st=document.getElementById('stage');
var yaw=0,cx=0,cz=0,down=false,lx=0,moved=0,k={f:0,b:0,l:0,r:0};
function draw(){w.style.transform='translateZ(500px) rotateY('+yaw+'deg) translate3d('+(-cx)+'px,0,'+(-cz)+'px)';}
st.addEventListener('pointerdown',function(e){down=true;moved=0;lx=e.clientX;});
window.addEventListener('pointermove',function(e){if(!down)return;
var dx=e.clientX-lx;lx=e.clientX;moved+=Math.abs(dx);yaw-=dx*0.25;draw();});
window.addEventListener('pointerup',function(){down=false;});
function bind(id,key){var b=document.getElementById(id);
['pointerdown'].forEach(function(t){b.addEventListener(t,function(e){e.preventDefault();k[key]=1;});});
['pointerup','pointerleave','pointercancel'].forEach(function(t){b.addEventListener(t,function(){k[key]=0;});});}
bind('bf','f');bind('bb','b');bind('bl','l');bind('br','r');
var map={ArrowUp:'f',w:'f',ArrowDown:'b',s:'b',ArrowLeft:'l',a:'l',ArrowRight:'r',d:'r'};
window.addEventListener('keydown',function(e){if(map[e.key])k[map[e.key]]=1;});
window.addEventListener('keyup',function(e){if(map[e.key])k[map[e.key]]=0;});
var avs=[document.getElementById('pg'),document.getElementById('pp')];
function pick(i){avs[0].classList.toggle('on',i==0);avs[1].classList.toggle('on',i==1);
try{localStorage.setItem('av',i);}catch(e){}}
document.getElementById('b1').onclick=function(){pick(0);};
document.getElementById('b2').onclick=function(){pick(1);};
try{var s=localStorage.getItem('av');if(s!==null)pick(parseInt(s));}catch(e){}
function loop(){
var act=k.f||k.b||k.l||k.r;
if(k.l)yaw-=1.8;if(k.r)yaw+=1.8;
var a=yaw*Math.PI/180;
if(k.f){cx+=Math.sin(a)*3;cz-=Math.cos(a)*3;}
if(k.b){cx-=Math.sin(a)*2.2;cz+=Math.cos(a)*2.2;}
var d=Math.sqrt(cx*cx+cz*cz),lim=R-80;
if(d>lim){cx*=lim/d;cz*=lim/d;}
if(act)draw();
avs.forEach(function(x){x.classList.toggle('walking',!!act);});
requestAnimationFrame(loop);}
draw();loop();
function openIt(el){if(moved>6)return;var lb=document.getElementById('lb');
var c=el.cloneNode(true);c.controls=true;if(c.tagName=='VIDEO'){c.muted=false;c.autoplay=true;}
lb.innerHTML='';lb.appendChild(c);lb.style.display='flex';}
</script></body></html>"""


def render_museum(m, items):
    bg, bg2, txt, fr, icon = STYLE.get(m.get("theme"), STYLE["romantik"])
    count = len(items)
    walls_n = max(8, count)
    t = math.tan(math.pi / walls_n)
    radius = max(340, int(140 / t))
    pw = int(2 * radius * t) + 3
    slots = {}
    for i, it in enumerate(items):
        slots[i * walls_n // count] = it
    walls = []
    for k in range(walls_n):
        ang = 360 / walls_n * k
        it = slots.get(k)
        if it:
            src = f"/f/{it['file_id']}"
            if it["kind"] == "video":
                tag = (f'<video src="{src}#t=0.1" muted playsinline '
                       f'preload="metadata" onclick="openIt(this)"></video>')
            else:
                tag = f'<img src="{src}" onclick="openIt(this)">'
            inner = (
                f'<div class="slot"><div class="spot"></div><div class="lamp"></div>'
                f'<div class="frame">{tag}</div><div class="plate">{icon}</div></div>'
            )
        else:
            inner = f'<div class="deco">{icon}</div>'
        walls.append(
            f'<div class="wall" style="width:{pw}px;left:-{pw // 2}px;'
            f'transform:rotateY({ang}deg) translateZ(-{radius}px)">'
            f'<div class="crown"></div>{inner}<div class="base"></div></div>'
        )
    msg = f'<div id="msg">{H.escape(m["message"])}</div>' if m.get("message") else ""
    size = int(radius * 2.4)
    out = PAGE
    for key, val in {
        "__TITLE__": H.escape(m.get("title") or "Mening muzeyim"),
        "__BG__": bg, "__BG2__": bg2, "__TXT__": txt, "__FR__": fr,
        "__ICON__": icon, "__WALLS__": "".join(walls), "__MSG__": msg,
        "__FL__": str(-size // 2), "__FS__": str(size), "__R__": str(radius),
    }.items():
        out = out.replace(key, val)
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
                if not items:
                    return self._send(200, "text/plain; charset=utf-8",
                                      "Muzey hozircha bo'sh".encode())
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
