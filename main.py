import requests
from bs4 import BeautifulSoup
import os

# --- CONFIGURATION ---
URL = "https://englishjobs.fr/jobs/marketing"
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send_telegram(message):
    print(f"DEBUG: Attempting to send Telegram message: {message}")
    if not BOT_TOKEN or not CHAT_ID:
        print("CRITICAL ERROR: Bot Token or Chat ID is missing from GitHub Secrets.")
        return
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    
    try:
        r = requests.post(url, json=payload, timeout=10)
        print(f"DEBUG: Telegram Response Code: {r.status_code}")
        print(f"DEBUG: Telegram Response Body: {r.text}")
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to connect to Telegram: {e}")

def main():
    print("--- DIAGNOSTIC RUN STARTED ---")
    
    # TEST 1: Check Connection to You
    send_telegram(f"⚠️ **Test Alert**\nIf you see this, your Bot Token and ID are correct.\nChecking website now...")

    # TEST 2: Check Website Connection
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        print(f"DEBUG: Fetching URL: {URL}")
        r = requests.get(URL, headers=headers, timeout=20)
        print(f"DEBUG: Website Status Code: {r.status_code}")
        
        if r.status_code == 403:
            print("CRITICAL FAILURE: The website is blocking GitHub (Error 403).")
            send_telegram("❌ **Failure**: The website blocked the bot (Error 403).")
            return

        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.title.string.strip() if soup.title else "No Title"
        print(f"DEBUG: Page Title: {title}")
        
        # TEST 3: Check for Links
        # We print the first 500 characters of HTML to see what we actually got
        print(f"DEBUG: Page HTML Snippet: {r.text[:500]}")
        
        job_links = soup.select("a[href^='/job/']")
        print(f"DEBUG: Found {len(job_links)} job links with selector a[href^='/job/']")
        
        if len(job_links) == 0:
            print("DEBUG: Trying fallback selector...")
            all_links = soup.find_all("a")
            print(f"DEBUG: Total 'a' tags found on page: {len(all_links)}")
            send_telegram(f"⚠️ **Warning**: Connected to site, but found 0 jobs. (Found {len(all_links)} total links).")
        else:
            send_telegram(f"✅ **Success**: Found {len(job_links)} jobs available to scrape.")

    except Exception as e:
        print(f"CRITICAL ERROR: Script crashed: {e}")
        send_telegram(f"❌ **Crash**: Script failed with error: {e}")

if __name__ == "__main__":
    main()
