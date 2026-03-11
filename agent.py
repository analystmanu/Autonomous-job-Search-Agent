"""
agent.py — Scrapes remote Data Science jobs from RemoteOK API
and classifies them using NLP keyword matching.
"""

import requests
import pandas as pd
import re
from datetime import datetime

REMOTEOK_URL = "https://remoteok.com/api"
HEADERS = {"User-Agent": "Mozilla/5.0 (JobSearchAgent/1.0)"}

DS_KEYWORDS = [
    # Data Science Core
    "data scientist", "data science", "applied scientist",
    "decision scientist", "research scientist",

    # Analyst Roles
    "data analyst", "business analyst", "product analyst",
    "marketing analyst", "financial analyst", "risk analyst",
    "operations analyst", "reporting analyst", "growth analyst",
    "revenue analyst", "people analyst", "crm analyst",
    "supply chain analyst", "pricing analyst", "quantitative analyst",
    "insights analyst", "strategy analyst", "data specialist",
    "business intelligence analyst",

    # Engineering
    "data engineer", "analytics engineer", "etl developer",
    "etl engineer", "pipeline engineer", "warehouse engineer",
    "dbt engineer", "database engineer", "spark engineer",

    # ML / AI
    "machine learning", "ml engineer", "ai engineer",
    "deep learning", "deep learning engineer", "nlp engineer",
    "nlp", "natural language", "computer vision",
    "llm engineer", "llm", "artificial intelligence",

    # BI / Visualization
    "bi developer", "bi engineer", "power bi", "power bi developer",
    "tableau", "tableau developer", "looker", "looker developer",

    # Internships
    "data intern", "analyst intern", "ml intern",
    "ai intern", "analytics intern", "data science intern",
    "business intelligence intern", "python intern",

    # Tools & Skills
    "python", "sql", "pandas", "pytorch", "tensorflow",
    "scikit-learn", "spark", "airflow", "kafka", "aws",
    "azure", "gcp", "snowflake", "databricks", "statistics", "ai",
]

SENIOR_KEYWORDS = ["senior", "lead", "principal", "staff", "head of", "director", "vp", "vice president", "chief"]
JUNIOR_KEYWORDS = ["junior", "entry", "associate", "intern", "graduate", "jr", "trainee", "fresher"]
MID_KEYWORDS = ["mid", "intermediate", "ii", "iii", "level 2", "level 3"]

CONTRACT_KEYWORDS = ["contract", "freelance", "consultant", "consulting", "temporary", "part-time"]
LOCATION_KEYWORDS = ["remote", "hybrid", "on-site", "onsite", "work from home", "wfh"]

EXTRA_ROLES = [
    "data manager", "data lead", "data architect",
    "cloud data engineer", "azure data engineer",
    "aws data engineer", "staff data scientist",
    "data platform engineer", "data infrastructure",
    "data governance", "data quality engineer",
    "data operations", "dataops"
]


def classify_job(title, description=""):
    text = (title + " " + description).lower()
    matched = [kw for kw in DS_KEYWORDS + EXTRA_ROLES if kw in text]
    relevance = min(len(matched) / 8.0, 1.0)

    if any(k in text for k in ["data scientist", "data science", "applied scientist", "decision scientist", "research scientist"]):
        category = "Data Scientist"
    elif any(k in text for k in ["machine learning", "ml engineer", "deep learning"]):
        category = "ML Engineer"
    elif any(k in text for k in ["data engineer", "etl developer", "etl engineer", "pipeline engineer", "warehouse engineer", "dbt", "spark engineer"]):
        category = "Data Engineer"
    elif any(k in text for k in ["business analyst", "product analyst", "marketing analyst", "financial analyst", "risk analyst", "operations analyst", "reporting analyst", "growth analyst", "revenue analyst", "people analyst", "crm analyst", "supply chain analyst", "pricing analyst", "quantitative analyst", "insights analyst", "strategy analyst"]):
        category = "Business Analyst"
    elif any(k in text for k in ["data analyst", "analytics engineer"]):
        category = "Data Analyst"
    elif any(k in text for k in ["bi developer", "bi engineer", "power bi", "tableau", "looker"]):
        category = "BI Developer"
    elif any(k in text for k in ["nlp", "natural language", "llm", "large language"]):
        category = "NLP/LLM Engineer"
    elif any(k in text for k in ["ai engineer", "artificial intelligence"]):
        category = "AI Engineer"
    elif any(k in text for k in ["intern", "internship"]):
        category = "Internship"
    else:
        category = "Other"

    if any(k in text for k in SENIOR_KEYWORDS):
        seniority = "Senior"
    elif any(k in text for k in JUNIOR_KEYWORDS):
        seniority = "Junior"
    elif any(k in text for k in MID_KEYWORDS):
        seniority = "Mid-Level"
    else:
        seniority = "Mid-Level"

    # Contract type
    if any(k in text for k in CONTRACT_KEYWORDS):
        job_type = "Contract/Freelance"
    else:
        job_type = "Full-Time"

    # Location type
    if "hybrid" in text:
        location_type = "Hybrid"
    elif any(k in text for k in ["on-site", "onsite"]):
        location_type = "On-Site"
    else:
        location_type = "Remote"

    return {
        "category": category,
        "seniority": seniority,
        "job_type": job_type,
        "location_type": location_type,
        "relevance_score": round(relevance, 2),
        "matched_keywords": ", ".join(matched[:5]),
        "is_ds_relevant": relevance > 0.1 or len(matched) >= 1
    }


def clean_html(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', str(text))).strip()[:500]


def scrape_remoteok(max_jobs=200):
    print("Fetching jobs from RemoteOK...")
    try:
        res = requests.get(REMOTEOK_URL, headers=HEADERS, timeout=15)
        res.raise_for_status()
        data = res.json()
        jobs_raw = [j for j in data if isinstance(j, dict) and j.get("id")]
        print(f"  Fetched {len(jobs_raw)} raw jobs")
    except Exception as e:
        print(f"  API error: {e}")
        return pd.DataFrame()

    jobs = []
    for job in jobs_raw[:max_jobs]:
        title = job.get("position", "")
        description = clean_html(job.get("description", ""))
        tags = job.get("tags", [])
        date_str = job.get("date", "")

        try:
            date_posted = datetime.fromisoformat(date_str.replace("Z", "+00:00")).strftime("%Y-%m-%d")
        except:
            date_posted = "Unknown"

        classification = classify_job(title, description + " " + " ".join(tags or []))

        jobs.append({
            "id": job.get("id", ""),
            "title": title,
            "company": job.get("company", "Unknown"),
            "description": description,
            "tags": ", ".join(tags[:8]) if tags else "",
            "salary": job.get("salary") or "Not specified",
            "date_posted": date_posted,
            "url": job.get("url", ""),
            "source": "RemoteOK",
            "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            **classification
        })

    df = pd.DataFrame(jobs)
    ds_jobs = df[df["is_ds_relevant"] == True].copy()
    print(f"  DS-relevant jobs: {len(ds_jobs)} / {len(df)}")
    return ds_jobs


if __name__ == "__main__":
    df = scrape_remoteok()
    print(df[["title", "company", "category", "seniority"]].head())
