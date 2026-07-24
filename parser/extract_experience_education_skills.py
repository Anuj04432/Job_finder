"""
Rule-based extractors for Skills, Education, and Experience —
fills the gap so the regex/heuristic pipeline can fully stand in
for the Gemini-based extractor if the API call fails.

These are intentionally simpler than the LLM version and won't handle
every resume layout perfectly (that's expected — see extract_resume_fallback.py
for how this is used only as a backup, not the primary path).
"""

import re


def _normalize_header(line: str) -> str:
    line = line.lower().replace("&", "and")
    line = re.sub(r"[^a-z ]", "", line)
    line = re.sub(r"\s+", " ", line).strip()
    return line


BULLET_PREFIX = re.compile(r"^[\-\u2022\*\u25CF\u25AA]\s*|^\d+[\.\)]\s*")

SKILLS_HEADERS = {"skills", "technical skills", "core skills", "key skills", "skill set"}
EDUCATION_HEADERS = {"education", "academic background", "educational qualifications"}
EXPERIENCE_HEADERS = {
    "experience", "work experience", "professional experience",
    "employment history", "work history",
}

# Every other known header, so each extractor knows where its section ends
ALL_SECTION_HEADERS = (
    SKILLS_HEADERS | EDUCATION_HEADERS | EXPERIENCE_HEADERS
    | {
        "summary", "professional summary", "objective", "career objective",
        "profile", "about me", "about", "projects", "personal projects",
        "academic projects", "key projects", "publications", "languages",
        "interests", "hobbies", "references", "training",
        "volunteer experience", "extracurricular activities", "activities",
        "additional information", "additional info", "other information",
        "declaration", "personal details", "personal information",
        "strengths", "areas of expertise",
        "certifications", "certificates", "licenses",
        "certifications and achievements", "certifications achievements",
        "achievements", "accomplishments", "honors and awards", "awards",
    }
)


def _capture_section_block(text: str, section_headers: set) -> list[str]:
    lines = [line.rstrip() for line in text.splitlines()]
    non_empty_indices = [i for i, line in enumerate(lines) if line.strip()]

    for idx in non_empty_indices:
        if _normalize_header(lines[idx]) in section_headers:
            block_lines = []
            blank_streak = 0
            for j in range(idx + 1, len(lines)):
                line = lines[j].strip()
                if not line:
                    blank_streak += 1
                    if blank_streak >= 2 and block_lines:
                        break
                    if block_lines:
                        block_lines.append("")
                    continue
                blank_streak = 0
                if _normalize_header(line) in ALL_SECTION_HEADERS:
                    break
                block_lines.append(line)
            if block_lines:
                return block_lines
    return []


# ---------- Skills ----------

def extract_skills(text: str) -> list[str]:
    """Returns a flat, deduplicated list of skills."""
    block_lines = _capture_section_block(text, SKILLS_HEADERS)
    if not block_lines:
        return []

    items = []
    for line in block_lines:
        if line == "":
            continue
        cleaned = BULLET_PREFIX.sub("", line).strip()
        if not cleaned:
            continue
        # Skills lines are usually comma/pipe/semicolon separated
        parts = re.split(r"[,;|]\s*", cleaned)
        items.extend(p.strip() for p in parts if p.strip())

    # Dedup, case-insensitive, preserve first-seen casing
    seen = set()
    unique_items = []
    for item in items:
        key = item.lower()
        if key not in seen:
            seen.add(key)
            unique_items.append(item)
    return unique_items


# ---------- Education ----------

def extract_education(text: str) -> list[dict]:
    """
    Returns a list of education entries. Each entry is kept as a raw
    combined string under 'raw_text' plus a best-effort 'degree' guess,
    since reliably splitting degree/institution/dates/GPA without an LLM
    is unreliable across the many formats resumes use.
    """
    block_lines = _capture_section_block(text, EDUCATION_HEADERS)
    if not block_lines:
        return []

    entries = []
    current_lines = []

    def push_entry():
        if current_lines:
            raw = " ".join(current_lines).strip()
            entries.append({"raw_text": raw})

    for line in block_lines:
        if line == "":
            push_entry()
            current_lines = []
            continue
        cleaned = BULLET_PREFIX.sub("", line).strip()
        if cleaned:
            current_lines.append(cleaned)

    push_entry()
    return entries


# ---------- Experience (same title+bullets pattern as projects) ----------

def _parse_title_bullet_entries(block_lines: list[str]) -> list[dict]:
    entries = []
    current = None
    last_was_bullet = False

    for line in block_lines:
        if line == "":
            last_was_bullet = False
            continue

        has_bullet = bool(BULLET_PREFIX.match(line))
        cleaned = BULLET_PREFIX.sub("", line).strip()
        if not cleaned:
            continue

        if has_bullet:
            if current is None:
                current = {"title": None, "description": []}
                entries.append(current)
            current["description"].append(cleaned)
            last_was_bullet = True
        else:
            if last_was_bullet and current and current["description"]:
                current["description"][-1] += " " + cleaned
            else:
                current = {"title": cleaned, "description": []}
                entries.append(current)
                last_was_bullet = False

    return entries


def extract_experience(text: str) -> list[dict]:
    """
    Returns a list of experience entries, each with a 'title' (role/company/
    dates line, however the resume formats it) and 'description' bullets.
    Unlike the LLM version, this does NOT reliably split company from job
    title from dates — that's a known limitation of the rule-based fallback.
    """
    block_lines = _capture_section_block(text, EXPERIENCE_HEADERS)
    if not block_lines:
        return []
    return _parse_title_bullet_entries(block_lines)


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) != 2:
        print("Usage: python extract_experience_education_skills.py <path_to_text_file>")
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        resume_text = f.read()

    result = {
        "skills": extract_skills(resume_text),
        "education": extract_education(resume_text),
        "experience": extract_experience(resume_text),
    }
    print(json.dumps(result, indent=2))