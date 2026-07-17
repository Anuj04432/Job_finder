import streamlit as st
from pypdf import PdfReader
from keywords.keys import job_keywords
from extracter.extracter import name, email,number
import re
from parser.resume_parsing import parser

if "analyze_resume" not in st.session_state:
    st.session_state.analyze_resume = ""

if 'resume_data' not in st.session_state:
    st.session_state.resume_data = None

st.title("📄 Resume Analyzer")

uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")


if st.button("Analyze_resume"):
    if uploaded_file:
        text = ""
        reader = PdfReader(uploaded_file)

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        st.session_state.analyze_resume = text

    # st.text_area("Extracted Text", text, height=300)

if st.session_state.analyze_resume:
        with st.spinner("Extracting Data...."):
            st.session_state.resume_data = parser(st.session_state.analyze_resume)
            
            col1,col2,col3 = st.columns(3)
            with col1:
                with st.expander("Personal_Info"):
                        st.write("Name : ",st.session_state.resume_data["Name"])
                        st.write("Phone : ",st.session_state.resume_data["Phone"])
                        st.write("Email : ",st.session_state.resume_data["Email"])
            with col2:
                with st.expander("skills"):
                        for index,i in enumerate(st.session_state.resume_data["Skills"],1):
                            st.write(f"{index}.{i}")

            with col3:
                with st.expander("Education"):
                    st.write(st.session_state.resume_data["Certifications"])
                        


st.divider()

text = st.session_state.analyze_resume
if text:
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

if text:
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


for index,i in enumerate(st.session_state.resume_data["Skills"],1):
    st.write(f"{index}.{i}")

st.write(st.session_state.resume_data)