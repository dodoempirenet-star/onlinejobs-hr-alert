import requests
from bs4 import BeautifulSoup
import json
import os

URL = "https://www.onlinejobs.ph/jobseekers/search/c/human-resources--hr-management"

# TEMPORARY VALUES (we will remove these later)
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

    jobs = []

    for link in soup.find_all("a", href=True):
        if "/job/" in link["href"]:
            title = link.text.strip()
            full_link = "https://www.onlinejobs.ph" + link["href"]
            jobs.append((title, full_link))

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
            message = f"New HR Job:\n{title}\n{link}"
            send_telegram(message)

    save_jobs(current_jobs)

if __name__ == "__main__":
    main()
