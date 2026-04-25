import telebot
from telebot import types
import os
import subprocess

BOT_TOKEN = os.getenv("8098097569:AAGP9XoDKtB_JWp14G8IrmBp96kRdYIDf08")  # Railway uchun

bot = telebot.TeleBot(BOT_TOKEN)

CHANNEL = "@bass_music_33"
user_links = {}

def check_sub(user_id):
    try:
        status = bot.get_chat_member(CHANNEL, user_id).status
        return status in ["member", "administrator", "creator"]
    except:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    if not check_sub(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 Obuna bo‘lish", url="https://t.me/bass_music_33"))
        markup.add(types.InlineKeyboardButton("🔄 Tekshirish", callback_data="check"))

        bot.send_message(message.chat.id, "Kanalga obuna bo‘ling:", reply_markup=markup)
        return

    bot.send_message(message.chat.id, "Instagram link yubor 📥")

@bot.callback_query_handler(func=lambda call: call.data == "check")
def recheck(call):
    if check_sub(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ OK")
        bot.send_message(call.message.chat.id, "Link yubor 📥")
    else:
        bot.answer_callback_query(call.id, "❌ Obuna bo‘ling")

@bot.message_handler(func=lambda m: m.text and "instagram.com" in m.text)
def handle_link(message):
    user_links[message.from_user.id] = message.text.strip()

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🎬 Video yuklash", callback_data="video"))

    bot.send_message(message.chat.id, "Tanlang:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "video")
def send_video(call):
    url = user_links.get(call.from_user.id)

    if not url:
        bot.send_message(call.message.chat.id, "❌ Avval link yubor")
        return

    filename = f"video_{call.from_user.id}.mp4"

    subprocess.run([
        "yt-dlp",
        "-f", "best",
        "-o", filename,
        url
    ])

    if os.path.exists(filename):
        with open(filename, "rb") as f:
            bot.send_video(call.message.chat.id, f)
        os.remove(filename)
    else:
        bot.send_message(call.message.chat.id, "❌ Video yuklab bo‘lmadi")

print("Bot ishlayapti...")
bot.infinity_polling()
