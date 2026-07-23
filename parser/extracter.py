# from pypdf import PdfReader
# import re

# file = PdfReader("Resume.pdf")
# text1 = ""
# for i in file.pages:
#     text1 += i.extract_text()+"\n"
# def name(text):
#     name = None
#     if name is None:
#         lines = [line.strip() for line in text.split("\n") if line.strip()]
#         if lines:
#             name = lines[0] 
#     return name

# def email(text):
#     email = re.search(r'[A-Za-z0-9]+@[A-Za-z0-9]+\.[A-Za-z]{2,}',text)

#     if not email:
#         return "Email not provided in the resume"
#     else:
#         return email.group()

# def number(text):
#     number = re.search(r'\+?9?1?\s?\d{5}[\s+]?\d{5}', text)
#     if number:
#         return number.group()
#     else:
#         return None


import re

try:
    import spacy
    _nlp = spacy.load("en_core_web_sm")
    _SPACY_AVAILABLE = True
except Exception:
    _SPACY_AVAILABLE = False
    _nlp = None


# ---------- Regex patterns ----------

EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

# Matches most phone formats: +91 98765 43210, (123) 456-7890, 123-456-7890, 9876543210, etc.
# Loose match on a run of digits/spaces/dashes/parens/dots; we validate the
# actual digit count afterward in extract_phone().
PHONE_PATTERN = re.compile(r"\+?\d[\d\s\-\.\(\)]{7,16}\d")

LINKEDIN_PATTERN = re.compile(r"(https?://)?(www\.)?linkedin\.com/in/[A-Za-z0-9\-_/]+", re.IGNORECASE)
GITHUB_PATTERN = re.compile(r"(https?://)?(www\.)?github\.com/[A-Za-z0-9\-_/]+", re.IGNORECASE)
PORTFOLIO_PATTERN = re.compile(
    r"(https?://)?(www\.)?[A-Za-z0-9\-]+\.(dev|me|io|com|net|in)(/[A-Za-z0-9\-_/]*)?",
    re.IGNORECASE
)

# Common email/webmail providers to exclude when looking for a personal portfolio link
_EMAIL_PROVIDER_DOMAINS = (
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com",
    "icloud.com", "protonmail.com", "aol.com", "live.com",
)


def extract_email(text: str) -> str | None:
    match = EMAIL_PATTERN.search(text)
    return match.group(0) if match else None


def extract_phone(text: str) -> str | None:
    for match in PHONE_PATTERN.finditer(text):
        candidate = match.group(0).strip()
        digits_only = re.sub(r"\D", "", candidate)
        # Real phone numbers have 10-13 digits; this filters out stray
        # short numbers (e.g. "2023", zip codes) that the regex might catch
        if 10 <= len(digits_only) <= 13:
            return candidate
    return None


def _looks_like_email_domain(url: str) -> bool:
    """Returns True if the matched URL is actually part of an email address's domain."""
    lowered = url.lower().lstrip("www.")
    return any(lowered == domain or lowered.startswith(domain) for domain in _EMAIL_PROVIDER_DOMAINS)


def extract_links(text: str) -> dict:
    linkedin = LINKEDIN_PATTERN.search(text)
    github = GITHUB_PATTERN.search(text)

    links = {
        "linkedin": linkedin.group(0) if linkedin else None,
        "github": github.group(0) if github else None,
        "portfolio": None,
    }

    # Look for a personal site that isn't linkedin/github/an email domain (basic heuristic)
    for match in PORTFOLIO_PATTERN.finditer(text):
        url = match.group(0)
        lower_url = url.lower()

        # Skip if this match is actually the domain part of an email address
        # (i.e. immediately preceded by '@' in the source text)
        start = match.start()
        if start > 0 and text[start - 1] == "@":
            continue

        if (
            "linkedin.com" not in lower_url
            and "github.com" not in lower_url
            and not _looks_like_email_domain(url)
        ):
            links["portfolio"] = url
            break

    return links


