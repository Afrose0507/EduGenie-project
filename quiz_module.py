import gemini_client
import json
import re

def clean_json_block(text: str) -> str:
    text = re.sub(r"^```json\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^```\s*", "", text, flags=re.MULTILINE)
    return text.strip()

def clean_topic(t: str) -> str:
    s = t.strip()
    s = re.sub(r'^(what is a|what is an|what is the|what is|what are|explain|quiz on|quiz about|test on)\s+', '', s, flags=re.I)
    s = re.sub(r'\?+$', '', s).strip()
    return s or t.strip()

def generate_quiz(passage: str, api_key: str):
    clean_key = (api_key or "").strip().strip('"').strip("'")
    clean_subj = clean_topic(passage)
    
    prompt = f"""You are EduGenie, an expert educational exam designer for all academic subjects.
Generate exactly 10 high-quality multiple-choice questions testing knowledge strictly on the subject: "{clean_subj}".

CRITICAL DIRECTIVES:
1. Every question must be directly and exclusively about "{clean_subj}".
2. Do not drift to unrelated subjects, people, or tangential events.
3. Provide 4 realistic options labeled A, B, C, D.
4. Mark the correct answer letter.

Return ONLY a valid JSON array matching this exact schema:
[
  {{
    "question": "Question text here?",
    "options": {{"A": "Choice A", "B": "Choice B", "C": "Choice C", "D": "Choice D"}},
    "answer": "A"
  }}
]"""

    if clean_key:
        res = gemini_client.generate_text(prompt, clean_key)
        if res:
            try:
                cleaned = clean_json_block(res)
                data = json.loads(cleaned)
                if isinstance(data, list) and len(data) >= 5:
                    return data
            except Exception as e:
                print(f"[Quiz Parse Error]: {e}")

    # Pure educational fallback strictly aligned to the topic
    return [
        {
            "question": f"Which best describes the primary definition of {clean_subj}?",
            "options": {
                "A": f"A foundational subject governing core principles and applications of {clean_subj}",
                "B": "A deprecated hardware protocol from the 1960s",
                "C": "An unverified speculative philosophy",
                "D": "A system without any academic or scientific relevance"
            },
            "answer": "A"
        },
        {
            "question": f"In academic study, why is {clean_subj} considered essential?",
            "options": {
                "A": "It has no practical utility in modern industry",
                "B": "It establishes structured frameworks and rules for problem solving",
                "C": "It is only required for elementary school students",
                "D": "It replaces all fundamental laws of nature"
            },
            "answer": "B"
        },
        {
            "question": f"What is a primary real-world application of {clean_subj}?",
            "options": {
                "A": f"Used by professionals to analyze, construct, and optimize {clean_subj} systems",
                "B": "Only used for decorative purposes",
                "C": "Restricted strictly to medieval history",
                "D": "Never applied outside theoretical classrooms"
            },
            "answer": "A"
        },
        {
            "question": f"When solving complex problems involving {clean_subj}, what is the best first step?",
            "options": {
                "A": "Identify core variables, definitions, and boundary constraints",
                "B": "Guess the final outcome randomly",
                "C": "Skip all prerequisite definitions",
                "D": "Assume standard rules do not apply"
            },
            "answer": "A"
        },
        {
            "question": f"How do structured principles in {clean_subj} benefit learners?",
            "options": {
                "A": "They create unnecessary confusion",
                "B": "They ensure repeatability, clarity, and analytical accuracy",
                "C": "They prevent collaboration across interdisciplinary teams",
                "D": "They eliminate the need for critical thinking"
            },
            "answer": "B"
        },
        {
            "question": f"Which study technique best verifies a student's mastery of {clean_subj}?",
            "options": {
                "A": "The Feynman Technique: explaining the concept simply in your own words",
                "B": "Rote memorization without understanding core definitions",
                "C": "Never testing yourself with practice questions",
                "D": "Reading only chapter titles"
            },
            "answer": "A"
        },
        {
            "question": f"What distinguishes high-level understanding of {clean_subj} from basic memorization?",
            "options": {
                "A": "Knowing 'why' mechanisms function and applying them to new problems",
                "B": "Reciting text without understanding the context",
                "C": "Ignoring error handling and edge cases",
                "D": "Avoiding real-world laboratory exercises"
            },
            "answer": "A"
        },
        {
            "question": f"Why are real-life analogies helpful when learning {clean_subj}?",
            "options": {
                "A": "They connect abstract theories to familiar everyday experiences",
                "B": "They distort scientific definitions",
                "C": "They are only used in fiction writing",
                "D": "They slow down learning speed"
            },
            "answer": "A"
        },
        {
            "question": f"What role does continuous testing play in mastering {clean_subj}?",
            "options": {
                "A": "Reinforces long-term memory recall and exposes knowledge gaps",
                "B": "Causes permanent loss of earlier concepts",
                "C": "Has no proven cognitive benefit",
                "D": "Replaces all hands-on practical project work"
            },
            "answer": "A"
        },
        {
            "question": f"What is the recommended next milestone after completing this {clean_subj} quiz?",
            "options": {
                "A": "Review incorrect answers and build a structured project roadmap",
                "B": "Stop learning the subject completely",
                "C": "Forget foundational definitions immediately",
                "D": "Switch to an unrelated topic without review"
            },
            "answer": "A"
        }
    ]
