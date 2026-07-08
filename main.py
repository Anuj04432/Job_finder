import streamlit as st
from pypdf import PdfReader
from keywords.keys import keywords

st.title("PDF Text Extractor")

uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file is not None:
    reader = PdfReader(uploaded_file)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text


    st.text_area("Extracted Text", text, height=400)

st.write("Applicable for job roles")

roles = []
for key, value in keywords.items():
    for keyword in value:
        if keyword.lower() in text.lower():
            roles.append(key)
for index,i in enumerate(set(roles),1):
    st.write(index,".",i)
    


