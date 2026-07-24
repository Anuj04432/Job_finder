import re


CERTIFICATION_HEADERS = {
    "certifications", "certificates", "certification", "licenses",
    "licenses and certifications", "licenses and certifications",
    "professional certifications", "certifications and licenses",
    "certifications and achievements", "certifications achievements",
}

ACHIEVEMENT_HEADERS = {
    "achievements", "accomplishments", "key achievements",
    "honors and awards", "honors and awards", "awards", "awards and honors",
    "awards and honors", "recognitions", "honors",
    "certifications and achievements", "certifications achievements",
}

# All other section headers, used so extraction stops correctly when it
# hits a different section (reused/expanded from extract_summary.py)
OTHER_SECTION_HEADERS = {
    "summary", "professional summary", "objective", "career objective",
    "profile", "about me", "about",
    "experience", "work experience", "professional experience",
    "employment history", "education", "skills", "technical skills",
    "core skills", "key skills", "projects", "publications", "languages",
    "interests", "hobbies", "references", "training",
    "volunteer experience", "extracurricular activities", "activities",
    "additional information", "additional info", "other information",
    "declaration", "personal details", "personal information",
    "strengths", "areas of expertise", "hobbies and interests",
}

ALL_KNOWN_HEADERS = CERTIFICATION_HEADERS | ACHIEVEMENT_HEADERS | OTHER_SECTION_HEADERS

BULLET_PREFIX = re.compile(r"^[\-\u2022\*\u25CF\u25AA]\s*|^\d+[\.\)]\s*")


def _normalize_header(line: str) -> str:
    line = line.lower().replace("&", "and")
    line = re.sub(r"[^a-z ]", "", line)
    line = re.sub(r"\s+", " ", line).strip()
    return line


def _split_into_items(block_lines: list[str]) -> list[str]:
    items = []
    current_text = None
    current_is_bulleted = False

    def finalize():
        nonlocal current_text, current_is_bulleted
        if current_text is None:
            return
        text = current_text.strip()
        # Only comma-split items that were never bulleted — a bulleted
        # item stays whole even if its own text contains commas.
        if not current_is_bulleted and ("," in text or ";" in text) and len(text.split()) <= 20:
            parts = re.split(r"[,;]\s*", text)
            items.extend(p.strip() for p in parts if p.strip())
        else:
            items.append(text)
        current_text = None
        current_is_bulleted = False

    for line in block_lines:
        line = line.strip()
        if not line:
            continue

        has_bullet = bool(BULLET_PREFIX.match(line))
        cleaned = BULLET_PREFIX.sub("", line).strip()

        if has_bullet:
            finalize()  # push whatever item was being built
            current_text = cleaned
            current_is_bulleted = True
        else:
            if current_text is None:
                # No bullet yet seen — this starts a new (non-bulleted) item
                current_text = cleaned
                current_is_bulleted = False
            else:
                # Continuation/wrapped line — merge into the current item
                current_text += " " + cleaned

    finalize()

    # Remove duplicates while preserving order
    seen = set()
    unique_items = []
    for item in items:
        if item.lower() not in seen:
            seen.add(item.lower())
            unique_items.append(item)

    return unique_items


def _extract_section(text: str, section_headers: set) -> list[str]:
    lines = [line.rstrip() for line in text.splitlines()]
    non_empty_indices = [i for i, line in enumerate(lines) if line.strip()]

    for idx in non_empty_indices:
        normalized = _normalize_header(lines[idx])
        if normalized in section_headers:
            block_lines = []
            blank_streak = 0
            for j in range(idx + 1, len(lines)):
                line = lines[j].strip()
                if not line:
                    blank_streak += 1
                    if blank_streak >= 2 and block_lines:
                        break  # double blank line = section likely ended
                    continue
                blank_streak = 0
                if _normalize_header(line) in ALL_KNOWN_HEADERS:
                    break
                block_lines.append(line)
            items = _split_into_items(block_lines)
            if items:
                return items

    return []


def extract_certifications(text: str) -> list[str]:
    return _extract_section(text, CERTIFICATION_HEADERS)


def extract_achievements(text: str) -> list[str]:
    return _extract_section(text, ACHIEVEMENT_HEADERS)


COMBINED_HEADERS = {"certifications and achievements", "certifications achievements"}


def extract_certifications_and_achievements(text: str) -> dict:
    """
    Smart wrapper: if the resume uses a single combined header (e.g.
    "Certifications & Achievements"), return one merged list under
    'combined' instead of duplicating the same items under both
    'certifications' and 'achievements'. If they're genuinely separate
    sections, returns them separately as usual.
    """
    lines = [line.rstrip() for line in text.splitlines()]
    for line in lines:
        if _normalize_header(line) in COMBINED_HEADERS:
            items = _extract_section(text, COMBINED_HEADERS)
            return {"combined": items, "certifications": [], "achievements": []}

    return {
        "combined": [],
        "certifications": extract_certifications(text),
        "achievements": extract_achievements(text),
    }


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) != 2:
        print("Usage: python extract_certifications_achievements.py <path_to_text_file>")
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        resume_text = f.read()

    result = extract_certifications_and_achievements(resume_text)
    print(json.dumps(result, indent=2))