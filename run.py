import json
import tempfile
from pathlib import Path

import streamlit as st

from parser.text_extracted import extract_resume_text
from parser.extracter import extract_personal_info
from parser.summary_extract import extract_summary
from parser.certifications_extracter import extract_certifications, extract_achievements, extract_certifications_and_achievements


st.set_page_config(page_title="Resume Analyzer", page_icon="📄", layout="centered")

st.title("📄 Resume Analyzer")
st.caption("Upload a resume to extract raw text and personal/contact info.")

uploaded_file = st.file_uploader(
    "Upload a resume",
    type=["pdf", "docx", "png", "jpg", "jpeg"],
)

if uploaded_file is not None:
    # Save the uploaded file to a temp path on disk, since extract_resume_text
    # works off a file path (it needs real file access for PDF/DOCX parsing libs)
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

    with st.spinner("Parsing personal info..."):
        try:
            personal_info = extract_personal_info(raw_text)
        except Exception as e:
            st.error(f"Personal info extraction failed: {e}")
            st.stop()

    st.success("Done!")

    # --- Personal Info Section ---
    st.subheader("👤 Personal Info")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Name", personal_info.get("name") or "Not found")
        st.metric("Email", personal_info.get("email") or "Not found")
    with col2:
        st.metric("Phone", personal_info.get("phone") or "Not found")

    links = personal_info.get("links", {})
    if any(links.values()):
        st.write("**Links:**")
        for label, url in links.items():
            if url:
                st.write(f"- {label.capitalize()}: {url}")

    with st.expander("View raw JSON"):
        st.json(personal_info)

    # --- Raw Text Section ---
    st.subheader("📝 Extracted Raw Text")
    with st.expander("Show full extracted text", expanded=False):
        st.text_area("Raw text", raw_text, height=300, label_visibility="collapsed")

    # --- Downloads ---
    st.subheader("⬇️ Downloads")
    d1, d2 = st.columns(2)
    with d1:
        st.download_button(
            "Download raw text (.txt)",
            data=raw_text,
            file_name="extracted_text.txt",
            mime="text/plain",
        )
    with d2:
        st.download_button(
            "Download personal info (.json)",
            data=json.dumps(personal_info, indent=2),
            file_name="personal_info.json",
            mime="application/json",
        )

    st.text_area("Summary", extract_summary(raw_text) or "No summary/objective section found.", height=150, label_visibility="collapsed")

    cert_result = extract_certifications_and_achievements(raw_text)

    if cert_result["combined"]:
        st.subheader("🏆 Certifications & Achievements")
        for item in cert_result["combined"]:
            st.write(f"- {item}")
    else:
        st.subheader("🏆 Certifications")
        if cert_result["certifications"]:
            for cert in cert_result["certifications"]:
                st.write(f"- {cert}")
        else:
            st.write("None found.")

        st.subheader("🎖️ Achievements")
        if cert_result["achievements"]:
            for ach in cert_result["achievements"]:
                st.write(f"- {ach}")
        else:
            st.write("None found.")
    
else:
    st.info("Upload a resume file to get started (PDF, DOCX, or image).")


