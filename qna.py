import google.generativeai as genai

def get_answer(question: str, api_key: str) -> str:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        prompt = f"""You are EduGenie, an expert educational AI assistant.
Answer the following question clearly, accurately, and in a student-friendly way.
Use simple language and examples where helpful.

Question: {question}"""
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"
