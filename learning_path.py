import google.generativeai as genai

def get_learning_recommendations(topic: str, api_key: str) -> str:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-3.8-flash")
    prompt = f"""You are EduGenie, a personalized learning guide.
Create a detailed, structured learning path for the topic: "{topic}".

Include:
1. Beginner Level - foundational concepts to start with
2. Intermediate Level - building on the basics
3. Advanced Level - expert-level topics

For each level provide:
- Key concepts to learn
- Recommended resources (videos, articles, books)
- Estimated time to complete
- Practice exercises or projects

Make it actionable, motivating, and easy to follow."""
    response = model.generate_content(prompt)
    return response.text
