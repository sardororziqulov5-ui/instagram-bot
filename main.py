import telebot
import os
import yt_dlp
import requests
from telebot import types
from flask import Flask
from threading import Thread
from g4f.client import Client # Bepul GPT uchun

# --- SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Sardor ai's Free AI Bot is Live!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- SOZLAMALAR ---
TOKEN = '8764022556:AAGblrMJUH3gkAdwJUgiJOmoZQTwtc4v5uo'
bot = telebot.TeleBot(TOKEN)
client = Client()

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🎨 Rasm yaratish", "🤖 AI bilan suhbat")
    markup.row("🔍 Musiqa qidirish", "💻 Kompyuter dasturlari")
    return markup

# --- 1. BEPUL AI SUHBATDOSH ---
@bot.message_handler(func=lambda m: m.text == "🤖 AI bilan suhbat")
def ai_mode(message):
    bot.reply_to(message, "Savolingizni yozing, men AI orqali javob beraman! 🧠")

# --- 2. BEPUL RASM YARATISH (Pollinations API) ---
@bot.message_handler(func=lambda m: m.text == "🎨 Rasm yaratish")
def image_mode(message):
    msg = bot.send_message(message.chat.id, "Nima rasmini chizay? (Masalan: Nano banana) 🍌")
    bot.register_next_step_handler(msg, generate_free_image)

def generate_free_image(message):
    prompt = message.text.replace(" ", "%20")
    wait = bot.reply_to(message, "Rasm chizilmoqda... ✨")
    # Bepul rasm yaratish API
    img_url = f"https://pollinations.ai/p/{prompt}?width=1024&height=1024&seed=42&model=flux"
    
    try:
        bot.send_photo(message.chat.id, img_url, caption=f"✅ Natija: {message.text}")
    except:
        bot.send_message(message.chat.id, "❌ Rasm yaratishda xatolik bo'ldi.")
    bot.delete_message(message.chat.id, wait.message_id)

# --- MEDIA VA CHAT ---
@bot.message_handler(content_types=['text', 'video', 'video_note'])
def handle_all(message):
    if message.text:
        # Link bo'lsa video/audio yuklash
        if any(x in message.text for x in ["instagram.com", "tiktok.com", "youtube.com", "youtu.be"]):
            wait = bot.reply_to(message, "Yuklanmoqda... 📥")
            is_mp3 = "mp3" in message.text.lower()
            file_path = f"f_{message.chat.id}.{'mp3' if is_mp3 else 'mp4'}"
            ydl_opts = {'format': 'bestaudio/best' if is_mp3 else 'best', 'outtmpl': file_path, 'quiet': True}
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl: ydl.download([message.text])
                with open(file_path, 'rb') as f:
                    if is_mp3: bot.send_audio(message.chat.id, f)
                    else: bot.send_video(message.chat.id, f)
                os.remove(file_path)
            except: bot.send_message(message.chat.id, "Xato!")
            bot.delete_message(message.chat.id, wait.message_id)
        
        # Shunchaki matn bo'lsa - Bepul GPT javob beradi
        else:
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": message.text}],
                )
                bot.reply_to(message, response.choices[0].message.content)
            except:
                bot.reply_to(message, "AI hozir biroz band, keyinroq urinib ko'ring.")

    # Aylana video funksiyalari (avvalgidek qoladi)
    elif message.content_type == 'video_note':
        file_info = bot.get_file(message.video_note.file_id)
        bot.send_video(message.chat.id, bot.download_file(file_info.file_path))
    elif message.content_type == 'video':
        file_info = bot.get_file(message.video.file_id)
        bot.send_video_note(message.chat.id, bot.download_file(file_info.file_path))

# --- START ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Salom Sardor! Bepul AI Bot tayyor. 🚀", reply_markup=main_menu())

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
