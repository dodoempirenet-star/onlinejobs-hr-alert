import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

URL = "https://www.onlinejobs.ph/jobseekers/search/c/human-resources--hr-management"

BOT_TOKEN = "8670907906:AAFKNwwIc9Jx0bZDYMhJdwQ0y0Chlg-gAhY"
CHAT_ID = "1520619770"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=data)

def get_jobs():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    today_str = datetime.utcnow().strftime("%Y-%m-%d")

    jobs = []

    for card in soup.find_all("div"):
        text = card.get_text()

        if "Posted on" in text:
            if today_str in text:
                link_tag = card.find("a", href=True)
                if link_tag and "/job/" in link_tag["href"]:
                    title = link_tag.text.strip()
                    link = "https://www.onlinejobs.ph" + link_tag["href"]
                    jobs.append((title, link))

    return list(set(jobs))

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

    new_jobs = [job for job in current_jobs if job not in previous_jobs]

    if new_jobs:
        for title, link in new_jobs:
            message = f"New HR Job Posted Today:\n{title}\n{link}"
            send_telegram(message)

    save_jobs(current_jobs)

if __name__ == "__main__":
    main()
