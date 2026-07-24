"""
Combined resume extraction: tries the Gemini LLM extractor first (best
quality), and automatically falls back to the rule-based/regex extractors
if the API call fails for any reason — missing/invalid key, rate limit,
network issue, model deprecation, etc.

Usage:
    python extract_resume_fallback.py extracted_text.txt

Returns a dict with the same overall shape either way, plus an
"extraction_method" field ("llm" or "rule_based") so your UI can show
the user which path was used.
"""

import sys
import json

from extract_resume_llm import extract_resume_data
from extract_personal_info import extract_personal_info
from extract_summary import extract_summary
from extract_certifications_achievements import extract_certifications_and_achievements
from extract_projects import extract_projects
from extract_experience_education_skills import (
    extract_skills,
    extract_education,
    extract_experience,
)


def extract_resume_rule_based(text: str) -> dict:
    """Assemble a resume data dict using only the regex/heuristic extractors."""
    personal = extract_personal_info(text)
    cert_result = extract_certifications_and_achievements(text)

    # Flatten combined cert/achievement result into simple lists either way
    certifications = cert_result["certifications"] or cert_result["combined"]
    achievements = cert_result["achievements"]

    return {
        "name": personal.get("name"),
        "email": personal.get("email"),
        "phone": personal.get("phone"),
        "location": None,  # not covered by the rule-based extractors
        "links": personal.get("links", {}),
        "summary": extract_summary(text),
        "skills": extract_skills(text),
        "experience": extract_experience(text),
        "education": extract_education(text),
        "projects": extract_projects(text),
        "certifications": certifications,
        "achievements": achievements,
    }


def get_resume_data(text: str, api_key: str | None = None) -> dict:
    """
    Main entry point. Tries the Gemini-based extraction first.
    Falls back to rule-based extraction on ANY failure, so the app
    always returns something rather than crashing.
    """
    try:
        result = extract_resume_data(text, api_key=api_key)
        data = result.model_dump()
        data["extraction_method"] = "llm"
        return data
    except Exception as e:
        print(f"[warning] LLM extraction failed ({e}); falling back to rule-based extraction.",
              file=sys.stderr)
        data = extract_resume_rule_based(text)
        data["extraction_method"] = "rule_based"
        return data


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_resume_fallback.py <path_to_text_file>")
        sys.exit(1)

    text = None
    for encoding in ("utf-8", "utf-8-sig", "utf-16"):
        try:
            with open(sys.argv[1], "r", encoding=encoding) as f:
                text = f.read()
            break
        except UnicodeDecodeError:
            continue

    if text is None:
        print(f"Could not decode {sys.argv[1]} with utf-8, utf-8-sig, or utf-16.")
        sys.exit(1)

    result = get_resume_data(text)
    print(json.dumps(result, indent=2))