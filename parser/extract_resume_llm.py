"""
Full resume extraction using the Gemini API (google-genai SDK).

Replaces the separate regex-based extractors (name/email/phone, summary,
certifications, projects) with a single LLM call that reads the resume
text and returns clean structured JSON — no section-header guessing,
no bullet-parsing, no line-wrap bugs.

Install:
    pip install google-genai --break-system-packages

Get a free API key (no credit card required):
    https://aistudio.google.com/apikey

Set your key as an environment variable before running (recommended,
keeps it out of your code):

    # Windows PowerShell
    $env:GEMINI_API_KEY = "your-key-here"

    # macOS/Linux
    export GEMINI_API_KEY="your-key-here"

Usage:
    python extract_resume_llm.py extracted_text.txt
"""

import os
import sys
import json

from google import genai
from google.genai import types
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()




# ---------- Schema: defines exactly what fields come back, and their types ----------

class Link(BaseModel):
    linkedin: str | None = None
    github: str | None = None
    portfolio: str | None = None


class Project(BaseModel):
    title: str
    tech_stack: list[str] = []
    description: list[str] = []
    link: str | None = None


class Experience(BaseModel):
    title: str
    company: str
    location: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    description: list[str] = []


class Education(BaseModel):
    degree: str
    institution: str
    field: str | None = None
    graduation_date: str | None = None
    gpa: str | None = None


class ResumeData(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    links: Link = Link()
    summary: str | None = None
    skills: list[str] = []
    experience: list[Experience] = []
    education: list[Education] = []
    projects: list[Project] = []
    certifications: list[str] = []
    achievements: list[str] = []


# ---------- Extraction ----------

MODEL_NAME = "gemini-3.6-flash"  # current GA Flash-tier model (as of July 2026), free-tier eligible

EXTRACTION_PROMPT = """\
You are a precise resume-parsing assistant. Read the resume text below and \
extract all information into the given structure. Follow these rules:

- Only extract information that is actually present in the text. Never invent, \
guess, or hallucinate values that aren't there — leave fields empty/null instead.
- Normalize dates to a consistent "Mon YYYY" format where possible (e.g. "Jan 2023"), \
but preserve "Present" for ongoing roles/projects.
- For "skills", include a deduplicated flat list of all technical and soft skills \
mentioned anywhere in the resume, not just from a dedicated Skills section.
- For "certifications" and "achievements": if the resume has a single combined \
section for both, use your judgement to sort each item into whichever field it \
actually belongs to (a completed course/certificate → certifications; an award, \
ranking, or recognition → achievements). If you genuinely cannot tell, put it in \
achievements.
- For "projects", extract the project title, any listed tech stack, and its \
description bullet points. Merge together any lines that are clearly just a \
single description point that happens to wrap across a line break in the source.
- Ignore any decorative icons/emojis in section headers.

Resume text:
---
{resume_text}
---
"""


def extract_resume_data(resume_text: str, api_key: str | None = None) -> ResumeData:
    """
    Send resume text to Gemini and get back a fully structured ResumeData object.
    Raises RuntimeError with a clear message if the API key is missing or invalid.
    """

    key = os.environ.get("GEMINI_API_KEY")

    if not key:
        raise RuntimeError(
            "No Gemini API key found. Set the GEMINI_API_KEY environment variable, "
            "or pass api_key= directly. Get a free key at https://aistudio.google.com/apikey"
        )

    client = genai.Client(api_key=key)

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=EXTRACTION_PROMPT.format(resume_text=resume_text),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ResumeData,
            temperature=0,  # deterministic extraction, not creative generation
        ),
    )

    # response.parsed is the SDK's auto-parsed Pydantic object when response_schema is set
    if response.parsed is not None:
        return response.parsed

    # Fallback: manually parse the JSON text if auto-parsing didn't populate .parsed
    return ResumeData.model_validate_json(response.text)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_resume_llm.py <path_to_text_file>")
        sys.exit(1)

    text = None
    # Try common encodings; Windows/PowerShell redirection (`>`) often writes
    # UTF-16 instead of UTF-8, which is the usual cause of decode errors here.
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

    try:
        result = extract_resume_data(text)
    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Extraction failed: {e}")
        sys.exit(1)

    print(result.model_dump_json(indent=2))