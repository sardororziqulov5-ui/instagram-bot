import telebot
from telebot import types
import instaloader
import os

BOT_TOKEN = os.getenv("8098097569:AAGP9XoDKtB_JWp14G8IrmBp96kRdYIDf08")  # TOKEN ENV orqali olinadi
bot = telebot.TeleBot(BOT_TOKEN)

L = instaloader.Instaloader(download_picture=True, download_videos=True)

# Papka yaratib qo'yamiz
if not os.path.exists("downloads"):
    os.makedirs("downloads")


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Salom 👋\nInstagram link yubor.")


# LINK QABUL
@bot.message_handler(func=lambda m: m.text and "instagram.com" in m.text)
def handle_link(message):
    url = message.text.strip()

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🎬 Video", callback_data=f"video|{url}"),
        types.InlineKeyboardButton("🖼 Rasm", callback_data=f"photo|{url}")
    )

    bot.send_message(message.chat.id, "Tanlang:", reply_markup=markup)


# BUTTON BOSILGANDA
@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    try:
        action, url = call.data.split("|")
        shortcode = url.split("/")[-2]

        post = instaloader.Post.from_shortcode(L.context, shortcode)
        L.download_post(post, target="downloads")

        sent = False

        for file in os.listdir("downloads"):
            path = os.path.join("downloads", file)

            # VIDEO
            if action == "video" and file.endswith(".mp4"):
                with open(path, "rb") as f:
                    bot.send_video(call.message.chat.id, f)
                sent = True

            # RASM
            elif action == "photo" and file.endswith(".jpg"):
                with open(path, "rb") as f:
                    bot.send_photo(call.message.chat.id, f)
                sent = True

            os.remove(path)

        if not sent:
            bot.send_message(call.message.chat.id, "❌ Mos fayl topilmadi")

    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Xato: {e}")


bot.infinity_polling()
