"""
scheduler.py — Runs the ETL pipeline every 8 hours automatically.
"""

import schedule
import time
import logging
from datetime import datetime
from pipeline import run_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("./data/scheduler.log"),
        logging.StreamHandler()
    ]
)

REFRESH_HOURS = 2


def scheduled_run():
    logging.info("Scheduled run triggered")
    try:
        stats = run_pipeline()
        logging.info(f"Done: {stats.get('new_jobs_added', 0)} new jobs added")
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")


if __name__ == "__main__":
    print(f"Scheduler started — runs every {REFRESH_HOURS} hours")
    print("Press Ctrl+C to stop\n")

    # Run immediately on start
    scheduled_run()

    # Schedule recurring runs
    schedule.every(REFRESH_HOURS).hours.do(scheduled_run)

    while True:
        schedule.run_pending()
        time.sleep(60)
