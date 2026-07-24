"""
Extract the Projects section from resume text as structured entries:
each project as {"title": ..., "description": [bullet points]}.

Strategy:
1. Find a line matching a known "Projects" section header.
2. Capture everything until the next known section header.
3. Within that block, a non-bulleted line starts a NEW project (its title);
   any bulleted lines that follow become that project's description points.
   Wrapped/continuation lines (no bullet, following a bullet) are merged
   back into the current bullet rather than treated as new lines.
"""

import re


PROJECT_HEADERS = {
    "projects", "personal projects", "academic projects", "key projects",
    "project experience", "academic and personal projects",
    "relevant projects", "notable projects", "major projects",
}

# Sections that mark the END of the projects block
OTHER_SECTION_HEADERS = {
    "summary", "professional summary", "objective", "career objective",
    "profile", "about me", "about",
    "experience", "work experience", "professional experience",
    "employment history", "education", "skills", "technical skills",
    "core skills", "key skills", "publications", "languages",
    "interests", "hobbies", "references", "training",
    "volunteer experience", "extracurricular activities", "activities",
    "additional information", "additional info", "other information",
    "declaration", "personal details", "personal information",
    "strengths", "areas of expertise",
    "certifications", "certificates", "licenses",
    "certifications and achievements", "certifications achievements",
    "achievements", "accomplishments", "honors and awards", "awards",
}

ALL_KNOWN_HEADERS = PROJECT_HEADERS | OTHER_SECTION_HEADERS

BULLET_PREFIX = re.compile(r"^[\-\u2022\*\u25CF\u25AA]\s*|^\d+[\.\)]\s*")


def _normalize_header(line: str) -> str:
    line = line.lower().replace("&", "and")
    line = re.sub(r"[^a-z ]", "", line)
    line = re.sub(r"\s+", " ", line).strip()
    return line


def _capture_section_block(text: str, section_headers: set) -> list[str]:
    """Return the raw lines between a matching header and the next known header."""
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
                        block_lines.append("")  # preserve as a separator marker
                    continue
                blank_streak = 0
                if _normalize_header(line) in ALL_KNOWN_HEADERS:
                    break
                block_lines.append(line)
            if block_lines:
                return block_lines

    return []


def _parse_projects(block_lines: list[str]) -> list[dict]:
    """
    Parse a projects block into structured entries.
    A non-bulleted line = a new project's title.
    Bulleted lines after it = description points for that project.
    A wrapped continuation line (no bullet, following a bullet line) merges
    into the last description point instead of becoming a new title.
    """
    projects = []
    current_project = None
    last_was_bullet = False

    def push_bullet(text: str):
        current_project["description"].append(text)

    for line in block_lines:
        if line == "":
            # Blank-line separator: whatever comes next is a new title,
            # never a continuation of the previous bullet.
            last_was_bullet = False
            continue

        line = line.strip()
        if not line:
            continue

        has_bullet = bool(BULLET_PREFIX.match(line))
        cleaned = BULLET_PREFIX.sub("", line).strip()

        if has_bullet:
            if current_project is None:
                # Bullet appeared before any title was found — start an
                # untitled project so we don't lose the content
                current_project = {"title": None, "description": []}
                projects.append(current_project)
            push_bullet(cleaned)
            last_was_bullet = True
        else:
            if last_was_bullet and current_project and current_project["description"]:
                # This is a wrapped continuation of the previous bullet
                current_project["description"][-1] += " " + cleaned
            else:
                # New project title
                current_project = {"title": cleaned, "description": []}
                projects.append(current_project)
                last_was_bullet = False

    return projects


def extract_projects(text: str) -> list[dict]:
    block_lines = _capture_section_block(text, PROJECT_HEADERS)
    if not block_lines:
        return []
    return _parse_projects(block_lines)


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) != 2:
        print("Usage: python extract_projects.py <path_to_text_file>")
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        resume_text = f.read()

    projects = extract_projects(resume_text)
    print(json.dumps(projects, indent=2) if projects else "No projects section found.")