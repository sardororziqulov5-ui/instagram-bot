import telebot

TOKEN = "8706039149:AAHnsjBVDizdUrlxQ-j4ZBB2EFbYgskRKcM"
CHANNEL = "@kanal_username"  # majburiy obuna kanaling

bot = telebot.TeleBot(TOKEN)

# Tekshirish funksiyasi
def check_sub(user_id):
    try:
        member = bot.get_chat_member(CHANNEL, user_id)
        return member.status in ["member", "creator", "administrator"]
    except:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    if not check_sub(message.from_user.id):
        btn = telebot.types.InlineKeyboardMarkup()
        btn.add(telebot.types.InlineKeyboardButton("📢 Kanalga obuna", url=f"https://t.me/{CHANNEL[1:]}"))
        btn.add(telebot.types.InlineKeyboardButton("✅ Tekshirish", callback_data="check"))
        
        bot.send_message(message.chat.id, "❗ Botdan foydalanish uchun kanalga obuna bo‘ling", reply_markup=btn)
    else:
        menu(message)

def menu(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📥 Video yuklash", "🎵 MP3 yuklash")
    markup.add("ℹ️ Yordam")
    bot.send_message(message.chat.id, "Tanlang:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "check":
        if check_sub(call.from_user.id):
            bot.send_message(call.message.chat.id, "✅ Obuna tasdiqlandi!")
            menu(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ Hali obuna bo‘lmagansiz!")

@bot.message_handler(func=lambda message: True)
def handle(message):
    if not check_sub(message.from_user.id):
        start(message)
        return
    
    if message.text == "📥 Video yuklash":
        bot.send_message(message.chat.id, "📎 Instagram link yubor")
    
    elif message.text == "🎵 MP3 yuklash":
        bot.send_message(message.chat.id, "🎧 Instagram link yubor (MP3 uchun)")
    
    elif message.text == "ℹ️ Yordam":
        bot.send_message(message.chat.id, "1. Link yubor\n2. Tugmani bos\n3. Tayyor 😎")

print("Bot ishlayapti...")
bot.infinity_polling(timeout=60, long_polling_timeout=60)
