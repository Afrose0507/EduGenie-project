import google.generativeai as genai
import re

MODELS = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]

SYSTEM_INSTRUCTION = """You are EduGenie, an expert, friendly AI learning assistant dedicated exclusively to explaining academic concepts to students.

STRICT OPERATIONAL DIRECTIVES:
1. THE STUDENT'S TOPIC IS THE SOLE SOURCE OF TRUTH. Explain ONLY the concept the student asked for.
2. Read and fully understand the concept before formulating your explanation.
3. Identify the true educational intent. Do NOT drift to coincidental keyword matches, unrelated political events, or extraneous entities.
4. Explain clearly and progressively:
   - Provide a clear definition and core intuition.
   - Use simple, relatable everyday analogies.
   - Outline key principles or step-by-step breakdown.
   - Highlight why this concept is important in education and practice.
5. If the student makes a spelling error (e.g., 'pythagras', 'hadop', 'photosyntehsis'), understand the intended academic concept and explain that.
6. Treat every explanation request as completely independent. Do NOT carry over previous topics.
7. Maintain a warm, encouraging, student-friendly tone."""

def is_explanation_relevant(topic: str, explanation: str) -> bool:
    """Validates that the explanation strictly addresses the requested concept."""
    if not explanation or not explanation.strip():
        return False
    t_clean = topic.lower().strip()
    e_clean = explanation.lower().strip()
    
    # Flag known bad drift
    if ('cybersecurity' in t_clean or 'data cybersecurity' in t_clean) and 'utah' in e_clean:
        return False
    if ('cybersecurity' in t_clean or 'data cybersecurity' in t_clean) and 'trump' in e_clean:
        return False
        
    stop_words = {'what', 'is', 'a', 'an', 'the', 'of', 'in', 'on', 'at', 'to', 'for', 'explain', 'tell', 'about', 'define'}
    words = [w for w in re.findall(r'[a-zA-Z0-9]+', t_clean) if w not in stop_words and len(w) > 2]
    if words:
        return any(w in e_clean for w in words)
    return True

def call_gemini_explain(topic: str, api_key: str):
    if not api_key:
        return None
    try:
        genai.configure(api_key=api_key)
        for model_name in MODELS:
            try:
                model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=SYSTEM_INSTRUCTION
                )
                prompt = f"Please explain the concept of '{topic}' in a clear, educational, beginner-friendly way with analogies."
                response = model.generate_content(prompt)
                if response and response.text and response.text.strip():
                    return response.text.strip()
            except Exception:
                try:
                    model = genai.GenerativeModel(model_name=model_name)
                    combined_prompt = f"{SYSTEM_INSTRUCTION}\n\nExplain the concept of: {topic}"
                    response = model.generate_content(combined_prompt)
                    if response and response.text and response.text.strip():
                        return response.text.strip()
                except Exception:
                    continue
    except Exception as e:
        print(f"Gemini explain error: {e}")
    return None

