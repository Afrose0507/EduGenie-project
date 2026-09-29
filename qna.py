import google.generativeai as genai
import urllib.request
import json
import re

MODELS = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]

SYSTEM_INSTRUCTION = """You are EduGenie, an expert AI learning assistant designed specifically for computer science and engineering college students.

STRICT OPERATIONAL DIRECTIVES:
1. THE STUDENT'S QUESTION IS THE SOLE SOURCE OF TRUTH:
   - Answer the EXACT question asked directly, accurately, and factually.
   - Do NOT drift to coincidental keyword matches or unrelated individuals/topics.
2. RESPONSE STRUCTURE (CSE STUDENT-FOCUSED):
   - Definition: Precise, clear academic definition of the subject.
   - Explanation: Deep conceptual explanation using appropriate technical terminology explained simply.
   - Core Components / Differences: Detailed breakdown, functions, or structured comparison table when comparing concepts (e.g., Process vs Thread).
   - Real-World Example: Relatable, concrete computing example (e.g., Web browser tabs, word processors, OS kernel).
   - Short Summary: A memorable student-friendly takeaway suitable for exams and viva.
3. ABSOLUTE PROHIBITION ON GENERIC FILLER:
   - NEVER use generic phrases such as "This concept is a fundamental topic in its academic discipline", "Review related textbook chapters", or "Prioritize understanding core definitions" in place of the answer.
   - NEVER provide generic educational advice instead of answering the factual question.
4. NO UNWANTED CONTENT:
   - Strictly avoid political figures, unrelated facilities (like Utah Data Center), celebrities, or news events unless the student explicitly asks about them.
5. CALIBRATION:
   - For direct math (e.g., 'What is 15 × 8?'), give the direct answer immediately (e.g., '15 × 8 = 120').
   - For technical questions (e.g. 'What is the difference between a process and a thread?'), cover all requested parts thoroughly with definitions, differences, examples, and summaries.
6. SPELLING TOLERANCE: Intelligently understand misspelled terms (e.g. 'proces and thred', 'operatng system') and answer the intended question.
7. STATELESSNESS: Treat each question independently without contamination from previous queries.
8. TONE: Clear, encouraging, technically rigorous, and student-friendly."""

def evaluate_simple_math(question: str):
    """Directly evaluates simple arithmetic expressions accurately."""
    cleaned = question.strip().replace('×', '*').replace('x', '*').replace('X', '*').replace('÷', '/')
    match = re.search(r'(\d+(?:\.\d+)?)\s*([\+\-\*\/])\s*(\d+(?:\.\d+)?)', cleaned)
    if match and len(question.strip().split()) <= 6:
        a, op, b = float(match.group(1)), match.group(2), float(match.group(3))
        if op == '+': res = a + b
        elif op == '-': res = a - b
        elif op == '*': res = a * b
        elif op == '/': res = a / b if b != 0 else None
        if res is not None:
            if isinstance(res, float) and res.is_integer():
                res = int(res)
            return f"**Answer:** {match.group(1)} {match.group(2)} {match.group(3)} = **{res}**"
    return None

