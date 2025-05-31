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

# removed whitespace, standardised casing and replaced empty strings with null
df["company"] = df["company"].str.strip().str.title().replace("", pd.NA)
df["position"] = df["position"].str.strip().str.title().replace("", pd.NA)
df["location"] = df["location"].str.strip().replace("", pd.NA)

# splits tags into separate strings
df["tags"] = df["tags"].fillna("").apply(lambda x: [tag.strip().lower() for tag in x.split(",") if tag])

# removing dupes
df.drop_duplicates(subset=["company","position","salary_avg"], inplace=True)

# removing rows that are missing company or position data
df.dropna(subset=["company","position"], inplace=True)

df["is_dev_job"] = df["tags"].apply(lambda tags: any("dev" in tag for tag in tags))
df["is_data_job"] = df["tags"].apply(lambda tags: any("data" in tag for tag in tags))

df.to_csv("jobs.csv", index=False)
