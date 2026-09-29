import google.generativeai as genai
import urllib.request
import urllib.parse
import json
import re

MODELS = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]

def clean_topic(t: str) -> str:
    s = t.strip()
    s = re.sub(r'^(what is a|what is an|what is the|what is|what are|explain|tell me about|define|describe)\s+', '', s, flags=re.I)
    s = re.sub(r'\?+$', '', s).strip()
    return s or t.strip()

def fetch_concept_knowledge(topic: str):
    clean = clean_topic(topic)
    for q_try in [clean, topic]:
        url = 'https://en.wikipedia.org/api/rest_v1/page/summary/' + urllib.parse.quote(q_try)
        req = urllib.request.Request(url, headers={'User-Agent': 'EduGenie/1.0 (educational app)'})
        try:
            with urllib.request.urlopen(req, timeout=4) as res:
                data = json.loads(res.read().decode('utf-8'))
                if data.get('extract') and data.get('type') != 'disambiguation':
                    return data.get('title', clean), data.get('extract')
        except Exception:
            continue
    return clean, None

def explain_concept(topic: str, api_key: str) -> str:
    clean_key = (api_key or "").strip().strip('"').strip("'")
    prompt = f"""You are EduGenie, a friendly, human-like AI tutor (like ChatGPT, Gemini, Claude).
Explain the concept: "{topic}".

Adopt an engaging, conversational, friendly tone.
Start with: "Hello! I am **EduGenie**, your friendly AI tutor. I'm excited to explain **{topic}** to you today!"
Use clear markdown headers (###), horizontal lines (---), bullet points with bold keywords, simple real-life analogies, and clear step-by-step examples.
End with a friendly question asking if they would like to try a quiz or see another example."""

    # 1. Try Google Gemini API
    if clean_key:
        try:
            genai.configure(api_key=clean_key)
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

    # 2. Hardcoded rich explanations for common concepts
    t_lower = topic.lower()
    if "pythagoras" in t_lower:
        return """Hello! I am **EduGenie**, your friendly AI tutor. I'm excited to explain **The Pythagoras Theorem** to you today!

---

### What is the Pythagoras Theorem?

Imagine you are standing at the corner of a square park. You want to get to the opposite corner. 

Do you walk along the two outside sidewalks, or do you take the diagonal shortcut right across the grass? 

Taking the diagonal shortcut is always faster! The **Pythagoras Theorem** is the magical math rule that tells you *exactly* how long that shortcut is.

---

### The Golden Rule

In any triangle that has a **90-degree right angle** (like the corner of a book or a room):

$$a^2 + b^2 = c^2$$

- **$a$ and $b$** are the two straight sides forming the corner.
- **$c$** is the long diagonal shortcut, called the **hypotenuse**.

---

### A Simple Everyday Example

Let's say you walk:
- **3 meters** East ($a = 3$)
- **4 meters** North ($b = 4$)

How far are you directly from your starting point ($c$)?

1. Square the first number: $3 \\times 3 = 9$
2. Square the second number: $4 \\times 4 = 16$
3. Add them together: $9 + 16 = 25$
4. Find the square root: $\\sqrt{25} = 5$ meters!

The direct shortcut distance is exactly **5 meters**!

***

Would you like to try calculating another triangle together, or test yourself with a quick quiz?"""

    # 3. Dynamic Real Concept Knowledge for ANY topic
    title, extract = fetch_concept_knowledge(topic)
    if extract:
        sentences = [s.strip() for s in extract.replace("\n", " ").split(".") if len(s.strip()) > 10]
        points = "\n".join([f"{i+1}. **Key Principle:** {s}." for i, s in enumerate(sentences[:4])])
        return f"""Hello! I am **EduGenie**, your friendly AI tutor. I'm excited to explain **{title}** to you today!

---

### What is {title}?

{extract}

---

### Core Principles Broken Down Simply

{points}

---

### Everyday Real-World Analogy

Think of **{title}** like an engineered system: every part has a specific responsibility, working harmoniously together to produce predictable, beneficial outcomes every time!

***

Would you like to see another practical example of **{title}**, or take a 10-question quiz to test yourself?"""

    clean = clean_topic(topic)
    return f"""Hello! I am **EduGenie**, your friendly AI tutor. I'm excited to explain **{clean}** to you today!

---

### What is {clean}?

**{clean}** is an important concept in your studies! Just like building with Lego blocks, understanding this topic becomes easy when we break it down into simple, manageable pieces:

1. **Foundational Definition:** The core rules and theories that establish what {clean} does.
2. **Everyday Analogy:** Connects abstract theory to familiar real-world experiences.
3. **Practical Application:** Solves concrete problems in modern technology, science, and industry.

***

Would you like to test your understanding with an interactive quiz on **{clean}**?"""
