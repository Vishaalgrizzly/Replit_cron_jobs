import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

# --- CONFIGURATION ---
URL = "https://englishjobs.fr/jobs/marketing"
STATE_FILE = "seen_jobs.json"

# We will fetch these from GitHub Secrets (Safe way)
BOT_TOKEN = os.environ.get("8339447368:AAHnRmvZyhV7nvKZ1ZtlX_7Xy3ZHETk2VQU")
CHAT_ID = os.environ.get("781969503")

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
        headers = {"User-Agent": "Mozilla/5.0 (JobAlertBot)"}
        r = requests.get(URL, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        jobs = []
        for job in soup.select("a[href^='/job/']"):
            title = job.get_text(strip=True)
            link = "https://englishjobs.fr" + job["href"]
            job_id = job["href"]
            jobs.append((job_id, title, link))
        return jobs
    except Exception as e:
        print(f"Error fetching jobs: {e}")
        return []

def main():
    print(f"Checking jobs at {datetime.now()}...")
    seen_jobs = load_seen_jobs()
    jobs = fetch_jobs()
    
    new_jobs_found = 0
    for job_id, title, link in jobs:
        if job_id not in seen_jobs:
            seen_jobs.add(job_id)
            send_telegram(
                f"🚨 <b>New English Job</b>\n\n"
                f"<b>{title}</b>\n"
                f"<a href='{link}'>View job</a>\n\n"
                f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            new_jobs_found += 1
            
    if new_jobs_found > 0:
        print(f"Found {new_jobs_found} new jobs.")
        save_seen_jobs(seen_jobs)
    else:
        print("No new jobs found.")

if __name__ == "__main__":
    main()
