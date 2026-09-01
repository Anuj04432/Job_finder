"""
Resume Analyzer — single-page flow.

Extracts structured information from an uploaded resume (PDF, DOCX, image)
and renders all extracted details, skills, role recommendations, skill gap
analysis, experience, education, projects, certifications, and achievements
in a single clean top-to-bottom layout.

Uses session_state only to cache extraction results by file hash so
interacting with widgets (e.g. role dropdown) doesn't re-trigger extraction.
"""

import json
import os
import sys
import hashlib
import tempfile
from pathlib import Path

import streamlit as st

from extract_resume_text import extract_resume_text
from extract_resume_fallback import get_resume_data_combined
from job_search import search_jobs, rank_jobs

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, ".."))
from skills_gap.skills_gap import analyze_roles, list_all_roles, get_role_breakdown


st.set_page_config(page_title="Resume Analyzer", page_icon="📄", layout="centered")

# ---------- Session state caching (to avoid redundant API calls) ----------
st.session_state.setdefault("resume_file_hash", None)
st.session_state.setdefault("raw_text", None)
st.session_state.setdefault("data", None)

st.title("📄 Resume Analyzer")
st.caption("Upload a resume to extract structured data and get role recommendations.")

uploaded_file = st.file_uploader("Upload a resume", type=["pdf", "docx", "png", "jpg", "jpeg"])

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    file_hash = hashlib.md5(file_bytes).hexdigest()

    force_reanalyze = st.button("🔄 Re-analyze (ignore cache)")

    if force_reanalyze or st.session_state.get("resume_file_hash") != file_hash:
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
            finally:
                if os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except OSError:
                        pass

        with st.spinner("Analyzing resume (Gemini + rule-based)..."):
            data = get_resume_data_combined(raw_text)

        st.session_state["resume_file_hash"] = file_hash
        st.session_state["raw_text"] = raw_text
        st.session_state["data"] = data
    else:
        data = st.session_state["data"]
        st.caption("💾 Using cached extraction from this session (same file).")

    if data.get("extraction_method") == "rule_based":
        st.warning("⚠️ AI extraction unavailable — showing rule-based results (may be less accurate).")
    else:
        st.success("✅ Extracted with Gemini")

    st.divider()

    # =========================================================================
    # 1. Personal Information
    # =========================================================================
    st.subheader("👤 Personal Information")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Name:** {data.get('name') or 'Not found'}")
        st.write(f"**Email:** {data.get('email') or 'Not found'}")
    with col2:
        st.write(f"**Phone:** {data.get('phone') or 'Not found'}")
        st.write(f"**Location:** {data.get('location') or 'Not found'}")

    links = data.get("links") or {}
    if isinstance(links, dict):
        link_items = []
        for k, v in links.items():
            if v and isinstance(v, str):
                link_items.append(f"[{k.capitalize()}]({v})")
        if link_items:
            st.write(f"**Links:** {' | '.join(link_items)}")

    st.divider()

    # =========================================================================
    # 2. Professional Summary
    # =========================================================================
    st.subheader("📝 Professional Summary")
    summary = data.get("summary")
    if summary:
        st.write(summary)
    else:
        st.info("No professional summary found.")

    st.divider()

    # =========================================================================
    # 3. Skills
    # =========================================================================
    st.subheader("🛠️ Skills")
    skills = data.get("skills") or []
    if skills:
        st.write(", ".join(f"`{s}`" for s in skills))
    else:
        st.info("No skills detected.")

    with st.expander("Skill source breakdown"):
        col_llm, col_rule = st.columns(2)
        with col_llm:
            st.write("**Gemini LLM Skills:**")
            llm_skills = data.get("llm_skills") or []
            if llm_skills:
                for s in llm_skills:
                    st.write(f"- {s}")
            else:
                st.write("_None_")
        with col_rule:
            st.write("**Rule-based Skills:**")
            rule_skills = data.get("rule_based_skills") or []
            if rule_skills:
                for s in rule_skills:
                    st.write(f"- {s}")
            else:
                st.write("_None_")

    st.divider()

    # =========================================================================
    # 4. Role Fit & Skill Gap
    # =========================================================================
    st.subheader("🎯 Role Fit & Skill Gap")
    if skills:
        analysis = analyze_roles(skills)
        top_matches = analysis.get("top_matches") or []
        best_fit_role = analysis.get("best_fit_role")

        if top_matches:
            st.write("**Top Role Matches:**")
            cols = st.columns(min(len(top_matches), 3))
            for i, match in enumerate(top_matches[:3]):
                with cols[i]:
                    st.metric(label=match.get("role", "Role"), value=f"{match.get('match_percentage', 0)}%")

        all_roles = list_all_roles()
        default_index = 0
        if best_fit_role and best_fit_role in all_roles:
            default_index = all_roles.index(best_fit_role)

        selected_role = st.selectbox(
            "Select a role to view detailed skill breakdown:",
            options=all_roles,
            index=default_index,
        )

        if selected_role:
            breakdown = get_role_breakdown(skills, selected_role)
            if breakdown:
                st.markdown(f"#### Skill Breakdown: **{selected_role}** ({breakdown.get('match_percentage', 0)}% match)")
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**✅ Core skills you have**")
                    if breakdown.get("present_core_skills"):
                        for s in breakdown["present_core_skills"]:
                            st.write(f"- {s}")
                    else:
                        st.write("_None yet_")

                    st.write("**✅ Nice-to-have skills you have**")
                    if breakdown.get("present_nice_to_have_skills"):
                        for s in breakdown["present_nice_to_have_skills"]:
                            st.write(f"- {s}")
                    else:
                        st.write("_None yet_")

                with col2:
                    st.write("**❌ Core skills to build**")
                    if breakdown.get("missing_core_skills"):
                        for s in breakdown["missing_core_skills"]:
                            st.write(f"- {s}")
                    else:
                        st.write("_You have them all!_")

                    st.write("**➕ Nice-to-have skills to build**")
                    if breakdown.get("missing_nice_to_have_skills"):
                        for s in breakdown["missing_nice_to_have_skills"]:
                            st.write(f"- {s}")
                    else:
                        st.write("_You have them all!_")

                # Matching job openings
                try:
                    jobs = search_jobs(keywords=selected_role, location="India", country_code="in")
                    ranked = rank_jobs(jobs, skills)
                    if ranked:
                        st.divider()
                        st.write(f"**💼 Matching Job Openings for {selected_role}:**")
                        for job in ranked:
                            st.write(f"**{job.get('title', 'Untitled role')}** — {job.get('company', 'Unknown company')} ({job.get('match_score', 0)}% match)")
                            if job.get("apply_url"):
                                st.write(f"[Apply here]({job['apply_url']})")
                except Exception:
                    pass
    else:
        st.info("No skills were extracted — role matching needs at least some skills to work with.")

    st.divider()

    # =========================================================================
    # 5. Experience
    # =========================================================================
    st.subheader("💼 Work Experience")
    experience = data.get("experience") or []
    if experience:
        for exp in experience:
            if isinstance(exp, dict):
                title = exp.get("title") or "Position"
                company = exp.get("company")
                dates = []
                if exp.get("start_date"):
                    dates.append(str(exp["start_date"]))
                if exp.get("end_date"):
                    dates.append(str(exp["end_date"]))
                date_str = " - ".join(dates) if dates else ""
                loc = exp.get("location")

                header_parts = [f"**{title}**"]
                if company:
                    header_parts.append(f"at **{company}**")
                if date_str:
                    header_parts.append(f"({date_str})")
                if loc:
                    header_parts.append(f"| {loc}")

                st.markdown(" ".join(header_parts))

                desc = exp.get("description") or []
                if isinstance(desc, list):
                    for bullet in desc:
                        st.write(f"- {bullet}")
                elif isinstance(desc, str) and desc.strip():
                    st.write(desc)
            elif isinstance(exp, str):
                st.write(f"- {exp}")
    else:
        st.info("No work experience found.")

    st.divider()

    # =========================================================================
    # 6. Education
    # =========================================================================
    st.subheader("🎓 Education")
    education = data.get("education") or []
    if education:
        for edu in education:
            if isinstance(edu, dict):
                if edu.get("raw_text"):
                    st.write(f"- {edu['raw_text']}")
                else:
                    degree = edu.get("degree") or "Degree"
                    inst = edu.get("institution")
                    field = edu.get("field")
                    grad_date = edu.get("graduation_date")
                    gpa = edu.get("gpa")

                    parts = [f"**{degree}**"]
                    if field:
                        parts.append(f"in {field}")
                    if inst:
                        parts.append(f"— {inst}")
                    if grad_date:
                        parts.append(f"({grad_date})")
                    if gpa:
                        parts.append(f"| GPA: {gpa}")
                    st.markdown(" ".join(parts))
            elif isinstance(edu, str):
                st.write(f"- {edu}")
    else:
        st.info("No education details found.")

    st.divider()

    # =========================================================================
    # 7. Projects
    # =========================================================================
    st.subheader("🚀 Projects")
    projects = data.get("projects") or []
    if projects:
        for proj in projects:
            if isinstance(proj, dict):
                title = proj.get("title") or "Project"
                link = proj.get("link")
                tech_stack = proj.get("tech_stack") or []

                title_md = f"**{title}**"
                if link:
                    title_md += f" ([Link]({link}))"
                st.markdown(title_md)

                if tech_stack:
                    if isinstance(tech_stack, list):
                        st.caption(f"Technologies: {', '.join(str(t) for t in tech_stack)}")
                    elif isinstance(tech_stack, str):
                        st.caption(f"Technologies: {tech_stack}")

                desc = proj.get("description") or []
                if isinstance(desc, list):
                    for bullet in desc:
                        st.write(f"- {bullet}")
                elif isinstance(desc, str) and desc.strip():
                    st.write(desc)
            elif isinstance(proj, str):
                st.write(f"- {proj}")
    else:
        st.info("No projects found.")

    st.divider()

    # =========================================================================
    # 8. Certifications & Achievements
    # =========================================================================
    st.subheader("📜 Certifications & Achievements")
    certifications = data.get("certifications") or []
    achievements = data.get("achievements") or []

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Certifications:**")
        if certifications:
            for cert in certifications:
                st.write(f"- {cert}")
        else:
            st.write("_None found_")
    with col2:
        st.write("**Achievements:**")
        if achievements:
            for ach in achievements:
                st.write(f"- {ach}")
        else:
            st.write("_None found_")

    st.divider()

    # =========================================================================
    # 9. Raw JSON expander + Download
    # =========================================================================
    with st.expander("View full extracted data (JSON)"):
        st.json(data)
        st.download_button(
            "Download full extraction (.json)",
            data=json.dumps(data, indent=2),
            file_name="resume_data.json",
            mime="application/json",
        )
else:
    st.info("Upload a resume file to get started (PDF, DOCX, or image).")