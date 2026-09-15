import requests
import time
import sys
import os
import json
import uuid

# Konfigurasi File
PROGRESS_FILE = "selesai.json"
CONFIG_FILE = "config.json"

# Ambil rahasia dari GitHub Secrets
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
# Batas episode per run agar tidak timeout di Github (Maks 3-4 jam)
MAX_EPISODES_PER_RUN = 180  

def load_json(filename):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def send_tg_msg(text):
    """Fungsi mengirim pesan ke Telegram"""
    if not BOT_TOKEN or not CHAT_ID: return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload)
    except:
        pass

def check_tg_updates():
    """Mengecek apakah ada perintah /setcookie baru dari Telegram"""
    if not BOT_TOKEN: return
    config = load_json(CONFIG_FILE)
    offset = config.get("last_update_id", 0) + 1
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={offset}&timeout=5"
    
    try:
        res = requests.get(url).json()
        if res.get("ok") and res.get("result"):
            for update in res["result"]:
                update_id = update["update_id"]
                config["last_update_id"] = update_id
                
                message = update.get("message", {}).get("text", "")
                if message.startswith("/setcookie "):
                    new_cookie = message.replace("/setcookie ", "").strip()
                    config["cookie"] = new_cookie
                    save_json(CONFIG_FILE, config)
                    send_tg_msg("✅ <b>Cookie berhasil diupdate dari Telegram!</b>\nMelanjutkan proses menonton...")
                    return new_cookie # Mengembalikan cookie baru
            save_json(CONFIG_FILE, config)
    except:
        pass
    return config.get("cookie", "")

def main():
    print("🎬 MULAI DRAMA WATCHER (GITHUB ACTIONS + TELEGRAM MODE) 🎬")
    
    # 1. Cek pesan Telegram terlebih dahulu, siapa tahu ada cookie baru
    user_cookie = check_tg_updates()
    
    if not user_cookie:
        send_tg_msg("⚠️ <b>Script berjalan tapi Cookie kosong!</b>\nSilakan kirim:\n<code>/setcookie isi_cookie_kamu_disini</code>")
        sys.exit(0)
        
    headers = {
        'User-Agent': "Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36 Chrome/152.0.0.0 Mobile Safari/537.36",
        'Cookie': user_cookie,
        'Content-Type': "application/json"
    }
    
    device_id = str(uuid.uuid4())
    
    # Cek Autentikasi
    try:
        auth_res = requests.get("https://drama.center/api/auth/me", headers=headers).json()
        if not auth_res.get("success"):
            send_tg_msg("❌ <b>Authentication Failed! Cookie Expired.</b>\nScript dihentikan.\nSilakan balas dengan perintah:\n<code>/setcookie [cookie_baru]</code>")
            sys.exit(0)
            
        user_info = auth_res.get("user", {})
        account_id = user_info.get("id")
        send_tg_msg(f"🚀 <b>Bot Mulai Berjalan!</b>\n🆔 Account ID: <code>{account_id}</code>")
    except Exception as e:
        print(f"Auth Error: {e}")
        sys.exit(0)

    all_progress = load_json(PROGRESS_FILE)
    if account_id not in all_progress:
        all_progress[account_id] = {}
    account_progress = all_progress[account_id]

    try:
        res = requests.get("https://drama.center/api/dramas?sort=popular&limit=1000&language=en", headers=headers)
        dramas_data = res.json().get('data', [])
    except:
        sys.exit(0)

    processed_count = 0

    for d_idx, drama in enumerate(dramas_data, start=1):
        drama_id = drama['id']
        drama_title = drama.get('title', 'Unknown Title')
        
        if drama_id in account_progress and account_progress[drama_id].get('completed'):
            continue

        episodes = requests.get(f"https://drama.center/api/dramas/{drama_id}", headers=headers).json().get('data', {}).get('episodes', [])
        if not episodes: continue

        total_episodes = len(episodes)
        last_saved_ep = account_progress.get(drama_id, {}).get('last_episode', 0)

        for ep_idx in range(last_saved_ep, total_episodes):
            if processed_count >= MAX_EPISODES_PER_RUN:
                send_tg_msg("🛑 <b>Batas Sesi Github Tercapai.</b>\nProgress disimpan. Akan dilanjutkan otomatis di jadwal berikutnya.")
                sys.exit(0)

            ep = episodes[ep_idx]
            ep_number = ep_idx + 1

            tick_url = f"https://drama.center/api/dramas/{drama_id}/episodes/watch-tick"
            tick_res = requests.post(tick_url, headers=headers, json={"episodeId": ep['id'], "deviceId": device_id}).json()
            tick_data = tick_res.get('data', {})

            credited = tick_data.get('credited', 0)
            reject_reason = tick_data.get('rejectReason')
            should_delay = False

            if credited > 0:
                collect_res = requests.post("https://drama.center/api/watch-reward/collect", headers=headers, json={}).json()
                collected = collect_res.get('data', {}).get('collected', 0)
                
                # Kirim log ke Telegram
                log_msg = (f"🎬 <b>{drama_title}</b> [{ep_number}/{total_episodes}]\n"
                           f"✅ <b>Credited:</b> {credited} 💰\n"
                           f"💎 <b>Collected:</b> {collected}")
                send_tg_msg(log_msg)
                
                should_delay = True
                processed_count += 1
            else:
                if reject_reason != "episode_maxed":
                    print(f"Reject: {reject_reason}")

            # Simpan progress setiap 1 episode
            account_progress[drama_id] = {
                "title": drama_title,
                "last_episode": ep_number,
                "total_episodes": total_episodes,
                "completed": (ep_number == total_episodes)
            }
            all_progress[account_id] = account_progress
            save_json(PROGRESS_FILE, all_progress)

            if reject_reason == "episode_maxed":
                continue
            elif should_delay:
                # Waktu delay dimanfaatkan untuk cek chat TG (barangkali cookie diupdate ditengah jalan)
                for _ in range(60):
                    time.sleep(1)
                    if _ % 15 == 0: # Cek update setiap 15 detik
                        new_cookie = check_tg_updates()
                        if new_cookie and new_cookie != user_cookie:
                            user_cookie = new_cookie
                            headers['Cookie'] = user_cookie # Update header real-time

        if account_progress[drama_id].get('completed'):
            send_tg_msg(f"🎉 <b>Drama Selesai!</b>\n{drama_title}")

if __name__ == "__main__":
    main()
