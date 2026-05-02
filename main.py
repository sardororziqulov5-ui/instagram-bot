import telebot
from telebot import types
import subprocess
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@bass_music_33"

if not BOT_TOKEN:
    print("❌ BOT_TOKEN topilmadi!")
    exit()

bot = telebot.TeleBot(BOT_TOKEN)

user_links = {}

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
        markup.add(types.InlineKeyboardButton("🔄 Tekshirish", callback_data="check_sub"))

        bot.send_message(message.chat.id, "Kanalga obuna bo‘ling:", reply_markup=markup)
        return

    bot.send_message(message.chat.id, "Instagram link yubor 📥")

# CHECK BUTTON
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def recheck(call):
    if check_sub(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ Obuna tasdiqlandi!")
        bot.send_message(call.message.chat.id, "Endi link yubor 📥")
    else:
        bot.answer_callback_query(call.id, "❌ Obuna yo‘q")

# LINK QABUL
@bot.message_handler(func=lambda m: m.text and "instagram.com" in m.text)
def handle_link(message):
    if not check_sub(message.from_user.id):
        start(message)
        return

    url = message.text.strip()
    user_links[message.from_user.id] = url

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🎬 Video", callback_data="video"))

    bot.send_message(message.chat.id, "Tanlang:", reply_markup=markup)

# VIDEO YUKLASH
@bot.callback_query_handler(func=lambda call: call.data == "video")
def send_video(call):
    url = user_links.get(call.from_user.id)

    if not url:
        bot.send_message(call.message.chat.id, "❌ Avval link yubor")
        return

    try:
        filename = "video.mp4"

        subprocess.run([
            "yt-dlp",
            "-f", "mp4",
            "-o", filename,
            url
        ])

        if os.path.exists(filename):
            with open(filename, "rb") as f:
                bot.send_video(call.message.chat.id, f)
            os.remove(filename)
        else:
            bot.send_message(call.message.chat.id, "❌ Yuklab bo‘lmadi")

    except Exception as e:
        bot.send_message(call.message.chat.id, f"Xato: {e}")

print("✅ Bot ishlayapti...")
bot.infinity_polling()
