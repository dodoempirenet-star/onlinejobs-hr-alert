import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import pytz

URL = "https://www.onlinejobs.ph/jobseekers/search/c/human-resources--hr-management"

BOT_TOKEN = "8670907906:AAFKNwwIc9Jx0bZDYMhJdwQ0y0Chlg-gAhY"
CHAT_ID = "1520619770"

TIMEZONE = pytz.timezone("Asia/Manila")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=data)

def parse_posted_datetime(text):
    try:
        # Extract timestamp after "Posted on "
        date_str = text.split("Posted on ")[1].strip()
        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return TIMEZONE.localize(dt)
    except:
        return None

def get_jobs():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    today = datetime.now(TIMEZONE).date()
    jobs = []

    for card in soup.find_all("div"):
        text = card.get_text()

        if "Posted on" in text:
            posted_dt = parse_posted_datetime(text)
            if posted_dt and posted_dt.date() == today:
                link_tag = card.find("a", href=True)
                if link_tag and "/job/" in link_tag["href"]:
                    title = link_tag.text.strip()
                    link = "https://www.onlinejobs.ph" + link_tag["href"]
                    jobs.append({
                        "title": title,
                        "link": link,
                        "timestamp": posted_dt.strftime("%Y-%m-%d %H:%M:%S")
                    })

    return jobs

def load_previous():
    if not os.path.exists("jobs.json"):
        return []
    with open("jobs.json", "r") as f:
        return json.load(f)

def save_jobs(jobs):
    with open("jobs.json", "w") as f:
        json.dump(jobs, f)

def main():
    current_jobs = get_jobs()
    previous_jobs = load_previous()

    previous_timestamps = {job["timestamp"] for job in previous_jobs}

    new_jobs = [job for job in current_jobs if job["timestamp"] not in previous_timestamps]

    for job in new_jobs:
        message = (
            f"New HR Job Posted (PH Time):\n"
            f"{job['title']}\n"
            f"{job['link']}\n"
            f"Posted at: {job['timestamp']}"
        )
        send_telegram(message)

    save_jobs(current_jobs)

if __name__ == "__main__":
    main()
