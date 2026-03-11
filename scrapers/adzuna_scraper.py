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
    "machine learning engineer", "business analyst",
    "analytics engineer", "ai engineer", "etl developer",
    "bi developer"
]


def scrape_adzuna(max_results=200):
    print("Fetching jobs from Adzuna...")
    all_jobs = []

    for term in DS_SEARCH_TERMS[:5]:
        try:
            url = f"https://api.adzuna.com/v1/api/jobs/us/search/1"
            params = {
                "app_id": APP_ID,
                "app_key": API_KEY,
                "what": term,
                "results_per_page": 20,
            }
            res = requests.get(url, params=params, timeout=15)
            print(f"  Adzuna status: {res.status_code} for '{term}'")
            res.raise_for_status()
            data = res.json()
            jobs = data.get("results", [])

            for job in jobs:
                salary_min = job.get("salary_min")
                salary_max = job.get("salary_max")
                salary = f"${int(salary_min):,} - ${int(salary_max):,}" if salary_min and salary_max else "Not specified"

                all_jobs.append({
                    "id": f"adzuna_{job.get('id', '')}",
                    "title": job.get("title", ""),
                    "company": job.get("company", {}).get("display_name", "Unknown"),
                    "description": job.get("description", "")[:500],
                    "tags": term,
                    "salary": salary,
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
    print(df[["title", "company", "salary"]].head() if not df.empty else "No jobs found")
