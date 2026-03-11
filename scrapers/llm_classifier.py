"""
llm_classifier.py — LLM-powered job classification using Groq (free)
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama3-8b-8192"


def classify_with_llm(title, description=""):
    """Use Groq LLM to classify a job listing"""

    prompt = f"""You are a job classifier. Analyze this job and return ONLY a JSON object.

Job Title: {title}
Description: {description[:300]}

Return ONLY this JSON, nothing else:
{{
    "category": "one of: Data Scientist, Data Analyst, Data Engineer, Business Analyst, ML Engineer, NLP/LLM Engineer, BI Developer, AI Engineer, Internship, Other",
    "seniority": "one of: Junior, Mid-Level, Senior",
    "relevance_score": 0.0 to 1.0 (how relevant to data roles),
    "is_ds_relevant": true or false,
    "reason": "one sentence explanation"
}}"""

    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 200
        }
        res = requests.post(GROQ_URL, headers=headers, json=payload, timeout=15)
        res.raise_for_status()
        content = res.json()["choices"][0]["message"]["content"].strip()

        # Clean and parse JSON
        if "```" in content:
            content = content.split("```")[1].replace("json", "").strip()

        result = json.loads(content)
        return result

    except Exception as e:
        print(f"  LLM error: {e}")
        return None


def classify_jobs_with_llm(df, sample_size=50):
    """Classify a sample of jobs using LLM to validate NLP results"""
    print(f"Running LLM classification on {min(sample_size, len(df))} jobs...")

    results = []
    for i, row in df.head(sample_size).iterrows():
        result = classify_with_llm(row.get("title", ""), row.get("description", ""))
        if result:
            results.append({
                "id": row.get("id"),
                "llm_category": result.get("category"),
                "llm_seniority": result.get("seniority"),
                "llm_relevance": result.get("relevance_score"),
                "llm_relevant": result.get("is_ds_relevant"),
                "llm_reason": result.get("reason")
            })

    print(f"  LLM classified {len(results)} jobs")
    return results


if __name__ == "__main__":
    result = classify_with_llm(
        "Senior Data Scientist",
        "Looking for someone with Python, ML and statistical modeling experience"
    )
    print(result)
