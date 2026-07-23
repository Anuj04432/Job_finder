"""
Extract the "professional summary" (also called Objective, Profile,
About Me, Career Objective, etc.) from resume text.

Strategy:
1. Look for a line that IS one of the known summary-section header names.
2. Capture everything after it, up until the next known section header
   (Experience, Education, Skills, etc.) or the end of the document.
3. If no explicit header is found, fall back to grabbing the first
   substantial paragraph near the top of the resume (after the name/contact
   block), since some resumes include a summary with no header at all.
"""

import re


# Headers that mark the START of a summary-like section.
# Matched as a whole line (case-insensitive, ignoring punctuation/colons).
SUMMARY_HEADERS = {
    "summary", "professional summary", "career summary", "profile",
    "professional profile", "objective", "career objective",
    "about me", "about", "personal statement", "executive summary",
    "candidate summary", "overview",
}

# Headers that mark the END of the summary section (start of the next section).
NEXT_SECTION_HEADERS = {
    "experience", "work experience", "professional experience",
    "employment history", "education", "skills", "technical skills",
    "core skills", "key skills", "projects", "certifications",
    "achievements", "awards", "publications", "languages",
    "interests", "hobbies", "references", "training", "volunteer experience",
    "extracurricular activities", "activities",
}


def _normalize_header(line: str) -> str:
    """Strip punctuation/colons and lowercase, for header matching."""
    return re.sub(r"[^a-z ]", "", line.lower()).strip()


def extract_summary(text: str) -> str | None:
    lines = [line.rstrip() for line in text.splitlines()]
    non_empty_indices = [i for i, line in enumerate(lines) if line.strip()]

    # --- Strategy 1: explicit header match ---
    for idx in non_empty_indices:
        normalized = _normalize_header(lines[idx])
        if normalized in SUMMARY_HEADERS:
            summary_lines = []
            for j in range(idx + 1, len(lines)):
                line = lines[j].strip()
                if not line:
                    if summary_lines:  # stop at first blank line after content starts
                        break
                    continue
                if _normalize_header(line) in NEXT_SECTION_HEADERS:
                    break
                summary_lines.append(line)
            summary = " ".join(summary_lines).strip()
            if summary:
                return summary

    # --- Strategy 2: fallback — first substantial paragraph near the top ---
    # Skip past what looks like name/contact info (short lines, emails, phones, links)
    # then grab the first paragraph-like block of reasonable length.
    contact_like = re.compile(r"@|http|www\.|linkedin|github|^\+?\d[\d\s\-]{7,}$")

    para_lines = []
    started = False
    for idx in non_empty_indices[:30]:  # only look near the top of the resume
        line = lines[idx].strip()
        normalized = _normalize_header(line)

        if normalized in NEXT_SECTION_HEADERS or normalized in SUMMARY_HEADERS:
            break

        word_count = len(line.split())
        is_contact_line = bool(contact_like.search(line)) or word_count <= 2

        if not started:
            # Look for the first line that seems like real prose (a sentence),
            # not a name/title/contact line
            if is_contact_line or word_count < 6:
                continue
            started = True
            para_lines.append(line)
        else:
            if is_contact_line:
                break
            para_lines.append(line)

    paragraph = " ".join(para_lines).strip()
    # Only trust this fallback if it's a reasonably sentence-like paragraph
    if paragraph and len(paragraph.split()) >= 8:
        return paragraph

    return None


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python extract_summary.py <path_to_text_file>")
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        resume_text = f.read()

    summary = extract_summary(resume_text)
    print(summary if summary else "No summary/objective section found.")