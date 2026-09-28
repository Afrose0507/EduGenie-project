import google.generativeai as genai

def explain_concept(topic: str, api_key: str) -> str:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        prompt = f"""You are EduGenie, a friendly AI tutor.
Explain the concept of "{topic}" in a simple, clear, and beginner-friendly way.
Break it down step by step. Use real-life examples and analogies."""
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"
