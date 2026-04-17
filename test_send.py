import os
from telegram import Bot

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("chenze_0629")  # 你的個人 Telegram ID

bot = Bot(token=TOKEN)

def send_test():
    bot.send_message(
        chat_id=CHAT_ID,
        text="🧪 測試成功：Bot 正常運作"
    )

if __name__ == "__main__":
    send_test()
