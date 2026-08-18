# 🤖 RemoteBot — Complete Guide
**Created by Tech AHM YT | t.me/TECHAHMYT**

---

## 📁 ফাইল লিস্ট
```
remotebot_project/
├── keygen.py      ← 🔑 শুধু ADMIN এর জন্য (license তৈরি)
├── remotebot.py   ← 🤖 ইউজার রান করবে
├── setup.sh       ← ⚙️  ইউজার একবার চালাবে
├── start.sh       ← ▶️  বট চালু (setup এর পরে তৈরি হয়)
└── stop.sh        ← 🛑 বট বন্ধ (setup এর পরে তৈরি হয়)
```

---

## 👑 ADMIN — আপনি যা করবেন (একবার)

### ধাপ ১ — Key তৈরি করুন
```bash
cd ~/remotebot_admin
python keygen.py
```
প্রথমবার চালালে `private_key.pem` ও `public_key.pem` তৈরি হবে।

> ⚠️ `private_key.pem` কখনো কাউকে দেবেন না!

### ধাপ ২ — GitHub এ আপলোড করুন
- `licenses.json` → GitHub repo তে আপলোড করুন
- `public_key.pem` → ইউজারদের দিন বা GitHub এ রাখুন

### ধাপ ৩ — নতুন License তৈরি
```bash
python keygen.py
# মেনু থেকে 1 চাপুন
# Username, Password, মেয়াদ দিন
# licenses.json GitHub এ আবার আপলোড করুন
```

---

## 👤 ইউজার — যা করবে

### ধাপ ১ — Setup (একবার)
```bash
bash setup.sh
```
জিজ্ঞেস করবে:
- 👤 License Username (আপনি দেবেন)
- 🔐 License Password (আপনি দেবেন)
- 🤖 Bot Token
- 💬 Chat ID
- 🔗 GitHub licenses.json URL (আপনার repo URL)
- 🔗 public_key.pem URL

### ধাপ ২ — বট চালু
```bash
bash start.sh
```

### ধাপ ৩ — ফোন অন হলেই অটো চালু
**Termux:Boot** (F-Droid) ইন্সটল করুন — ব্যস!

---

## 🤖 Bot Commands
| Command | কাজ |
|---------|-----|
| `/start` | স্ট্যাটাস |
| `/status` | র‍্যাম ও আপটাইম |
| `/run ls` | ফাইল লিস্ট |
| `/run <যেকোনো কমান্ড>` | কমান্ড রান |
| `/help` | সাহায্য |

---

## ⏳ License মেয়াদ
| প্যাকেজ | দিন |
|---------|-----|
| সাপ্তাহিক | ৭ দিন |
| ১০ দিন | ১০ দিন |
| মাসিক | ৩০ দিন |
| ত্রৈমাসিক | ৯০ দিন |
| কাস্টম | যেকোনো |

---
📢 **t.me/TECHAHMYT** | ▶️ **youtu.be/_pv3W4CXvwg**
