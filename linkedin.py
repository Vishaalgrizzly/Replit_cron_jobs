import requests
from bs4 import BeautifulSoup
import json
import os
import time
import random
from datetime import datetime

# --- CONFIGURATION ---
LOCATIONS = ["France"]

# Comprehensive list of roles (targeted for English speakers)
KEYWORDS = [
    # --- Core Marketing & Strategy ---
    "Digital Marketer", 
    "Digital Marketing Manager", 
    "Digital Marketing Strategist",
    "Marketing Manager", 
    "International Marketing Manager", 
    "Global Marketing Manager",
    "EMEA Marketing Manager",  # EMEA roles are almost 100% English
    "Brand Manager", 
    "Brand Communications Manager",
    
    # --- Content & Creative ---
    "Content Marketer", 
    "Content Marketing Manager", 
    "Content Marketing Specialist", 
    "Content Strategist",
    "Head of Content",
    "English Content Writer",  # Explicit English
    "Technical Content Writer", 
    "Technical Writer",
    "Copywriter",
    "English Copywriter",      # Explicit English
    
    # --- Product & Growth ---
    "Product Marketing Manager", 
    "PMM",                     # Common abbreviation
    "Growth Marketer", 
    "Growth Marketing Manager", 
    "Growth Marketing Lead",
    "Demand Generation Manager",
    "Acquisition Manager",
    
    # --- Operations & Tech ---
    "Marketing Operations Manager", 
    "Marketing Operations Specialist",
    "Marketing Automation Specialist",
    
    # --- English Specific Variations ---
    "Marketing English",
    "Communication Officer English",
    "English Speaking Marketing",
    "Native English Marketing"
]
STATE_FILE = "seen_linkedin.json"

# Secrets
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send_telegram(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("Error: Secrets missing.")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Failed to send message: {e}")

def load_seen_jobs():
    if not os.path.exists(STATE_FILE):
        return set()
    try:
        with open(STATE_FILE, "r") as f:
            return set(json.load(f))
    except:
        return set()

def save_seen_jobs(jobs):
    with open(STATE_FILE, "w") as f:
        json.dump(list(jobs), f)

def scrape_linkedin():
    start_time = datetime.now().strftime('%H:%M')
    print(f"--- LINKEDIN RUN STARTED AT {start_time} ---")
    
    # Notify you that the long run has started
    send_telegram(
        f"⏳ **LinkedIn Scraper Started** at {start_time}\n"
        f"Checking {len(KEYWORDS)} roles in France.\n"
        f"Running slowly to avoid detection..."
    )

    seen_jobs = load_seen_jobs()
    new_jobs_count = 0
    checked_count = 0
    blocked = False

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    for loc in LOCATIONS:
        for keyword in KEYWORDS:
            if blocked: break
            
            print(f"Checking: {keyword} in {loc}...")
            checked_count += 1
            
            # Format URL
            fmt_keyword = keyword.replace(" ", "%20")
            url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={fmt_keyword}&location={loc}&start=0"
            
            try:
                # SUPER SAFE MODE: Sleep for 15 to 45 seconds between every search.
                # This makes the run take ~15 minutes, but guarantees safety.
                sleep_time = random.uniform(15, 45)
                time.sleep(sleep_time)
                
                r = requests.get(url, headers=headers, timeout=10)
                
                # Check for Blocks
                if r.status_code == 429 or r.status_code == 999:
                    print(f"⚠️ Blocked by LinkedIn (Status {r.status_code}).")
                    send_telegram(f"⚠️ **LinkedIn Blocked the Bot** (Error {r.status_code}).\nStopping run early.")
                    blocked = True
                    break 
                
                soup = BeautifulSoup(r.text, 'html.parser')
                job_cards = soup.find_all('li')
                
                for card in job_cards:
                    try:
                        link_tag = card.find('a', class_='base-card__full-link')
                        if not link_tag: continue
                        link = link_tag['href'].split('?')[0]
                        job_id = link
                        
                        if job_id in seen_jobs: continue
                        
                        title = card.find('h3', class_='base-search-card__title').text.strip()
                        company = card.find('h4', class_='base-search-card__subtitle').text.strip()
                        location = card.find('span', class_='job-search-card__location').text.strip()
                        date_tag = card.find('time')
                        date_posted = date_tag.text.strip() if date_tag else "Recently"
                        
                        # Send Alert
                        send_telegram(
                            f"🔵 <b>New LinkedIn Job</b>\n\n"
                            f"<b>{title}</b>\n"
                            f"🏢 {company}\n"
                            f"📍 {location} ({date_posted})\n"
                            f"<a href='{link}'>Apply on LinkedIn</a>"
                        )
                        seen_jobs.add(job_id)
                        new_jobs_count += 1
                        
                    except: continue

            except Exception as e:
                print(f"Connection Error: {e}")

    # Summary
    if new_jobs_count > 0:
        save_seen_jobs(seen_jobs)
        send_telegram(f"✅ **Run Complete**\nFound {new_jobs_count} new jobs.")
    elif not blocked:
        send_telegram(f"✅ **Run Complete**\nChecked {checked_count} searches.\nNo new jobs found.")

if __name__ == "__main__":
    scrape_linkedin()
