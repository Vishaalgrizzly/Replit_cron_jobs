import requests
from bs4 import BeautifulSoup
from datetime import datetime

# --- HARDCODED CONFIGURATION (FOR TESTING ONLY) ---
# Replace the text inside the quotes with your actual details
BOT_TOKEN = "8339447368:AAHnRmvZyhV7nvKZ1ZtlX_7Xy3ZHETk2VQU" 
CHAT_ID = "781969503"
URL = "https://englishjobs.fr/jobs/marketing"

def send_telegram(message):
    print(f"Attempting to send to {CHAT_ID}...")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    
    try:
        r = requests.post(url, json=payload, timeout=10)
        print(f"Telegram Response: {r.status_code}")
        print(r.text)
    except Exception as e:
        print(f"Telegram Failed: {e}")

def main():
    print("--- STARTING HARDCODED TEST ---")
    
    # 1. TEST TELEGRAM
    send_telegram("🚀 **Bot Test**: If you read this, the Secrets were the problem.")

    # 2. TEST WEBSITE
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    print(f"Checking {URL}...")
    r = requests.get(URL, headers=headers)
    
    if r.status_code != 200:
        print(f"❌ Website Error: {r.status_code}")
        send_telegram(f"❌ Website returned Error {r.status_code}")
        return

    soup = BeautifulSoup(r.text, "html.parser")
    jobs = soup.select("a[href^='/job/']")
    
    print(f"✅ Found {len(jobs)} jobs on the page.")
    send_telegram(f"✅ Website Connection Success! Found {len(jobs)} jobs.")

if __name__ == "__main__":
    main()
