import requests
from bs4 import BeautifulSoup
import json
import os
import time
from openai import OpenAI

# --- USER PROFILE ---
USER_PROFILE = {
    "name": "Vishaal Babu",
    "role": "Digital Marketing Strategist & Technologist",
    "summary": "Digital Marketing Strategist with 5+ years of experience in SaaS/Tech. Specialized in AI content automation (N8N), Python analytics, and technical storytelling. Based in France.",
    "skills": ["SEO & GTM Strategy", "N8N & Automation", "Python (Pandas/Scikit-Learn)", "Technical Content Writing", "HubSpot/GA4"],
    "achievements": [
        "Drove 500,000+ signups for a Data Science program via targeted positioning.",
        "Achieved 125% organic traffic growth via intent-based content strategy.",
        "Built fully automated AI Content Ops pipeline using N8N and LLMs."
    ],
    "portfolio": "https://linktr.ee/vishaalgrizzly",
    "experience_years": 5
}

# --- CONFIGURATION ---
SEARCH_URLS = {
    "Marketing": "https://englishjobs.fr/jobs/marketing",
    "Data": "https://englishjobs.fr/jobs/data",
    "Product": "https://englishjobs.fr/jobs/product"
}
STATE_FILE = "seen_jobs_ai.json"

# Secrets
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# Configure OpenRouter Client
client = None
if OPENROUTER_API_KEY:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

def send_telegram(message):
    if not BOT_TOKEN or not CHAT_ID: return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Telegram Fail: {e}")

def analyze_job_with_ai(job_title, job_link):
    print(f"🤖 AI Analyzing: {job_title}...")
    
    try:
        # 1. Scrape Description
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(job_link, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        
        description_div = soup.find("div", class_="job-description") 
        if not description_div: description_div = soup.find("body")
        job_text = description_div.get_text(separator="\n", strip=True)[:3000]
        
        # 2. The Prompt
        prompt = f"""
        ACT AS: A Career Coach for Vishaal Babu.
        
        CONTEXT:
        My Profile: {json.dumps(USER_PROFILE)}
        
        JOB TO ANALYZE:
        Title: {job_title}
        Description Snippet: {job_text}
        
        TASK:
        1. Rate Match % (0-100).
        2. EXPERIENCE RULE: If the job asks for 2, 3, or 4 years, treat it as a HIGH MATCH. I am an international applicant willing to take a mid-level role.
        3. If Match < 50%, output ONLY "SKIP".
        4. If Match > 50%, write a Telegram notification in this format:
        
        🔥 **MATCH SCORE: [Score]%**
        **Role:** {job_title}
        
        💡 **Why you match:** [1 sentence summary]
        
        🏹 **The Hook:**
        "[Draft a 2-sentence hook using my metrics (500k signups / 125% growth / N8N) to solve their problem.]"
        
        ❓ **Interview Prep:**
        "Be ready to answer: [Hardest technical question]"
        """
        
        # 3. Call OpenRouter
        completion = client.chat.completions.create(
            model="xiaomi/mimo-v2-flash:free", # <--- YOUR MODEL HERE
            messages=[
                {"role": "user", "content": prompt}
            ],
            extra_headers={
                "HTTP-Referer": "https://github.com/vishaalgrizzly", 
                "X-Title": "Job Hunter Bot",
            },
        )
        return completion.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"AI Error: {e}")
        return None

def load_seen_jobs():
    if not os.path.exists(STATE_FILE): return set()
    try:
        with open(STATE_FILE, "r") as f: return set(json.load(f))
    except: return set()

def save_seen_jobs(jobs):
    with open(STATE_FILE, "w") as f: json.dump(list(jobs), f)

def main():
    if not client:
        print("Error: OpenRouter API Key missing.")
        return

    print("--- AI JOB AGENT STARTED (OpenRouter) ---")
    seen_jobs = load_seen_jobs()
    new_jobs_found = 0
    
    for category, url in SEARCH_URLS.items():
        try:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            jobs = soup.find_all("a", href=True)
            
            for job in jobs:
                if "/job/" in job["href"]:
                    link = "https://englishjobs.fr" + job["href"]
                    title = job.get_text(strip=True)
                    
                    if link in seen_jobs: continue
                    
                    ai_analysis = analyze_job_with_ai(title, link)
                    
                    if ai_analysis and "SKIP" not in ai_analysis:
                        send_telegram(f"{ai_analysis}\n\n🔗 [View Job]({link})")
                        new_jobs_found += 1
                    else:
                        print(f"Skipped {title}")
                        
                    seen_jobs.add(link)
                    time.sleep(5) 
                    
        except Exception as e:
            print(f"Scraping Error: {e}")

    if new_jobs_found > 0:
        save_seen_jobs(seen_jobs)
        print(f"Sent {new_jobs_found} AI reports.")

if __name__ == "__main__":
    main()
