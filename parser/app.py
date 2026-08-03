# import os
# import sys

# import json
# import tempfile
# from pathlib import Path

# import streamlit as st
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# PROJECT_ROOT = os.path.join(BASE_DIR, "..")
# sys.path.append(PROJECT_ROOT)

# from extract_resume_text import extract_resume_text
# from extract_resume_fallback import get_resume_data
# from skills_gap.skills_gap import analyze_roles


# st.set_page_config(page_title="Resume Analyzer", page_icon="📄", layout="centered")

# st.title("📄 Resume Analyzer")
# st.caption("Upload a resume to extract structured data — powered by Gemini, with a rule-based fallback.")

# uploaded_file = st.file_uploader(
#     "Upload a resume",
#     type=["pdf", "docx", "png", "jpg", "jpeg"],
# )

# if uploaded_file is not None:
#     suffix = Path(uploaded_file.name).suffix
#     with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
#         tmp_file.write(uploaded_file.getvalue())
#         tmp_path = tmp_file.name

#     with st.spinner("Extracting text..."):
#         try:
#             raw_text = extract_resume_text(tmp_path)
#         except Exception as e:
#             st.error(f"Text extraction failed: {e}")
#             st.stop()

#     with st.spinner("Analyzing resume..."):
#         data = get_resume_data(raw_text)

#     if data["extraction_method"] == "rule_based":
#         st.warning(
#             "⚠️ AI extraction unavailable (API key missing, rate-limited, or offline) — "
#             "showing results from the rule-based fallback instead. Some fields may be "
#             "less accurate or empty."
#         )
#     else:
#         st.success("✅ Extracted with Gemini")

#     # --- Personal Info ---
#     st.subheader("👤 Personal Info")
#     col1, col2 = st.columns(2)
#     with col1:
#         st.metric("Name", data.get("name") or "Not found")
#         st.metric("Email", data.get("email") or "Not found")
#     with col2:
#         st.metric("Phone", data.get("phone") or "Not found")
#         st.metric("Location", data.get("location") or "Not found")

#     links = data.get("links") or {}
#     if any(links.values()):
#         st.write("**Links:**")
#         for label, url in links.items():
#             if url:
#                 st.write(f"- {label.capitalize()}: {url}")

#     # --- Summary ---
#     with st.expander("More Information"):
#         with st.expander("summary"):
#             if data.get("summary"):
#                 st.subheader("🧾 Professional Summary")
#                 st.write(data["summary"])

#         # --- Skills ---
#         with st.expander("Skills"):
#             st.subheader("🛠️ Skills")
#             if data.get("skills"):
#                 st.write(", ".join(data["skills"]))
#             else:
#                 st.write("None found.")

#         # --- Experience ---
#         with st.expander("Experience"):
#             st.subheader("💼 Experience")
#             if data.get("experience"):
#                 for exp in data["experience"]:
#                     # Rule-based fallback entries only have 'title' + 'description'.
#                     # LLM entries have separate title/company/dates fields.
#                     if "company" in exp:
#                         header = f"**{exp.get('title', '')}** — {exp.get('company', '')}"
#                         dates = " to ".join(filter(None, [exp.get("start_date"), exp.get("end_date")]))
#                         if dates:
#                             header += f" ({dates})"
#                     else:
#                         header = f"**{exp.get('title') or 'Untitled role'}**"
#                     st.markdown(header)
#                     for point in exp.get("description", []):
#                         st.write(f"- {point}")
#             else:
#                 st.write("None found.")

#         # --- Education ---
#         with st.expander("Education"):
#             st.subheader("🎓 Education")
#             if data.get("education"):
#                 for edu in data["education"]:
#                     if "raw_text" in edu:
#                         st.write(f"- {edu['raw_text']}")
#                     else:
#                         line = f"**{edu.get('degree', '')}** — {edu.get('institution', '')}"
#                         if edu.get("graduation_date"):
#                             line += f" ({edu['graduation_date']})"
#                         st.markdown(line)
#             else:
#                 st.write("None found.")

#         # --- Projects ---
#         with st.expander("Projects"):
#             st.subheader("💻 Projects")
#             if data.get("projects"):
#                 for proj in data["projects"]:
#                     st.markdown(f"**{proj.get('title') or 'Untitled Project'}**")
#                     if proj.get("tech_stack"):
#                         st.caption(", ".join(proj["tech_stack"]))
#                     for point in proj.get("description", []):
#                         st.write(f"- {point}")
#             else:
#                 st.write("None found.")

#         # --- Certifications & Achievements ---
#         with st.expander("🏆 Certifications & Achievements"):
#             st.subheader("🏆 Certifications & Achievements")
#             certs = data.get("certifications") or []
#             achievements = data.get("achievements") or []
#             if certs:
#                 st.write("**Certifications:**")
#                 for c in certs:
#                     st.write(f"- {c}")
#             if achievements:
#                 st.write("**Achievements:**")
#                 for a in achievements:
#                     st.write(f"- {a}")
#             if not certs and not achievements:
#                 st.write("None found.")

