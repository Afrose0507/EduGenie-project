import google.generativeai as genai
import urllib.request
import json
import re

MODELS = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]

SYSTEM_INSTRUCTION = """You are EduGenie, an expert AI learning assistant dedicated exclusively to explaining computer science and engineering concepts clearly to college students.

STRICT OPERATIONAL DIRECTIVES:
1. THE STUDENT'S TOPIC IS THE SOLE SOURCE OF TRUTH:
   - Explain the concept requested with academic rigor and intuitive clarity.
2. RESPONSE STRUCTURE (CSE STUDENT-FOCUSED):
   - Definition & Core Intuition
   - Technical Breakdown / Core Mechanisms
   - Real-World Analogy (connecting abstract theory to everyday systems)
   - Practical Application in Computer Science
   - Short Summary / Viva Tip
3. NEVER PRODUCE GENERIC FILLER:
   - Do NOT use generic phrases like "This concept is a fundamental topic in its academic discipline" or "Prioritize understanding theoretical foundations".
   - Always deliver domain-specific, actionable knowledge.
4. STATELESSNESS: Treat every request independently without carryover from previous topics.
5. TONE: Warm, encouraging, technically precise, and student-focused."""

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
    if 'process' in t_clean and 'thread' in t_clean and ('process' not in e_clean or 'thread' not in e_clean):
        return False
    if "this concept is a fundamental topic in its academic discipline" in e_clean:
        return False
        
    stop_words = {'what', 'is', 'a', 'an', 'the', 'of', 'in', 'on', 'at', 'to', 'for', 'explain', 'tell', 'about', 'define', 'main', 'functions', 'difference', 'between'}
    words = [w for w in re.findall(r'[a-zA-Z0-9]+', t_clean) if w not in stop_words and len(w) > 2]
    if words:
        return any(w in e_clean for w in words)
    return True

def call_gemini_explain_sdk(topic: str, api_key: str):
    try:
        genai.configure(api_key=api_key)
        for model_name in MODELS:
            try:
                model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=SYSTEM_INSTRUCTION
                )
                prompt = f"Please explain the concept of '{topic}' in a clear, structured way for CSE college students with technical mechanisms, analogies, and exam takeaways."
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
        print(f"[Gemini Explain SDK Error]: {e}")
    return None

def call_gemini_explain_rest(topic: str, api_key: str):
    for model_name in ["gemini-1.5-flash", "gemini-2.0-flash"]:
        payload = {
            "contents": [{"parts": [{"text": f"{SYSTEM_INSTRUCTION}\n\nExplain the concept of '{topic}' for CSE students."}]}]
        }
        data = json.dumps(payload).encode("utf-8")
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
            req = urllib.request.Request(
                url, 
                data=data, 
                headers={"Content-Type": "application/json", "x-goog-api-key": api_key}
            )
            with urllib.request.urlopen(req, timeout=12) as res:
                res_data = json.loads(res.read().decode("utf-8"))
                candidates = res_data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    text = "".join(p.get("text", "") for p in parts).strip()
                    if text:
                        return text
        except Exception as e:
            print(f"[Gemini Explain REST Error {model_name}]: {e}")
    return None

def call_gemini_explain(topic: str, api_key: str):
    if not api_key:
        return None
    res = call_gemini_explain_sdk(topic, api_key)
    if res:
        return res
    return call_gemini_explain_rest(topic, api_key)

def fallback_explanation(topic: str) -> str:
    t_lower = topic.lower().strip()
    
    # 1. Process vs Thread
    if ('process' in t_lower and 'thread' in t_lower) or ('difference between a process and a thread' in t_lower):
        return """### 🔄 Process vs. Thread Explained Simply

**Core Concepts:**
- **Process:** An independent program in execution with its own separate memory address space (PCB).
- **Thread:** A lightweight unit of execution within a process that shares memory and resources with sibling threads (TCB).

---

### The Restaurant Kitchen Analogy:
- **The Restaurant (Process):** Has its own dedicated kitchen, storage room, and business license. One restaurant's kitchen fire does not affect the restaurant next door (Fault Isolation).
- **The Chefs (Threads):** Multiple chefs working simultaneously in the same kitchen. They share the same counter, stoves, and ingredients (Shared Memory), allowing them to prepare orders in parallel!

---

### Key Takeaways for CSE Exams:
1. **Memory:** Process has isolated memory; Threads share memory.
2. **Context Switching:** Switching threads is much faster than switching processes.
3. **IPC:** Processes require Inter-Process Communication (Pipes/Sockets); Threads communicate directly via shared memory.
4. **Crash Impact:** If one process crashes, others survive; if a thread corrupts memory, the entire process can crash."""

    # 2. Operating System
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

    # 3. Pythagoras Theorem
    if 'pythagoras' in t_lower:
        return """### 📐 Pythagoras Theorem Explained Simply

**The Core Concept:**
The Pythagorean Theorem is a fundamental rule in geometry that applies to any **right-angled triangle** (a triangle with one 90° angle).

**The Formula:**
$$a^2 + b^2 = c^2$$

- **$a$ and $b$** are the two shorter perpendicular sides forming the right angle.
- **$c$** is the longest side opposite the right angle, called the **hypotenuse**."""

    # 4. Photosynthesis
    if 'photosynthesis' in t_lower:
        return """### 🌿 Photosynthesis Explained Simply

**What is it?**
Photosynthesis is how green plants, algae, and some bacteria synthesize their own food using sunlight, water, and carbon dioxide.

**The Plant Recipe:**
$$\\text{Carbon Dioxide} + \\text{Water} + \\text{Light} \\longrightarrow \\text{Glucose (Food)} + \\text{Oxygen}$$"""

    # 5. Cybersecurity
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

    # Clean student-facing notice (Zero Technical/API Details)
    return "EduGenie is temporarily unable to generate an AI explanation. Please try again in a moment."

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
            retry_prompt = f"CRITICAL RE-GENERATION: Explain ONLY the educational concept: '{t_stripped}'. Provide clear definitions, mechanisms, and analogies for CSE students."
            retry_explanation = call_gemini_explain(retry_prompt, clean_key)
            if retry_explanation and is_explanation_relevant(t_stripped, retry_explanation):
                return retry_explanation
                
    # 3. Fallback
    return fallback_explanation(t_stripped)
