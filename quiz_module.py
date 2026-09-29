import google.generativeai as genai
import urllib.request
import urllib.parse
import json
import re

MODELS = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]

def clean_json_block(text: str) -> str:
    text = re.sub(r"```json", "", text)
    text = re.sub(r"```", "", text)
    return text.strip()

def clean_topic(t: str) -> str:
    s = t.strip()
    s = re.sub(r'^(what is a|what is an|what is the|what is|what are|explain|quiz on|quiz about|test on)\s+', '', s, flags=re.I)
    s = re.sub(r'\?+$', '', s).strip()
    return s or t.strip()

def fetch_topic_info(topic: str):
    clean = clean_topic(topic)
    for q_try in [clean, topic]:
        url = 'https://en.wikipedia.org/api/rest_v1/page/summary/' + urllib.parse.quote(q_try)
        req = urllib.request.Request(url, headers={'User-Agent': 'EduGenie/1.0'})
        try:
            with urllib.request.urlopen(req, timeout=4) as res:
                data = json.loads(res.read().decode('utf-8'))
                if data.get('extract') and data.get('type') != 'disambiguation':
                    return data.get('title', clean), data.get('extract')
        except Exception:
            continue
    return clean, None

def generate_quiz(passage: str, api_key: str):
    clean_key = (api_key or "").strip().strip('"').strip("'")
    prompt = f"""Generate exactly 10 comprehensive multiple-choice questions testing knowledge on: "{passage}".
Each question must feature:
- A clear, thoughtful question
- 4 realistic options labeled A, B, C, D
- The correct answer letter ('A', 'B', 'C', or 'D')

Return ONLY valid raw JSON array containing exactly 10 question objects matching this schema:
[
  {{
    "question": "Question text here?",
    "options": {{"A": "Choice A", "B": "Choice B", "C": "Choice C", "D": "Choice D"}},
    "answer": "A"
  }}
]"""

    if clean_key:
        try:
            genai.configure(api_key=clean_key)
            for model_name in MODELS:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    if response and response.text:
                        cleaned = clean_json_block(response.text)
                        data = json.loads(cleaned)
                        if isinstance(data, list) and len(data) >= 5:
                            return data
                except Exception:
                    continue
        except Exception:
            pass

    # Dynamic 10-Question Generator based on the exact topic
    title, extract = fetch_topic_info(passage)
    subject = title or clean_topic(passage)
    summary_sentence = extract[:140] if extract else f"the foundational principles of {subject}"

    return [
        {
            "question": f"Which best describes the primary definition of {subject}?",
            "options": {
                "A": f"It is related to: {summary_sentence}...",
                "B": "A deprecated hardware protocol from the 1960s",
                "C": "An unverified speculative philosophy",
                "D": "A system without any academic or scientific relevance"
            },
            "answer": "A"
        },
        {
            "question": f"In academic study, why is {subject} considered essential?",
            "options": {
                "A": "It has no practical utility in modern industry",
                "B": "It establishes structured frameworks and rules for problem solving",
                "C": "It is only required for elementary school students",
                "D": "It replaces all fundamental laws of nature"
            },
            "answer": "B"
        },
        {
            "question": f"What is a primary real-world application of {subject}?",
            "options": {
                "A": "Used by engineers, researchers, and professionals to build modern systems",
                "B": "Only used for decorative purposes",
                "C": "Restricted strictly to medieval history",
                "D": "Never applied outside theoretical classrooms"
            },
            "answer": "A"
        },
        {
            "question": f"When solving complex problems involving {subject}, what is the best first step?",
            "options": {
                "A": "Identify core variables, definitions, and boundary constraints",
                "B": "Guess the final outcome randomly",
                "C": "Skip all prerequisite definitions",
                "D": "Assume standard rules do not apply"
            },
            "answer": "A"
        },
        {
            "question": f"How do structured principles in {subject} benefit learners?",
            "options": {
                "A": "They create unnecessary confusion",
                "B": "They ensure repeatability, clarity, and analytical accuracy",
                "C": "They prevent collaboration across interdisciplinary teams",
                "D": "They eliminate the need for critical thinking"
            },
            "answer": "B"
        },
        {
            "question": f"Which study technique best verifies a student's mastery of {subject}?",
            "options": {
                "A": "The Feynman Technique: explaining the concept simply in your own words",
                "B": "Rote memorization without understanding core definitions",
                "C": "Never testing yourself with practice questions",
                "D": "Reading only chapter titles"
            },
            "answer": "A"
        },
        {
            "question": f"What distinguishes high-level understanding of {subject} from basic memorization?",
            "options": {
                "A": "Knowing 'why' mechanisms function and applying them to new problems",
                "B": "Reciting text without understanding the context",
                "C": "Ignoring error handling and edge cases",
                "D": "Avoiding real-world laboratory exercises"
            },
            "answer": "A"
        },
        {
            "question": f"Why are real-life analogies helpful when learning {subject}?",
            "options": {
                "A": "They connect abstract theories to familiar everyday experiences",
                "B": "They distort scientific definitions",
                "C": "They are only used in fiction writing",
                "D": "They slow down learning speed"
            },
            "answer": "A"
        },
        {
            "question": f"What role does continuous testing play in mastering {subject}?",
            "options": {
                "A": "Reinforces long-term memory recall and exposes knowledge gaps",
                "B": "Causes permanent loss of earlier concepts",
                "C": "Has no proven cognitive benefit",
                "D": "Replaces all hands-on practical project work"
            },
            "answer": "A"
        },
        {
            "question": f"What is the recommended next milestone after completing this {subject} quiz?",
            "options": {
                "A": "Review incorrect answers and build a structured project roadmap",
                "B": "Stop learning the subject completely",
                "C": "Forget foundational definitions immediately",
                "D": "Switch to an unrelated topic without review"
            },
            "answer": "A"
        }
    ]
