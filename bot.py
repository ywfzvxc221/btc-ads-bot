import telebot
import json
import os
import random
from datetime import datetime

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = os.environ.get("ADMIN_ID")
FAUCETPAY_EMAIL = os.environ.get("FAUCETPAY_EMAIL")
BINANCE_ADDRESS = os.environ.get("BINANCE_ADDRESS")

bot = telebot.TeleBot(TOKEN)

# تحميل أو إنشاء بيانات المستخدمين
if not os.path.exists("users.json"):
    with open("users.json", "w") as f:
        json.dump({}, f)

with open("users.json", "r") as f:
    users = json.load(f)

def save_users():
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

subscriptions = {
    10: {"daily": 15, "price": 0.2},
    20: {"daily": 25, "price": 0.5},
    30: {"daily": 40, "price": 0.8},
    50: {"daily": 60, "price": 1.0},
    100: {"daily": 9999, "price": 1.5}
}

female_replies = ["رد مميز لأنثى"]
male_replies = ["رد مميز لذكر"]

def gender_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("أنثى", "ذكر")
    return markup

def main_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("محادثة مجانية", "محادثة مدفوعة")
    markup.add("شراء نقاط", "إحصائياتي")
    markup.add("المكافأة اليومية", "رابط الإحالة")
    if ADMIN_ID:
        markup.add("نشر إعلان")  # يظهر فقط للأدمن
    return markup

@bot.message_handler(commands=["start"])
def start(message):
    user_id = str(message.from_user.id)
    args = message.text.split()
    referrer_id = args[1] if len(args) > 1 else None

    if user_id not in users:
        users[user_id] = {
            "points": 0,
            "free_chats": 10,
            "gender": None,
            "subscription": 0,
            "daily_limit": 0,
            "used_today": 0,
            "referrals": [],
            "last_claim": "",
        }
        if referrer_id and referrer_id in users:
            users[referrer_id]["points"] += 2
            users[referrer_id]["referrals"].append(user_id)
    save_users()
    bot.send_message(message.chat.id, "مرحباً بك! اختر جنسك:", reply_markup=gender_keyboard())

@bot.message_handler(func=lambda msg: msg.text in ["أنثى", "ذكر"])
def set_gender(message):
    user_id = str(message.from_user.id)
    users[user_id]["gender"] = message.text
    save_users()
    bot.send_message(message.chat.id, "تم الحفظ، يمكنك الآن استخدام البوت.", reply_markup=main_keyboard())

@bot.message_handler(func=lambda msg: msg.text == "شراء نقاط")
def buy_points(message):
    text = "خطط الاشتراك:\n"
    for k, v in subscriptions.items():
        text += f"{k} نقطة = {v['price']} دولار شهريًا\n"
    text += f"\nطرق الدفع:\nFaucetPay: {FAUCETPAY_EMAIL}\nBinance: {BINANCE_ADDRESS}"
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda msg: msg.text == "إحصائياتي")
def stats(message):
    user = users.get(str(message.from_user.id), {})
    text = f"""رصيدك: {user.get('points', 0)} نقطة
محادثات مجانية: {user.get('free_chats', 0)}
الجنس: {user.get('gender', 'غير محدد')}
الخطة الحالية: {user.get('subscription', 0)} نقطة
إحالاتك: {len(user.get('referrals', []))}
"""
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda msg: msg.text == "محادثة مجانية")
def free_chat(message):
    user_id = str(message.from_user.id)
    user = users[user_id]
    if user["free_chats"] > 0:
        user["free_chats"] -= 1
        save_users()
        reply = random.choice(female_replies if user["gender"] == "أنثى" else male_replies)
        bot.send_message(message.chat.id, reply)
    else:
        bot.send_message(message.chat.id, "انتهت محادثاتك المجانية.")

@bot.message_handler(func=lambda msg: msg.text == "محادثة مدفوعة")
def paid_chat(message):
    user_id = str(message.from_user.id)
    user = users[user_id]
    plan = subscriptions.get(user["subscription"])
    if plan and user["used_today"] < plan["daily"]:
        user["used_today"] += 1
        save_users()
        reply = random.choice(female_replies if user["gender"] == "أنثى" else male_replies)
        bot.send_message(message.chat.id, reply)
    else:
        bot.send_message(message.chat.id, "تجاوزت الحد اليومي للمحادثات المدفوعة.")

@bot.message_handler(func=lambda msg: msg.text == "المكافأة اليومية")
def daily_bonus(message):
    user_id = str(message.from_user.id)
    today = datetime.now().strftime("%Y-%m-%d")
    if users[user_id]["last_claim"] != today:
        users[user_id]["last_claim"] = today
        users[user_id]["points"] += 1
        save_users()
        bot.send_message(message.chat.id, "تم منحك 1 نقطة مكافأة يومية!")
    else:
        bot.send_message(message.chat.id, "لقد حصلت على مكافأتك اليومية بالفعل.")

@bot.message_handler(func=lambda msg: msg.text == "رابط الإحالة")
def referral_link(message):
    user_id = str(message.from_user.id)
    link = f"https://t.me/{bot.get_me().username}?start={user_id}"
    bot.send_message(message.chat.id, f"شارك هذا الرابط لدعوة أصدقائك وكسب نقاط:\n{link}")

@bot.message_handler(func=lambda msg: msg.text == "نشر إعلان" and str(message.from_user.id) == ADMIN_ID)
def post_ad(message):
    bot.send_message(message.chat.id, "أرسل الآن نص الإعلان الذي تريد نشره.")
    bot.register_next_step_handler(message, broadcast)

def broadcast(message):
    for uid in users:
        try:
            bot.send_message(uid, f"إعلان من الأدمن:\n{message.text}")
        except:
            continue

@bot.message_handler(func=lambda msg: True)
def fallback(message):
    bot.send_message(message.chat.id, "الرجاء استخدام الأزرار فقط.", reply_markup=main_keyboard())

bot.infinity_polling()
