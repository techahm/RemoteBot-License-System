#!/data/data/com.termux/files/usr/bin/bash
# ═══════════════════════════════════════════════════════
# RemoteBot — Auto Setup for Termux
# Created by Tech AHM YT | t.me/TECHAHMYT
# ═══════════════════════════════════════════════════════

R="\033[91m"; G="\033[92m"; Y="\033[93m"
C="\033[96m"; B="\033[1m";  X="\033[0m"

clear
echo -e "${C}${B}"
echo " ██████╗ ███████╗███╗   ███╗ ██████╗ ████████╗███████╗"
echo " ██╔══██╗██╔════╝████╗ ████║██╔═══██╗╚══██╔══╝██╔════╝"
echo " ██████╔╝█████╗  ██╔████╔██║██║   ██║   ██║   █████╗  "
echo " ██╔══██╗██╔══╝  ██║╚██╔╝██║██║   ██║   ██║   ██╔══╝  "
echo " ██║  ██║███████╗██║ ╚═╝ ██║╚██████╔╝   ██║   ███████╗"
echo " ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝ ╚═════╝   ╚═╝   ╚══════╝"
echo -e "${X}"
echo -e "${Y}${B} ╔══════════════════════════════════════════════════╗"
echo -e " ║       🤖 RemoteBot Auto Setup for Termux         ║"
echo -e " ║          Created By  Tech AHM YT                 ║"
echo -e " ╚══════════════════════════════════════════════════╝${X}"
echo ""

# ═══════════════════════════════════════════════════════
# STEP 1: User Config
# ═══════════════════════════════════════════════════════
echo -e "${Y}${B}📋 STEP 1: আপনার তথ্য দিন${X}"
echo -e "${C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${X}"
echo ""

read -p "$(echo -e ${Y}'👤 License Username : '${X})" LIC_USER
read -s -p "$(echo -e ${Y}'🔐 License Password : '${X})" LIC_PASS
echo ""
read -p "$(echo -e ${Y}'🤖 Bot Token        : '${X})" BOT_TOKEN
read -p "$(echo -e ${Y}'💬 Chat ID          : '${X})" CHAT_ID
read -p "$(echo -e ${Y}'🔗 GitHub RAW licenses.json URL : '${X})" LICENSE_URL

echo ""

# config.env সেভ
cat > config.env <<CONFEOF
LICENSE_USERNAME=${LIC_USER}
LICENSE_PASSWORD=${LIC_PASS}
BOT_TOKEN=${BOT_TOKEN}
CHAT_ID=${CHAT_ID}
LICENSE_URL=${LICENSE_URL}
CONFEOF

echo -e "${G}✅ config.env সেভ হয়েছে${X}"
echo ""

# ═══════════════════════════════════════════════════════
# STEP 2: Permissions
# ═══════════════════════════════════════════════════════
echo -e "${Y}${B}📋 STEP 2: Storage Permission${X}"
echo -e "${C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${X}"
termux-setup-storage 2>/dev/null || true
echo -e "${G}✅ Storage permission দেওয়া হয়েছে${X}"
echo ""

# ═══════════════════════════════════════════════════════
# STEP 3: Packages
# ═══════════════════════════════════════════════════════
echo -e "${Y}${B}📋 STEP 3: Packages Install হচ্ছে...${X}"
echo -e "${C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${X}"
pkg update -y && pkg upgrade -y
pkg install -y python openssl termux-tools
pip install --upgrade pip
pip install requests
echo -e "${G}✅ সব package install হয়েছে${X}"
echo ""

# ═══════════════════════════════════════════════════════
# STEP 4: public_key.pem ডাউনলোড
# ═══════════════════════════════════════════════════════
echo -e "${Y}${B}📋 STEP 4: Public Key ডাউনলোড${X}"
echo -e "${C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${X}"

if [ ! -f "public_key.pem" ]; then
    read -p "$(echo -e ${Y}'🔗 public_key.pem এর URL দিন: '${X})" KEY_URL
    curl -sL "$KEY_URL" -o public_key.pem
    if [ -f "public_key.pem" ] && [ -s "public_key.pem" ]; then
        echo -e "${G}✅ public_key.pem ডাউনলোড হয়েছে${X}"
    else
        echo -e "${R}❌ public_key.pem ডাউনলোড ব্যর্থ!${X}"
        echo -e "${Y}👉 ফাইলটি ম্যানুয়ালি এই ফোল্ডারে রাখুন।${X}"
    fi
