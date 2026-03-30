import telebot
import os
import yt_dlp
import requests
from telebot import types
from flask import Flask
from threading import Thread

# --- SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Sardor's Music Bot is Live!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- SOZLAMALAR ---
TOKEN = '8764022556:AAGblrMJUH3gkAdwJUgiJOmoZQTwtc4v5uo'
bot = telebot.TeleBot(TOKEN)

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("📥 Video yuklash", "🎵 Musiqa ajratish")
    markup.add("🎨 Rasm yaratish (AI)", "🤖 AI bilan suhbat")
    markup.add("🔍 Musiqa qidirish", "💻 Kompyuter dasturlari")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Tayyor! Musiqa qidirish tugmasini bosing:", reply_markup=main_menu())

@bot.message_handler(func=lambda m: True)
def handle_menu(message):
    if message.text == "🔍 Musiqa qidirish":
        msg = bot.send_message(message.chat.id, "Musiqa nomini yozing (Masalan: Sherali Jo'rayev Pariro'y):")
        bot.register_next_step_handler(msg, search_music)
    
    elif message.text == "🎵 Musiqa ajratish":
        msg = bot.send_message(message.chat.id, "Video linkini yuboring, men musiqasini olib beraman:")
        bot.register_next_step_handler(msg, extract_audio)
    
    # Qolgan tugmalar... (avvalgi koddagidek ishlayveradi)

# --- MUSIQA QIDIRISH FUNKSIYASI ---
def search_music(message):
    query = message.text
    wait = bot.reply_to(message, f"🔎 '{query}' qidirilmoqda...")
    
    # Renderda FFmpeg yo'qligi sababli eng sodda formatni tanlaymiz
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'musiqa_{message.chat.id}.%(ext)s',
        'default_search': 'ytsearch1',
        'noplaylist': True,
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)
            filename = ydl.prepare_filename(info['entries'][0])
            
            with open(filename, 'rb') as audio:
                bot.send_audio(message.chat.id, audio, caption=f"✅ Topildi: {query}")
            
            os.remove(filename) # Faylni o'chirish
    except Exception as e:
        bot.send_message(message.chat.id, "❌ Musiqa topilmadi yoki yuklashda xato bo'ldi.")
    
    bot.delete_message(message.chat.id, wait.message_id)

# --- MUSIQA AJRATISH (LINKDAN) ---
def extract_audio(message):
    url = message.text
    wait = bot.reply_to(message, "🎵 Musiqa olinmoqda...")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'audio_{message.chat.id}.%(ext)s',
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            with open(filename, 'rb') as audio:
                bot.send_audio(message.chat.id, audio, caption="✅ Musiqa ajratib olindi!")
            
            os.remove(filename)
    except:
        bot.send_message(message.chat.id, "❌ Linkda xatolik!")
    
    bot.delete_message(message.chat.id, wait.message_id)

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