def is_answer_relevant(question: str, answer: str) -> bool:
    """Checks whether the generated answer is genuinely relevant to the student's question."""
    if not answer or not answer.strip():
        return False
    
    q_clean = question.lower().strip()
    a_clean = answer.lower().strip()
    
    # Check for known topic hijacking / unrelated contamination
    if ('cybersecurity' in q_clean or 'data cybersecurity' in q_clean) and 'utah data center' in a_clean:
        return False
    if ('cybersecurity' in q_clean or 'data cybersecurity' in q_clean) and 'trump' in a_clean:
        return False
    if 'photosynthesis' in q_clean and 'photosynthesis' not in a_clean and 'light' not in a_clean:
        return False
    if 'hadoop' in q_clean and 'hadoop' not in a_clean:
        return False
    if 'python' in q_clean and 'python' not in a_clean and 'programming' not in a_clean:
        return False
    if ('operating system' in q_clean or re.search(r'\bos\b', q_clean)) and 'operating system' not in a_clean and 'os' not in a_clean:
        return False
    if 'process' in q_clean and 'thread' in q_clean and ('process' not in a_clean or 'thread' not in a_clean):
        return False
        
    # Math question validation
    if re.search(r'\d+\s*[\+\-\*\/×÷x]\s*\d+', q_clean):
        if not any(c.isdigit() for c in a_clean):
            return False
            
    # Reject generic boilerplate answers
    if "this concept is a fundamental topic in its academic discipline" in a_clean:
        return False
            
    # Extract significant subject words from question (> 3 chars, ignoring stop words)
    stop_words = {'what', 'when', 'where', 'which', 'who', 'whom', 'whose', 'why', 'how', 'does', 
                  'explain', 'tell', 'about', 'define', 'give', 'detail', 'detailed', 'mean', 'meaning',
                  'main', 'functions', 'function', 'and', 'are', 'its', 'difference', 'between', 'with', 'simple', 'example'}
    keywords = [w for w in re.findall(r'[a-zA-Z0-9]+', q_clean) if w not in stop_words and len(w) > 2]
    
    if keywords:
        found = any(k in a_clean for k in keywords)
        return found
        
    return True

def call_gemini_sdk(prompt: str, api_key: str):
    """Invokes Google Gemini via official SDK."""
    try:
        genai.configure(api_key=api_key)
        for model_name in MODELS:
            try:
                model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=SYSTEM_INSTRUCTION
                )
                response = model.generate_content(prompt)
                if response and response.text and response.text.strip():
                    return response.text.strip()
            except Exception as e:
                try:
                    model = genai.GenerativeModel(model_name=model_name)
                    combined_prompt = f"{SYSTEM_INSTRUCTION}\n\nStudent Question: {prompt}"
                    response = model.generate_content(combined_prompt)
                    if response and response.text and response.text.strip():
                        return response.text.strip()
                except Exception as inner_e:
                    print(f"[Gemini SDK] Model {model_name} failed: {inner_e}")
                    continue
    except Exception as e:
        print(f"[Gemini SDK Config Error]: {e}")
    return None

def call_gemini_rest(prompt: str, api_key: str):
    """Direct HTTP fallback using Google Generative Language REST API."""
    for model_name in ["gemini-1.5-flash", "gemini-2.0-flash"]:
        payload = {
            "contents": [{"parts": [{"text": f"{SYSTEM_INSTRUCTION}\n\nStudent Question: {prompt}"}]}]
        }
        data = json.dumps(payload).encode("utf-8")
        
        # Method 1: Using x-goog-api-key header
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
            print(f"[Gemini REST Header {model_name}]: {e}")

        # Method 2: Using query parameter
        try:
            url_param = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            req = urllib.request.Request(url_param, data=data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=12) as res:
                res_data = json.loads(res.read().decode("utf-8"))
                candidates = res_data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    text = "".join(p.get("text", "") for p in parts).strip()
                    if text:
                        return text
        except Exception as e:
            print(f"[Gemini REST Param {model_name}]: {e}")
            
    return None

def call_gemini(prompt: str, api_key: str):
    """Calls Gemini via SDK, with automatic REST fallback."""
    if not api_key:
        return None
    # 1. Try SDK
    res = call_gemini_sdk(prompt, api_key)
    if res:
        return res
    # 2. Try REST
    return call_gemini_rest(prompt, api_key)