else
    echo -e "${C}ℹ️  public_key.pem আগে থেকেই আছে${X}"
fi
echo ""

# ═══════════════════════════════════════════════════════
# STEP 5: Boot Auto-start
# ═══════════════════════════════════════════════════════
echo -e "${Y}${B}📋 STEP 5: Auto Boot Setup${X}"
echo -e "${C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${X}"

BOOT_DIR="${HOME}/.termux/boot"
mkdir -p "${BOOT_DIR}"
PROJECT_DIR="$(pwd)"

cat > "${BOOT_DIR}/remotebot_autostart.sh" <<BOOTEOF
#!/data/data/com.termux/files/usr/bin/bash
sleep 8
cd "${PROJECT_DIR}"
termux-wake-lock
source config.env
python remotebot.py >> remotebot.log 2>&1 &
BOOTEOF

chmod +x "${BOOT_DIR}/remotebot_autostart.sh"
echo -e "${G}✅ Auto Boot সেটআপ হয়েছে${X}"
echo ""

# ═══════════════════════════════════════════════════════
# STEP 6: start.sh ও stop.sh তৈরি
# ═══════════════════════════════════════════════════════
echo -e "${Y}${B}📋 STEP 6: start.sh ও stop.sh তৈরি${X}"
echo -e "${C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${X}"

cat > start.sh <<'STARTEOF'
#!/data/data/com.termux/files/usr/bin/bash
R="\033[91m"; G="\033[92m"; Y="\033[93m"; C="\033[96m"; B="\033[1m"; X="\033[0m"

if [ ! -f "config.env" ]; then
    echo -e "${R}❌ config.env নেই! আগে setup.sh রান করুন।${X}"; exit 1
fi
if [ ! -f "public_key.pem" ]; then
    echo -e "${R}❌ public_key.pem নেই! Admin এর কাছ থেকে নিন।${X}"; exit 1
fi

echo -e "${Y}🔒 Wake Lock চালু হচ্ছে...${X}"
termux-wake-lock

OLD_PID=$(pgrep -f remotebot.py)
if [ -n "$OLD_PID" ]; then
    echo -e "${Y}⚠️  আগের বট বন্ধ হচ্ছে...${X}"
    kill "$OLD_PID" 2>/dev/null; sleep 2
fi

source config.env
echo -e "${G}${B}🚀 RemoteBot চালু হচ্ছে...${X}"
echo -e "${C}📋 Log: tail -f remotebot.log${X}"
echo -e "${C}🛑 বন্ধ: bash stop.sh${X}"
echo ""
python remotebot.py 2>&1 | tee -a remotebot.log
STARTEOF

cat > stop.sh <<'STOPEOF'
#!/data/data/com.termux/files/usr/bin/bash
echo -e "\033[91m🛑 RemoteBot বন্ধ হচ্ছে...\033[0m"
pkill -f remotebot.py 2>/dev/null
termux-wake-unlock 2>/dev/null
echo -e "\033[92m✅ বট বন্ধ হয়েছে\033[0m"
STOPEOF

chmod +x start.sh stop.sh
echo -e "${G}✅ start.sh ও stop.sh তৈরি হয়েছে${X}"
echo ""

# ═══════════════════════════════════════════════════════
# DONE
# ═══════════════════════════════════════════════════════
echo -e "${G}${B}"
echo " ╔══════════════════════════════════════════════════╗"
echo " ║         ✅ সেটআপ সম্পন্ন!                       ║"
echo " ╠══════════════════════════════════════════════════╣"
echo " ║  বট চালু : bash start.sh                         ║"
echo " ║  বট বন্ধ  : bash stop.sh                         ║"
echo " ║  Log      : tail -f remotebot.log                ║"
echo " ╠══════════════════════════════════════════════════╣"
echo " ║  ⚠️  Termux:Boot app ইন্সটল করুন (F-Droid)       ║"
echo " ║  ফোন অন হলেই বট অটো চালু হবে!                   ║"
echo " ╚══════════════════════════════════════════════════╝"
echo -e "${X}"

read -p "$(echo -e ${Y}'▶️  এখনই বট চালু করবেন? (y/n): '${X})" START_NOW
if [[ "$START_NOW" == "y" || "$START_NOW" == "Y" ]]; then
    bash start.sh
fi
