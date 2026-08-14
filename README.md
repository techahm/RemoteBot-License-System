# 🤖 RemoteBot — Setup Guide
**Created by Tech AHM YT | t.me/TECHAHMYT**

---

## 📁 ফাইল লিস্ট
```
RemoteBot-License-System/
├── setup.sh       ← প্রথমে এটা রান করুন (একবারই)
├── remotebot.py   ← মেইন বট ফাইল
├── start.sh       ← বট চালু করুন (setup এর পরে তৈরি হবে)
├── stop.sh        ← বট বন্ধ করুন (setup এর পরে তৈরি হবে)
├── config.env     ← আপনার তথ্য (setup এর পরে তৈরি হবে)
├── public_key.pem ← RSA Key (setup এর পরে তৈরি হবে)
└── remotebot.log  ← বট লগ (বট চালু হলে তৈরি হবে)
```

---

## 🚀 প্রথমবার সেটআপ (মাত্র একবার)

### ধাপ ১ — Termux খুলুন এবং ফাইল কপি করুন
```bash
# প্রজেক্ট ফোল্ডারে যান
cd ~/RemoteBot-License-System
```

### ধাপ ২ — Setup রান করুন
```bash
bash setup.sh
```
> এখানে আপনাকে জিজ্ঞেস করবে:
> - 👤 License Username
> - 🔐 License Password
> - 🤖 Bot Token
> - 💬 Chat ID

### ধাপ ৩ — বট চালু হবে!
Setup শেষে জিজ্ঞেস করবে "এখনই চালু করবেন?"
`y` চাপলে বট চালু হয়ে যাবে।

---

## 📱 ফোন অফ-অন করলেও বট চলবে

### Termux:Boot App লাগবে
1. F-Droid থেকে **Termux:Boot** ইন্সটল করুন
2. একবার অ্যাপটি খুলুন (permission দিন)
3. এরপর থেকে ফোন রিস্টার্ট করলেই বট অটো চালু হবে!

---

## ▶️ পরবর্তীবার বট চালু করতে
```bash
cd ~/RemoteBot-License-System
bash start.sh
```

## 🛑 বট বন্ধ করতে
```bash
bash stop.sh
```

## 📋 লগ দেখতে
```bash
tail -f remotebot.log
```

---

## 🤖 Bot Commands
| Command | কাজ |
|---------|-----|
| `/start` | বট স্ট্যাটাস দেখুন |
| `/status` | র‍্যাম ও আপটাইম দেখুন |
| `/run <cmd>` | যেকোনো কমান্ড রান করুন |
| `/help` | সাহায্য দেখুন |

### উদাহরণ:
```
/run ls -la
/run uname -a
/run free -h
/run pwd
```

---

## 📢 Support
- Telegram: t.me/TECHAHMYT
- YouTube: youtu.be/_pv3W4CXvwg
