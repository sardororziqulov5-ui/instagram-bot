import telebot
import os
import yt_dlp
from telebot import types
from flask import Flask
from threading import Thread

# --- RENDER UCHUN WEB SERVER (O'CHIB QOLMASLIGI UCHUN) ---
app = Flask('')

@app.route('/')
def home():
    return "Azat Bey Bot is Live!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- ASOSIY MA'LUMOTLAR ---
TOKEN = '8764022556:AAGblrMJUH3gkAdwJUgiJOmoZQTwtc4v5uo'
REQUIRED_CHANNEL = '@bass_music_33'
PROG_CHANNEL_URL = 'https://t.me/kompyuter_dasturi_001'

bot = telebot.TeleBot(TOKEN)

# --- DOIMIY TUGMA (REPLY KEYBOARD) ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton("💻 Kompyuter dasturlari")
    markup.add(btn)
    return markup

# --- OBUNANI TEKSHIRISH FUNKSIYASI ---
def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(REQUIRED_CHANNEL, user_id).status
        return status in ['member', 'administrator', 'creator']
    except:
        return False

# --- BUYRUQLAR VA XABARLAR ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if is_subscribed(message.from_user.id):
        bot.send_message(
            message.chat.id, 
            f"Salom {message.from_user.first_name}! Botga xush kelibsiz.\nLink yuboring, videoni yuklab beraman.", 
            reply_markup=main_menu()
        )
    else:
        markup = types.InlineKeyboardMarkup()
        btn_sub = types.InlineKeyboardButton("A'zo bo'lish 📢", url=f"https://t.me/{REQUIRED_CHANNEL[1:]}")
        btn_check = types.InlineKeyboardButton("Tekshirish ✅", callback_data="check_sub")
        markup.add(btn_sub)
        markup.add(btn_check)
        bot.send_message(message.chat.id, "Botdan foydalanish uchun kanalga a'zo bo'ling!", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "💻 Kompyuter dasturlari")
def prog_link(message):
    bot.send_message(message.chat.id, f"Guruhimizga qo'shiling: {PROG_CHANNEL_URL}")

@bot.message_handler(func=lambda m: any(link in m.text for link in ["instagram.com", "tiktok.com", "youtube.com", "youtu.be"]))
def handle_video(message):
    if not is_subscribed(message.from_user.id):
        bot.reply_to(message, "Avval kanalga a'zo bo'ling!")
        return

    wait = bot.reply_to(message, "Yuklanmoqda, kuting... 📥")
    file_path = f"video_{message.chat.id}.mp4"
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': file_path,
        'quiet': True,
        'no_warnings': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([message.text])
        
        with open(file_path, 'rb') as video:
            bot.send_video(message.chat.id, video, caption="✅ Azat Bey bot orqali yuklandi")
        
        os.remove(file_path)
        bot.delete_message(message.chat.id, wait.message_id)
    except Exception as e:
        bot.edit_message_text("❌ Xatolik! Link noto'g'ri yoki video hajmi juda katta.", message.chat.id, wait.message_id)
        if os.path.exists(file_path): os.remove(file_path)

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_callback(call):
    if is_subscribed(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "Rahmat! Endi botdan foydalanishingiz mumkin.", reply_markup=main_menu())
    else:
        bot.answer_callback_query(call.id, "Hali a'zo bo'lmadingiz! ❌", show_alert=True)

# --- ISHGA TUSHIRISH ---
if __name__ == "__main__":
    keep_alive()
    print("Bot 24/7 rejimda ishga tushdi!")
    bot.infinity_polling()
