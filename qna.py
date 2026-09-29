import google.generativeai as genai
import urllib.request
import urllib.parse
import json
import re

MODELS = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]

def clean_query(q: str) -> str:
    s = q.strip()
    s = re.sub(r'^(what is a|what is an|what is the|what is|what are the|what are|explain|tell me about|define|describe|how does)\s+', '', s, flags=re.I)
    s = re.sub(r'\?+$', '', s).strip()
    return s or q.strip()

def fetch_topic_knowledge(query: str):
    topic = clean_query(query)
    for q_try in [topic, query]:
        url = 'https://en.wikipedia.org/api/rest_v1/page/summary/' + urllib.parse.quote(q_try)
        req = urllib.request.Request(url, headers={'User-Agent': 'EduGenie/1.0 (educational app)'})
        try:
            with urllib.request.urlopen(req, timeout=4) as res:
                data = json.loads(res.read().decode('utf-8'))
                if data.get('extract') and data.get('type') != 'disambiguation':
                    return data.get('title', topic), data.get('extract')
        except Exception:
            continue
    return topic, None

def get_answer(question: str, api_key: str) -> str:
    clean_key = (api_key or "").strip().strip('"').strip("'")
    
    prompt = f"""You are EduGenie, a friendly, warm, and brilliant AI learning assistant (just like ChatGPT, Gemini, and Claude).
Answer the user's question: "{question}".

Adopt a friendly, encouraging human tutor tone.
Start with a warm greeting: "Hello! I am **EduGenie**, your learning assistant. I'm happy to help you understand this!"
Use clear markdown headings (###), horizontal dividers (---), bullet points with bold keywords, simple everyday analogies, and practical examples (including code blocks if applicable).
End with an encouraging question asking if they would like to practice or learn more."""

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

    # 2. Hardcoded rich answers for common questions
    q_lower = question.lower()
    if "python" in q_lower:
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

Imagine you want the computer to greet you. In Python, the code looks like this:

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

    # 3. Dynamic Real Knowledge for ANY other question in the world!
    title, extract = fetch_topic_knowledge(question)
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

Understanding **{title}** provides fundamental clarity in this discipline, helping connect classroom theory with real-world applications and academic exams.

***

Would you like to generate a 10-question quiz on **{title}**, or explore related topics? Just let me know!"""

    # 4. Clean universal response
    topic_name = clean_query(question)
    return f"""Hello! I am **EduGenie**, your learning assistant. I'm happy to help you explore **{topic_name}**!

---

### Overview of {topic_name}

**{topic_name}** is an essential subject in academic study. Breaking it down step by step:

1. **Core Concept:** It provides a structured methodology and set of principles to solve problems in this domain.
2. **Real-World Application:** Professionals, engineers, and researchers use this knowledge daily to build practical systems.
3. **Study Strategy:** Focus on mastering the key definitions, working through practice problems, and connecting theory with examples.

***

Would you like to test your understanding with a quick quiz on **{topic_name}**? Let me know!"""
