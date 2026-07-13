import google.generativeai as genai
import os
import json

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

    json_text = response.text

    # Remove markdown if present
    json_text = json_text.replace("```json", "").replace("```", "").strip()

    # Convert JSON string to Python dictionary
    data = json.loads(json_text)

    return data