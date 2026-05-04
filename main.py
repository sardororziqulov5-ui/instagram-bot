import telebot
from telebot import types
import subprocess
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@bass_music_33"

bot = telebot.TeleBot(BOT_TOKEN)

# OBUNA TEKSHIRISH
def check_sub(user_id):
    try:
        status = bot.get_chat_member(CHANNEL, user_id).status
        return status in ["member", "administrator", "creator"]
    except:
        return False

# START
@bot.message_handler(commands=['start'])
def start(message):
    if not check_sub(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 Obuna bo‘lish", url="https://t.me/bass_music_33"))
        markup.add(types.InlineKeyboardButton("🔄 Tekshirish", callback_data="check"))

        bot.send_message(message.chat.id, "❗ Kanalga obuna bo‘ling:", reply_markup=markup)
        return

    bot.send_message(message.chat.id, "📥 Instagram link yubor")

# TEKSHIRISH
@bot.callback_query_handler(func=lambda call: call.data == "check")
def check(call):
    if check_sub(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ Obuna tasdiqlandi")
        bot.send_message(call.message.chat.id, "📥 Endi link yubor")
    else:
        bot.answer_callback_query(call.id, "❌ Hali obuna emassan")

# LINK QABUL
@bot.message_handler(func=lambda m: m.text and "instagram.com" in m.text)
def download_video(message):
    if not check_sub(message.from_user.id):
        start(message)
        return

    url = message.text.strip()
    filename = "video.mp4"

    bot.send_message(message.chat.id, "⏳ Yuklanmoqda...")

    try:
        subprocess.run([
            "yt-dlp",
            "-f", "mp4",
            "-o", filename,
            url
        ])

        if os.path.exists(filename):
            with open(filename, "rb") as f:
                bot.send_video(message.chat.id, f)
            os.remove(filename)
        else:
            bot.send_message(message.chat.id, "❌ Yuklab bo‘lmadi")

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Xato: {e}")

print("✅ Bot ishlayapti...")
bot.infinity_polling()
