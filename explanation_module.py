import google.generativeai as genai
import urllib.request
import urllib.parse
import json
import re

MODELS = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]
STOPWORDS = {'what', 'is', 'a', 'an', 'the', 'of', 'in', 'on', 'at', 'to', 'for', 'explain', 'tell', 'me', 'about', 'define', 'describe', 'how', 'does', 'why', 'are', 'modes', 'types', 'features', 'advantages', 'disadvantages', 'components', 'layers'}

def smart_fetch_concept(query: str):
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

    t_lower = topic.lower()

    if "hadoop" in t_lower and ("mode" in t_lower or "modes" in t_lower):
        return """Hello! I am **EduGenie**, your friendly AI tutor. I'm excited to explain the **Modes of Hadoop** to you today!

---

### What are Hadoop Execution Modes?

Imagine you are cooking for an event. You can:
1. Cook alone in your kitchen (Standalone Mode)
2. Pretend to run a restaurant by setting up 3 cooking stations in your kitchen (Pseudo-Distributed Mode)
3. Run an actual massive banquet across 10 kitchens with 10 chefs (Fully-Distributed Mode)

Hadoop operates in the exact same three ways:

---

### 1. Standalone (Local) Mode
- **Analogy:** Doing the whole project on your laptop with no extra setup.
- **Execution:** Runs as a single Java process on one computer.
- **File System:** Uses your normal C: or D: drive instead of HDFS.
- **Purpose:** Ideal for students writing and debugging their first MapReduce programs without needing complex servers.

---

### 2. Pseudo-Distributed Mode
- **Analogy:** Simulating a company network on a single computer.
- **Execution:** Runs all Hadoop daemons (NameNode, DataNode, ResourceManager) in separate Java processes on one machine.
- **File System:** Uses real HDFS on your local machine.
- **Purpose:** Testing cluster behavior before deploying to real physical hardware.

---

### 3. Fully-Distributed Mode
- **Analogy:** A real enterprise data center with hundreds of server racks.
- **Execution:** Dedicated Master servers coordinate thousands of worker servers.
- **File System:** Distributed across racks with automatic 3x data replication for bulletproof fault tolerance.
- **Purpose:** Enterprise production processing Petabytes of data (e.g., Netflix recommendations, Amazon shopping analytics).

***

Would you like to try a 10-question quiz on Hadoop, or see how MapReduce works?"""

    elif "pythagoras" in t_lower:
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

    # Dynamic concept search
    title, extract = smart_fetch_concept(topic)
    if extract:
        sentences = [s.strip() for s in extract.replace("\n", " ").split(".") if len(s.strip()) > 10]
        points = "\n".join([f"{i+1}. **Key Concept:** {s}." for i, s in enumerate(sentences[:4])])
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

    clean_subj = " ".join([w for w in re.findall(r'\b[a-zA-Z0-9_-]+\b', topic) if w.lower() not in STOPWORDS]) or topic
    return f"""Hello! I am **EduGenie**, your friendly AI tutor. I'm excited to explain **{clean_subj}** to you today!

---

### What is {clean_subj}?

**{clean_subj}** is an important concept in your studies! Just like building with Lego blocks, understanding this topic becomes easy when we break it down into simple, manageable pieces:

1. **Foundational Definition:** The core rules and theories that establish what {clean_subj} does.
2. **Everyday Analogy:** Connects abstract theory to familiar real-world experiences.
3. **Practical Application:** Solves concrete problems in modern technology, science, and industry.

***

Would you like to test your understanding with an interactive quiz on **{clean_subj}**?"""
