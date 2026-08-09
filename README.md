# 🤖 RemoteBot — সম্পূর্ণ Setup গাইড

<sub>Created By [Tech AHM YT](https://youtu.be/_pv3W4CXvwg) &nbsp;|&nbsp; [📢 Telegram](https://t.me/TECHAHMYT) &nbsp;|&nbsp; [▶️ YouTube](https://youtu.be/_pv3W4CXvwg)</sub>

---

## 📋 শুরু করার আগে যা যা লাগবে

| জিনিস | প্রয়োজন |
|-------|---------|
| **Termux** | Android-এ Python চালানোর জন্য |
| **Termux:API** | Termux API features ব্যবহারের জন্য |
| **Termux:Boot** | ফোন Restart-এর পর প্রয়োজন হলে startup চালানোর জন্য |
| **remotebot.py** | মূল RemoteBot program |
| **Bot Token** | Telegram @BotFather থেকে |
| **Chat ID** | Telegram account/group-এর Chat ID |
| **Username** | Admin/License system থেকে পাওয়া username |
| **Password** | Admin/License system থেকে পাওয়া password |

> ⚠️ Bot Token, Username এবং Password কাউকে প্রকাশ করবেন না।

---

# 1️⃣ GitHub থেকে Project নেওয়া

Repository clone করতে:

```bash
pkg update -y
pkg install git python -y
