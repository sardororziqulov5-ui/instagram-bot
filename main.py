import telebot
from telebot import types
import yt_dlp
import os
TOKEN = "8613087756:AAHsVgfWRoeg_FkBe5CxnuqMC69kb--SZw0"
CHANNEL = "@bass_music_33"

bot = telebot.TeleBot(TOKEN)

# 🔒 OBUNA TEKSHIRISH
def check_sub(user_id):
    try:
        m = bot.get_chat_member(CHANNEL, user_id)
        return m.status in ["member", "administrator", "creator"]
    except:
        return False

# 🎵 BASS
def bass_boost(inp, out, level):
    os.system(f'ffmpeg -i "{inp}" -af "bass=g={level}" "{out}"')

# 🎧 3D
def audio_3d(inp, out):
    os.system(f'ffmpeg -i "{inp}" -af "apulsator=hz=0.08" "{out}"')

# 🚀 START
@bot.message_handler(commands=['start'])
def start(message):
    if not check_sub(message.from_user.id):
        m = types.InlineKeyboardMarkup()
        m.add(types.InlineKeyboardButton("📢 Obuna", url="https://t.me/bass_music_33"))
        m.add(types.InlineKeyboardButton("✅ Tekshirish", callback_data="check"))
        bot.send_message(message.chat.id, "❗ Kanalga obuna bo‘ling", reply_markup=m)
        return

    bot.send_message(message.chat.id, "🔗 Link yubor (YouTube / Instagram / TikTok)")

# 🔄 CHECK
@bot.callback_query_handler(func=lambda c: c.data == "check")
def check(call):
    if check_sub(call.from_user.id):
        bot.send_message(call.message.chat.id, "✅ Tasdiqlandi")
    else:
        bot.answer_callback_query(call.id, "❌ Obuna bo‘l")

# 🔗 MENU
@bot.message_handler(func=lambda m: True)
def menu(message):
    if not check_sub(message.from_user.id):
        bot.send_message(message.chat.id, "❗ Obuna bo‘ling!")
        return

    url = message.text

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🎥 Video", callback_data=f"video|{url}"),
        types.InlineKeyboardButton("🎵 MP3", callback_data=f"mp3|{url}")
    )
    markup.add(
        types.InlineKeyboardButton("🔊 Bass", callback_data=f"bass|{url}"),
        types.InlineKeyboardButton("🎧 3D", callback_data=f"3d|{url}")
    )

    bot.send_message(message.chat.id, "👇 Tanlang:", reply_markup=markup)

# ⬇️ YUKLASH
@bot.callback_query_handler(func=lambda c: "|" in c.data)
def download(call):
    action, url = call.data.split("|")
    bot.answer_callback_query(call.id, "⏳ Yuklanmoqda...")

    try:
        ydl_opts = {'format': 'best', 'outtmpl': 'file.%(ext)s'}

        if action in ["mp3", "bass", "3d"]:
            ydl_opts = {
                'format': 'bestaudio',
                'outtmpl': 'audio.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3'
                }]
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        for f in os.listdir():
            if action == "video" and f.startswith("file"):
                bot.send_video(call.message.chat.id, open(f, "rb"))
                os.remove(f)

            elif action == "mp3" and f.endswith(".mp3"):
                bot.send_audio(call.message.chat.id, open(f, "rb"))
                os.remove(f)

            elif action == "bass" and f.endswith(".mp3"):
                bass_boost(f, "bass.mp3", 10)
                bot.send_audio(call.message.chat.id, open("bass.mp3", "rb"))
                os.remove(f); os.remove("bass.mp3")

            elif action == "3d" and f.endswith(".mp3"):
                audio_3d(f, "3d.mp3")
                bot.send_audio(call.message.chat.id, open("3d.mp3", "rb"))
                os.remove(f); os.remove("3d.mp3")

    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Xato: {e}")

print("🔥 BOT ISHGA TUSHDI")
bot.infinity_polling()
