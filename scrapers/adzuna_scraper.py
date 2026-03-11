"""
adzuna_scraper.py — Scrapes data jobs from Adzuna API
"""

import requests
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
API_KEY = os.getenv("ADZUNA_API_KEY")

DS_SEARCH_TERMS = [
    "data scientist", "data analyst", "data engineer",
    "machine learning", "business analyst", "nlp engineer",
    "analytics engineer", "ai engineer", "etl developer",
    "bi developer", "power bi", "tableau"
]

BASE_URL = "https://api.adzuna.com/v1/api/jobs/us/search"


def scrape_adzuna(max_results=200):
    print("Fetching jobs from Adzuna...")
    all_jobs = []

    for term in DS_SEARCH_TERMS[:5]:  # limit to 5 terms to stay within rate limit
        try:
            params = {
                "app_id": APP_ID,
                "app_key": API_KEY,
                "what": term,
                "results_per_page": 20,
                "page": 1,
                "content-type": "application/json"
            }
            res = requests.get(BASE_URL + "/1", params=params, timeout=15)
            res.raise_for_status()
            data = res.json()
            jobs = data.get("results", [])

            for job in jobs:
                all_jobs.append({
                    "id": f"adzuna_{job.get('id', '')}",
                    "title": job.get("title", ""),
                    "company": job.get("company", {}).get("display_name", "Unknown"),
                    "description": job.get("description", "")[:500],
                    "tags": term,
                    "salary": f"{job.get('salary_min', '')} - {job.get('salary_max', '')}" if job.get("salary_min") else "Not specified",
                    "date_posted": job.get("created", "")[:10],
                    "url": job.get("redirect_url", ""),
                    "source": "Adzuna",
                    "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                })

            print(f"  Adzuna '{term}': {len(jobs)} jobs")

        except Exception as e:
            print(f"  Adzuna error for '{term}': {e}")
            continue

    print(f"  Total Adzuna jobs: {len(all_jobs)}")
    return pd.DataFrame(all_jobs) if all_jobs else pd.DataFrame()


if __name__ == "__main__":
    df = scrape_adzuna()
    print(df[["title", "company", "salary"]].head())
