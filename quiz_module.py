import google.generativeai as genai
import json
import re

def clean_json_block(text: str) -> str:
    text = re.sub(r"```json", "", text)
    text = re.sub(r"```", "", text)
    return text.strip()

def generate_quiz(passage: str, api_key: str):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-3.8-flash")
    prompt = f"""You are EduGenie quiz generator.
Generate exactly 3 multiple-choice questions from the following topic or passage.
Each question must have exactly 4 options (A, B, C, D) and one correct answer.

Return ONLY valid JSON in this exact format:
[
  {{
    "question": "Question text here?",
    "options": {{"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}},
    "answer": "A"
  }}
]

Topic/Passage: {passage}"""
    try:
        response = model.generate_content(prompt)
        cleaned = clean_json_block(response.text)
        questions = json.loads(cleaned)
        return questions
    except Exception as e:
        return [{"error": f"Quiz generation failed: {str(e)}"}]
