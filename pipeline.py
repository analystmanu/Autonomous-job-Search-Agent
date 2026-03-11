"""
pipeline.py — ETL pipeline: scrape all sources, clean, deduplicate, save to CSV
"""

import pandas as pd
import os
import json
from datetime import datetime
from pathlib import Path

from agent import scrape_remoteok, classify_job
from scrapers.adzuna_scraper import scrape_adzuna
from scrapers.muse_scraper import scrape_themuse

CSV_PATH = "./data/jobs.csv"
META_PATH = "./data/meta.json"


def ensure_data_dir():
    Path("./data").mkdir(exist_ok=True)


def load_existing():
    if os.path.exists(CSV_PATH):
        try:
            return pd.read_csv(CSV_PATH)
        except:
            pass
    return pd.DataFrame()


def save_jobs(df):
    ensure_data_dir()
    df.to_csv(CSV_PATH, index=False)
    print(f"  Saved {len(df)} jobs to CSV")


def load_meta():
    if os.path.exists(META_PATH):
        with open(META_PATH) as f:
            return json.load(f)
    return {}


def save_meta(stats):
    ensure_data_dir()
    with open(META_PATH, "w") as f:
        json.dump(stats, f, indent=2)


def clean_jobs(df):
    if df.empty:
        return df
    df = df.dropna(subset=["title", "company"])
    df["title"] = df["title"].str.strip().str.title()
    df["company"] = df["company"].str.strip()
    df["salary"] = df["salary"].fillna("Not specified").replace("", "Not specified")
    df["description"] = df["description"].fillna("")
    df["tags"] = df["tags"].fillna("")
    df = df[df["title"].str.len() > 3]
    return df.reset_index(drop=True)


def classify_all(df):
    if df.empty:
        return df
    classifications = []
    for _, row in df.iterrows():
        if pd.isna(row.get("category")) if "category" in df.columns else True:
            result = classify_job(
                row.get("title", ""),
                str(row.get("description", "")) + " " + str(row.get("tags", ""))
            )
            classifications.append(result)
        else:
            classifications.append({
                "category": row.get("category"),
                "seniority": row.get("seniority", "Mid-Level"),
                "job_type": row.get("job_type", "Full-Time"),
                "location_type": row.get("location_type", "Remote"),
                "relevance_score": row.get("relevance_score", 0.5),
                "matched_keywords": row.get("matched_keywords", ""),
                "is_ds_relevant": row.get("is_ds_relevant", True)
            })
    class_df = pd.DataFrame(classifications)
    for col in class_df.columns:
        df[col] = class_df[col].values
    return df


def deduplicate(new_df, existing_df):
    if existing_df.empty:
        return new_df
    existing_ids = set(existing_df["id"].astype(str).tolist())
    new_df = new_df[~new_df["id"].astype(str).isin(existing_ids)]
    existing_keys = set(
        (str(r["title"]).lower() + str(r["company"]).lower())
        for _, r in existing_df.iterrows()
    )
    new_df = new_df[~new_df.apply(
        lambda r: (str(r["title"]).lower() + str(r["company"]).lower()) in existing_keys,
        axis=1
    )]
    print(f"  New unique jobs: {len(new_df)}")
    return new_df.reset_index(drop=True)


def run_pipeline():
    print(f"\n{'='*40}")
    print(f"Pipeline started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*40}")

    start = datetime.now()
    all_new = []

    # Extract from all sources
    remoteok_df = scrape_remoteok(max_jobs=200)
    if not remoteok_df.empty:
        all_new.append(remoteok_df)

    adzuna_df = scrape_adzuna(max_results=200)
    if not adzuna_df.empty:
        all_new.append(adzuna_df)

    muse_df = scrape_themuse(max_pages=5)
    if not muse_df.empty:
        all_new.append(muse_df)

    if not all_new:
        print("No jobs fetched from any source!")
        return {"status": "failed"}

    combined_new = pd.concat(all_new, ignore_index=True)
    print(f"\nTotal raw jobs from all sources: {len(combined_new)}")

    # Transform
    cleaned = clean_jobs(combined_new)
    classified = classify_all(cleaned)
    ds_only = classified[classified["is_ds_relevant"] == True].copy()
    print(f"DS-relevant after filtering: {len(ds_only)}")

    # Load
    existing = load_existing()
    new_unique = deduplicate(ds_only, existing)

    if not new_unique.empty:
        final = pd.concat([existing, new_unique], ignore_index=True) if not existing.empty else new_unique
        final = final.sort_values("scraped_at", ascending=False).head(1000)
        save_jobs(final)
        total = len(final)
    else:
        print("  No new jobs to add")
        total = len(existing)

    duration = (datetime.now() - start).seconds
    stats = {
        "last_run": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "new_jobs_added": len(new_unique) if not new_unique.empty else 0,
        "total_jobs": total,
        "duration_seconds": duration,
        "sources": ["RemoteOK", "Adzuna", "The Muse"],
        "status": "success"
    }
    save_meta(stats)
    print(f"\nDone in {duration}s — {stats['new_jobs_added']} new jobs, {total} total")
    return stats


if __name__ == "__main__":
    run_pipeline()
