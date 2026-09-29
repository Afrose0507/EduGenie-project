import gemini_client
import json
import re

SYSTEM_INSTRUCTION = """You are EduGenie, an expert AI learning assistant designed specifically for computer science and engineering college students.

STRICT OPERATIONAL DIRECTIVES:
1. THE STUDENT'S QUESTION IS THE SOLE SOURCE OF TRUTH:
   - Answer the EXACT question asked directly, accurately, and factually.
   - Do NOT drift to coincidental keyword matches or unrelated individuals/topics.
2. RESPONSE STRUCTURE (CSE STUDENT-FOCUSED):
   - Definition: Precise, clear academic definition of the subject.
   - Explanation: Deep conceptual explanation using appropriate technical terminology explained simply.
   - Core Components / Differences: Detailed breakdown, functions, or structured comparison table when comparing concepts (e.g., Process vs Thread, TCP vs UDP).
   - Real-World Example: Relatable, concrete computing example (e.g., Database normalization table, network protocols, OS kernel).
   - Short Summary: A memorable student-friendly takeaway suitable for exams and viva.
3. ABSOLUTE PROHIBITION ON GENERIC FILLER:
   - NEVER use generic phrases such as "This concept is a fundamental topic in its academic discipline", "Review related textbook chapters", or "Prioritize understanding core definitions" in place of the answer.
   - NEVER provide generic educational advice instead of answering the factual question.
4. NO UNWANTED CONTENT:
   - Strictly avoid political figures, unrelated facilities (like Utah Data Center), celebrities, or news events unless the student explicitly asks about them.
5. CALIBRATION:
   - For direct math (e.g., 'What is 15 × 8?'), give the direct answer immediately (e.g., '15 × 8 = 120').
   - For technical questions, cover all requested parts thoroughly with definitions, differences, examples, and summaries.
6. SPELLING TOLERANCE: Intelligently understand misspelled terms (e.g. 'normalisation', 'proces and thred', 'operatng system') and answer the intended question.
7. STATELESSNESS: Treat each question independently without contamination from previous queries.
8. TONE: Clear, encouraging, technically rigorous, and student-focused."""

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
    if 'normalization' in q_clean and 'normal' not in a_clean and '1nf' not in a_clean:
        return False
    if 'tcp' in q_clean and 'udp' in q_clean and ('tcp' not in a_clean or 'udp' not in a_clean):
        return False
    if 'binary search' in q_clean and 'binary search' not in a_clean:
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

def call_gemini(prompt: str, api_key: str):
    """Invokes Google Gemini with modern models and REST/SDK fallback."""
    return gemini_client.generate_text(prompt, api_key, system_instruction=SYSTEM_INSTRUCTION)

