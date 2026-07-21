import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY_3"))

model = genai.GenerativeModel("models/gemini-3.5-flash")

def parser(text):
    prompt = f"""
You are a resume parser.

Return ONLY valid JSON.

Do not include markdown.
Do not use ```json.
Do not add explanations.
Add only the skills that used for resume analyzing with , only important keywords.
If a field is missing, return an empty string "" or an empty list [].



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
    try:
        response = model.generate_content(prompt)
        json_text = response.text

        # Remove markdown if present
        json_text = json_text.replace("```json", "").replace("```", "").strip()

        # Convert JSON string to Python dictionary
        data = json.loads(json_text)

        return data
    
    except Exception as e:
        print("Gemini Error:", e)
        return None
    
    