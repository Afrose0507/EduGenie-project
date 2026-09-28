import google.generativeai as genai

def get_learning_recommendations(topic: str, api_key: str) -> str:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        prompt = f"""Create a detailed learning path for: "{topic}"
Include Beginner, Intermediate and Advanced levels.
For each level list key concepts, resources and estimated time."""
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"
