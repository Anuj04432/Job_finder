"""
Job search via the Adzuna API, with resume-skill matching.

Get free credentials at https://developer.adzuna.com (instant, no approval wait).

Set as environment variables before running:
    $env:ADZUNA_APP_ID = "your-id-here"
    $env:ADZUNA_APP_KEY = "your-key-here"

Usage:
    python job_search.py "data scientist" "New York" --skills "Python,SQL,Machine Learning"
"""

import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()


ADZUNA_BASE_URL = "https://api.adzuna.com/v1/api/jobs"


def search_jobs(
    keywords: str,
    location: str,
    country_code: str = "us",
    results_per_page: int = 20,
    app_id: str | None = None,
    app_key: str | None = None,
) -> list[dict]:
    """
    Search Adzuna for jobs matching the given keywords and location.
    Returns a cleaned list of job dicts. Returns an empty list if there
    are simply no matching jobs (not an error) — raises RuntimeError only
    for actual problems (missing credentials, bad request, network issue).
    """
    resolved_app_id = app_id or os.environ.get("ADZUNA_APP_ID")
    resolved_app_key = app_key or os.environ.get("ADZUNA_API_KEY")

    if not resolved_app_id or not resolved_app_key:
        raise RuntimeError(
            "Missing Adzuna credentials. Set ADZUNA_APP_ID and ADZUNA_APP_KEY "
            "environment variables, or pass app_id=/app_key= directly. "
            "Get free credentials at https://developer.adzuna.com"
        )

    # country_code goes in the URL PATH, not as a query parameter
    url = f"{ADZUNA_BASE_URL}/{country_code.lower()}/search/1"

    params = {
        "app_id": resolved_app_id,
        "app_key": resolved_app_key,
        "what": keywords,
        "where": location,
        "results_per_page": results_per_page,
        "content-type": "application/json",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
    except requests.RequestException as e:
        raise RuntimeError(f"Could not reach Adzuna: {e}")

    if response.status_code == 401:
        raise RuntimeError("Adzuna rejected the request — check your APP_ID/APP_KEY are correct.")
    if response.status_code != 200:
        raise RuntimeError(f"Adzuna returned an error (status {response.status_code}): {response.text[:200]}")

    data = response.json()
    raw_results = data.get("results", [])

    jobs = []
    for r in raw_results:
        jobs.append({
            "title": r.get("title", "Untitled role"),
            "company": (r.get("company") or {}).get("display_name", "Unknown company"),
            "location": (r.get("location") or {}).get("display_name", location),
            "description": r.get("description", ""),
            "apply_url": r.get("redirect_url", ""),
            "salary_min": r.get("salary_min"),
            "salary_max": r.get("salary_max"),
            "created": r.get("created"),
        })

    return jobs


def _tokenize(text: str) -> set:
    """Lowercase, strip punctuation, split into a set of words for matching."""
    return set(re.findall(r"[a-z0-9\+\#\.]+", text.lower()))


def score_job_match(job: dict, resume_skills: list[str]) -> dict:
    """
    Adds 'matched_skills' and 'match_score' (0-100) to a copy of the job dict,
    based on how many resume skills appear in the job's description text.
    """
    description_tokens = _tokenize(job.get("description", ""))

    matched_skills = []
    for skill in resume_skills:
        if not isinstance(skill, str) or not skill.strip():
            continue
        skill_tokens = _tokenize(skill)
        # A multi-word skill (e.g. "machine learning") counts as matched if
        # ALL its words appear somewhere in the description
        if skill_tokens and skill_tokens.issubset(description_tokens):
            matched_skills.append(skill)

    match_score = round(100 * len(matched_skills) / len(resume_skills), 1) if resume_skills else 0.0

    job_with_score = dict(job)
    job_with_score["matched_skills"] = matched_skills
    job_with_score["match_score"] = match_score
    return job_with_score


def rank_jobs(jobs: list[dict], resume_skills: list[str]) -> list[dict]:
    """Scores every job against the resume's skills and sorts best-match first."""
    scored = [score_job_match(job, resume_skills) for job in jobs]
    scored.sort(key=lambda j: j["match_score"], reverse=True)
    return scored


if __name__ == "__main__":
    import sys
    import json
    import argparse

    parser = argparse.ArgumentParser(description="Search Adzuna and rank results against resume skills.")
    parser.add_argument("keywords", help="Job title or keywords, e.g. 'data scientist'")
    parser.add_argument("location", help="City/state, or 'remote'")
    parser.add_argument("--country", default="us", help="ISO country code (default: us)")
    parser.add_argument("--skills", default="", help="Comma-separated resume skills for match scoring")
    args = parser.parse_args()

    try:
        jobs = search_jobs(args.keywords, args.location, country_code=args.country)
    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)

    resume_skills = [s.strip() for s in args.skills.split(",") if s.strip()]
    if resume_skills:
        jobs = rank_jobs(jobs, resume_skills)

    print(json.dumps(jobs, indent=2))