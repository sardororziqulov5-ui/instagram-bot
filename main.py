import telebot
import os
import yt_dlp
import requests
from telebot import types
from flask import Flask
from threading import Thread

# --- SERVER (RENDER UCHUN) ---
app = Flask('')
@app.route('/')
def home(): return "Sardor's Menu Bot is Live!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- SOZLAMALAR ---
TOKEN = '8764022556:AAGblrMJUH3gkAdwJUgiJOmoZQTwtc4v5uo'
bot = telebot.TeleBot(TOKEN)

# --- ASOSIY MENYU ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("📥 Video yuklash")
    btn2 = types.KeyboardButton("🎵 Musiqa yuklash (MP3)")
    btn3 = types.KeyboardButton("🎨 Rasm yaratish (AI)")
    btn4 = types.KeyboardButton("🤖 AI bilan suhbat")
    btn5 = types.KeyboardButton("🔍 Musiqa qidirish")
    btn6 = types.KeyboardButton("💻 Kompyuter dasturlari")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    return markup

# --- START ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Salom Sardor! Kerakli bo'limni tanlang:", reply_markup=main_menu())

# --- TUGMALARNI QAYTA ISHLASH ---
@bot.message_handler(func=lambda m: True)
def handle_menu(message):
    if message.text == "📥 Video yuklash":
        msg = bot.send_message(message.chat.id, "Menga Instagram, TikTok yoki YouTube linkini yuboring:")
        bot.register_next_step_handler(msg, download_video)
        
    elif message.text == "🎵 Musiqa yuklash (MP3)":
        msg = bot.send_message(message.chat.id, "Videodan musiqasini ajratib olish uchun link yuboring:")
        bot.register_next_step_handler(msg, download_audio)
        
    elif message.text == "🎨 Rasm yaratish (AI)":
        msg = bot.send_message(message.chat.id, "Nima rasmini chizay? (Masalan: Nano banana) 🍌")
        bot.register_next_step_handler(msg, create_art)
        
    elif message.text == "🤖 AI bilan suhbat":
        msg = bot.send_message(message.chat.id, "Savolingizni yozing, AI javob beradi:")
        bot.register_next_step_handler(msg, chat_with_ai)
        
    elif message.text == "🔍 Musiqa qidirish":
        msg = bot.send_message(message.chat.id, "Musiqa nomini yozing:")
        bot.register_next_step_handler(msg, search_music)
        
    elif message.text == "💻 Kompyuter dasturlari":
        bot.send_message(message.chat.id, "💻 Kompyuter dasturlari kanali: https://t.me/kompyuter_dasturi_001")

# --- FUNKSIYALAR ---

def download_video(message):
    wait = bot.reply_to(message, "Video yuklanmoqda... 📥")
    file_path = f"v_{message.chat.id}.mp4"
    try:
        with yt_dlp.YoutubeDL({'format': 'best', 'outtmpl': file_path, 'quiet': True}) as ydl:
            ydl.download([message.text])
        with open(file_path, 'rb') as v:
            bot.send_video(message.chat.id, v, caption="✅ Sardor bot orqali")
        os.remove(file_path)
    except: bot.send_message(message.chat.id, "❌ Linkda xatolik!")
    bot.delete_message(message.chat.id, wait.message_id)

def download_audio(message):
    wait = bot.reply_to(message, "Musiqa ajratilmoqda... 🎵")
    file_path = f"m_{message.chat.id}.mp3"
    opts = {'format': 'bestaudio/best', 'outtmpl': file_path, 'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl: ydl.download([message.text])
        with open(file_path, 'rb') as a: bot.send_audio(message.chat.id, a)
        os.remove(file_path)
    except: bot.send_message(message.chat.id, "❌ Xatolik!")
    bot.delete_message(message.chat.id, wait.message_id)

def create_art(message):
    wait = bot.reply_to(message, "Rasm chizilmoqda... ✨")
    img_url = f"https://pollinations.ai/p/{message.text.replace(' ', '%20')}?width=1024&height=1024&model=flux"
    try: bot.send_photo(message.chat.id, img_url, caption=f"✅ Natija: {message.text}")
    except: bot.send_message(message.chat.id, "❌ Xato!")
    bot.delete_message(message.chat.id, wait.message_id)

def chat_with_ai(message):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        res = requests.get(f"https://api.simsimi.net/v2/?text={message.text}&lc=uz").json()
        bot.reply_to(message, res['success'])
    except: bot.reply_to(message, "AI hozir band.")

def search_music(message):
    wait = bot.reply_to(message, "Qidirilmoqda... 🔎")
    file_path = f"s_{message.chat.id}.mp3"
    opts = {'format': 'bestaudio', 'outtmpl': file_path, 'default_search': 'ytsearch1', 'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3'}]}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl: ydl.download([message.text])
        with open(file_path, 'rb') as f: bot.send_audio(message.chat.id, f)
        os.remove(file_path)
    except: bot.send_message(message.chat.id, "Topilmadi.")
    bot.delete_message(message.chat.id, wait.message_id)

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
