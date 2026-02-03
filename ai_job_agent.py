import requests
from bs4 import BeautifulSoup
import json
import os
import time
from openai import OpenAI

USER_PROFILE = {
    "name": "Vishaal Babu",
    "headline": "Growth Engineer | Digital Marketing Strategist | CS Engineer turned Marketer | Specialized in Building AI Agents",
    "location": "Antibes, France (Open to relocation worldwide)",
    "phone": "+33 743636710",
    "email": "vishaalgrizzly1@gmail.com",
    "portfolio": "https://linktr.ee/vishaalgrizzly",
    "linkedin": "www.linkedin.com/in/vishaalgrizzly/",
    
    "summary": (
        "Computer Science Engineer turned Digital Marketer with 5+ years of experience bridging the gap between "
        "technical product development and revenue growth. I don't just execute campaigns; I engineer them. "
        "Expert in building Data-Driven Growth Engines, automating Content Operations (N8N/LLMs), and deploying "
        "Machine Learning models (Propensity Scoring, Churn Prediction) to optimize Marketing ROAS. "
        "Proven track record in high-stakes environments (Blockchain, EdTech, SaaS) including a launch that drove 500k+ signups."
    ),
    
    "core_competencies": {
        "Strategic": [
            "Go-to-Market (GTM) Strategy", 
            "Revenue Operations (RevOps)", 
            "Product-Led Growth (PLG)", 
            "Technical SEO & AEO (Answer Engine Optimization)",
            "Conversion Rate Optimization (CRO)"
        ],
        "Technical": [
            "Marketing Automation Architecture",
            "Predictive Analytics & Modeling",
            "CRM Architecture & Lead Scoring",
            "Prompt Engineering & LLM Integration",
            "Data Visualization & Storytelling"
        ]
    },
    
    "tech_stack": {
        "Languages & Data": ["Python (Pandas, NumPy, Scikit-Learn)", "SQL", "HTML/CSS", "Streamlit"],
        "Automation & AI": ["N8N", "Zapier", "Perplexity API", "OpenAI API", "Make.com"],
        "Marketing Platforms": ["HubSpot (Admin)", "Salesforce", "Google Analytics (GA4)", "Semrush", "Ahrefs"],
        "Project Management": ["Jira", "Notion", "Trello", "Slack"],
        "Visualization": ["Power BI", "Tableau", "Matplotlib/Seaborn"]
    },

    "key_achievements": [
        "Growth at Scale: Orchestrated the full-stack digital launch for an IIT Madras Data Science program, driving 500,000+ signups.",
        "Revenue Optimization: Deployed a 'Propensity to Buy' scoring model using Python that reduced Ad Spend by 20% while maintaining conversion volume.",
        "Operational Efficiency: Built a proprietary AI Content Ops pipeline (N8N + LLMs) that reduced content drafting time by 60% and automated SEO keyword clustering.",
        "Organic Growth: Achieved 125% organic traffic growth for a SaaS client by restructuring site architecture based on 'Semantic Search' intent."
    ],

    "projects": [
        {
            "name": "Marketing Revenue Prediction Model",
            "stack": "Python, Linear Regression, Scikit-Learn",
            "description": "Built a regression model to correlate specific channel spend with Net Profit, identifying that 'Brand' campaigns had a 2x higher LTV impact than 'Promo' campaigns."
        },
        {
            "name": "AI Content Ops Ecosystem",
            "stack": "N8N, Perplexity API, Webhooks, OpenAI",
            "description": "Automated the end-to-end content workflow: from Trend Spotting (API) -> Brief Generation (LLM) -> Draft Creation -> CMS Upload."
        },
        {
            "name": "E-Commerce Customer Segmentation Engine",
            "stack": "Python, K-Means Clustering, RFM Analysis",
            "description": "Segmented a user base into 4 behavioral personas ('Whales', 'Window Shoppers', etc.) to hyper-target CRM emails, increasing open rates by 15%."
        },
        {
            "name": "Fintech Transaction Pulse",
            "stack": "Streamlit, PhonePe Pulse Data, Plotly",
            "description": "Developed an interactive geospatial dashboard visualizing millions of digital transactions to identify regional adoption trends."
        }
    ],

    "work_history": [
        {
            "role": "SEO & Web Strategy Consultant",
            "company": "Skål International Côte d'Azur",
            "dates": "Recent",
            "impact": "Leading the digital transformation of a legacy tourism association. Restructuring web architecture for modern SEO standards and implementing automated membership workflows, ensuring GDPR compilance."
        },
        {
            "role": "Content Marketer & Strategist",
            "company": "Calibraint (SaaS/Blockchain)",
            "dates": "Previous",
            "impact": "Managed B2B messaging for complex tech stacks (Blockchain, AI). Translated engineering documentation into compelling sales assets and whitepapers. Managed a content team of 5."
        },
        {
            "role": "Senior Technical Editorial In-Charge",
            "company": "Maxposure Media (Client: IIT Madras)",
            "dates": "Previous",
            "impact": "Managed the high-pressure launch of India's first online B.Sc degree. Coordinated between academic stakeholders and marketing teams to drive 500k+ applications."
        },
        {
            "role": "Technical Writer",
            "company": "Zaigo Infotech",
            "dates": "Previous",
            "impact": "Reduced churn and support tickets by authoring developer-friendly API documentation and user manuals. Bridged the communication gap between Product and Sales."
        }
    ],

    "education": [
        "M.Sc. in Digital Marketing and Artificial Intelligence | SKEMA Business School, France (Grand École)",
        "B.E. in Computer Science & Engineering | Anna University, India"
    ],
    
    "languages": ["English (Fluent/C2)", "French (A2 - Actively Learning)", "Hindi (Native)", "Tamil (Native)"]
}
}

