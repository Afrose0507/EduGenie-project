import google.generativeai as genai
import urllib.request
import urllib.parse
import json
import re

MODELS = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]
STOPWORDS = {'what', 'is', 'a', 'an', 'the', 'of', 'in', 'on', 'at', 'to', 'for', 'explain', 'tell', 'me', 'about', 'define', 'describe', 'how', 'does', 'why', 'are', 'modes', 'types', 'features', 'advantages', 'disadvantages', 'components', 'layers'}

def smart_fetch_knowledge(query: str):
    words = [w for w in re.findall(r'\b[a-zA-Z0-9_-]+\b', query.lower()) if w not in STOPWORDS and len(w) > 2]
    candidates = [query]
    if words:
        candidates.append(' '.join(words))
        for w in words:
            if w not in candidates:
                candidates.append(w)
                
    for c in candidates:
        url = 'https://en.wikipedia.org/w/api.php?action=opensearch&search=' + urllib.parse.quote(c) + '&limit=3&namespace=0&format=json'
        req = urllib.request.Request(url, headers={'User-Agent': 'EduGenie/1.0 (educational app)'})
        try:
            with urllib.request.urlopen(req, timeout=4) as res:
                data = json.loads(res.read().decode('utf-8'))
                if data[1]:
                    title = data[1][0]
                    s_url = 'https://en.wikipedia.org/api/rest_v1/page/summary/' + urllib.parse.quote(title)
                    s_req = urllib.request.Request(s_url, headers={'User-Agent': 'EduGenie/1.0'})
                    with urllib.request.urlopen(s_req, timeout=4) as sres:
                        sdata = json.loads(sres.read().decode('utf-8'))
                        if sdata.get('extract') and sdata.get('type') != 'disambiguation':
                            return sdata.get('title'), sdata.get('extract')
        except Exception:
            continue
    return query, None

