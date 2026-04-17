import os
import logging
import pytz
from flask import Flask, request

from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler

from apscheduler.schedulers.background import BackgroundScheduler

from crawler import get_tainan_schedule, get_president_schedule
from database import subscribe, get_users, get_user_targets, is_new, save_history

# ========= 基本設定 =========

TOKEN = os.getenv("BOT_TOKEN")
APP_URL = os.getenv("APP_URL")  # Railway 網址

bot = Bot(token=TOKEN)

app = Flask(__name__)
dispatcher = Dispatcher(bot, None, use_context=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========= 指令 =========

def start(update, context):
    update.message.reply_text(
        "📢 首長公開行程通知 Bot\n\n"
        "/subscribe tainan\n"
        "/subscribe president"
    )

def subscribe_cmd(update, context):
    user_id = update.message.chat_id

    if not context.args:
        update.message.reply_text("用法：/subscribe tainan")
        return

    target = context.args[0].lower()

    if target not in ["tainan", "president"]:
        update.message.reply_text("只能 tainan 或 president")
        return

    subscribe(user_id, target)
    update.message.reply_text(f"✅ 已訂閱 {target}")

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("subscribe", subscribe_cmd))

# ========= 推播 =========

def check_updates():
    try:
        tainan = get_tainan_schedule()
        president = get_president_schedule()

        all_data = {
            "tainan": tainan,
            "president": president
        }

        users = get_users()

        for user in users:
            targets = get_user_targets(user)

            for t in targets:
                if t not in all_data:
                    continue

                for item in all_data[t]:
                    if is_new(item):

                        text = (
                            f"📢 首長行程更新\n\n"
                            f"🏛 來源：{t}\n"
                            f"━━━━━━━━━━\n"
                            f"{item}"
                        )

                        bot.send_message(chat_id=user, text=text)
                        save_history(item)

    except Exception as e:
        logger.error(e)

# ========= webhook =========

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

@app.route("/")
def index():
    return "Bot running"

# ========= 啟動 =========

def main():
    if not TOKEN or not APP_URL:
        raise ValueError("缺 BOT_TOKEN 或 APP_URL")

    # 設 webhook
    bot.set_webhook(url=f"{APP_URL}/{TOKEN}")

    # 排程
    scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Taipei"))
    scheduler.add_job(check_updates, "interval", minutes=10)
    scheduler.start()

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    main()
