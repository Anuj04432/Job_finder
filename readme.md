# 📄 Resume-Analyzer & Job-Finder

An intelligent, AI-powered resume analysis, skill-gap assessment, and job-matching platform built with Python, Streamlit, Google Gemini, and the Adzuna Jobs API.

---

## 🚀 Completed Features (Current Progress)

### 1. 📑 Robust Multi-Format Document Extraction
- **Supported Formats:** PDF, DOCX, PNG, JPG, JPEG, TIFF, BMP.
- **Primary Parser:** Microsoft's **MarkItDown** for structure-aware markdown extraction (preserving headers `#`, lists, tables).
- **Multi-Tier Fallbacks:**
  - **Native PDFs:** `pdfplumber`
  - **Scanned / Image PDFs:** PyMuPDF (`fitz`) page rendering + **Tesseract OCR**
  - **Word Documents:** `python-docx`
  - **Images:** Local `pytesseract` OCR

### 2. 🧠 Dual-Path Structured Parsing Engine
- **AI Extraction (Google Gemini):**
  - Uses `google-genai` SDK with strict **Pydantic schema validation** (`ResumeData`).
  - Extracts candidate contact info, links, summary, structured work experiences, education history, projects, certifications, and achievements.
- **Rule-Based & Heuristic Fallback:**
  - Offline regex and `spaCy` NLP extractors for personal info, summary, experience, education, projects, and certifications when API keys are absent or network is unavailable.
- **Hybrid Skill Union:** Combines AI and rule-based skill sets to maximize skill capture and prevent omissions.

### 3. 🎯 Intelligent Skill-Gap & Role Matcher
- **Weighted Role Matching:** Differentiates between **Core skills** (2x weight) and **Nice-to-have skills** (1x weight) across 10 standard tech roles.
- **Fuzzy Resolution & Synonyms:** Employs `difflib` and synonym mapping (e.g., `postgres` → `postgresql`, `ml` → `machine learning`) to handle terminology variations.
- **Actionable Insights:** Outputs fit percentage, present skills, missing skills, and a prioritized **"Skills to learn next"** roadmap for the best-fit role.

### 4. 🔍 Live Job Search & Skill Match Ranking
- **Adzuna API Integration:** Fetches live job openings matching the chosen target role.
- **Resume-Skill Match Scoring:** Scores and ranks live job postings based on the percentage of resume skills present in the job description.

### 5. 💻 Interactive Guided Wizard UI (Streamlit)
- **Step 1 (Upload & Analyze):** Upload resume with hash-based caching to prevent redundant API calls during wizard navigation.
- **Step 2 (Role Selection):** View top-3 best-fit roles with match scores, or explore fit for any other tech role via dropdown.
- **Step 3 (Skill Gap & Live Jobs):** Detailed breakdown of present vs. missing core/nice-to-have skills, plus live matched job listings with direct application links.

---

## 📁 Project Structure

```
Job_finder/
├── parser/
│   ├── app.py                             # Streamlit guided wizard application
│   ├── extract_resume_text.py             # Multi-format document text & OCR extraction
│   ├── extract_resume_llm.py              # Gemini AI structured JSON extractor
│   ├── extract_resume_fallback.py         # Dual hybrid extractor (LLM + Rule-based)
│   ├── extract_personal_info.py           # Contact information & name heuristics
│   ├── extract_summary.py                 # Resume summary/objective extractor
│   ├── extract_projects.py                # Project parsing & bullet stitching
│   ├── extract_certifications_achievements.py
│   ├── extract_experience_education_skills.py
│   └── job_search.py                      # Adzuna job search API + ranking engine
├── skills_gap/
│   └── skills_gap.py                      # Weighted role scoring & fuzzy matching logic
├── keywords/
│   └── keys.py                            # Role keyword definitions
├── requirements.txt                       # Project dependencies
├── pyproject.toml                         # Project metadata
└── README.md                              # Documentation
```

---

## ⚙️ Setup & Installation

### 1. Prerequisites
- Python 3.12+
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) (for scanned PDFs and image resumes)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Configure API Keys
Create a `.env` file in the root directory (or set system environment variables):

```env
# Google Gemini API Key (Free tier at https://aistudio.google.com/apikey)
GEMINI_API_KEY=your_gemini_api_key_here

# Adzuna Jobs API (Free credentials at https://developer.adzuna.com)
ADZUNA_APP_ID=your_adzuna_app_id_here
ADZUNA_API_KEY=your_adzuna_api_key_here
```

---

## 🚀 Running the App

The project is built as an editable package using `uv`, meaning the internal folders (`parser`, `skills_gap`, `keywords`) are globally importable within the project environment. 

To ensure the environment and absolute imports work correctly, **always run the app from the root `Job_finder` directory** (do not `cd` into `parser/`).

```bash
uv run streamlit run parser/app.py
```

---

## 🗺️ Roadmap & Next Phases

- [ ] **AI Resume Tailoring / Enhancer (Step 4):** Use Gemini to rephrase project bullets and tailor resume content for target roles.
- [ ] **ATS Score Breakdown:** Calculate keyword density and format compliance score against target job descriptions.
- [ ] **Resume Export:** Download optimized resume in formatted PDF, DOCX, or Markdown.
- [ ] **Job Search UI Filters:** Allow users to filter jobs by location, country, salary range, and remote preference directly from the UI.