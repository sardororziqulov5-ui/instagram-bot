import telebot
import os
import yt_dlp
import requests
from telebot import types
from flask import Flask
from threading import Thread
from pydub import AudioSegment

# --- RENDER UCHUN WEB SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Sardor's Mega Bot is Live!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- SOZLAMALAR ---
TOKEN = '8764022556:AAGblrMJUH3gkAdwJUgiJOmoZQTwtc4v5uo'
bot = telebot.TeleBot(TOKEN)
user_data = {}

# --- ASOSIY MENYU ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(types.KeyboardButton("📥 Video yuklash"), types.KeyboardButton("🎵 Musiqa ajratish"))
    markup.add(types.KeyboardButton("🔊 Musiqani Bass qilish"), types.KeyboardButton("🎨 Rasm yaratish (AI)"))
    markup.add(types.KeyboardButton("🤖 AI bilan suhbat"), types.KeyboardButton("🔍 Musiqa qidirish"))
    markup.add(types.KeyboardButton("💻 Kompyuter dasturlari"), types.KeyboardButton("🎸 Bass music"))
    return markup

# --- START ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f"Xush kelibsiz, Sardor! Kerakli bo'limni tanlang:", reply_markup=main_menu())

# --- TUGMALARNI BOSHQARISH ---
@bot.message_handler(func=lambda m: True)
def handle_menu(message):
    if message.text == "📥 Video yuklash":
        msg = bot.send_message(message.chat.id, "Instagram yoki YouTube linkini yuboring:")
        bot.register_next_step_handler(msg, download_video)

    elif message.text == "🎵 Musiqa ajratish":
        msg = bot.send_message(message.chat.id, "Videodan MP3 olish uchun link yuboring:")
        bot.register_next_step_handler(msg, extract_mp3)

    elif message.text == "🔊 Musiqani Bass qilish":
        msg = bot.send_message(message.chat.id, "Menga .mp3 formatdagi musiqa yuboring:")
        bot.register_next_step_handler(msg, get_audio_for_bass)

    elif message.text == "🎨 Rasm yaratish (AI)":
        msg = bot.send_message(message.chat.id, "Nima rasmini chizay? (Inglizcha yozish yaxshi natija beradi):")
        bot.register_next_step_handler(msg, create_art)

    elif message.text == "🤖 AI bilan suhbat":
        msg = bot.send_message(message.chat.id, "Savolingizni yozing, AI javob beradi:")
        bot.register_next_step_handler(msg, chat_ai)

    elif message.text == "🔍 Musiqa qidirish":
        msg = bot.send_message(message.chat.id, "Musiqa nomini yozing:")
        bot.register_next_step_handler(msg, search_music)

    elif message.text == "💻 Kompyuter dasturlari":
        bot.send_message(message.chat.id, "💻 Kanal: https://t.me/kompyuter_dasturi_001")

    elif message.text == "🎸 Bass music":
        bot.send_message(message.chat.id, "🎸 Kanal: https://t.me/bass_music_33")

# --- FUNKSIYALAR ---

def download_video(message):
    wait = bot.reply_to(message, "Video yuklanmoqda... 📥")
    path = f"v_{message.chat.id}.mp4"
    try:
        with yt_dlp.YoutubeDL({'format': 'best', 'outtmpl': path}) as ydl: ydl.download([message.text])
        with open(path, 'rb') as f: bot.send_video(message.chat.id, f)
        os.remove(path)
    except: bot.send_message(message.chat.id, "❌ Xatolik!")
    bot.delete_message(message.chat.id, wait.message_id)

def extract_mp3(message):
    wait = bot.reply_to(message, "Musiqa ajratilmoqda... 🎵")
    path = f"m_{message.chat.id}.m4a"
    try:
        with yt_dlp.YoutubeDL({'format': 'bestaudio', 'outtmpl': path}) as ydl: ydl.download([message.text])
        with open(path, 'rb') as f: bot.send_audio(message.chat.id, f)
        os.remove(path)
    except: bot.send_message(message.chat.id, "❌ Xatolik!")
    bot.delete_message(message.chat.id, wait.message_id)

def create_art(message):
    wait = bot.reply_to(message, "Rasm chizilmoqda... ✨")
    url = f"https://pollinations.ai/p/{message.text.replace(' ', '%20')}?width=1024&height=1024&model=flux"
    try: bot.send_photo(message.chat.id, url, caption=f"✅ Natija: {message.text}")
    except: bot.send_message(message.chat.id, "❌ Xato!")
    bot.delete_message(message.chat.id, wait.message_id)

def chat_ai(message):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        res = requests.get(f"https://api.simsimi.net/v2/?text={message.text}&lc=uz").json()
        bot.reply_to(message, res['success'])
    except: bot.reply_to(message, "AI hozir band.")

def search_music(message):
    wait = bot.reply_to(message, "🔎 Qidirilmoqda...")
    path = f"s_{message.chat.id}.m4a"
    try:
        ydl_opts = {'format': 'bestaudio', 'outtmpl': path, 'default_search': 'ytsearch1', 'noplaylist': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl: ydl.download([message.text])
        with open(path, 'rb') as f: bot.send_audio(message.chat.id, f)
        os.remove(path)
    except: bot.send_message(message.chat.id, "Topilmadi.")
    bot.delete_message(message.chat.id, wait.message_id)

# --- BASS QILISH FUNKSIYASI ---
def get_audio_for_bass(message):
    if message.content_type == 'audio':
        user_data[message.chat.id] = message.audio.file_id
        msg = bot.send_message(message.chat.id, "Bass darajasini yozing (1 dan 50 gacha):")
        bot.register_next_step_handler(msg, apply_bass)
    else: bot.send_message(message.chat.id, "Iltimos, musiqa faylini yuboring!")

def apply_bass(message):
    try:
        level = int(message.text)
        if not (1 <= level <= 50): raise ValueError
        wait = bot.reply_to(message, "Bass kuchaytirilmoqda... 🔊")
        file_id = user_data[message.chat.id]
        file_info = bot.get_file(file_id)
        downloaded = bot.download_file(file_info.file_path)
        
        in_p = f"i_{message.chat.id}.mp3"
        out_p = f"b_{message.chat.id}.mp3"
        with open(in_p, 'wb') as f: f.write(downloaded)
        
        audio = AudioSegment.from_file(in_p)
        bass = audio.low_pass_filter(200).apply_gain(level * 0.5)
        audio.overlay(bass).export(out_p, format="mp3")
        
        with open(out_p, 'rb') as f: bot.send_audio(message.chat.id, f, caption=f"Bass: {level}")
        os.remove(in_p); os.remove(out_p)
        bot.delete_message(message.chat.id, wait.message_id)
    except: bot.send_message(message.chat.id, "Xato! Faqat 1-50 oraliqda raqam yozing.")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
