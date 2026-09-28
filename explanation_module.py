import google.generativeai as genai

def explain_concept(topic: str, api_key: str) -> str:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-3.8-flash")
    prompt = f"""You are EduGenie, a friendly AI tutor.
Explain the concept of "{topic}" in a simple, clear, and beginner-friendly way.
Break it down step by step. Use real-life examples and analogies.
Keep it easy to understand for a student with no prior knowledge."""
    response = model.generate_content(prompt)
    return response.text
