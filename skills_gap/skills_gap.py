import re
from keywords.keys import ROLE_SKILLS,SYNONYMS

def _normalize_skill(skill: str) -> str:
    cleaned = skill.strip().lower()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return SYNONYMS.get(cleaned, cleaned)
 
 
def analyze_roles(resume_skills: list[str], top_n: int = 3) -> dict:
    """
    Compares resume skills against each role's reference skill set.
    Returns the top N best-matching roles (by percentage match), plus a
    detailed present/missing breakdown for the single best match.
    """
    normalized_resume_skills = {_normalize_skill(s) for s in resume_skills}
 
    role_scores = []
    for role, required_skills in ROLE_SKILLS.items():
        present = normalized_resume_skills & required_skills
        missing = required_skills - normalized_resume_skills
        match_pct = round(100 * len(present) / len(required_skills), 1) if required_skills else 0
        role_scores.append({
            "role": role,
            "match_percentage": match_pct,
            "present_skills": sorted(present),
            "missing_skills": sorted(missing),
        })
 
    role_scores.sort(key=lambda r: r["match_percentage"], reverse=True)
 
    return {
        "top_matches": role_scores[:top_n],
        "best_fit_role": role_scores[0]["role"] if role_scores else None,
    }
 
 
if __name__ == "__main__":
    import sys
    import json
 
    if len(sys.argv) != 2:
        print("Usage: python skill_gap_analysis.py <comma_separated_skills>")
        print('Example: python skill_gap_analysis.py "Python, SQL, Machine Learning, Docker"')
        sys.exit(1)
 
    skills = [s.strip() for s in sys.argv[1].split(",") if s.strip()]
    result = analyze_roles(skills)
    print(json.dumps(result, indent=2))