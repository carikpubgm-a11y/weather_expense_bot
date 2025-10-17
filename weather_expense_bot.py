# pyTelegramBotAPI
# requests
# sqlite3

import telebot
import requests
import sqlite3
import os
from datetime import datetime

# API kalitlari
BOT_TOKEN = '7751259919:AAGa5RZwpiXui__QatfTLWsCvRqPYB97xug'
WEATHER_API_KEY = 'befce02507aa1d5e444397c8a386be8b'

bot = telebot.TeleBot(BOT_TOKEN)

# ------------------ DATABASE ------------------
def setup_database():
    db_path = os.path.join(os.path.dirname(__file__), 'bot_database.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS expenses
                 (user_id INTEGER, amount REAL, category TEXT, date TEXT)''')
    conn.commit()
    conn.close()
    return db_path


# ------------------ MENYU ------------------
def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('🌤 Ob-havo', '💰 Harajatlar')
    markup.row('💱 Valyuta kurslari', '🚪 Chiqish')
    return markup


def weather_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    regions = ['Toshkent', 'Samarqand', 'Buxoro', 'Andijon', 'Namangan', 'Farg‘ona', 'Jizzax', 'Navoiy', 'Surxondaryo', 'Xorazm', 'Qashqadaryo', 'Sirdaryo', 'Qoraqalpog‘iston']
    for i in range(0, len(regions), 2):
        markup.row(*regions[i:i + 2])
    markup.row('🔙 Orqaga')
    return markup


def expense_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('🍞 Oziq-ovqat', '🚗 Mashina')
    markup.row('🏠 Ehtiyoj', '💼 Boshqalar')
    markup.row('📋 Harajatlar ro‘yxati', '🔙 Orqaga')
    return markup


def currency_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('USD', 'EUR', 'RUB')
    markup.row('🔙 Orqaga')
    return markup


# ------------------ START ------------------
@bot.message_handler(commands=['start'])
def start(message):
    setup_database()
    bot.send_message(message.chat.id, "👋 Assalomu alaykum!\nSmartLife botiga xush kelibsiz!", reply_markup=main_menu())


# ------------------ OB-HAVO ------------------
@bot.message_handler(func=lambda m: m.text == '🌤 Ob-havo')
def weather_start(message):
    bot.send_message(message.chat.id, "Viloyatni tanlang:", reply_markup=weather_menu())


@bot.message_handler(func=lambda m: m.text in ['Toshkent', 'Samarqand', 'Buxoro', 'Andijon', 'Namangan', 'Farg‘ona', 'Jizzax', 'Navoiy', 'Surxondaryo', 'Xorazm', 'Qashqadaryo', 'Sirdaryo', 'Qoraqalpog‘iston'])
def show_weather(message):
    city = message.text
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city},UZ&appid={WEATHER_API_KEY}&units=metric&lang=uz"
        res = requests.get(url)
        data = res.json()

        temp = data['main']['temp']
        feels = data['main']['feels_like']
        desc = data['weather'][0]['description']
        humidity = data['main']['humidity']
        wind = data['wind']['speed']

        text = f"""🌤 <b>{city}</b> shahri:
🌡 Harorat: {temp}°C
🤔 His qilinadigan: {feels}°C
💧 Namlik: {humidity}%
💨 Shamol: {wind} m/s
🌈 Holat: {desc.capitalize()}"""

        bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=main_menu())
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Xatolik: ob-havo ma'lumotini olishda muammo yuz berdi.", reply_markup=main_menu())


# ------------------ HARAJATLAR ------------------
@bot.message_handler(func=lambda m: m.text == '💰 Harajatlar')
def expense_start(message):
    bot.send_message(message.chat.id, "Harajatlar bo‘limi:", reply_markup=expense_menu())


@bot.message_handler(func=lambda m: m.text in ['🍞 Oziq-ovqat', '🚗 Mashina', '🏠 Ehtiyoj', '💼 Boshqalar'])
def add_expense(message):
    category = message.text
    msg = bot.send_message(message.chat.id, f"{category} uchun sarflangan summani kiriting (masalan: 150000):")
    bot.register_next_step_handler(msg, save_expense, category)


def save_expense(message, category):
    try:
        amount = float(message.text)
        db_path = setup_database()
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("INSERT INTO expenses VALUES (?, ?, ?, ?)", (message.from_user.id, amount, category, datetime.now().strftime('%Y-%m-%d')))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, "✅ Harajat muvaffaqiyatli saqlandi!", reply_markup=main_menu())
    except:
        bot.send_message(message.chat.id, "⚠️ Noto‘g‘ri qiymat! Qaytadan urinib ko‘ring.", reply_markup=main_menu())


@bot.message_handler(func=lambda m: m.text == '📋 Harajatlar ro‘yxati')
def show_expenses(message):
    db_path = setup_database()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT category, SUM(amount) FROM expenses WHERE user_id=? GROUP BY category", (message.from_user.id,))
    rows = c.fetchall()
    conn.close()

    if rows:
        text = "📊 <b>Harajatlaringiz:</b>\n\n"
        for row in rows:
            text += f"{row[0]}: {row[1]:,.0f} so‘m\n"
    else:
        text = "ℹ️ Sizda hali harajatlar yo‘q."

    bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=main_menu())


# ------------------ VALYUTA ------------------
@bot.message_handler(func=lambda m: m.text == '💱 Valyuta kurslari')
def currency_start(message):
    bot.send_message(message.chat.id, "Valyutani tanlang:", reply_markup=currency_menu())


@bot.message_handler(func=lambda m: m.text in ['USD', 'EUR', 'RUB'])
def show_currency(message):
    try:
        res = requests.get("https://cbu.uz/oz/arkhiv-kursov-valyut/json/")
        data = res.json()

        rates = {item['Ccy']: float(item['Rate']) for item in data}
        code = message.text
        if code in rates:
            bot.send_message(message.chat.id, f"💱 1 {code} = {rates[code]:,.2f} so‘m", reply_markup=main_menu())
        else:
            bot.send_message(message.chat.id, "❌ Ma’lumot topilmadi.", reply_markup=main_menu())
    except Exception:
        bot.send_message(message.chat.id, "❌ Valyuta kursini olishda xatolik.", reply_markup=main_menu())


# ------------------ CHIQISH ------------------
@bot.message_handler(func=lambda m: m.text == '🚪 Chiqish')
def exit_bot(message):
    bot.send_message(message.chat.id, "👋 Botdan chiqdingiz. Yana ko‘rishguncha!", reply_markup=telebot.types.ReplyKeyboardRemove())


# ------------------ ORQAGA ------------------
@bot.message_handler(func=lambda m: m.text == '🔙 Orqaga')
def go_back(message):
    bot.send_message(message.chat.id, "Asosiy menyu:", reply_markup=main_menu())


# ------------------ DEFAULT ------------------
@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.send_message(message.chat.id, "Iltimos, menyudan tanlang:", reply_markup=main_menu())


# ------------------ RUN ------------------
if __name__ == "__main__":
    print("✅ Bot ishga tushdi...")
    setup_database()
    bot.polling(none_stop=True)