def get_answer(question: str, api_key: str) -> str:
    clean_key = (api_key or "").strip().strip('"').strip("'")
    
    prompt = f"""You are EduGenie, an expert, friendly AI learning assistant (like ChatGPT, Gemini, and Claude).
Answer this question accurately, thoroughly, and clearly: "{question}".

Adopt a friendly, encouraging human tutor tone.
Start with: "Hello! I am **EduGenie**, your learning assistant. I'm happy to help you understand this!"
Use clear markdown headings (###), horizontal dividers (---), bullet points with bold keywords, simple real-life analogies, and practical examples (including code blocks if relevant).
End with an encouraging question asking if they would like to practice or learn more."""

    # 1. Primary Engine: Live Google Gemini Generative AI
    if clean_key:
        try:
            genai.configure(api_key=clean_key)
            for model_name in MODELS:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    if response and response.text:
                        return response.text
                except Exception as err:
                    print(f"Gemini {model_name} error: {err}")
                    continue
        except Exception as err:
            print(f"Genai config error: {err}")

    # 2. Specific Academic Answers for Top Viva / Exam Topics
    q_lower = question.lower()
    if "hadoop" in q_lower and ("mode" in q_lower or "modes" in q_lower):
        return """Hello! I am **EduGenie**, your learning assistant. I'm happy to help you understand the **Modes of Hadoop**!

---

### What are the Modes of Hadoop?

Apache Hadoop operates in **three distinct execution modes** depending on how the cluster and background daemons (NameNode, DataNode, ResourceManager, NodeManager) are configured:

---

### 1. Standalone (Local) Mode
- **Configuration:** Default out-of-the-box mode with no distributed configuration in `core-site.xml`.
- **Execution:** Runs as a single Java Virtual Machine (JVM) process on a single machine.
- **Daemons:** No Hadoop daemons are running.
- **File System:** Uses the standard local file system instead of HDFS.
- **Best For:** Learning, developing, testing, and debugging MapReduce programs.

---

### 2. Pseudo-Distributed Mode
- **Configuration:** Configured to run on a single machine, but simulates a distributed environment.
- **Execution:** Each Hadoop daemon (NameNode, DataNode, Secondary NameNode, ResourceManager, NodeManager) runs in its own separate JVM.
- **File System:** Uses actual HDFS (Hadoop Distributed File System) on local storage.
- **Best For:** Verifying cluster configurations and proof-of-concept testing.

---

### 3. Fully-Distributed Mode (Cluster Mode)
- **Configuration:** Configured across multiple physical or cloud servers.
- **Execution:** Separate Master nodes (NameNode, ResourceManager) manage multiple Worker / Data nodes (DataNodes, NodeManagers).
- **File System:** Distributed fault-tolerant storage spanning hundreds or thousands of nodes with automatic block replication (default replication factor = 3).
- **Best For:** Enterprise production environments processing Petabytes of Big Data at scale.

***

Would you like to explore how HDFS replicates data across nodes, or try a 10-question quiz on Big Data?"""

    elif "python" in q_lower:
        return """Hello! I am **EduGenie**, your learning assistant. I'm happy to help you understand Python!

---

### What is Python?

**Python** is a popular computer programming language. Just like humans use languages like English or Spanish to talk to each other, programmers use Python to "talk" to computers and tell them what to do.

It was created in 1991 by a programmer named Guido van Rossum, and he actually named it after a funny British comedy show called *Monty Python's Flying Circus*—not the snake!

---

### Why is Python so great for students?

1. **It looks like English:** Unlike other languages that use lots of confusing symbols and brackets, Python reads very much like plain English. This makes it super easy to learn.
2. **It is super powerful:** Even though it is simple to read, Python is used by top companies like Google, Netflix, and NASA to build websites, analyze data, and build Artificial Intelligence (AI).
3. **Huge Community:** Millions of programmers share free code libraries (like NumPy, Pandas, and FastAPI), so you rarely have to start from scratch!

---

### A Simple Example

```python
print("Hello, World!")
```

**What this does:**
The word `print` simply tells the computer, *"Show this message on the screen."* When you run this code, the computer displays:
> Hello, World!

***

Would you like to try writing your very own Python code today? Just let me know!"""

    elif "dbms" in q_lower or "database" in q_lower:
        return """Hello! I am **EduGenie**, your learning assistant. I'm happy to help you understand DBMS!

---

### What is a DBMS?

**DBMS** stands for **Database Management System**. Think of it as a super-organized digital filing cabinet with a smart librarian managing it 24/7!

Instead of keeping messy papers or plain text files, a DBMS stores data neatly in tables (rows and columns) so you can find anything in milliseconds.

---

### Why do we need a DBMS?

1. **No Lost or Duplicate Data:** Eliminates accidental copies and inconsistencies.
2. **Super Fast Search:** You can query millions of records in a fraction of a second using SQL.
3. **Safety & Security:** Only authorized users can see private data, and data is protected even if the power cuts out!
4. **Multi-User Access:** Thousands of people can use apps like Instagram or Amazon at the exact same time without crashing the database.

---

### Popular Examples You Use Everyday

- **MySQL & PostgreSQL:** Powers websites, apps, and online shopping carts.
- **SQLite:** Built directly inside your smartphone to store your text messages and contacts!
- **MongoDB:** Stores flexible modern data like posts and comments.

***

Would you like to see how we write a simple SQL command to fetch data? Just let me know!"""

    # 3. Dynamic Real Topic Knowledge for ANY Other Topic
    title, extract = smart_fetch_knowledge(question)
    if extract:
        sentences = [s.strip() for s in extract.replace("\n", " ").split(".") if len(s.strip()) > 10]
        points = "\n".join([f"{i+1}. **Key Aspect:** {s}." for i, s in enumerate(sentences[:4])])
        return f"""Hello! I am **EduGenie**, your learning assistant. I'm happy to help you understand **{title}**!

---

### What is {title}?

{extract}

---

### Key Points to Remember

{points}

---

### Why is this important for students?

Understanding **{title}** builds conceptual clarity, connecting academic textbook theories with modern real-world systems, industry workflows, and exam questions.

***

Would you like to generate a 10-question quiz on **{title}**, or explore related topics? Just let me know!"""

    # 4. Clean fallback with actionable key setup reminder
    clean_subject = " ".join([w for w in re.findall(r'\b[a-zA-Z0-9_-]+\b', question) if w.lower() not in STOPWORDS]) or question
    return f"""Hello! I am **EduGenie**, your learning assistant. I'm happy to help you explore **{clean_subject}**!

---

### Overview of {clean_subject}

**{clean_subject}** is an essential subject in academic study. Breaking it down step by step:

1. **Core Concept:** It provides a structured methodology and set of principles to solve problems in this domain.
2. **Real-World Application:** Professionals, engineers, and researchers use this knowledge daily to build practical systems.
3. **Study Strategy:** Focus on mastering the key definitions, working through practice problems, and connecting theory with examples.

***

💡 *Tip:* To unlock unlimited live AI answers for every random topic across the globe, ensure your `GEMINI_API_KEY` is added under Render Environment Variables!"""
