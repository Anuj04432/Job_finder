"""
Resume Analyzer — guided wizard flow.

Step 1 (upload):     Upload resume, extract + analyze automatically.
Step 2 (role_select): See ranked best-fit roles, or manually pick any role.
Step 3 (skill_gap):   See present/missing skills for the chosen role.

Uses st.session_state to track which step the user is on and to cache the
extraction result so switching between steps (or picking a different role)
never re-triggers the Gemini API call — only uploading a genuinely new file
does.

Run with:
    streamlit run app.py

Place this file in the SAME folder as all the extract_*.py files, with
skills_gap/ as a sibling package (see the sys.path setup below).
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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, ".."))
from skills_gap.skills_gap import analyze_roles, list_all_roles, get_role_breakdown


st.set_page_config(page_title="Resume Analyzer", page_icon="📄", layout="centered")


# ---------- Session state defaults ----------
st.session_state.setdefault("step", "upload")
st.session_state.setdefault("resume_file_hash", None)
st.session_state.setdefault("raw_text", None)
st.session_state.setdefault("data", None)
st.session_state.setdefault("selected_role", None)


def go_to(step: str):
    st.session_state["step"] = step


def reset_all():
    for key in ("step", "resume_file_hash", "raw_text", "data", "selected_role"):
        st.session_state.pop(key, None)
    st.session_state.setdefault("step", "upload")


# ---------- Step indicator ----------
STEP_LABELS = {"upload": "1. Upload & Analyze", "role_select": "2. Pick a Role", "skill_gap": "3. Skill Gap"}
st.caption(" → ".join(
    f"**{label}**" if key == st.session_state["step"] else label
    for key, label in STEP_LABELS.items()
))

st.title("📄 Resume Analyzer")


# =====================================================================
# STEP 1: Upload & Analyze
# =====================================================================
if st.session_state["step"] == "upload":
    st.caption("Upload a resume to extract structured data and get role recommendations.")

    uploaded_file = st.file_uploader("Upload a resume", type=["pdf", "docx", "png", "jpg", "jpeg"])

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        file_hash = hashlib.md5(file_bytes).hexdigest()

        force_reanalyze = st.button("🔄 Re-analyze (ignore cache)")

        if force_reanalyze or st.session_state["resume_file_hash"] != file_hash:
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

            with st.spinner("Analyzing resume (Gemini + rule-based)..."):
                data = get_resume_data_combined(raw_text)

            st.session_state["resume_file_hash"] = file_hash
            st.session_state["raw_text"] = raw_text
            st.session_state["data"] = data
            st.session_state["selected_role"] = None  # new resume, clear any prior role pick
        else:
            data = st.session_state["data"]
            st.caption("💾 Using cached extraction from this session (same file).")

        if data["extraction_method"] == "rule_based":
            st.warning("⚠️ AI extraction unavailable — showing rule-based results (may be less accurate).")
        else:
            st.success("✅ Extracted with Gemini")

        # --- Quick summary ---
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Name", data.get("name") or "Not found")
            st.metric("Email", data.get("email") or "Not found")
        with col2:
            st.metric("Phone", data.get("phone") or "Not found")
            st.metric("Skills found", len(data.get("skills") or []))

        with st.expander("View full extracted data"):
            st.json(data)
            st.download_button(
                "Download full extraction (.json)",
                data=json.dumps(data, indent=2),
                file_name="resume_data.json",
                mime="application/json",
            )

        if data.get("skills"):
            st.divider()
            if st.button("➡️ Continue to Role Recommendations", type="primary"):
                go_to("role_select")
                st.rerun()
        else:
            st.info("No skills were extracted — role matching needs at least some skills to work with.")
    else:
        st.info("Upload a resume file to get started (PDF, DOCX, or image).")


# =====================================================================
# STEP 2: Role Recommendations
# =====================================================================
elif st.session_state["step"] == "role_select":
    data = st.session_state["data"]
    st.caption(f"Based on **{data.get('name') or 'this resume'}**'s skills, here's what fits best.")

    analysis = analyze_roles(data["skills"])

    st.subheader("🏆 Best matches")
    for match in analysis["top_matches"]:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"**{match['role']}** — {match['match_percentage']}% match")
        with col2:
            if st.button("View gap", key=f"top_{match['role']}"):
                st.session_state["selected_role"] = match["role"]
                go_to("skill_gap")
                st.rerun()

    st.divider()
    st.subheader("🔍 Or explore any other role")
    all_roles = list_all_roles()
    manual_role = st.selectbox("Pick a role to check your fit for", all_roles)
    if st.button("View gap for this role"):
        st.session_state["selected_role"] = manual_role
        go_to("skill_gap")
        st.rerun()

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back to resume"):
            go_to("upload")
            st.rerun()
    with col2:
        if st.button("🔁 Start over with a new resume"):
            reset_all()
            st.rerun()


# =====================================================================
# STEP 3: Skill Gap Detail
# =====================================================================
elif st.session_state["step"] == "skill_gap":
    data = st.session_state["data"]
    role = st.session_state["selected_role"]

    breakdown = get_role_breakdown(data["skills"], role)

    if breakdown is None:
        st.error("Something went wrong — that role wasn't found. Please go back and pick again.")
    else:
        st.subheader(f"🎯 {role} — {breakdown['match_percentage']}% match")

        col1, col2 = st.columns(2)
        with col1:
            st.write("**✅ Core skills you have**")
            if breakdown["present_core_skills"]:
                for s in breakdown["present_core_skills"]:
                    st.write(f"- {s}")
            else:
                st.write("_None yet_")

            st.write("**✅ Nice-to-have skills you have**")
            if breakdown["present_nice_to_have_skills"]:
                for s in breakdown["present_nice_to_have_skills"]:
                    st.write(f"- {s}")
            else:
                st.write("_None yet_")

        with col2:
            st.write("**❌ Core skills to build**")
            if breakdown["missing_core_skills"]:
                for s in breakdown["missing_core_skills"]:
                    st.write(f"- {s}")
            else:
                st.write("_You have them all!_")

            st.write("**➕ Nice-to-have skills to build**")
            if breakdown["missing_nice_to_have_skills"]:
                for s in breakdown["missing_nice_to_have_skills"]:
                    st.write(f"- {s}")
            else:
                st.write("_You have them all!_")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back to role list"):
            go_to("role_select")
            st.rerun()
    with col2:
        if st.button("🔁 Start over with a new resume"):
            reset_all()
            st.rerun()