def _plausibly_matches_email(candidate: str, email: str) -> bool:
    """
    Sanity check: does this name candidate share letters with the email's
    local part? A real name usually does (e.g. 'Anuj Wagmore' vs
    'anujwagmore835'); a stray skill/tool name usually won't.
    This catches blacklist misses without needing an exhaustive keyword list.
    """
    if not email or "@" not in email:
        return True  # can't check, so don't block it

    local_part = re.sub(r"[^a-z]", "", email.split("@")[0].lower())
    candidate_letters = re.sub(r"[^a-z]", "", candidate.lower())

    if not local_part or not candidate_letters:
        return True

    # Check what fraction of the candidate's letters appear, in order,
    # as a subsequence of the email local part (cheap fuzzy containment check)
    matched = 0
    pos = 0
    for ch in candidate_letters:
        idx = local_part.find(ch, pos)
        if idx != -1:
            matched += 1
            pos = idx + 1

    overlap_ratio = matched / len(candidate_letters)
    return overlap_ratio >= 0.6


def extract_name(text: str, email: str | None = None) -> str | None:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    top_chunk = "\n".join(lines[:10])

    if _SPACY_AVAILABLE:
        doc = _nlp(top_chunk)
        for ent in doc.ents:
            if (
                ent.label_ == "PERSON"
                and not _is_blacklisted_line(ent.text)
                and _plausibly_matches_email(ent.text, email)
            ):
                return ent.text.strip()

    # Fallback heuristic
    for line in lines[:8]:
        if _is_blacklisted_line(line):
            continue
        if EMAIL_PATTERN.search(line) or "http" in line.lower() or "www." in line.lower():
            continue
        if PHONE_PATTERN.search(line) and len(re.sub(r"\D", "", line)) >= 8:
            continue
        word_count = len(line.split())
        if 1 <= word_count <= 4 and sum(c.isalpha() or c.isspace() for c in line) / len(line) > 0.8:
            if _plausibly_matches_email(line, email):
                return line

    return None


# Common resume section headers, skill names, and job titles that should
# never be mistaken for a person's name.
_NAME_BLACKLIST = {
    "resume", "curriculum vitae", "cv", "objective", "summary", "profile",
    "experience", "education", "skills", "projects", "certifications",
    "machine learning", "data science", "software engineer", "web developer",
    "full stack developer", "contact", "contact info", "career objective",
    "professional summary", "technical skills", "about me",
}


def _is_blacklisted_line(line: str) -> bool:
    return line.strip().lower() in _NAME_BLACKLIST


def _guess_name_from_email(email: str) -> str | None:
    """
    Fallback: derive a plausible name from the email's local part.
    e.g. 'anujwagmore835@gmail.com' -> tries to split into 'Anuj Wagmore'.
    This is a rough guess (no dictionary to know exact word boundaries),
    so it's only used when nothing else worked.
    """
    if not email or "@" not in email:
        return None

    local_part = email.split("@")[0]
    # Strip trailing digits (e.g. "835") and common separators
    local_part = re.sub(r"\d+$", "", local_part)
    local_part = re.sub(r"[._\-]+", " ", local_part).strip()

    if not local_part:
        return None

    return local_part.title() if " " in local_part else local_part.capitalize()


def extract_personal_info(text: str) -> dict:
    """Main entry point: returns a dict of extracted personal/contact info."""
    email = extract_email(text)
    name = extract_name(text, email=email)

    # Last resort: if no valid name was found, guess from the email
    if not name and email:
        name = _guess_name_from_email(email)

    return {
        "name": name,
        "email": email,
        "phone": extract_phone(text),
        "links": extract_links(text),
    }


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) != 2:
        print("Usage: python extract_personal_info.py <path_to_text_or_resume_txt_file>")
        sys.exit(1)

    resume_text = None
    # Try common encodings in order; Windows/PowerShell redirection (`>`) often
    # writes UTF-16 instead of UTF-8, which is the usual cause of decode errors here.
    for encoding in ("utf-8", "utf-8-sig", "utf-16"):
        try:
            with open(sys.argv[1], "r", encoding=encoding) as f:
                resume_text = f.read()
            break
        except UnicodeDecodeError:
            continue

    if resume_text is None:
        print(f"Could not decode {sys.argv[1]} with utf-8, utf-8-sig, or utf-16.")
        sys.exit(1)

    info = extract_personal_info(resume_text)
    print(json.dumps(info, indent=2))