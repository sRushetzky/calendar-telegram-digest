# 📆 Calendar Telegram Digest Bot

⚡️ **Automatic daily & weekly digest of your Google Calendar — sent straight to Telegram!**

---

## 🌟 Overview

This project connects your **Google Calendar** with **Telegram**, automatically sending:
- 🗓️ **Daily digest** every morning  
- 📅 **Weekly summary** every Sunday  
- 🔁 **Real-time updates** when events are added or changed

It’s designed to run **24/7 on the cloud (Render)**, requiring no local machine after setup.

---

## 🚀 Features

✅ **Google Calendar Integration** — Reads events securely using OAuth  
✅ **Telegram Bot Integration** — Sends formatted Markdown messages  
✅ **Smart Event Recognition** — Detects birthdays, holidays, sports, lectures, etc.  
✅ **Emoji Context** — Automatically adds matching emojis 🎉⚽🎓✡️🎾✂️  
✅ **Auto Deploy on Commit** — Every Git push triggers a new build on Render  
✅ **24/7 Operation** — Hosted as a background service, always on  

---

## 🧠 How It Works

1. **Google API Authorization**
   - Uses `client_secret.json` & `token.json` for OAuth credentials  
   - Automatically refreshes tokens when needed  

2. **Event Formatting**
   - `formatter.py` converts raw Google event data into Telegram-ready Markdown text  
   - Adds spacing, bold titles, and relevant emojis  

3. **Scheduler**
   - Managed by `APScheduler`  
   - Runs:
     - `send_daily_digest()` every day at 08:00  
     - `send_weekly_digest_if_sunday()` every Sunday  
     - `poll_and_send_updates_if_changed()` every few minutes  

4. **Telegram Delivery**
   - Messages sent via the Telegram Bot API using your bot token & chat ID  

---

# ☁️ Deployment Workflow & How It Runs

⚙️ **Fully Automated Cloud Setup**  
The bot is continuously deployed and hosted using **Render.com**, ensuring it runs 24/7 with no dependency on your local computer.

### 🧩 How the Deployment Works

1. **Version Control with GitHub**
   - All project code is stored on GitHub.
   - Every commit automatically triggers a build on Render.

2. **Render Build & Deploy**
   - Render pulls the latest commit from GitHub.
   - It installs dependencies via `requirements.txt`.
   - Then it executes `python -m src.main`, which:
     - Starts the background scheduler (daily, weekly, and live updates)
     - Launches a small Flask server for health checks.

3. **Google OAuth Secrets**
   - Your Google API credentials are stored securely on Render under:
     - `/etc/secrets/client_secret.json`
     - `/etc/secrets/token.json`
   - These are **Secret Files**, not part of the repository.

4. **Environment Variables**
   - The `.env` file variables (`BOT_TOKEN`, `CHAT_ID`, `TZ`) are stored safely as **Render Environment Variables**.

5. **Auto Deploy on Commit**
   - Every time you push a change to GitHub → Render automatically rebuilds & redeploys the bot.

6. **Uptime Monitoring**
   - The bot’s web service is pinged every few minutes using **UptimeRobot**.
   - This ensures the Flask server stays “awake” and the background jobs never stop running.  
   - Even if Render tries to idle, UptimeRobot’s ping keeps it alive indefinitely 🔁  

---

## 🛡️ Security Notes

- `credentials/` and `.env` are **excluded from Git** via `.gitignore`
- Google tokens are **never exposed** in commits
- All sensitive data should be stored in Render **Secret Files** or **Environment Variables**
- The codebase is safe to publish — no private information is tracked in Git history

---

## 🧑‍💻 Author

**Shahar Rushetzky**  
🎓 Computer Science Student @ HIT  
🌐 [GitHub Profile](https://github.com/sRushetzky)
📞 Phone: +972 52-7729726
📧 Email: sroshetzky@gmail.com
🔗 [LinkedIn Profile](https://www.linkedin.com/in/shahar-rushetzky/)


