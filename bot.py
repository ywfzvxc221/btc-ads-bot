import telebot
import json
import os
import random

# قراءة البيانات الحساسة من متغيرات البيئة
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
PAYMENT_INFO = {
    "faucetpay": os.getenv("FAUCETPAY_ADDRESS"),
    "binance": os.getenv("BINANCE_ADDRESS")
}

bot = telebot.TeleBot(TOKEN)

# إنشاء ملف المستخدمين إذا لم يكن موجود
if not os.path.exists("users.json"):
    with open("users.json", "w") as f:
        json.dump({}, f)

with open("users.json", "r") as f:
    users = json.load(f)

def save_users():
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

# خطط الاشتراك
subscriptions = {
    10: {"daily": 15, "price": 0.2},
    20: {"daily": 25, "price": 0.5},
    30: {"daily": 40, "price": 0.8},
    50: {"daily": 60, "price": 1.0},
    100: {"daily": 9999, "price": 1.5}
}

# ردود مثال
female_replies = [
    "هلا فيك، كيف يومك؟", "وش تحب تسوي بوقت فراغك؟", "أنا مهتمة أتعرف عليك أكثر.",
    "وش أكثر شي يفرحك؟", "هل تحب السفر؟", "تحب تسمع موسيقى؟"
]
male_replies = [
    "أهلاً، كيف حالك؟", "وش اهتماماتك؟", "تحب تتكلم عن أفلام أو ألعاب؟",
    "أنا موجود لأي سؤال!", "تحب تطور نفسك؟", "وش طموحك بالحياة؟"
]

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    if user_id not in users:
        users[user_id] = {
            "points": 0,
            "free_chats": 10,
            "gender": None,
            "subscription": 0,
            "daily_limit": 0,
            "used_today": 0,
            "referrals": []
        }
        save_users()
    bot.send_message(message.chat.id, "مرحباً بك في بوت المحادثة المميزة!\nاختر جنسك لبدء المحادثة:",
                     reply_markup=gender_keyboard())

def gender_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("ذكر", "أنثى")
    return markup

@bot.message_handler(func=lambda msg: msg.text in ["ذكر", "أنثى"])
def set_gender(message):
    user_id = str(message.from_user.id)
    users[user_id]["gender"] = message.text
    save_users()
    bot.send_message(message.chat.id, f"تم تعيين جنسك: {message.text}. يمكنك إرسال الرسائل الآن.")

@bot.message_handler(commands=['buy'])
def show_payment(message):
    reply = "لشراء النقاط:\n"
    for pts, sub in subscriptions.items():
        reply += f"{pts} نقطة = {sub['price']} دولار / شهر\n"
    reply += f"\nFaucetPay: {PAYMENT_INFO['faucetpay']}\n"
    reply += f"Binance: {PAYMENT_INFO['binance']}\n"
    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=['stats'])
def show_stats(message):
    user_id = str(message.from_user.id)
    user = users.get(user_id, {})
    reply = f"نقاطك: {user.get('points', 0)}\n"
    reply += f"محادثات مجانية متبقية: {user.get('free_chats', 0)}\n"
    reply += f"اشتراكك: {user.get('subscription', 0)} نقطة\n"
    bot.send_message(message.chat.id, reply)

@bot.message_handler(func=lambda msg: True)
def chat_handler(message):
    user_id = str(message.from_user.id)
    user = users.get(user_id)
    if not user or not user.get("gender"):
        bot.send_message(message.chat.id, "اختر جنسك أولاً:", reply_markup=gender_keyboard())
        return

    if user["free_chats"] > 0:
        user["free_chats"] -= 1
        reply = get_reply(user["gender"])
        bot.send_message(message.chat.id, reply)
    elif user["subscription"] > 0:
        plan = subscriptions.get(user["subscription"], {})
        if user["used_today"] < plan.get("daily", 0):
            user["used_today"] += 1
            reply = get_reply(user["gender"])
            bot.send_message(message.chat.id, reply)
        else:
            bot.send_message(message.chat.id, "لقد استخدمت عدد الرسائل اليومي المسموح به في اشتراكك.")
    else:
        bot.send_message(message.chat.id, "انتهت محادثاتك المجانية، اشترِ اشتراكًا أو نقاطًا للاستمرار.")

    save_users()

def get_reply(gender):
    return random.choice(female_replies if gender == "أنثى" else male_replies)

bot.infinity_polling()