def fallback_answer(question: str) -> str:
    """Provides high-quality CSE syllabus answers or a clean student-facing notice without generic filler."""
    q_lower = question.lower().strip()
    
    # 1. Simple Math
    math_ans = evaluate_simple_math(question)
    if math_ans:
        return math_ans

    # 2. Normalization in DBMS (1NF, 2NF, 3NF)
    if 'normalization' in q_lower or 'normal form' in q_lower or ('1nf' in q_lower and '2nf' in q_lower):
        return r"""### 🗄️ Database Normalization: 1NF, 2NF, and 3NF Explained

---

### 1. What is Normalization?
**Normalization** is a systematic database design technique in DBMS that organizes tables to **minimize data redundancy** (duplication) and eliminate **undesirable anomalies** (Insertion, Update, and Deletion anomalies).

Without normalization, storing duplicate customer or course data in multiple rows leads to inconsistent records and bloated databases.

---

### 2. First Normal Form (1NF)
**Rule:** A table is in 1NF if and only if **all attribute values are atomic** (indivisible) and there are **no repeating groups or arrays**.

#### ❌ Unnormalized Example:
| Student_ID | Student_Name | Courses |
| :---: | :---: | :---: |
| 101 | Rahul | DBMS, OS |
| 102 | Priya | Python, Networks |

*(Violation: The 'Courses' column contains multiple values, not atomic single values).*

#### ✅ Converted to 1NF:
| Student_ID | Student_Name | Course |
| :---: | :---: | :---: |
| 101 | Rahul | DBMS |
| 101 | Rahul | OS |
| 102 | Priya | Python |
| 102 | Priya | Networks |

---

### 3. Second Normal Form (2NF)
**Rule:** A table is in 2NF if:
1. It is already in **1NF**.
2. There are **no Partial Functional Dependencies** (i.e., every non-prime attribute must depend on the **whole** candidate key, not just a part of a composite key).

#### ❌ 1NF Table with Partial Dependency:
Consider Composite Primary Key: `(Student_ID, Course_ID)`
| Student_ID (Key) | Course_ID (Key) | Course_Fee |
| :---: | :---: | :---: |
| 101 | C101 | \$300 |
| 102 | C101 | \$300 |

*(Violation: `Course_Fee` depends ONLY on `Course_ID`, not on `Student_ID`. That is a partial dependency!)*

#### ✅ Converted to 2NF (Split into Two Tables):
- **Table 1 (Enrollment):** `(Student_ID, Course_ID)`
- **Table 2 (Courses):** `(Course_ID, Course_Fee)`

---

### 4. Third Normal Form (3NF)
**Rule:** A table is in 3NF if:
1. It is already in **2NF**.
2. There is **no Transitive Dependency** (i.e., non-prime attributes must not depend on other non-prime attributes: if $A \rightarrow B$ and $B \rightarrow C$, then $A \rightarrow C$ must be removed).

#### ❌ 2NF Table with Transitive Dependency:
Primary Key: `Student_ID`
| Student_ID (Key) | Student_Name | Dept_ID | Dept_Head |
| :---: | :---: | :---: | :---: |
| 101 | Rahul | D01 | Dr. Sharma |
| 102 | Priya | D01 | Dr. Sharma |

*(Violation: `Student_ID` $\rightarrow$ `Dept_ID`, and `Dept_ID` $\rightarrow$ `Dept_Head`. Therefore, `Dept_Head` transitively depends on `Student_ID`).*

#### ✅ Converted to 3NF (Split into Two Tables):
- **Table 1 (Students):** `(Student_ID, Student_Name, Dept_ID)`
- **Table 2 (Departments):** `(Dept_ID, Dept_Head)`

---

### 5. Quick Viva Summary:
- **1NF:** Eliminate repeating multi-valued attributes (Make values **atomic**).
- **2NF:** 1NF + Eliminate **partial dependencies** (Depend on the *whole* key).
- **3NF:** 2NF + Eliminate **transitive dependencies** (Depend on *nothing but* the key)."""

    # 3. TCP vs UDP
    if ('tcp' in q_lower and 'udp' in q_lower) or ('difference between tcp and udp' in q_lower):
        return """### 🌐 Difference Between TCP and UDP

---

### 1. What is TCP (Transmission Control Protocol)?
**TCP** is a connection-oriented, reliable transport layer protocol.
- Before transmitting any data, TCP establishes a connection using a **Three-Way Handshake** (`SYN` $\rightarrow$ `SYN-ACK` $\rightarrow$ `ACK`).
- It guarantees that all packets arrive in their exact order without corruption, using sequence numbers, checksums, and acknowledgments. If a packet is lost, TCP automatically retransmits it.

---

### 2. What is UDP (User Datagram Protocol)?
**UDP** is a connectionless, lightweight transport layer protocol.
- UDP sends independent datagrams directly to the destination without establishing an upfront connection or waiting for acknowledgments.
- It does **not** guarantee delivery order or retransmit lost packets, making it dramatically faster and having lower latency than TCP.

---

### 3. Key Differences: TCP vs. UDP

| Feature | TCP (Transmission Control Protocol) | UDP (User Datagram Protocol) |
| :--- | :--- | :--- |
| **Connection Type** | Connection-Oriented (Requires Handshake) | Connectionless (No Handshake) |
| **Reliability** | Highly Reliable (Guaranteed delivery & retransmission) | Unreliable (Best-effort delivery, no retransmissions) |
| **Ordering** | Guarantees packets arrive in exact sequence | Packets may arrive out of order or be dropped |
| **Speed & Overhead** | Slower (20-60 byte header, acknowledgment overhead) | Ultra Fast (8-byte fixed header, lightweight) |
| **Flow & Congestion Control** | Supported (Sliding window, congestion avoidance) | None |
| **Data Boundary** | Byte-stream oriented | Message-oriented (Datagrams) |
| **Common Protocols** | HTTP/HTTPS (Web), FTP (Files), SMTP (Email), SSH | DNS, DHCP, VoIP, Online Gaming, Live Video Streaming |

---

### 4. Simple Real-World Example:
- **TCP is like a Certified Phone Call:** You say *"Hello, can you hear me?"* (Handshake). If a sentence is unclear, the other person asks *"Can you repeat that?"* (Acknowledgment & Retransmission).
- **UDP is like a Live Radio Broadcast or Mail Postcard:** The DJ broadcasts music into the air. If there is static for 1 second, the radio doesn't stop or rewind—it keeps playing live in real time!

---

### 5. Summary (Viva Tip):
Use **TCP** when **accuracy and complete data** are critical (web pages, banking, emails). Use **UDP** when **speed and low latency** matter more than an occasional dropped frame (live gaming, Zoom calls)."""

    # 4. Binary Search
    if 'binary search' in q_lower:
        return """### 🔍 Binary Search Algorithm Explained

---

### 1. What is Binary Search?
**Binary Search** is an efficient divide-and-conquer search algorithm used to find the position of a target element within a **strictly sorted array**.

Unlike Linear Search (which scans every item one by one with $O(n)$ time complexity), Binary Search achieves **$O(\\log n)$** time complexity by repeatedly halving the search interval.

---

### 2. How Binary Search Works (Step-by-Step):
1. **Requirement:** The array must be sorted in ascending (or descending) order.
2. Initialize two pointers: `low = 0` and `high = n - 1`.
3. Calculate the middle index: `mid = low + (high - low) // 2`.
4. **Compare Target with `arr[mid]`:**
   - If `arr[mid] == target`: Element found! Return `mid`.
   - If `arr[mid] < target`: The target is in the right half $\rightarrow$ Set `low = mid + 1`.
   - If `arr[mid] > target`: The target is in the left half $\rightarrow$ Set `high = mid - 1`.
5. Repeat until `low > high` (Element not present).

---

### 3. Concrete Example:
Search for **Target = 23** in sorted array:
`arr = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]` ($n = 10$)

- **Pass 1:** `low = 0`, `high = 9`. 
  `mid = (0 + 9) // 2 = 4` $\rightarrow$ `arr[4] = 16`.
  Since $23 > 16$, search the right half $\rightarrow$ Set `low = 4 + 1 = 5`.

- **Pass 2:** `low = 5`, `high = 9`.
  `mid = (5 + 9) // 2 = 7` $\rightarrow$ `arr[7] = 56`.
  Since $23 < 56$, search the left half $\rightarrow$ Set `high = 7 - 1 = 6`.

- **Pass 3:** `low = 5`, `high = 6`.
  `mid = (5 + 6) // 2 = 5` $\rightarrow$ `arr[5] = 23`.
  **Match found!** Target 23 is at index `5` in just **3 comparisons** (Linear search would have taken 6!).

---

### 4. Complexity Analysis:
- **Best Case:** $O(1)$ (Target is directly at the middle index).
- **Average & Worst Case:** $O(\\log_2 n)$ (Halves array size each step).
- **Space Complexity:** $O(1)$ for Iterative implementation, $O(\\log n)$ for Recursive call stack.

---

### 5. Short Viva Summary:
Binary Search works like looking up a word in a dictionary: you open directly to the middle, decide if your word comes before or after, and discard half the pages instantly!"""

    # 5. Process vs Thread
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

    # 6. Deadlock in OS
    if 'deadlock' in q_lower:
        return r"""### 🔒 Deadlock in Operating Systems

---

### 1. What is a Deadlock?
A **Deadlock** is an undesirable situation in multi-programming operating systems where a set of concurrent processes are **permanently blocked** because each process holds a resource and waits to acquire another resource held by another process in the set.

None of the processes can run, release their resources, or terminate, causing system throughput to drop to zero.

---

### 2. The 4 Necessary Coffman Conditions for Deadlock:
All four conditions must hold simultaneously for a deadlock to occur:

1. **Mutual Exclusion:** At least one resource must be held in a non-shareable mode (only one process can use the resource at any given instant).
2. **Hold and Wait:** A process must currently hold at least one resource and simultaneously wait to acquire additional resources held by other processes.
3. **No Preemption:** Resources cannot be forcibly seized from a process; a resource can only be released voluntarily after the process finishes execution.
4. **Circular Wait:** A closed cycle of processes exists $\{P_0, P_1, \\dots, P_n\}$ such that $P_0$ waits for a resource held by $P_1$, $P_1$ waits for $P_2$, ..., and $P_n$ waits for $P_0$.

---

### 3. Classic Real-World Analogy:
Imagine four cars arriving simultaneously at an unregulated four-way traffic intersection from North, South, East, and West. Each car wants to turn left, blocking the path of the car to its left. No car can move forward without a collision, resulting in a complete gridlock!

---

### 4. Deadlock Handling Strategies:
1. **Deadlock Prevention:** Design protocols ensuring at least one of the 4 Coffman conditions can never hold.
2. **Deadlock Avoidance:** Dynamically monitor resource allocation states using algorithms like **Banker's Algorithm** to avoid unsafe states.
3. **Deadlock Detection & Recovery:** Allow deadlocks to occur, detect cycles using Resource Allocation Graphs (RAG), and recover by terminating processes or preempting resources.
4. **Deadlock Ignorance (Ostrich Algorithm):** Pretend deadlocks never occur (adopted by general-purpose OS like Windows and Linux due to the rarity of deadlocks vs. the performance cost of prevention)."""

    # 7. Operating System & Functions
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

    # 8. Data Cybersecurity & Cybersecurity
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

    # 9. Photosynthesis
    if 'photosynthesis' in q_lower:
        return """### 🌿 What is Photosynthesis?

**Photosynthesis** is the biological process through which green plants, algae, and certain cyanobacteria synthesize chemical energy (glucose) using solar light energy, carbon dioxide, and water.

---

### Biochemical Equation:
$$6\\text{CO}_2 + 6\\text{H}_2\\text{O} + \\text{Light Energy} \\longrightarrow \\text{C}_6\\text{H}_{12}\\text{O}_6 + \\text{Oxygen}$$

The reaction takes place inside **chloroplasts** containing the light-absorbing pigment **chlorophyll**, providing the fundamental source of oxygen and organic nutrients for life on Earth."""

    # 10. Hadoop
    if 'hadoop' in q_lower:
        if 'mode' in q_lower or 'modes' in q_lower:
            return """### 🐘 What are the Modes of Hadoop?

Apache Hadoop operates in **three distinct execution modes**:

1. **Standalone (Local) Mode:** Default mode running on a single JVM without daemons; uses the local OS file system rather than HDFS. Used primarily for initial testing and debugging MapReduce logic.
2. **Pseudo-Distributed Mode:** Runs on a single physical machine simulating an entire cluster. Each Hadoop daemon (NameNode, DataNode, ResourceManager, NodeManager) executes in a separate Java process using HDFS.
3. **Fully-Distributed Mode:** Enterprise production environment distributed across multiple physical or cloud server nodes, enabling distributed storage (HDFS) and parallel processing (MapReduce/YARN)."""
        return """### 🐘 What is Apache Hadoop?

**Apache Hadoop** is an open-source distributed computing framework designed to store and process Big Data across clusters of commodity hardware.

---

### Core Components:
1. **HDFS (Hadoop Distributed File System):** Splits massive files into distributed blocks (default 128 MB) replicated across DataNodes for high fault tolerance.
2. **YARN (Yet Another Resource Negotiator):** Coordinates cluster resources and schedules compute jobs.
3. **MapReduce:** A parallel programming paradigm dividing jobs into a **Map** phase (filtering/sorting) and a **Reduce** phase (aggregation)."""

    # 11. Python & ML
    if 'python' in q_lower:
        return """### 🐍 What is Python?

**Python** is a high-level, interpreted, dynamically-typed programming language created by Guido van Rossum and released in 1991.

---

### Key Attributes:
- **Clean Syntax:** Prioritizes code readability using significant indentation, resembling pseudo-code.
- **Multi-Paradigm:** Supports Procedural, Object-Oriented (OOP), and Functional programming styles.
- **Ecosystem:** Powers Machine Learning (PyTorch, TensorFlow), Data Science (Pandas, NumPy), and Web Backend (FastAPI, Django)."""

    # 12. Clean Student-Facing Notice (Zero Technical/API Details)
    return "EduGenie is temporarily unable to generate an AI answer. Please try again in a moment."

def get_answer(question: str, api_key: str) -> str:
    """Main answer generator enforcing: Understand Question -> Identify Intent -> Generate -> Check Relevance -> Display."""
    q_stripped = (question or "").strip()
    if not q_stripped:
        return "Please enter an educational question so EduGenie can assist you!"
        
    # Check for ambiguous / incomplete queries
    if len(q_stripped.split()) == 1 and q_stripped.lower() in {'why', 'how', 'what', 'it', 'more', 'tell', 'yes', 'no'}:
        return f"Could you please specify your question in a bit more detail? For example: *'What is normalization in DBMS?'* or *'What is binary search?'*"

    # Math optimization (instant exact computation)
    math_res = evaluate_simple_math(q_stripped)
    if math_res:
        return math_res

    clean_key = (api_key or "").strip().strip('"').strip("'")
    
    # 1. Primary Engine: Google Gemini API (Direct REST + SDK fallback)
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
