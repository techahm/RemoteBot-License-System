#!/data/data/com.termux/files/usr/bin/bash
# ═══════════════════════════════════════════════════════
# RemoteBot — Auto Setup Script for Termux
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
echo -e " ║  📢 t.me/TECHAHMYT                               ║"
echo -e " ╚══════════════════════════════════════════════════╝${X}"
echo ""

# ═══════════════════════════════════════════════════════
# STEP 1: Config input from user
# ═══════════════════════════════════════════════════════
echo -e "${Y}${B}📋 STEP 1: আপনার তথ্য দিন${X}"
echo -e "${C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${X}"
echo ""

read -p "$(echo -e ${Y}'👤 License Username : '${X})" LIC_USER
read -s -p "$(echo -e ${Y}'🔐 License Password : '${X})" LIC_PASS
echo ""
read -p "$(echo -e ${Y}'🤖 Bot Token        : '${X})" BOT_TOKEN
read -p "$(echo -e ${Y}'💬 Chat ID          : '${X})" CHAT_ID

echo ""
echo -e "${G}✅ তথ্য সেভ হচ্ছে...${X}"

# config.env ফাইলে সেভ করো
cat > config.env <<EOF
LICENSE_USERNAME=${LIC_USER}
LICENSE_PASSWORD=${LIC_PASS}
BOT_TOKEN=${BOT_TOKEN}
CHAT_ID=${CHAT_ID}
EOF

echo -e "${G}✅ config.env সেভ হয়েছে${X}"
echo ""

# ═══════════════════════════════════════════════════════
# STEP 2: Termux permissions
# ═══════════════════════════════════════════════════════
echo -e "${Y}${B}📋 STEP 2: Termux Storage Permission${X}"
echo -e "${C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${X}"
termux-setup-storage 2>/dev/null || true
echo -e "${G}✅ Storage permission দেওয়া হয়েছে${X}"
echo ""

# ═══════════════════════════════════════════════════════
# STEP 3: Package update & install
# ═══════════════════════════════════════════════════════
echo -e "${Y}${B}📋 STEP 3: Package Install হচ্ছে...${X}"
echo -e "${C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${X}"

pkg update -y && pkg upgrade -y
pkg install -y python openssl termux-services termux-tools

pip install --upgrade pip
pip install python-telegram-bot requests cryptography

echo -e "${G}✅ সব package install হয়েছে${X}"
echo ""

# ═══════════════════════════════════════════════════════
# STEP 4: OpenSSL Key Generate
# ═══════════════════════════════════════════════════════
echo -e "${Y}${B}📋 STEP 4: RSA Key তৈরি হচ্ছে...${X}"
echo -e "${C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${X}"

if [ ! -f "public_key.pem" ]; then
    openssl genrsa -out private_key.pem 2048 2>/dev/null
    openssl rsa -in private_key.pem -pubout -out public_key.pem 2>/dev/null
    echo -e "${G}✅ RSA Key তৈরি হয়েছে${X}"
else
    echo -e "${C}ℹ️  Key আগে থেকেই আছে, skip করা হলো${X}"
fi
echo ""

# ═══════════════════════════════════════════════════════
# STEP 5: Termux Boot Auto-start setup
# ═══════════════════════════════════════════════════════
echo -e "${Y}${B}📋 STEP 5: Auto Boot Setup হচ্ছে...${X}"
echo -e "${C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${X}"

# Termux:Boot ডিরেক্টরি
BOOT_DIR="${HOME}/.termux/boot"
mkdir -p "${BOOT_DIR}"

PROJECT_DIR="$(pwd)"

cat > "${BOOT_DIR}/remotebot_autostart.sh" <<BOOTEOF
#!/data/data/com.termux/files/usr/bin/bash
# RemoteBot Auto Start on Boot
sleep 5
cd "${PROJECT_DIR}"
source config.env
python remotebot.py >> remotebot.log 2>&1 &
BOOTEOF

chmod +x "${BOOT_DIR}/remotebot_autostart.sh"

echo -e "${G}✅ Auto Boot সেটআপ হয়েছে${X}"
echo -e "${C}ℹ️  Termux:Boot app ইন্সটল থাকলে ফোন রিস্টার্টেও বট চলবে${X}"
echo ""

# ═══════════════════════════════════════════════════════
# STEP 6: Keep-alive with termux-wake-lock
# ═══════════════════════════════════════════════════════
echo -e "${Y}${B}📋 STEP 6: Wake Lock সেটআপ হচ্ছে...${X}"
echo -e "${C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${X}"

# start.sh — বট চালু করার স্ক্রিপ্ট
cat > start.sh <<'STARTEOF'
#!/data/data/com.termux/files/usr/bin/bash
R="\033[91m"; G="\033[92m"; Y="\033[93m"; X="\033[0m"; B="\033[1m"

echo -e "${Y}${B}🔒 Wake Lock চালু হচ্ছে (ফোন স্লিপে গেলেও বট চলবে)...${X}"
termux-wake-lock

echo -e "${G}${B}🤖 RemoteBot চালু হচ্ছে...${X}"
source config.env
python remotebot.py
STARTEOF

chmod +x start.sh

echo -e "${G}✅ Wake Lock স্ক্রিপ্ট তৈরি হয়েছে${X}"
echo ""

# ═══════════════════════════════════════════════════════
# STEP 7: Stop script
# ═══════════════════════════════════════════════════════
cat > stop.sh <<'STOPEOF'
#!/data/data/com.termux/files/usr/bin/bash
echo -e "\033[91m🛑 RemoteBot বন্ধ হচ্ছে...\033[0m"
pkill -f remotebot.py
termux-wake-unlock
echo -e "\033[92m✅ বট বন্ধ হয়েছে\033[0m"
STOPEOF

chmod +x stop.sh

# ═══════════════════════════════════════════════════════
# DONE
# ═══════════════════════════════════════════════════════
echo ""
echo -e "${G}${B}"
echo " ╔══════════════════════════════════════════════════╗"
echo " ║         ✅ সেটআপ সম্পন্ন হয়েছে!                ║"
echo " ╠══════════════════════════════════════════════════╣"
echo " ║  বট চালু করতে  : bash start.sh                  ║"
echo " ║  বট বন্ধ করতে  : bash stop.sh                   ║"
echo " ║  Log দেখতে     : tail -f remotebot.log           ║"
echo " ╠══════════════════════════════════════════════════╣"
echo " ║  ⚠️  Termux:Boot app ইন্সটল করুন                ║"
echo " ║  তাহলে ফোন অন করলেই বট চালু হবে!               ║"
echo " ╚══════════════════════════════════════════════════╝"
echo -e "${X}"
echo ""
echo -e "${Y}▶️  এখনই বট চালু করতে চান? (y/n): ${X}"
read -r START_NOW

if [[ "$START_NOW" == "y" || "$START_NOW" == "Y" ]]; then
    bash start.sh
fi
