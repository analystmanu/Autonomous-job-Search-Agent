"""
muse_scraper.py — Scrapes data jobs from The Muse API
"""

import requests
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

THEMUSE_API_KEY = os.getenv("THEMUSE_API_KEY")
BASE_URL = "https://www.themuse.com/api/public/jobs"

DS_CATEGORIES = [
    "Data Science", "Analytics", "Data & Analytics"
]


def scrape_themuse(max_pages=5):
    print("Fetching jobs from The Muse...")
    all_jobs = []

    for category in DS_CATEGORIES:
        for page in range(max_pages):
            try:
                params = {
                    "category": category,
                    "page": page,
                    "api_key": THEMUSE_API_KEY
                }
                res = requests.get(BASE_URL, params=params, timeout=15)
                res.raise_for_status()
                data = res.json()
                jobs = data.get("results", [])

                if not jobs:
                    break

                for job in jobs:
                    # Extract location
                    locations = job.get("locations", [])
                    location = locations[0].get("name", "Remote") if locations else "Remote"

                    # Extract levels
                    levels = job.get("levels", [])
                    level = levels[0].get("name", "Mid Level") if levels else "Mid Level"

                    all_jobs.append({
                        "id": f"muse_{job.get('id', '')}",
                        "title": job.get("name", ""),
                        "company": job.get("company", {}).get("name", "Unknown"),
                        "description": job.get("contents", "")[:500],
                        "tags": category,
                        "salary": "Not specified",
                        "date_posted": job.get("publication_date", "")[:10],
                        "url": job.get("refs", {}).get("landing_page", ""),
                        "source": "The Muse",
                        "location_type": "Remote" if "remote" in location.lower() or "flexible" in location.lower() else location,
                        "seniority": level,
                        "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                    })

                print(f"  The Muse '{category}' page {page}: {len(jobs)} jobs")

                if len(jobs) < 20:
                    break

            except Exception as e:
                print(f"  The Muse error: {e}")
                break

    print(f"  Total The Muse jobs: {len(all_jobs)}")
    return pd.DataFrame(all_jobs) if all_jobs else pd.DataFrame()


if __name__ == "__main__":
    df = scrape_themuse()
    print(df[["title", "company", "seniority"]].head())
