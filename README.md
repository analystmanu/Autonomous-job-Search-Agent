# 🔍 Autonomous Job Search Agent

> An intelligent, multi-source job scraping and classification system built for Data professionals — fully automated, NLP-powered, and deployed live.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red)
![NLP](https://img.shields.io/badge/NLP-Keyword%20Classification-green)
![LLM](https://img.shields.io/badge/LLM-Groq%20%7C%20Llama3-purple)
![ETL](https://img.shields.io/badge/ETL-Automated%20Pipeline-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🚀 Live Demo

🔗 **[View Live Dashboard](#)** ← Add Streamlit Cloud link here after deployment

---

## 📌 Overview

The Autonomous Job Search Agent is an end-to-end automated data pipeline that:

- Scrapes **500+ data job listings** from 4 sources every 2 hours
- Classifies jobs using **NLP keyword matching** and **LLM semantic classification**
- Stores results in a deduplicated CSV via an automated ETL pipeline
- Displays everything in a live **Streamlit dashboard** with real-time filters

Built by **Manu Sharma** — because the best way to find a data job is to engineer a system that finds it for you.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.13 |
| Data Manipulation | Pandas |
| Job Sources | RemoteOK API, Adzuna API, The Muse API |
| NLP Classification | Keyword Matching (60+ keywords, 9 categories) |
| LLM Classification | Groq API (Llama 3) |
| ETL Pipeline | Custom Python pipeline with deduplication |
| Automation | Schedule library + Windows Task Scheduler |
| Dashboard | Streamlit |
| Visualizations | Plotly |
| Deployment | Streamlit Cloud |
| Version Control | GitHub |

---

## ✨ Features

- **Multi-source scraping** — RemoteOK, Adzuna, The Muse via REST APIs
- **NLP classification** — 60+ keywords across 9 job categories
- **LLM classification** — Groq/Llama3 for semantic understanding
- **Smart deduplication** — no duplicate jobs across sources
- **Seniority detection** — Junior, Mid-Level, Senior
- **Contract type detection** — Full-Time vs Contract/Freelance
- **Location detection** — Remote, Hybrid, On-Site
- **2-hour auto-refresh** — via Windows Task Scheduler
- **Interactive dashboard** — real-time filters by category, seniority, source, location
- **Plotly analytics** — charts for category, seniority, source breakdown
- **CSV export** — download filtered results anytime
- **Recruiter branding** — personalized message with live metrics

---

## 📊 Job Categories Tracked

```
✅ Data Scientist        ✅ Data Analyst
✅ Data Engineer         ✅ Business Analyst
✅ ML Engineer           ✅ NLP/LLM Engineer
✅ BI Developer          ✅ AI Engineer
✅ Internships
```

---

## 🗂️ Project Structure

```
job-search-agent/
│
├── agent.py                  # RemoteOK scraper + NLP classifier
├── pipeline.py               # ETL pipeline (all sources)
├── dashboard.py              # Streamlit dashboard
├── scheduler.py              # 2-hour auto-refresh
│
├── scrapers/
│   ├── adzuna_scraper.py     # Adzuna API scraper
│   ├── muse_scraper.py       # The Muse API scraper
│   └── llm_classifier.py    # Groq LLM classifier
│
├── data/
│   ├── jobs.csv              # Job listings (auto-generated)
│   └── meta.json             # Pipeline metadata
│
├── requirements.txt
├── .env                      # API keys (not committed)
├── .gitignore
└── README.md
```

---

## ⚙️ Setup & Installation

### 1. Clone the repo
```bash
git clone https://github.com/analystmanu/Autonomous-job-Search-Agent.git
cd Autonomous-job-Search-Agent
```

### 2. Create virtual environment
```bash
python -m venv venv
.\venv\Scripts\activate      # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add API keys
Create a `.env` file in the root folder:
```
ADZUNA_APP_ID=your_app_id
ADZUNA_API_KEY=your_api_key
THEMUSE_API_KEY=your_api_key
GROQ_API_KEY=your_api_key
```

Get free API keys from:
- Adzuna → [developer.adzuna.com](https://developer.adzuna.com)
- The Muse → [themuse.com/developers](https://www.themuse.com/developers)
- Groq → [console.groq.com](https://console.groq.com)

### 5. Run the dashboard
```bash
streamlit run dashboard.py
```

Opens at `http://localhost:8501` 🚀

---

## 🔄 Automation

### Run pipeline manually
```bash
python pipeline.py
```

### Run scheduler (every 2 hours)
```bash
python scheduler.py
```

### Windows Task Scheduler
```
1. Open Task Scheduler
2. Create Basic Task → Name: "Job Search Agent"
3. Trigger: Daily, repeat every 2 hours
4. Action: Start a program → python pipeline.py
5. Start in: C:\path\to\your\project
```

---

## 👤 About

Built by **Manu Sharma**

> "I know how to engineer things the way they can benefit the best. I believe in numbers, results and most importantly — presenting them neatly."

- 🔗 [GitHub](https://github.com/analystmanu)
- 💼 [LinkedIn](#) ← Add your LinkedIn

---

## 📄 License

MIT License — free to use and modify.
