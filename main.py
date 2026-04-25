import telebot
from telebot import types
import instaloader
import os
import subprocess

BOT_TOKEN = os.getenv("8098097569:AAGP9XoDKtB_JWp14G8IrmBp96kRdYIDf08")  # TOKENNI ENV GA QO‘Y
bot = telebot.TeleBot(BOT_TOKEN)

L = instaloader.Instaloader(download_pictures=True, download_videos=True)

# START
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📥 Yuklash", callback_data="download"))

    bot.send_message(message.chat.id, "Salom 👋\nInstagram link yubor:", reply_markup=markup)


# LINK QABUL QILISH
@bot.message_handler(func=lambda m: "instagram.com" in m.text)
def get_link(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🎬 Video", callback_data="video"),
        types.InlineKeyboardButton("🎵 MP3", callback_data="mp3")
    )
    markup.add(
        types.InlineKeyboardButton("🖼 Rasm", callback_data="photo")
    )

    bot.send_message(message.chat.id, "Qanday yuklaysiz?", reply_markup=markup)

    bot.register_next_step_handler(message, process_link)


def process_link(message):
    bot.user_data = {"url": message.text}


# BUTTON BOSILGANDA
@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    url = getattr(bot, "user_data", {}).get("url")

    if not url:
        bot.send_message(call.message.chat.id, "❌ Avval link yuboring")
        return

    shortcode = url.split("/")[-2]

    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        L.download_post(post, target="downloads")

        for file in os.listdir("downloads"):
            path = os.path.join("downloads", file)

            # 🎬 VIDEO
            if call.data == "video" and file.endswith(".mp4"):
                with open(path, "rb") as f:
                    bot.send_video(call.message.chat.id, f)

            # 🖼 RASM
            elif call.data == "photo" and file.endswith(".jpg"):
                with open(path, "rb") as f:
                    bot.send_photo(call.message.chat.id, f)

            # 🎵 MP3
            elif call.data == "mp3" and file.endswith(".mp4"):
                mp3_file = path.replace(".mp4", ".mp3")

                subprocess.run([
                    "ffmpeg", "-i", path, "-q:a", "0", "-map", "a", mp3_file
                ])

                with open(mp3_file, "rb") as f:
                    bot.send_audio(call.message.chat.id, f)

                os.remove(mp3_file)

            os.remove(path)

    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Xato: {e}")


bot.infinity_polling()
