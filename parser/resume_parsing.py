import google.generativeai as genai
import os

def parser(text):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    model = genai.GenerativeModel("gemini-3.5-flash")

    prompt = f"""
Extract the following information from this resume.

Return ONLY valid JSON.

Fields:
- Name
- Email
- Phone
- Skills
- Education
- Experience
- Projects
- Certifications

Resume:

{text}
"""
    response = model.generate_content(prompt)


    return response