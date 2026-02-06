import telebot
from telebot import types
import sqlite3

TOKEN = "8480701056:AAHVEdU3qKMl3PCyomK49Aqzp07SiOUrNP8"  # Твой рабочий TOKEN
bot = telebot.TeleBot(TOKEN)

# БД — создаётся автоматически
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users 
             (chat_id INTEGER PRIMARY KEY, name TEXT, phone TEXT)''')
conn.commit()
print("✅ БД готова!")

# Кто первый раз
first_time_users = set()  

def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🍕 Пицца", "🥗 Салаты")
    kb.row("📦 Корзина", "❌ Выход")
    return kb

def phone_keyboard():
    kb = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    kb.add(types.KeyboardButton("📱 Поделиться телефоном", request_contact=True))
    return kb

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    # Проверяем БД
    c.execute("SELECT * FROM users WHERE chat_id=?", (chat_id,))
    if not c.fetchone():
        bot.send_message(chat_id, "👋 Привет! Введите имя:")
        bot.register_next_step_handler(message, get_name)
    else:
        bot.send_message(chat_id, "🍕 Меню:", reply_markup=main_menu())

def get_name(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, f"Привет, {message.text}!\n📱 Телефон:", reply_markup=phone_keyboard())
    bot.register_next_step_handler(message, get_phone)

def get_phone(message):
    chat_id = message.chat.id
    name = message.reply_to_message.text.split('Привет, ')[-1].split('!')[0] if message.reply_to_message else "Клиент"
    phone = message.contact.phone_number if message.contact else message.text
    
    # Сохраняем в БД НАВСЕГДА
    c.execute("INSERT OR REPLACE INTO users VALUES (?,?,?)", (chat_id, name, phone))
    conn.commit()
    
    bot.send_message(chat_id, f"✅ {name}\n📱 {phone}\n🍕 Меню:", reply_markup=main_menu())

@bot.message_handler(func=lambda m: True)
def menu(message):
    bot.send_message(message.chat.id, "🍕 Выберите:", reply_markup=main_menu())

print("🚀 Бот + БД!")
bot.infinity_polling()