#     # --- Raw JSON + downloads ---
#     with st.expander("View raw JSON"):
#         st.json(data)

#     st.download_button(
#         "Download full extraction (.json)",
#         data=json.dumps(data, indent=2),
#         file_name="resume_data.json",
#         mime="application/json",
#     )


#     st.subheader("🎯 Role Fit & Skill Gap")
#     if data.get("skills"):
#         analysis = analyze_roles(data["skills"])
#         st.write(f"**Best fit role:** {analysis['best_fit_role']}")

#         for match in analysis["top_matches"]:
#             with st.expander(f"{match['role']} — {match['match_percentage']}% match"):
#                 st.write("**✅ Present skills:**", ", ".join(match["present_skills"]) or "None")
#                 st.write("**❌ Missing skills:**", ", ".join(match["missing_skills"]) or "None")
#     else:
#         st.write("No skills extracted yet — can't analyze role fit.")

# else:
#     st.info("Upload a resume file to get started (PDF, DOCX, or image).")





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
import os
import sys
import hashlib
import tempfile
from pathlib import Path

import streamlit as st

from extract_resume_text import extract_resume_text
from extract_resume_fallback import get_resume_data

# Add project root so sibling packages (e.g. skills_gap/) can be imported
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, ".."))
from skills_gap.skills_gap import analyze_roles


st.set_page_config(page_title="Resume Analyzer", page_icon="📄", layout="centered")

st.title("📄 Resume Analyzer")
st.caption("Upload a resume to extract structured data — powered by Gemini, with a rule-based fallback.")

uploaded_file = st.file_uploader(
    "Upload a resume",
    type=["pdf", "docx", "png", "jpg", "jpeg"],
)

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    file_hash = hashlib.md5(file_bytes).hexdigest()

    force_reanalyze = st.button("🔄 Re-analyze (ignore cache)")

    # Only re-run the (potentially slow/costly) extraction pipeline if this is
    # a genuinely new file, or the user explicitly asked to re-analyze.
    # Otherwise reuse what's already in session_state — this is what prevents
    # every unrelated Streamlit rerun (e.g. clicking any other widget) from
    # re-calling the Gemini API on the same file over and over.
    if (
        force_reanalyze
        or st.session_state.get("resume_file_hash") != file_hash
    ):
        suffix = Path(uploaded_file.name).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(file_bytes)
            tmp_path = tmp_file.name

        with st.spinner("Extracting text..."):
            try:
                raw_text = extract_resume_text(tmp_path)
            except Exception as e:
                st.error(f"Text extraction failed: {e}")
                st.stop()

        with st.spinner("Analyzing resume..."):
            data = get_resume_data(raw_text)

        st.session_state["resume_file_hash"] = file_hash
        st.session_state["raw_text"] = raw_text
        st.session_state["resume_data"] = data
    else:
        raw_text = st.session_state["raw_text"]
        data = st.session_state["resume_data"]
        st.caption("💾 Using cached extraction from this session (same file, no re-analysis).")

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
    with st.expander("More Information"):
        with st.expander("summary"):
            if data.get("summary"):
                st.subheader("🧾 Professional Summary")
                st.write(data["summary"])

        # --- Skills ---
        with st.expander("Skills"):
            st.subheader("🛠️ Skills")
            if data.get("skills"):
                st.write(", ".join(data["skills"]))
            else:
                st.write("None found.")


        # --- Experience ---
        with st.expander("Experience"):
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
        with st.expander("Education"):
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
        with st.expander("Projects"):
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
        with st.expander("🏆 Certifications & Achievements"):
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


        # --- Role Fit & Skill Gap ---
   # --- Role Fit & Skill Gap ---
    st.subheader("🎯 Role Fit & Skill Gap")
    if data.get("skills"):
        analysis = analyze_roles(data["skills"])
        st.write(f"**Best-fit role:** {analysis.get('best_fit_role') or 'Not enough data'}")
 
        if analysis.get("skills_to_learn_next"):
            st.write(
                "**Top skills to learn next:** "
                + ", ".join(analysis["skills_to_learn_next"])
            )
 
        for match in analysis.get("top_matches", []):
            with st.expander(f"{match['role']} — {match['match_percentage']}% match"):
                st.write("**✅ Core skills present:**",
                         ", ".join(match["present_core_skills"]) or "None")
                st.write("**❌ Core skills missing:**",
                         ", ".join(match["missing_core_skills"]) or "None")
                st.write("**✅ Nice-to-have present:**",
                         ", ".join(match["present_nice_to_have_skills"]) or "None")
                st.write("**➕ Nice-to-have missing:**",
                         ", ".join(match["missing_nice_to_have_skills"]) or "None")
    else:
        st.write("No skills extracted yet — can't analyze role fit.")

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