# --- 2. CONFIGURATION ---
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
}
STATE_FILE = "seen_jobs_ai.json"

# Secrets
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# Configure OpenRouter
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
        # A. Scrape the Description
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(job_link, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        
        description_div = soup.find("div", class_="job-description") 
        if not description_div: description_div = soup.find("body")
        job_text = description_div.get_text(separator="\n", strip=True)[:4000] # Increased token limit slightly
        
        # B. The "Career Coach" Prompt (Updated to use the detailed profile)
        prompt = f"""
        ACT AS: A Senior Technical Recruiter coaching Vishaal Babu.
        
        CONTEXT (Vishaal's Detailed Profile):
        {json.dumps(USER_PROFILE, indent=2)}
        
        JOB TO ANALYZE:
        Title: {job_title}
        Description Snippet: {job_text}
        
        TASK:
        1. **Analyze Match % (0-100):** - Be strict on skills, but FLEXIBLE on "Years of Experience" (I am willing to take Mid-level roles).
           - If the job requires French (Fluent/Native), penalize the score heavily (I am only A2).
           
        2. **Decision:**
           - If Match < 50%, output ONLY the word "SKIP".
           
        3. **If Match > 50%, write a Telegram notification:**
           
           🔥 **MATCH SCORE: [Score]%**
           **Role:** {job_title}
           
           💡 **Why you match:** [1 sentence connecting my specific Tech Stack (e.g. N8N/Python) to their needs]
           
           ⚠️ **Gap Analysis:** [Briefly mention if French is required or if I lack a specific tool]
           
           🏹 **The Hook (Cover Letter Intro):**
           "[Draft a 'Golden Paragraph' (2-3 sentences) that matches my specific project to their problem. 
           Example: 'At Calibraint, I managed a team of 5 to launch blockchain products...' or 'I used Python K-Means to segment traffic...' 
           Use the MOST relevant achievement from my profile. Do not be generic.]"
           
           ❓ **Interview Prep:**
           "Be ready to answer: [One specific, hard technical question based on the JD]"
        """
        
        # C. Call OpenRouter
        completion = client.chat.completions.create(
            model="xiaomi/mimo-v2-flash:free", 
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
        print("Error: OPENROUTER_API_KEY is missing.")
        return

    print("--- AI JOB AGENT STARTED ---")
    seen_jobs = load_seen_jobs()
    new_jobs_found = 0
    
    for category, url in SEARCH_URLS.items():
        try:
            print(f"Checking {category}...")
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            
            jobs = soup.find_all("a", href=True)
            
            for job in jobs:
                if "/job/" in job["href"]:
                    link = "https://englishjobs.fr" + job["href"]
                    title = job.get_text(strip=True)
                    
                    if link in seen_jobs: continue
                    
                    # Call the AI
                    ai_analysis = analyze_job_with_ai(title, link)
                    
                    if ai_analysis and "SKIP" not in ai_analysis:
                        send_telegram(f"{ai_analysis}\n\n🔗 [View Job]({link})")
                        new_jobs_found += 1
                    else:
                        print(f"Skipped {title} (Low Match)")
                        
                    seen_jobs.add(link)
                    time.sleep(5) 
                    
        except Exception as e:
            print(f"Scraping Error: {e}")

    if new_jobs_found > 0:
        save_seen_jobs(seen_jobs)
        print(f"Sent {new_jobs_found} AI reports.")
    else:
        print("Run Complete. No matches found this time.")

if __name__ == "__main__":
    main()
