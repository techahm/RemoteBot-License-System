#!/usr/bin/env python3
"""
RemoteBot — Telegram Remote Control Bot
Created by Tech AHM YT | t.me/TECHAHMYT
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
import time
import urllib.request

# ═══════════════════════════════════════════════════════
# ⚙️  CONFIG — config.env থেকে লোড
# ═══════════════════════════════════════════════════════
def load_config():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.env")
    if not os.path.exists(config_path):
        print("❌ config.env পাওয়া যায়নি! আগে setup.sh রান করুন।")
        sys.exit(1)
    config = {}
    with open(config_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and "=" in line and not line.startswith("#"):
                key, _, val = line.partition("=")
                config[key.strip()] = val.strip()
    return config

CONFIG      = load_config()
BOT_TOKEN   = CONFIG.get("BOT_TOKEN", "")
CHAT_ID     = CONFIG.get("CHAT_ID", "")
LIC_USER    = CONFIG.get("LICENSE_USERNAME", "")
LIC_PASS    = CONFIG.get("LICENSE_PASSWORD", "")
LICENSE_URL = CONFIG.get("LICENSE_URL", "")

# ═══════════════════════════════════════════════════════
# ⚠️  CREATOR PROTECTION
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
        print("  ║  এই tool টি শুধুমাত্র Tech AHM YT এর।       ║")
        print("  ║  চুরি করা ভালো না! 🚫                        ║")
        print("  ╠══════════════════════════════════════════════╣")
        print(f"  ║  {C}Original Channel : t.me/TECHAHMYT{R}          ║")
        print("  ╚══════════════════════════════════════════════╝")
        print(f"{X}")
        for i in range(3, 0, -1):
            print(f"{Y}     {i}...{X}", flush=True)
            time.sleep(1)
        os.system(f'termux-open-url "{CHANNEL}"')
        sys.exit(1)

_verify_creator()

# ═══════════════════════════════════════════════════════
# 🔑  LICENSE SYSTEM
# ═══════════════════════════════════════════════════════
PRODUCT_NAME    = "RemoteBot"
PUBLIC_KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public_key.pem")


def download_database():
    if not LICENSE_URL:
        print("⚠️ LICENSE_URL নেই config.env এ!")
        return None
    try:
        req = urllib.request.Request(LICENSE_URL, headers={"User-Agent": "RemoteBot-License-System"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = r.read().decode("utf-8")
        db = json.loads(data)
        if isinstance(db, dict) and isinstance(db.get("licenses"), list):
            return db
        return None
    except Exception as e:
        print(f"\n⚠️ License server error: {e}")
        return None


def secrets_compare(a, b):
    if not (isinstance(a, str) and isinstance(b, str)) or len(a) != len(b):
        return False
    result = 0
    for x, y in zip(a.encode(), b.encode()):
        result |= x ^ y
    return result == 0


def verify_signature(payload):
    msg_file = sig_file = None
    try:
        unsigned = {k: payload[k] for k in
                    ["license_id","username","password_hash","salt","expiry","product"]}
        message  = json.dumps(unsigned, sort_keys=True, separators=(",",":")).encode()
        signature = base64.b64decode(payload["signature"], validate=True)

        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(message); msg_file = f.name
        sig_file = msg_file + ".sig"
        with open(sig_file, "wb") as f:
            f.write(signature)

        result = subprocess.run(
            ["openssl","pkeyutl","-verify","-pubin",
             "-inkey", PUBLIC_KEY_FILE,"-rawin","-in",msg_file,"-sigfile",sig_file],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return result.returncode == 0
    except Exception:
        return False
    finally:
        for fp in [msg_file, sig_file]:
            if fp and os.path.exists(fp):
                try: os.remove(fp)
                except: pass


def verify_login(username, password):
    if not os.path.exists(PUBLIC_KEY_FILE):
        return False, "public_key.pem নেই। Admin এর কাছ থেকে নিন।"

    db = download_database()
    if db is None:
        return False, "License server এ connect করা যাচ্ছে না।"

    record = next((i for i in db["licenses"] if i.get("username") == username), None)
    if record is None:
        return False, "Username পাওয়া যায়নি।"
    if record.get("product") != PRODUCT_NAME:
        return False, "Invalid product."
    if not verify_signature(record):
        return False, "License signature ভুল।"

    try:
        salt        = base64.b64decode(record["salt"])
        calc_hash   = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000).hex()
    except Exception:
        return False, "Password data ভুল।"

    if not secrets_compare(calc_hash, record.get("password_hash", "")):
        return False, "Password ভুল।"

    try:
        expiry = datetime.datetime.strptime(record["expiry"], "%Y-%m-%d")
    except Exception:
        return False, "Expiry date ভুল।"

    if datetime.datetime.now().date() > expiry.date():
        return False, "License মেয়াদ শেষ।"

    remaining = (expiry.date() - datetime.datetime.now().date()).days
    return True, {
        "license_id":     record.get("license_id", ""),
        "username":       record.get("username", ""),
        "expiry":         record.get("expiry", ""),
        "remaining_days": remaining
    }


# ═══════════════════════════════════════════════════════
# 🔐  LICENSE CHECK — config.env থেকে অটো
# ═══════════════════════════════════════════════════════
def check_license():
    R="\033[91m"; G="\033[92m"; Y="\033[93m"; B="\033[1m"; X="\033[0m"

    print(f"\n{Y}{B}╔══════════════════════════════════════════╗")
    print(f"║         RemoteBot License Check          ║")
    print(f"╚══════════════════════════════════════════╝{X}\n")

    username = LIC_USER or input(f"{Y}👤 Username: {X}").strip()
    password = LIC_PASS or getpass.getpass(f"{Y}🔐 Password: {X}")

    if not username or not password:
        print(f"{R}❌ Username/Password প্রয়োজন।{X}"); sys.exit(1)

    print(f"\n{Y}⏳ License যাচাই হচ্ছে...{X}")
    valid, result = verify_login(username, password)

    if not valid:
        print(f"\n{R}{B}╔══════════════════════════════════════════╗")
        print(f"║             ❌ ACCESS DENIED             ║")
        print(f"╠══════════════════════════════════════════╣")
        print(f"║  {str(result):<38} ║")
        print(f"╚══════════════════════════════════════════╝{X}\n")
        sys.exit(1)

    print(f"\n{G}{B}╔══════════════════════════════════════════╗")
    print(f"║             ✅ ACCESS GRANTED            ║")
    print(f"╠══════════════════════════════════════════╣")
    print(f"║  👤 User  : {result['username']:<28} ║")
    print(f"║  📅 Expiry: {result['expiry']:<28} ║")
    print(f"║  ⏳ Days  : {result['remaining_days']:<28} ║")
    print(f"╚══════════════════════════════════════════╝{X}\n")
    return True


# ═══════════════════════════════════════════════════════
# 🎨  BANNER
# ═══════════════════════════════════════════════════════
def print_banner():
    C="\033[96m"; G="\033[92m"; Y="\033[93m"; R="\033[91m"; B="\033[1m"; X="\033[0m"
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


# ═══════════════════════════════════════════════════════
# 🤖  TELEGRAM BOT
# ═══════════════════════════════════════════════════════
def send_message(text):
    url  = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = json.dumps({"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}).encode()
    try:
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"⚠️ Send error: {e}")


def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?timeout=30"
    if offset:
        url += f"&offset={offset}"
    try:
        with urllib.request.urlopen(url, timeout=35) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        print(f"⚠️ Update error: {e}")
        return None


def handle_command(text):
    text = text.strip()
    if text == "/start":
        return ("🤖 <b>RemoteBot চালু আছে!</b>\n\n"
                "📋 <b>Commands:</b>\n"
                "/start — স্ট্যাটাস\n"
                "/run &lt;cmd&gt; — কমান্ড রান\n"
                "/status — সিস্টেম ইনফো\n"
                "/help — সাহায্য")
    elif text == "/status":
        try:
            uptime = subprocess.check_output(["uptime","-p"], stderr=subprocess.DEVNULL).decode().strip()
        except: uptime = "N/A"
        try:
            mem = subprocess.check_output(["free","-h"], stderr=subprocess.DEVNULL).decode().strip()
        except: mem = "N/A"
        return f"📊 <b>System Status</b>\n\n⏱ {uptime}\n\n💾 Memory:\n<pre>{mem}</pre>"
    elif text.startswith("/run "):
        cmd = text[5:].strip()
        if not cmd: return "❌ কমান্ড দিন। যেমন: /run ls"
        try:
            out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT,
                                          timeout=15).decode("utf-8", errors="replace").strip()
            out = out[:3000] if len(out) > 3000 else out
            return f"✅ <b>Output:</b>\n<pre>{out}</pre>"
        except subprocess.TimeoutExpired:
            return "⏰ Timeout হয়েছে।"
        except subprocess.CalledProcessError as e:
            err = e.output.decode("utf-8", errors="replace").strip()[:2000]
            return f"❌ <b>Error:</b>\n<pre>{err}</pre>"
    elif text == "/help":
        return ("📖 <b>Help</b>\n\n"
                "/run ls — ফাইল লিস্ট\n"
                "/run pwd — বর্তমান পাথ\n"
                "/run uname -a — সিস্টেম ইনফো\n"
                "/status — র‍্যাম ও আপটাইম")
    else:
        return "❓ অজানা কমান্ড। /help দেখুন।"


def run_bot():
    G="\033[92m"; Y="\033[93m"; X="\033[0m"; B="\033[1m"
    print(f"{G}{B}🤖 Bot polling শুরু হয়েছে...{X}")
    send_message("🟢 <b>RemoteBot চালু হয়েছে!</b>\n/help দিয়ে কমান্ড দেখুন।")

    offset = None
    while True:
        try:
            updates = get_updates(offset)
            if not updates or not updates.get("ok"):
                time.sleep(5); continue

            for update in updates.get("result", []):
                offset  = update["update_id"] + 1
                msg     = update.get("message", {})
                chat_id = str(msg.get("chat", {}).get("id", ""))
                text    = msg.get("text", "")

                if chat_id != str(CHAT_ID):
                    continue
                if text:
                    print(f"{Y}📩 {text}{X}")
                    send_message(handle_command(text))

        except KeyboardInterrupt:
            print(f"\n{Y}🛑 Bot বন্ধ।{X}")
            send_message("🔴 <b>RemoteBot বন্ধ হয়েছে।</b>")
            break
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(10)


# ═══════════════════════════════════════════════════════
# ▶️  MAIN
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":
    check_license()
    print_banner()
    run_bot()