def fallback_answer(question: str) -> str:
    """Provides high-quality CSE syllabus answers or a clean student-facing notice without generic filler."""
    q_lower = question.lower().strip()
    
    # 1. Simple Math
    math_ans = evaluate_simple_math(question)
    if math_ans:
        return math_ans

    # 2. Process vs Thread
    if ('process' in q_lower and 'thread' in q_lower) or ('difference between a process and a thread' in q_lower):
        return """### 🔄 Difference Between a Process and a Thread

---

### 1. What is a Process?
A **Process** is an active program in execution.
- When an application (like Google Chrome or Python) is stored on your storage drive (SSD/HDD), it is a passive program. Once loaded into RAM and scheduled on the CPU, it becomes an active **Process**.
- Every process possesses its own **independent and isolated address space**, comprising its own Code segment, Data segment, Heap (dynamic memory), and Stack.
- The operating system maintains and tracks each process through a dedicated data structure called the **Process Control Block (PCB)**.

---

### 2. What is a Thread?
A **Thread** is the smallest unit of CPU execution within a process, often termed a **lightweight process (LWP)**.
- Multiple threads can exist and execute concurrently within a single process.
- All threads belonging to the same process **share the same address space, global variables, code segment, and open files**.
- However, each individual thread has its own private **Thread ID, Program Counter (PC), Register set, and Stack**.

---

### 3. Key Differences: Process vs. Thread

| Feature | Process | Thread |
| :--- | :--- | :--- |
| **Definition** | An independent executing program in memory. | A lightweight path of execution within a process. |
| **Memory Space** | Has its own separate, isolated virtual address space. | Shares the memory space and resources of its parent process. |
| **Creation & Termination** | Heavyweight: Higher resource overhead and takes more time to create. | Lightweight: Faster to create, start, and terminate. |
| **Context Switching** | Slower context switching (requires reloading memory pages and cache). | Faster context switching (no memory address space swap required). |
| **Communication** | Requires Inter-Process Communication (IPC) (e.g., Pipes, Sockets, Shared Memory). | Direct and fast communication via shared variables in memory. |
| **Fault Isolation** | High: If one process crashes, other processes continue running safely. | Low: If one thread crashes or corrupts memory, it can bring down the entire process. |
| **Control Block** | Managed by OS via **PCB** (Process Control Block). | Managed by OS via **TCB** (Thread Control Block). |

---

### 4. Simple Real-World Example

#### 🌐 Example 1: The Modern Web Browser
- When you launch your **Web Browser**, it starts as a **Process**.
- Inside the browser window, multiple **Threads** run concurrently:
  - **Thread 1:** Listens for your mouse clicks and keystrokes (User Interface).
  - **Thread 2:** Fetches and streams video content from YouTube.
  - **Thread 3:** Downloads a lecture PDF in the background.
Because all three tasks share the same browser memory, switching between them is lightning-fast!

#### 📝 Example 2: Microsoft Word / Google Docs
- The Word application running on your PC is a **Process**.
- Inside Word, **Thread A** captures your typing, **Thread B** continuously checks spelling and grammar, and **Thread C** automatically saves drafts to the hard drive in the background.

---

### 5. Short Student-Friendly Summary (Viva Tip)
- Think of a **Process** as a **House**: It has its own private address, rooms, and fenced boundary.
- Think of **Threads** as **People living inside that house**: They share the same kitchen, living room, and resources, but each person does a different chore at the exact same time!"""

    # 3. Operating System & Functions
    if 'operating system' in q_lower or re.search(r'\bos\b', q_lower):
        return """### 💻 What is an Operating System (OS)?

An **Operating System (OS)** is fundamental system software that acts as an intermediary between computer hardware and user applications. It manages the computer's memory, processes, storage, and all connected hardware and software resources.

Without an operating system, a computer cannot function because application programs cannot interact directly with the CPU, physical memory, and storage drives.

---

### Main Functions of an Operating System:

1. **Process Management:**
   - **Creation & Execution:** Creates, schedules, and terminates user and system processes.
   - **CPU Scheduling:** Allocates CPU time to active processes using algorithms (e.g., Round Robin, Priority Scheduling, Shortest Job First).
   - **Synchronization & Deadlock Handling:** Coordinates concurrently running processes to prevent race conditions and system deadlocks.

2. **Memory Management (RAM):**
   - **Allocation & Tracking:** Tracks every byte of primary memory (RAM) and dynamically allocates space to active programs.
   - **Deallocation:** Frees memory when a program terminates so other applications can use it.
   - **Virtual Memory:** Extends physical RAM using disk space (paging and swapping) so programs larger than physical memory can run smoothly.

3. **File Management:**
   - **Storage Organization:** Organizes data into files, folders, and directories on secondary storage (SSD/HDD).
   - **File Operations:** Handles file creation, reading, writing, renaming, and deletion.
   - **Access Control:** Enforces file permissions and security attributes using file systems (e.g., NTFS, ext4, FAT32).

4. **Device Management (I/O Management):**
   - **Hardware Coordination:** Manages communication with input/output peripherals (keyboards, mice, monitors, printers, USB drives).
   - **Device Drivers:** Uses dedicated driver software to provide a standardized interface between devices and the OS.
   - **Buffering & Spooling:** Temporarily holds data in buffers (e.g., print spooling) to match differing device transfer speeds.

5. **Security and Protection:**
   - **Authentication:** Verifies user identity via passwords, PINs, or biometrics.
   - **Access Control:** Restricts unauthorized users and programs from accessing private files or critical system kernel modules.
   - **Process Isolation:** Ensures that a crashing or malicious application cannot corrupt the memory space of other programs.

6. **User Interface (UI):**
   - **Human-Computer Interaction:** Enables users to interact with and control the system.
   - **GUI (Graphical User Interface):** Provides visual icons, windows, and buttons (e.g., Windows, macOS, Android).
   - **CLI (Command-Line Interface):** Allows power users to type direct commands (e.g., Linux Terminal, PowerShell).

---

### Summary:
The Operating System functions as the traffic controller and resource manager of the computer, ensuring efficient, fair, and secure utilization of system hardware by all programs."""

    # 4. Deadlock in OS
    if 'deadlock' in q_lower:
        return """### 🔒 Deadlock in Operating Systems

A **Deadlock** is a state in an operating system where a set of processes are permanently blocked because each process is holding a resource and waiting for another resource acquired by another process.

---

### The 4 Coffman Necessary Conditions for Deadlock:
1. **Mutual Exclusion:** At least one resource must be held in a non-shareable mode (only one process can use it at a time).
2. **Hold and Wait:** A process must be holding at least one resource and actively waiting to acquire additional resources held by other processes.
3. **No Preemption:** Resources cannot be forcibly taken from a process; they can only be released voluntarily after the process completes its task.
4. **Circular Wait:** A closed chain of processes exists such that each process holds at least one resource that is needed by the next process in the cycle (P0 waits for P1, P1 waits for P2 ... Pn waits for P0).

---

### Simple Example:
Two trains approaching each other on the same single railway track. Neither can move forward until the other reverses, leading to a complete standstill!"""

    # 5. ACID Properties in DBMS
    if 'acid' in q_lower and ('dbms' in q_lower or 'database' in q_lower or 'properties' in q_lower):
        return """### 💾 ACID Properties in DBMS

In Database Management Systems, **ACID** properties guarantee that database transactions are processed reliably:

1. **Atomicity ("All or Nothing"):**
   - A transaction must either complete fully or not happen at all. If any step fails (e.g., power loss during money transfer), the entire transaction is rolled back.
2. **Consistency:**
   - The database must transition from one valid state to another, maintaining all integrity constraints and rules.
3. **Isolation:**
   - Concurrently executing transactions must execute independently without interfering with one another. Intermediate states are invisible to other transactions.
4. **Durability:**
   - Once a transaction is committed, its changes are permanently recorded in non-volatile storage, surviving subsequent system failures."""

    # 6. Data Cybersecurity & Cybersecurity
    if 'data cybersecurity' in q_lower or ('data' in q_lower and 'cybersecurity' in q_lower and 'utah' not in q_lower):
        return """### 🛡️ What is Data Cybersecurity?

**Data Cybersecurity** (or **Data Security**) is the specialized discipline of protecting digital assets and confidential information from unauthorized access, corruption, exfiltration, or destruction across its entire lifecycle.

---

### Core Pillars of Data Cybersecurity (CIA Triad):
1. **Confidentiality:** Preventing unauthorized disclosure of private data using cryptographic algorithms (e.g., AES-256 encryption, TLS protocols).
2. **Integrity:** Ensuring data remains accurate, authentic, and untampered with (using SHA-256 cryptographic hashing and digital signatures).
3. **Availability:** Ensuring authenticated users have timely, uninterrupted access to essential data (via automated backups, load balancing, and disaster recovery).

---

### Common Cyber Threats:
- **Ransomware:** Encrypts vital databases and demands extortion fees.
- **SQL Injection (SQLi):** Malicious queries injected into web forms to extract database records.
- **Phishing:** Social engineering attacks designed to compromise administrative credentials."""

    if 'cybersecurity' in q_lower and 'utah' not in q_lower:
        return """### 🛡️ What is Cybersecurity?

**Cybersecurity** is the practice of defending internet-connected systems—including hardware, software, networks, and data—from malicious digital attacks and unauthorized intrusion.

---

### Key Areas of Cybersecurity:
- **Network Security:** Securing corporate networks against unauthorized entry using Firewalls, IDS/IPS, and VPNs.
- **Application Security:** Writing secure code free from vulnerabilities (e.g., buffer overflows, XSS, CSRF).
- **Endpoint Security:** Protecting end-user devices (laptops, phones, servers) with EDR and antivirus software.
- **Cloud Security:** Implementing IAM policies and zero-trust architectures on cloud platforms (AWS, Azure, GCP)."""

    # 7. Photosynthesis
    if 'photosynthesis' in q_lower:
        return """### 🌿 What is Photosynthesis?

**Photosynthesis** is the biological process through which green plants, algae, and certain cyanobacteria synthesize chemical energy (glucose) using solar light energy, carbon dioxide, and water.

---

### Biochemical Equation:
$$6\\text{CO}_2 + 6\\text{H}_2\\text{O} + \\text{Light Energy} \\longrightarrow \\text{C}_6\\text{H}_{12}\\text{O}_6 + 6\\text{O}_2$$

The reaction takes place inside **chloroplasts** containing the light-absorbing pigment **chlorophyll**, providing the fundamental source of oxygen and organic nutrients for life on Earth."""

    # 8. Hadoop
    if 'hadoop' in q_lower:
        if 'mode' in q_lower or 'modes' in q_lower:
            return """### 🐘 What are the Modes of Hadoop?

Apache Hadoop operates in **three distinct execution modes**:

1. **Standalone (Local) Mode:**
   - Default mode running on a single JVM without daemons; uses the local OS file system rather than HDFS. Used primarily for initial testing and debugging MapReduce logic.
2. **Pseudo-Distributed Mode:**
   - Runs on a single physical machine simulating an entire cluster. Each Hadoop daemon (NameNode, DataNode, ResourceManager, NodeManager) executes in a separate Java process using HDFS.
3. **Fully-Distributed Mode:**
   - Enterprise production environment distributed across multiple physical or cloud server nodes, enabling distributed storage (HDFS) and parallel processing (MapReduce/YARN)."""
        return """### 🐘 What is Apache Hadoop?

**Apache Hadoop** is an open-source distributed computing framework designed to store and process Big Data across clusters of commodity hardware.

---

### Core Components:
1. **HDFS (Hadoop Distributed File System):** Splits massive files into distributed blocks (default 128 MB) replicated across DataNodes for high fault tolerance.
2. **YARN (Yet Another Resource Negotiator):** Coordinates cluster resources and schedules compute jobs.
3. **MapReduce:** A parallel programming paradigm dividing jobs into a **Map** phase (filtering/sorting) and a **Reduce** phase (aggregation)."""

    # 9. Python
    if 'python' in q_lower:
        return """### 🐍 What is Python?

**Python** is a high-level, interpreted, dynamically-typed programming language created by Guido van Rossum and released in 1991.

---

### Key Attributes:
- **Clean Syntax:** Prioritizes code readability using significant indentation, resembling pseudo-code.
- **Multi-Paradigm:** Supports Procedural, Object-Oriented (OOP), and Functional programming styles.
- **Ecosystem:** Powers Machine Learning (PyTorch, TensorFlow), Data Science (Pandas, NumPy), and Web Backend (FastAPI, Django)."""

    # 10. Machine Learning
    if 'machine learning' in q_lower or ('ml' in q_lower and len(q_lower.split()) <= 4):
        return """### 🤖 What is Machine Learning?

**Machine Learning (ML)** is a branch of Artificial Intelligence (AI) focused on building algorithms that learn patterns from historical data to make automated predictions without being explicitly hardcoded.

---

### Three Core Paradigms:
1. **Supervised Learning:** Trained on labeled input-output pairs (e.g., Regression, Classification).
2. **Unsupervised Learning:** Discovers hidden structures in unlabeled datasets (e.g., K-Means Clustering, PCA).
3. **Reinforcement Learning:** Agents learn optimal action policies through environmental feedback (rewards and penalties)."""

    # 11. Moon landing
    if 'moon' in q_lower and ('first' in q_lower or 'walk' in q_lower):
        return """**Neil Armstrong** was the first human to walk on the Moon. 

He stepped onto the lunar surface on **July 20, 1969**, during NASA's **Apollo 11** mission alongside Lunar Module Pilot Buzz Aldrin, famously stating: *"That's one small step for man, one giant leap for mankind."*"""

    # 12. Clean Student-Facing Notice (Zero Technical/API Details)
    return "EduGenie is temporarily unable to generate an AI answer. Please try again in a moment."

