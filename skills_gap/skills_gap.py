"""
Role recommendation + skill-gap analysis (v2).

Improvements over v1:
  - Each role's skills are split into "core" (heavily weighted) and
    "nice_to_have" (lightly weighted) for a more realistic match score.
  - Fuzzy matching (via difflib) catches close variants your synonym list
    doesn't explicitly cover (e.g. "Postgres" vs "PostgreSQL").
  - Returns a prioritized "skills to learn next" list — the missing CORE
    skills for your best-fit role, since those move the needle most.
"""

import re
import difflib


# ---------- Reference skill sets per role ----------
# "core" = skills that strongly define the role (weighted x2)
# "nice_to_have" = skills that help but aren't essential (weighted x1)

ROLE_SKILLS = {
    "Data Scientist": {
        "core": {"python", "sql", "machine learning", "statistics", "pandas", "numpy"},
        "nice_to_have": {"scikit-learn", "deep learning", "data visualization",
                          "tensorflow", "pytorch", "r", "tableau", "power bi"},
    },
    "Data Analyst": {
        "core": {"sql", "excel", "data visualization", "statistics", "reporting"},
        "nice_to_have": {"python", "power bi", "tableau", "data cleaning",
                          "google sheets", "dashboarding", "a/b testing"},
    },
    "Machine Learning Engineer": {
        "core": {"python", "machine learning", "deep learning", "tensorflow", "pytorch"},
        "nice_to_have": {"docker", "kubernetes", "mlops", "model deployment",
                          "aws", "gcp", "azure", "sql", "fastapi", "flask", "git"},
    },
    "Backend Developer": {
        "core": {"python", "sql", "rest api", "git"},
        "nice_to_have": {"java", "node.js", "fastapi", "flask", "django", "docker",
                          "postgresql", "mongodb", "microservices", "aws",
                          "system design", "redis"},
    },
    "Frontend Developer": {
        "core": {"javascript", "react", "html", "css"},
        "nice_to_have": {"typescript", "next.js", "vue", "redux", "tailwind css",
                          "git", "responsive design", "webpack", "figma"},
    },
    "Full Stack Developer": {
        "core": {"javascript", "python", "react", "sql", "html", "css"},
        "nice_to_have": {"node.js", "rest api", "git", "mongodb", "docker",
                          "typescript", "express.js"},
    },
    "DevOps Engineer": {
        "core": {"docker", "kubernetes", "ci/cd", "linux"},
        "nice_to_have": {"aws", "azure", "gcp", "terraform", "jenkins", "bash",
                          "git", "ansible", "monitoring", "prometheus", "grafana"},
    },
    "Software Engineer": {
        "core": {"data structures", "algorithms", "git", "system design"},
        "nice_to_have": {"python", "java", "c++", "sql", "rest api", "docker",
                          "testing", "object-oriented programming"},
    },
    "Product Manager": {
        "core": {"product strategy", "roadmapping", "stakeholder management", "agile"},
        "nice_to_have": {"user research", "scrum", "data analysis", "sql",
                          "wireframing", "a/b testing", "jira", "market research"},
    },
    "UI/UX Designer": {
        "core": {"figma", "wireframing", "prototyping", "user research"},
        "nice_to_have": {"adobe xd", "sketch", "usability testing",
                          "design systems", "interaction design", "photoshop"},
    },
}


SYNONYMS = {
    "ml": "machine learning", "dl": "deep learning", "js": "javascript",
    "ts": "typescript", "nlp": "natural language processing",
    "cv": "computer vision", "k8s": "kubernetes", "postgres": "postgresql",
    "reactjs": "react", "node": "node.js", "oop": "object-oriented programming",
}

# Every distinct skill name used anywhere in ROLE_SKILLS — used as the
# fuzzy-matching vocabulary.
ALL_KNOWN_SKILLS = sorted({
    skill
    for role in ROLE_SKILLS.values()
    for group in (role["core"], role["nice_to_have"])
    for skill in group
})


