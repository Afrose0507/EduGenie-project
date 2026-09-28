import google.generativeai as genai

def summarize_text(passage: str, api_key: str) -> str:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        prompt = f"""Summarize the following educational passage into clear bullet points.
Keep all key information but remove unnecessary details.

Passage:
{passage}"""
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"
