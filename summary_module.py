import google.generativeai as genai

def summarize_text(passage: str, api_key: str) -> str:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-3.8-flash")
    prompt = f"""You are EduGenie, an expert summarizer.
Summarize the following educational passage into a concise, clear, and easy-to-understand version.
Retain all key points and important information. Remove unnecessary details.
Format with bullet points for clarity.

Passage:
{passage}"""
    response = model.generate_content(prompt)
    return response.text
