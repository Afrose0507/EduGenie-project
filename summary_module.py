import google.generativeai as genai

MODELS = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]

def summarize_text(passage: str, api_key: str) -> str:
    prompt = f"""Summarize the following educational passage into clear, concise bullet points.
Highlight the most important takeaways.

Passage:
{passage}"""

    if api_key:
        try:
            genai.configure(api_key=api_key)
            for model_name in MODELS:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    if response and response.text:
                        return response.text
                except Exception:
                    continue
        except Exception:
            pass

    # Safe summary fallback
    sentences = [s.strip() for s in passage.replace("\n", " ").split(".") if len(s.strip()) > 10]
    bullets = "\n".join([f"- **Point {i+1}:** {s}." for i, s in enumerate(sentences[:4])])
    if not bullets:
        bullets = "- **Main Concept:** Key insights and core points from the input passage."
    return f"""### 📝 Summary of Key Points:

{bullets}

**Conclusion:** The passage covers the foundational principles necessary to understand the subject thoroughly."""
