"""
Streamlit UI for the resume analyzer — full pipeline version.

Combines:
  - extract_resume_text.py        (Step 1: PDF/DOCX/image -> raw text)
  - extract_resume_fallback.py    (Step 2: raw text -> structured data,
                                    tries Gemini first, falls back to
                                    rule-based extractors if the API fails)

Run with:
    streamlit run app.py

Requirements:
    pip install streamlit google-genai pydantic --break-system-packages

Set your Gemini API key before launching (optional — app still works
without it, just always uses the rule-based fallback):
    $env:GEMINI_API_KEY = "your-key-here"

Place this file in the SAME folder as all the extract_*.py files.
"""

import json
import tempfile
from pathlib import Path

import streamlit as st

from extract_resume_text import extract_resume_text
from extract_resume_fallback import get_resume_data


st.set_page_config(page_title="Resume Analyzer", page_icon="📄", layout="centered")

st.title("📄 Resume Analyzer")
st.caption("Upload a resume to extract structured data — powered by Gemini, with a rule-based fallback.")

uploaded_file = st.file_uploader(
    "Upload a resume",
    type=["pdf", "docx", "png", "jpg", "jpeg"],
)

if uploaded_file is not None:
    suffix = Path(uploaded_file.name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name

    with st.spinner("Extracting text..."):
        try:
            raw_text = extract_resume_text(tmp_path)
        except Exception as e:
            st.error(f"Text extraction failed: {e}")
            st.stop()

    with st.spinner("Analyzing resume..."):
        data = get_resume_data(raw_text)

    if data["extraction_method"] == "rule_based":
        st.warning(
            "⚠️ AI extraction unavailable (API key missing, rate-limited, or offline) — "
            "showing results from the rule-based fallback instead. Some fields may be "
            "less accurate or empty."
        )
    else:
        st.success("✅ Extracted with Gemini")

    # --- Personal Info ---
    st.subheader("👤 Personal Info")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Name", data.get("name") or "Not found")
        st.metric("Email", data.get("email") or "Not found")
    with col2:
        st.metric("Phone", data.get("phone") or "Not found")
        st.metric("Location", data.get("location") or "Not found")

    links = data.get("links") or {}
    if any(links.values()):
        st.write("**Links:**")
        for label, url in links.items():
            if url:
                st.write(f"- {label.capitalize()}: {url}")

    # --- Summary ---
    if data.get("summary"):
        st.subheader("🧾 Professional Summary")
        st.write(data["summary"])

    # --- Skills ---
    st.subheader("🛠️ Skills")
    if data.get("skills"):
        st.write(", ".join(data["skills"]))
    else:
        st.write("None found.")

    # --- Experience ---
    st.subheader("💼 Experience")
    if data.get("experience"):
        for exp in data["experience"]:
            # Rule-based fallback entries only have 'title' + 'description'.
            # LLM entries have separate title/company/dates fields.
            if "company" in exp:
                header = f"**{exp.get('title', '')}** — {exp.get('company', '')}"
                dates = " to ".join(filter(None, [exp.get("start_date"), exp.get("end_date")]))
                if dates:
                    header += f" ({dates})"
            else:
                header = f"**{exp.get('title') or 'Untitled role'}**"
            st.markdown(header)
            for point in exp.get("description", []):
                st.write(f"- {point}")
    else:
        st.write("None found.")

    # --- Education ---
    st.subheader("🎓 Education")
    if data.get("education"):
        for edu in data["education"]:
            if "raw_text" in edu:
                st.write(f"- {edu['raw_text']}")
            else:
                line = f"**{edu.get('degree', '')}** — {edu.get('institution', '')}"
                if edu.get("graduation_date"):
                    line += f" ({edu['graduation_date']})"
                st.markdown(line)
    else:
        st.write("None found.")

    # --- Projects ---
    st.subheader("💻 Projects")
    if data.get("projects"):
        for proj in data["projects"]:
            st.markdown(f"**{proj.get('title') or 'Untitled Project'}**")
            if proj.get("tech_stack"):
                st.caption(", ".join(proj["tech_stack"]))
            for point in proj.get("description", []):
                st.write(f"- {point}")
    else:
        st.write("None found.")

    # --- Certifications & Achievements ---
    st.subheader("🏆 Certifications & Achievements")
    certs = data.get("certifications") or []
    achievements = data.get("achievements") or []
    if certs:
        st.write("**Certifications:**")
        for c in certs:
            st.write(f"- {c}")
    if achievements:
        st.write("**Achievements:**")
        for a in achievements:
            st.write(f"- {a}")
    if not certs and not achievements:
        st.write("None found.")

    # --- Raw JSON + downloads ---
    with st.expander("View raw JSON"):
        st.json(data)

    st.download_button(
        "Download full extraction (.json)",
        data=json.dumps(data, indent=2),
        file_name="resume_data.json",
        mime="application/json",
    )

else:
    st.info("Upload a resume file to get started (PDF, DOCX, or image).")