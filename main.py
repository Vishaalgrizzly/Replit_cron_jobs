import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

# --- CONFIGURATION ---
# UPDATED: Now targeting only Marketing jobs
URL = "https://englishjobs.fr/jobs/marketing"
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
        requests.post(url, json=payload)
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

def fetch_jobs():
    try:
        # User-Agent header to look like a real browser (prevents blocking)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        print(f"Checking specific category: {URL}...")
        r = requests.get(URL, headers=headers, timeout=20)
        
        if r.status_code != 200:
            print(f"Failed to load page. Status: {r.status_code}")
            return []

        soup = BeautifulSoup(r.text, "html.parser")
        jobs = []
        
        # Scrape all job links
        for job in soup.select("a[href^='/job/']"):
            title = job.get_text(strip=True)
            link = "https://englishjobs.fr" + job["href"]
            job_id = job["href"]
            jobs.append((job_id, title, link))
            
        print(f"Found {len(jobs)} jobs on the page.")
        return jobs

    except Exception as e:
        print(f"Error fetching jobs: {e}")
        return []

def main():
    print(f"--- STARTING MARKETING JOB CHECK AT {datetime.now()} ---")
    seen_jobs = load_seen_jobs()
    jobs = fetch_jobs()
    
    new_jobs_found = 0
    for job_id, title, link in jobs:
        if job_id not in seen_jobs:
            seen_jobs.add(job_id)
            # Send Alert
            send_telegram(
                f"🎯 <b>New Marketing Job</b>\n\n"
                f"<b>{title}</b>\n"
                f"<a href='{link}'>View job</a>\n\n"
                f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            new_jobs_found += 1
            
    if new_jobs_found > 0:
        print(f"Sent alerts for {new_jobs_found} new jobs.")
        save_seen_jobs(seen_jobs)
    else:
        print("No new marketing jobs found since last run.")

if __name__ == "__main__":
    main()
