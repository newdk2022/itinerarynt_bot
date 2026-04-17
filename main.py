import os
import logging
import pytz

from flask import Flask
from telegram import Bot
from telegram.ext import Updater, CommandHandler

from apscheduler.schedulers.background import BackgroundScheduler

from crawler import get_tainan_schedule, get_president_schedule
from database import (
    subscribe,
    unsubscribe,
    get_users,
    get_user_targets,
    is_new,
    save_history
)

# ========= 基本設定 =========

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID_TEST = os.getenv("TEST_CHAT_ID")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

bot = Bot(token=TOKEN)
updater = Updater(token=TOKEN, use_context=True)
dp = updater.dispatcher


# ========= 指令 =========

def start(update, context):
    update.message.reply_text(
        "📢 首長行程通知 Bot\n\n"
        "指令列表：\n"
        "/subscribe tainan\n"
        "/subscribe president\n"
        "/unsubscribe tainan\n"
        "/unsubscribe president\n"
        "/my"
    )


def subscribe_cmd(update, context):
    user_id = update.message.chat_id

    if not context.args:
        update.message.reply_text("請輸入 /subscribe tainan 或 /subscribe president")
        return

    target = context.args[0].lower()

    if target not in ["tainan", "president"]:
        update.message.reply_text("只能訂閱：tainan / president")
        return

    subscribe(user_id, target)
    update.message.reply_text(f"✅ 已訂閱：{target}")


def unsubscribe_cmd(update, context):
    user_id = update.message.chat_id

    if not context.args:
        update.message.reply_text("請輸入 /unsubscribe tainan 或 /unsubscribe president")
        return

    target = context.args[0].lower()

    unsubscribe(user_id, target)
    update.message.reply_text(f"❌ 已取消訂閱：{target}")


def my_subscriptions(update, context):
    user_id = update.message.chat_id
    targets = get_user_targets(user_id)

    if not targets:
        update.message.reply_text("你目前沒有訂閱任何通知")
        return

    text = "📌 你的訂閱：\n\n" + "\n".join(f"• {t}" for t in targets)
    update.message.reply_text(text)


# ========= 推播 =========

def check_updates():
    logger.info("🔥 check_updates triggered")

    try:
        all_data = {
            "tainan": get_tainan_schedule() or [],
            "president": get_president_schedule() or []
        }

        users = get_users() or []

        for user in users:
            targets = get_user_targets(user) or []

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

                        try:
                            bot.send_message(chat_id=user, text=text)
                            save_history(item)
                        except Exception as e:
                            logger.error(f"send_message error: {e}")

    except Exception as e:
        logger.error(f"check_updates error: {e}")


# ========= Flask =========

@app.route("/")
def home():
    return "Bot is running"


# ========= 測試 =========

def send_test():
    if CHAT_ID_TEST:
        try:
            bot.send_message(
                chat_id=CHAT_ID_TEST,
                text="🧪 Bot 已成功啟動"
            )
        except Exception as e:
            logger.error(f"test send error: {e}")


# ========= 主程式 =========

def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN 沒設定")

    # handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("subscribe", subscribe_cmd))
    dp.add_handler(CommandHandler("unsubscribe", unsubscribe_cmd))
    dp.add_handler(CommandHandler("my", my_subscriptions))

    # 🚨 避免重複 scheduler
    scheduler = BackgroundScheduler(
        timezone=pytz.timezone("Asia/Taipei"),
        daemon=True
    )

    scheduler.add_job(check_updates, "interval", minutes=10)
    scheduler.start()

    # start bot
    updater.start_polling()

    # test
    send_test()

    updater.idle()


if __name__ == "__main__":
    main()
