import google.generativeai as genai

def get_answer(question: str, api_key: str) -> str:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-pro")
        prompt = f"""You are EduGenie, an expert educational AI assistant.
Answer this question clearly in a student-friendly way with examples.
Question: {question}"""
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"
