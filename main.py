import streamlit as st
from pypdf import PdfReader

st.title("PDF Text Extractor")

uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file is not None:
    reader = PdfReader(uploaded_file)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    st.text_area("Extracted Text", text, height=400)