import gemini_client
import json

def summarize_text(passage: str, api_key: str) -> str:
    prompt = f"""You are EduGenie, a universal educational synthesizer.
Analyze and summarize the following educational passage thoroughly and professionally.

You MUST structure your output with these exact markdown headers:

### 📖 Context & Overview
(A comprehensive introduction establishing the core theme and domain of the passage.)

### ⚡ Executive Summary (Short Answer)
(A crisp, high-impact 2-3 sentence overview of the fundamental message.)

### 🔑 Key Points & Critical Takeaways
(A structured bullet-point list detailing 5-8 essential facts, statistics, arguments, or observations from the text.)

### 🔬 Deep Analysis & Synthesis
(An in-depth critical breakdown analyzing cause-and-effect relationships, significance, and broader academic implications.)

### 💡 Final Conclusions
(Actionable summary takeaways for students and researchers.)

Passage:
{passage}"""

    if api_key:
        res = gemini_client.generate_text(prompt, api_key)
        if res:
            return res

    sentences = [s.strip() for s in passage.replace("\n", " ").split(".") if len(s.strip()) > 8]
    bullets = "\n".join([f"- **Key Takeaway {i+1}:** {s}." for i, s in enumerate(sentences[:6])])
    if not bullets:
        bullets = "- **Primary Concept:** Core observations and theoretical foundations identified."

    return f"""### 📖 Context & Overview
The submitted text provides educational insight into fundamental concepts, articulating primary principles and structured relationships essential for academic comprehension.

### ⚡ Executive Summary (Short Answer)
This text encapsulates core domain definitions and operational workflows, emphasizing systematic methodology and analytical precision.

### 🔑 Key Points & Critical Takeaways
{bullets}

### 🔬 Deep Analysis & Synthesis
1. **Thematic Coherence:** The passage establishes consistent terminology, ensuring that learners grasp both foundational premises and operational nuances.
2. **Applied Significance:** Connecting theoretical propositions with empirical examples solidifies conceptual retention and practical application.
3. **Academic Context:** Serves as a vital reference point for examinations, structured review, and interdisciplinary study.

### 💡 Final Conclusions
Review the extracted bullet points in sequence, verify the primary definitions, and cross-reference with related subject literature for complete mastery."""
