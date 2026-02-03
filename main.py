import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import time

# --- CONFIGURATION ---
# UPDATED: A Dictionary of "Role Name" -> "URL"
# You can add as many as you want here!
SEARCH_URLS = {
    "Marketing": "https://englishjobs.fr/jobs/marketing",
    "Content_Marketer": "https://englishjobs.fr/jobs/Content_Marketer",
    "Content_Marketing": "https://englishjobs.fr/jobs/content_marketing",
    "Community_Manager": "https://englishjobs.fr/jobs/community_manager", 
    "DM_Manager": "https://englishjobs.fr/jobs/digital_marketing_manager", 
    "Content_Marketing_Specialist": "https://englishjobs.fr/jobs/Content_Marketing_Specialist",  
    "Content_Marketing_Manager": "https://englishjobs.fr/jobs/Content_Marketing_Manager",  
    "Growth_Marketer": "https://englishjobs.fr/jobs/Growth_Marketer",
    "Product_Marketing_Manager": "https://englishjobs.fr/jobs/Product_Marketing_Manager",
    # Uncomment to add more
}

STATE_FILE = "seen_jobs.json"
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send_telegram(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("Error: Bot token or Chat ID missing.")
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

def fetch_jobs(category_name, url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        print(f"Checking {category_name} jobs...")
        r = requests.get(url, headers=headers, timeout=20)
        
        if r.status_code != 200:
            print(f"Failed to load {category_name}. Status: {r.status_code}")
            return []

        soup = BeautifulSoup(r.text, "html.parser")
        jobs = []
        
        for job in soup.find_all("a", href=True):
            if "/job/" in job["href"]:
                title = job.get_text(strip=True)
                if job["href"].startswith("http"):
                    link = job["href"]
                else:
                    link = "https://englishjobs.fr" + job["href"]
                
                job_id = link 
                
                # Check for duplicates in current batch
                if not any(j[0] == job_id for j in jobs):
                    jobs.append((job_id, title, link))
            
        print(f"Found {len(jobs)} jobs in {category_name}.")
        return jobs

    except Exception as e:
        print(f"Error fetching {category_name}: {e}")
        return []

def main():
    print(f"--- MULTI-TRACKER RUN AT {datetime.now()} ---")
    seen_jobs = load_seen_jobs()
    
    total_new = 0
    
    # LOOP: Check every category in our list
    for category, url in SEARCH_URLS.items():
        jobs = fetch_jobs(category, url)
        
        for job_id, title, link in jobs:
            if job_id not in seen_jobs:
                seen_jobs.add(job_id)
                # Customized Alert with Category Name
                send_telegram(
                    f"🎯 <b>New {category} Job</b>\n\n"
                    f"<b>{title}</b>\n"
                    f"<a href='{link}'>View job</a>\n\n"
                    f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )
                total_new += 1
        
        # Sleep for 2 seconds between requests to be polite to the server
        time.sleep(2)

    if total_new > 0:
        print(f"Sent alerts for {total_new} new jobs.")
        save_seen_jobs(seen_jobs)
    else:
        print("No new jobs found in any category.")

if __name__ == "__main__":
    main()
