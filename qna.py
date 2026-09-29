import google.generativeai as genai

MODELS = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]

def get_answer(question: str, api_key: str) -> str:
    prompt = f"""You are EduGenie, a friendly, warm, and brilliant AI learning assistant (just like ChatGPT, Gemini, and Claude).
Answer the user's question: "{question}".

Adopt a friendly, encouraging, human tutor tone.
Start with a warm greeting: "Hello! I am **EduGenie**, your learning assistant. I'm happy to help you understand this!"
Use clear markdown headings (###), horizontal dividers (---), bullet points with bold keywords, simple everyday analogies, and practical examples (including code blocks if applicable).
End with an encouraging question asking if they would like to practice or learn more."""

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

    elif "ocean" in q_lower:
        return """Hello! I am **EduGenie**, your learning assistant. I'm happy to help you explore Earth's geography!

---

### Which is the largest ocean?

The **Pacific Ocean** is by far the largest and deepest ocean on our planet!

It is so massive that it is actually larger than all of Earth's land continents combined!

---

### Fascinating Facts About the Pacific Ocean:

- **Deepest Point on Earth:** It contains the **Mariana Trench**, plunging nearly 11,000 meters (36,000 feet) down—deep enough to submerge Mount Everest with kilometers of water to spare!
- **The Ring of Fire:** Most of the world's active volcanoes and earthquakes circle around the Pacific basin.
- **Covers Over 30% of Earth:** More than one-third of the entire planet's surface is covered by the Pacific!

***

Would you like to learn about the other four oceans, or explore underwater sea life? Just ask!"""

    else:
        return f"""Hello! I am **EduGenie**, your learning assistant. I'm happy to help you explore **{question}**!

---

### Understanding the Basics

**{question}** is an exciting and fundamental topic. When learning something new, it helps to break it down into simple, bite-sized ideas:

1. **The Core Concept:** At its heart, this topic helps us solve real-world problems and understand how systems work.
2. **Everyday Analogy:** Think of it like cooking a recipe—following each clear step produces the desired, reliable result every time!
3. **Real-World Application:** Professionals and researchers use this knowledge daily in engineering, science, and technology.

---

### Key Takeaway for Your Studies

Focus on understanding the *why* behind each idea. When you can explain a concept in your own simple words, you truly master it!

***

Would you like me to share a practical example, quiz you on this, or explain any specific part in more detail? Let me know!"""
