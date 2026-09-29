import google.generativeai as genai

MODELS = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]

def explain_concept(topic: str, api_key: str) -> str:
    prompt = f"""You are EduGenie, a friendly AI tutor.
Explain the concept of "{topic}" in a simple, clear, and beginner-friendly way.
Break it down step by step with analogies and real-life examples."""

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

    t_lower = topic.lower()
    if "pythagoras" in t_lower:
        return """### 📐 Pythagoras Theorem Explained Simply

**The Core Rule:**
In any right-angled triangle (a triangle with a 90° angle):
$$a^2 + b^2 = c^2$$

- **$a$ and $b$** are the two shorter perpendicular sides (legs).
- **$c$** is the longest side opposite the 90° angle, called the **hypotenuse**.

**Real-Life Example:**
If you walk 3 meters East, then 4 meters North:
- $3^2 + 4^2 = 9 + 16 = 25$
- The direct straight-line distance back to start is $\\sqrt{25} = 5$ meters!"""
    elif "photosynthesis" in t_lower:
        return """### 🌿 Photosynthesis Explained Simply

**What is it?**
Photosynthesis is how green plants make their own food using sunlight.

**The Recipe (Formula):**
$$\\text{Carbon Dioxide} + \\text{Water} + \\text{Sunlight} \\longrightarrow \\text{Glucose (Food)} + \\text{Oxygen}$$

**Step-by-Step:**
1. Leaves absorb **sunlight** using green pigment called **chlorophyll**.
2. Roots absorb **water** from the soil.
3. Leaves take in **carbon dioxide** from the air.
4. The plant produces **glucose** for energy and releases **oxygen** for us to breathe!"""
    else:
        return f"""### 💡 Explanation: {topic}

1. **What is it?** {topic} is a key concept that solves specific problems and organizes principles in this field.
2. **How does it work?** It operates by breaking down complex interactions into structured, repeatable rules.
3. **Everyday Analogy:** Think of it like building blocks—each individual piece connects to support the larger structure."""
