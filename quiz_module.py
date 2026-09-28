import google.generativeai as genai
import json
import re

def clean_json_block(text: str) -> str:
    text = re.sub(r"```json", "", text)
    text = re.sub(r"```", "", text)
    return text.strip()

def generate_quiz(passage: str, api_key: str):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        prompt = f"""Generate exactly 3 multiple-choice questions from: "{passage}"
Each question must have 4 options (A,B,C,D) and one correct answer.
Return ONLY valid JSON like this:
[
  {{
    "question": "Question here?",
    "options": {{"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}},
    "answer": "A"
  }}
]"""
        response = model.generate_content(prompt)
        cleaned = clean_json_block(response.text)
        return json.loads(cleaned)
    except Exception as e:
        return [{"error": f"Quiz generation failed: {str(e)}"}]
