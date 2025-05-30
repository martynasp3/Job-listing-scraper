import requests
import os
import pandas as pd
from datetime import datetime

url = "https://remoteok.com/api"

headers = {
    'User-Agent': 'Mozilla/5.0'
}

response = requests.get(url, headers=headers)
data = response.json()

jobs_data = data[1:]

# Selecting columns to scrape from RemoteOK
jobs = []
for job in jobs_data:
    jobs.append({
        "company": job.get("company"),
        "position": job.get("position"),
        "location": job.get("location"),
        "tags": ", ".join(job.get("tags", [])),
        "url": job.get("url"),
        "date_posted": job.get("date"),
        "salary_avg": (job.get("salary_min") + job.get("salary_max")) / 2,
    })

df = pd.DataFrame(jobs)
df["scraped_on"] = datetime.today().strftime("%Y-%m-%d")

filename = "jobs.csv"

if os.path.exists(filename):
    old_df = pd.read_csv(filename)
    df = pd.concat([old_df, df], ignore_index=True)

# removing dupes
df.drop_duplicates(subset=["company", "position", "location"], inplace=True)

df.to_csv("jobs.csv", index=False)
