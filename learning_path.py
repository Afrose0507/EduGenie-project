import google.generativeai as genai

MODELS = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]

def get_learning_recommendations(topic: str, api_key: str) -> str:
    prompt = f"""Create a structured, step-by-step learning roadmap for: "{topic}"
Organize it into:
1. Beginner Level (Core Concepts & Fundamentals)
2. Intermediate Level (Practical Applications & Projects)
3. Advanced Level (Mastery & Real-World Best Practices)
Include estimated timelines and recommended resources."""

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

    return f"""### 🗺️ Learning Roadmap: {topic}

#### 🟢 Phase 1: Beginner Level (Weeks 1 - 2)
- **Goal:** Understand foundational definitions and terminology.
- **Key Concepts:** Core theory, setup, syntax/tools, simple exercises.
- **Milestone:** Complete 3 beginner tutorial problems.

#### 🟡 Phase 2: Intermediate Level (Weeks 3 - 4)
- **Goal:** Apply theoretical concepts to hands-on mini-projects.
- **Key Concepts:** Practical problem solving, workflows, debugging.
- **Milestone:** Build a functional application or case study.

#### 🔴 Phase 3: Advanced Level (Weeks 5 - 6)
- **Goal:** Master optimization, scalability, and complex integrations.
- **Key Concepts:** Architecture design, industry best practices, performance.
- **Milestone:** Complete a capstone project and showcase on portfolio."""