def _normalize_skill(skill: str) -> str:
    cleaned = skill.strip().lower()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return SYNONYMS.get(cleaned, cleaned)


def _fuzzy_resolve(skill: str, cutoff: float = 0.82) -> str:
    """
    If a normalized skill doesn't exactly match anything in our known skill
    vocabulary, try a close match (handles minor spelling/formatting
    differences like 'Postgre SQL' vs 'postgresql').
    Falls back to the original normalized string if nothing close is found.
    """
    if skill in ALL_KNOWN_SKILLS:
        return skill
    close = difflib.get_close_matches(skill, ALL_KNOWN_SKILLS, n=1, cutoff=cutoff)
    return close[0] if close else skill


def _normalize_resume_skills(resume_skills: list) -> set:
    result = set()
    for s in resume_skills:
        if not isinstance(s, str) or not s.strip():
            continue  # skip None, empty strings, or unexpected non-string entries
        normalized = _normalize_skill(s)
        resolved = _fuzzy_resolve(normalized)
        result.add(resolved)
    return result


def analyze_roles(resume_skills: list, top_n: int = 3) -> dict:
    """
    Weighted role match: core skills count double toward the match score.
    Returns top N role matches plus a prioritized "skills to learn next"
    list for the single best-fit role.

    Always returns a dict with 'top_matches', 'best_fit_role', and
    'skills_to_learn_next' keys, even if resume_skills is empty or messy —
    callers can safely use .get() but this guarantees the keys exist.
    """
    if not resume_skills:
        return {"top_matches": [], "best_fit_role": None, "skills_to_learn_next": []}

    normalized_resume = _normalize_resume_skills(resume_skills)

    role_scores = []
    for role, groups in ROLE_SKILLS.items():
        core = groups["core"]
        nice = groups["nice_to_have"]

        present_core = normalized_resume & core
        missing_core = core - normalized_resume
        present_nice = normalized_resume & nice
        missing_nice = nice - normalized_resume

        weighted_have = 2 * len(present_core) + 1 * len(present_nice)
        weighted_total = 2 * len(core) + 1 * len(nice)
        match_pct = round(100 * weighted_have / weighted_total, 1) if weighted_total else 0

        role_scores.append({
            "role": role,
            "match_percentage": match_pct,
            "present_core_skills": sorted(present_core),
            "missing_core_skills": sorted(missing_core),
            "present_nice_to_have_skills": sorted(present_nice),
            "missing_nice_to_have_skills": sorted(missing_nice),
        })

    role_scores.sort(key=lambda r: r["match_percentage"], reverse=True)
    top_matches = role_scores[:top_n]

    # Prioritized "learn next" list: missing CORE skills of the best-fit role
    # move the needle most, so surface those first.
    skills_to_learn_next = top_matches[0]["missing_core_skills"] if top_matches else []

    return {
        "top_matches": top_matches,
        "all_roles": role_scores,  # full ranked list, for manual role selection
        "best_fit_role": top_matches[0]["role"] if top_matches else None,
        "skills_to_learn_next": skills_to_learn_next,
    }


def list_all_roles() -> list[str]:
    """All role names this module knows about, for building a manual-pick dropdown."""
    return sorted(ROLE_SKILLS.keys())


def get_role_breakdown(resume_skills: list, role_name: str) -> dict | None:
    """
    Get the present/missing skill breakdown for ONE specific role, regardless
    of whether it's in that resume's top matches. Returns None if role_name
    isn't a known role.
    """
    if role_name not in ROLE_SKILLS:
        return None
    analysis = analyze_roles(resume_skills, top_n=len(ROLE_SKILLS))
    for entry in analysis["all_roles"]:
        if entry["role"] == role_name:
            return entry
    return None


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) != 2:
        print("Usage: python skills_gap.py <comma_separated_skills>")
        print('Example: python skills_gap.py "Python, SQL, Machine Learning, Docker"')
        sys.exit(1)

    skills = [s.strip() for s in sys.argv[1].split(",") if s.strip()]
    result = analyze_roles(skills)
    print(json.dumps(result, indent=2))