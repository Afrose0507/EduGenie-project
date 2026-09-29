import google.generativeai as genai

MODELS = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]

def explain_concept(topic: str, api_key: str) -> str:
    prompt = f"""You are EduGenie, a friendly, human-like AI tutor (like ChatGPT, Gemini, Claude).
Explain the concept: "{topic}".

Adopt an engaging, conversational, friendly tone.
Start with: "Hello! I am **EduGenie**, your friendly AI tutor. I'm excited to explain **{topic}** to you today!"
Use clear markdown headers (###), horizontal lines (---), bullet points with bold keywords, simple real-life analogies, and clear step-by-step examples.
End with a friendly question asking if they would like to try a quiz or see another example."""

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

    elif "photosynthesis" in t_lower:
        return """Hello! I am **EduGenie**, your friendly AI tutor. I'm excited to explain **Photosynthesis** to you today!

---

### What is Photosynthesis?

Have you ever wondered how giant trees grow strong and green without ever eating food like humans do?

The secret is **Photosynthesis**! Green plants have the superpower to make their own food completely from scratch using pure sunlight, water, and air.

---

### The Simple Plant Recipe

$$\\text{Sunlight} + \\text{Water} + \\text{Carbon Dioxide} \\longrightarrow \\text{Glucose (Plant Food)} + \\text{Oxygen}$$

Here is how each plant part acts like a kitchen:
1. **The Solar Panels (Leaves):** Leaves contain a green substance called **chlorophyll** that traps sunlight energy.
2. **The Straws (Roots):** Roots soak up water and minerals from deep in the soil.
3. **The Tiny Noses (Stomata):** Microscopic pores under leaves breathe in carbon dioxide from the air.
4. **The Gift for Us (Oxygen):** As the plant makes sugary glucose to grow, it breathes out fresh **oxygen** into the atmosphere for humans and animals to breathe!

***

Isn't nature incredible? Would you like to learn how plants survive at night, or try a fun quiz on this?"""

    else:
        return f"""Hello! I am **EduGenie**, your friendly AI tutor. I'm excited to explain **{topic}** to you today!

---

### What is {topic}?

**{topic}** is a fascinating concept! Just like learning how to ride a bike or play an instrument, understanding this topic becomes super simple when we break it down into easy, relatable pieces.

---

### Why is this important?

1. **Everyday Problem Solving:** It helps us understand how things work in the real world.
2. **Logical Building Blocks:** Complex technologies all start from simple foundations like this.
3. **Fun to Apply:** Once you grasp the core idea, you can easily apply it to exams, coding, and science projects!

***

Would you like to see a fun real-world example of this in action? Just let me know!"""