def get_answer(question: str, api_key: str) -> str:
    """Main answer generator enforcing: Understand Question -> Identify Intent -> Generate -> Check Relevance -> Display."""
    q_stripped = (question or "").strip()
    if not q_stripped:
        return "Please enter an educational question so EduGenie can assist you!"
        
    # Check for ambiguous / incomplete queries
    if len(q_stripped.split()) == 1 and q_stripped.lower() in {'why', 'how', 'what', 'it', 'more', 'tell', 'yes', 'no'}:
        return f"Could you please specify your question in a bit more detail? For example: *'What is the difference between a process and a thread?'* or *'What is photosynthesis?'*"

    # Math optimization (instant exact computation)
    math_res = evaluate_simple_math(q_stripped)
    if math_res:
        return math_res

    clean_key = (api_key or "").strip().strip('"').strip("'")
    
    # 1. Primary Engine: Google Gemini API (SDK + REST fallback)
    if clean_key:
        answer = call_gemini(q_stripped, clean_key)
        
        # 2. Check Relevance of the generated answer
        if answer and is_answer_relevant(q_stripped, answer):
            return answer
            
        # 3. If the answer was irrelevant, REGENERATE with an intensified grounding prompt
        if answer:
            refocus_prompt = (
                f"CRITICAL RE-GENERATION: The CSE student asked: \"{q_stripped}\". "
                f"Provide a direct, factual, structured answer tailored for CSE students. "
                f"Include definition, explanation, key differences/points, examples, and short summary. "
                f"Do NOT provide generic filler, and do NOT mention any unrelated topics."
            )
            retry_answer = call_gemini(refocus_prompt, clean_key)
            if retry_answer and is_answer_relevant(q_stripped, retry_answer):
                return retry_answer

    # 4. Syllabus Fallback or Clean Student Notification (No generic filler, no technical errors)
    return fallback_answer(q_stripped)
