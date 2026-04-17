import os
import logging

from telegram.ext import Updater, CommandHandler

TOKEN = os.getenv("8765114886:AAERMDxtU87_6JEvDu6OMSYENIEpQ18czWo")
from apscheduler.schedulers.background import BackgroundScheduler

from crawler import get_tainan_schedule, get_president_schedule
from database import subscribe, get_users, get_user_targets, is_new, save_history

# ========= 基本設定 =========

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


# ========= 指令 =========

def start(update, context):
    update.message.reply_text(
        "📢 首長公開行程通知 Bot\n\n"
        "可用指令：\n"
        "/subscribe tainan\n"
        "/subscribe president"
    )


def subscribe_cmd(update, context):
    user_id = update.message.chat_id

    if len(context.args) == 0:
        update.message.reply_text("請輸入 /subscribe tainan 或 /subscribe president")
        return

    target = context.args[0].lower()

    if target not in ["tainan", "president"]:
        update.message.reply_text("只能訂閱：tainan 或 president")
        return

    subscribe(user_id, target)
    update.message.reply_text(f"✅ 已訂閱 {target}")


# ========= 推播檢查 =========

def check_updates(context):
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
                        context.bot.send_message(
                            chat_id=user,
                            text=f"📢 新行程通知\n\n{item}"
                        )
                        save_history(item)

    except Exception as e:
        logger.error(f"Error in check_updates: {e}")


# ========= 主程式 =========

def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN 沒有設定！請到 Render 設定環境變數")

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # 指令
    dp.add_handler(CommandHandler("start", start))
    dp
