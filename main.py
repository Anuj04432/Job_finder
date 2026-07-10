import streamlit as st
from pypdf import PdfReader
from keywords.keys import job_keywords
import re

st.title("📄 Resume Analyzer")

uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")

text = ""

if uploaded_file is not None:
    reader = PdfReader(uploaded_file)

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    st.text_area("Extracted Text", text, height=300)

    email =re.search(r'[A-Za-z0-9]+@[A-Za-z0-9]+\.[A-Za-z]{2,}',text)
    number = re.search(r'\+91\s?\d{5}[\s+]?\d{5}', text)
    with st.expander("Show details"):
        st.write(f"Email:{email.group()}")
        st.write(f"Contact_number:{number.group()}")


    st.subheader("Applicable Job Roles")

    role_scores = {}

    for role, keywords in job_keywords.items():
        matched = 0

        for keyword in keywords:
            if keyword.lower() in text.lower():
                matched += 1

        score = matched / len(keywords) * 100
        role_scores[role] = score


    best_role = max(role_scores,key = role_scores.get)

    st.success(f"🏆 Best Matching Role: {best_role}")
    st.metric("Match Score", f"{role_scores[best_role]:.1f}%")


    st.divider()

    selected_role = st.selectbox(
        "Select Job Role",
        list(job_keywords.keys())
    )

    present_keywords = []
    missing_keywords = []

    for keyword in job_keywords[selected_role]:
        if keyword.lower() in text.lower():
            present_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)

    ats_score = len(present_keywords) / len(job_keywords[selected_role]) * 100

    st.subheader("ATS Analysis")
    st.metric("ATS Match", f"{ats_score:.1f}%")

    col1, col2 = st.columns(2)

    with col1:
        st.success("Matched Skills")
        if present_keywords:
            for skill in present_keywords:
                st.write(f"✅ {skill}")
        else:
            st.write("No matching skills found.")

    with col2:
        st.error("Missing Skills")
        if missing_keywords:
            for skill in missing_keywords:
                st.write(f"❌ {skill}")
        else:
            st.write("No missing skills.")



    