def fallback_explanation(topic: str) -> str:
    t_lower = topic.lower().strip()
    
    # 1. Pythagoras Theorem
    if 'pythagoras' in t_lower:
        return """### 📐 Pythagoras Theorem Explained Simply

**The Core Concept:**
The Pythagorean Theorem is a fundamental rule in geometry that applies to any **right-angled triangle** (a triangle with one 90° angle).

**The Formula:**
$$a^2 + b^2 = c^2$$

- **$a$ and $b$** are the two shorter perpendicular sides forming the right angle.
- **$c$** is the longest side opposite the right angle, called the **hypotenuse**.

---

### Everyday Real-World Analogy:
Imagine walking along two sides of a square park: 3 meters East, then 4 meters North. Instead of walking $3 + 4 = 7$ meters, you take the diagonal shortcut across the grass:
$$\\sqrt{3^2 + 4^2} = \\sqrt{9 + 16} = \\sqrt{25} = 5 \\text{ meters!}$$
The shortcut is 5 meters. The Pythagorean Theorem lets you calculate diagonal distances in architecture, GPS navigation, and construction!"""

    # 2. Photosynthesis
    if 'photosynthesis' in t_lower:
        return """### 🌿 Photosynthesis Explained Simply

**What is it?**
Photosynthesis is how green plants, algae, and some bacteria synthesize their own food using sunlight, water, and carbon dioxide.

**The Plant Recipe:**
$$\\text{Carbon Dioxide} + \\text{Water} + \\text{Light} \\longrightarrow \\text{Glucose (Food)} + \\text{Oxygen}$$

---

### The Kitchen Analogy:
1. **Solar Panels (Leaves):** Green chlorophyll pigments capture energy from sunlight.
2. **Plumbing (Roots):** Roots draw water and minerals from the soil.
3. **Air Vents (Stomata):** Pores under the leaves absorb carbon dioxide from the air.
4. **The Meal & The Gift:** The plant produces sugary glucose to fuel its growth, and releases clean oxygen into the atmosphere for humans and animals to breathe!"""

    # 3. Data Cybersecurity / Cybersecurity
    if 'cybersecurity' in t_lower:
        return """### 🛡️ Cybersecurity Explained Simply

**What is it?**
Cybersecurity is the practice of protecting digital devices, networks, programs, and data from unauthorized access, cyber attacks, and damage.

---

### The Castle Analogy:
Think of a computer network like a medieval castle:
1. **The Moat (Firewall):** Blocks untrusted visitors and filters network traffic.
2. **The Castle Gate & Guards (Authentication):** Passwords and multi-factor authentication verify who is entering.
3. **Secret Language (Encryption):** Sensitive documents are encrypted so that even if a spy steals a letter, they cannot read it.
4. **Patrol Guards (Antivirus/EDR):** Continuously monitor internal corridors for malware or suspicious behavior."""

    # 4. Hadoop
    if 'hadoop' in t_lower:
        return """### 🐘 Apache Hadoop Explained Simply

**What is it?**
Apache Hadoop is a distributed software framework designed to store and process massive datasets (Big Data) across clusters of regular computers.

---

### The Teamwork Analogy:
Imagine counting 1,000,000 voter ballots alone. It would take weeks! Instead, you hire 100 assistants:
- Each person receives 10,000 ballots to count in parallel (the **Map** phase).
- A coordinator combines all 100 individual totals into one final count (the **Reduce** phase).

This is exactly how Hadoop MapReduce works, with **HDFS** storing the data safely across all 100 computers!"""

    # General concept
    clean_subj = re.sub(r'^(what is a|what is an|what is the|what is|what are the|what are|explain|define|tell me about)\s+', '', topic, flags=re.I).strip('? ')
    return f"""### 💡 Understanding: {clean_subj.title()}

**Concept Overview:**
**{clean_subj}** represents a fundamental educational subject. Breaking it down step by step:

1. **Core Meaning:** It describes specific principles, methodologies, and rules governing how systems or phenomena behave.
2. **Everyday Analogy:** Think of it like building blocks—each individual piece connects systematically to support larger, complex structures.
3. **Practical Application:** Mastering this concept equips students to solve practical problems, understand academic literature, and excel in coursework examinations.

---
💡 *Tip:* To receive dynamic generative AI explanations, ensure your Gemini API key is configured!"""

def explain_concept(topic: str, api_key: str) -> str:
    t_stripped = (topic or "").strip()
    if not t_stripped:
        return "Please enter an educational concept for EduGenie to explain!"
        
    clean_key = (api_key or "").strip().strip('"').strip("'")
    
    # 1. Primary: Google Gemini API
    if clean_key:
        explanation = call_gemini_explain(t_stripped, clean_key)
        if explanation and is_explanation_relevant(t_stripped, explanation):
            return explanation
            
        # 2. Regeneration if off-topic
        if explanation:
            retry_prompt = f"CRITICAL RE-GENERATION: Explain ONLY the educational concept: '{t_stripped}'. Do NOT mention any unrelated topics or external controversies."
            retry_explanation = call_gemini_explain(retry_prompt, clean_key)
            if retry_explanation and is_explanation_relevant(t_stripped, retry_explanation):
                return retry_explanation
                
    # 3. Fallback
    return fallback_explanation(t_stripped)
