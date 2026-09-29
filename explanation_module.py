import google.generativeai as genai
import re

MODELS = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]

SYSTEM_INSTRUCTION = """You are EduGenie, an expert AI learning assistant dedicated exclusively to explaining academic concepts to students clearly, factually, and thoroughly.

STRICT OPERATIONAL DIRECTIVES:
1. THE STUDENT'S TOPIC IS THE SOLE SOURCE OF TRUTH. Explain what the student actually asked for first.
2. RESPONSE PRIORITY & STRUCTURE:
   - PRIORITY 1: Clear definition and factual overview of the concept.
   - PRIORITY 2: Core components, functions, or step-by-step breakdown (e.g. for an Operating System: Process Management, Memory Management, File Management, Device Management, Security, and UI).
   - PRIORITY 3: A simple, relatable everyday analogy to make the concept intuitive.
   - PRIORITY 4: (Optional) A practical student takeaway or study tip at the end.
3. NEVER PRODUCE GENERIC FILLER:
   - Do NOT use generic phrases like "This concept is a fundamental topic in its academic discipline" or "Prioritize understanding theoretical foundations" instead of explaining the actual concept.
   - Always deliver factual, domain-specific insights immediately.
4. SPELLING TOLERANCE: Understand misspelled academic terms (e.g., 'operatng system', 'pythagras', 'hadop') and explain the intended concept.
5. STATELESSNESS: Treat every request independently without carryover from previous topics.
6. TONE: Warm, encouraging, clear, and student-focused."""

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
    if ('operating system' in t_clean or re.search(r'\bos\b', t_clean)) and 'operating system' not in e_clean and 'os' not in e_clean:
        return False
    if "this concept is a fundamental topic in its academic discipline" in e_clean:
        return False
        
    stop_words = {'what', 'is', 'a', 'an', 'the', 'of', 'in', 'on', 'at', 'to', 'for', 'explain', 'tell', 'about', 'define', 'main', 'functions'}
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
                prompt = f"Please explain the concept of '{topic}' in a clear, educational, beginner-friendly way with core functions and analogies."
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
    
    # 1. Operating System
    if 'operating system' in t_lower or re.search(r'\bos\b', t_lower):
        return """### 💻 Operating System (OS) Explained Simply

**What is it?**
An **Operating System (OS)** is the master software that coordinates all hardware (CPU, RAM, storage, peripherals) and provides an environment for software applications to run.

---

### The Restaurant Manager Analogy:
Think of a computer like a busy restaurant:
- **The Hardware (Kitchen & Ovens):** Raw computing power.
- **The Programs (Customers):** Wanting dishes prepared.
- **The Operating System (The Restaurant Manager):** Directs which orders the chefs cook first (Process Management), ensures tables are available (Memory Management), maintains the recipe book (File Management), and handles customer payments securely (Security).

---

### Main Functions of an OS:
1. **Process Management:** Schedules and allocates CPU time to all active applications.
2. **Memory Management:** Keeps track of primary RAM so programs don't overwrite each other.
3. **File Management:** Organizes files into directories on SSDs/hard drives.
4. **Device Management:** Uses device drivers to talk to keyboards, mice, screens, and printers.
5. **Security & Access Control:** Protects system files and prevents unauthorized logins.
6. **User Interface:** Provides the visual desktop (GUI) or terminal (CLI) for users to interact with."""

    # 2. Pythagoras Theorem
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

    # 3. Photosynthesis
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

    # 4. Data Cybersecurity / Cybersecurity
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

    # 5. Hadoop
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

    # Clear Notification when AI is unavailable (NO generic fake answers!)
    return f"""⚠️ **AI Explanation Unavailable**

EduGenie was unable to generate an AI explanation for: *"**{topic}**"*

**Reason:** The Google Gemini AI service could not be reached, or the configured API key is invalid/unauthenticated.

**How to resolve:**
1. Configure a valid Gemini API key in the application settings or Render environment variables (`GEMINI_API_KEY`).
2. You can generate a free Gemini API key anytime at [Google AI Studio](https://aistudio.google.com/app/apikey)."""

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
            retry_prompt = f"CRITICAL RE-GENERATION: Explain ONLY the educational concept: '{t_stripped}'. Provide clear definitions and factual breakdowns without generic fluff."
            retry_explanation = call_gemini_explain(retry_prompt, clean_key)
            if retry_explanation and is_explanation_relevant(t_stripped, retry_explanation):
                return retry_explanation
                
    # 3. Fallback
    return fallback_explanation(t_stripped)
