import gemini_client
import json
import re

SYSTEM_INSTRUCTION = """You are EduGenie, a universal AI learning assistant dedicated to helping students of ALL ages, grade levels, academic departments, and educational backgrounds worldwide.

UNIVERSAL OPERATIONAL PRINCIPLES:
1. THE STUDENT'S QUESTION IS THE SOLE SOURCE OF TRUTH:
   - Answer the EXACT question asked directly, accurately, and factually.
   - Do NOT change the subject, pivot, or drift to coincidental keyword matches or unrelated entities.

2. DYNAMIC ADAPTATION OF RESPONSE LENGTH & DEPTH:
   - Automatically adapt answer length and style to the student's question:
     * FOR SIMPLE / CONCISE QUESTIONS (e.g. "What is AI?", "What is Python?", "What is DNA?", "What is a database?", or single-concept questions):
       Do NOT automatically generate a long textbook-style answer.
       Strictly follow this 3-part structure:
       1. Clear definition (1–2 direct sentences answering what it is immediately)
       2. 2–4 important points or examples
       3. One simple explanation or real-world example if useful
       Keep simple questions concise, crisp, and direct. Avoid unnecessary information.
     * FOR DETAILED / MULTI-PART QUESTIONS (e.g. questions asking "explain in detail", "explain everything", "give a detailed explanation", "explain with examples", or containing multiple parts/sub-questions):
       Provide a comprehensive, well-structured answer covering every specific part requested with clear headings, bullet points, and domain-appropriate examples.
   - Automatically detect subject (Computer Science, Engineering, Medicine, Biology, Physics, Chemistry, Math, Commerce, Economics, Arts, Law, etc.) and student level.

3. RESPONSE PRIORITY:
   - Priority 1: Answer the exact question first with factual clarity.
   - Priority 2: Structured formatting (bullet points, clear headings, comparison tables when contrasting concepts).
   - Priority 3: Concrete real-world examples or illustrations appropriate to the discipline.
   - Priority 4: Avoid unnecessary information when the question is simple. Never remove important factual information when requested.

4. STRICT PROHIBITION ON GENERIC FILLER:
   - NEVER use generic placeholder phrases such as "This concept is a fundamental topic in its academic discipline", "Review related textbook chapters", or "Prioritize understanding theoretical foundations" in place of the real answer.
   - Always deliver factual, domain-specific knowledge immediately in the first paragraph.
   - Never introduce unrelated celebrities, political figures, or unprompted facilities.

5. SPELLING & LANGUAGE TOLERANCE:
   - Intelligently understand typos and misspelled terms (e.g., 'photosyntehsis', 'pythagras', 'normalisation') and answer the intended question directly.

6. STATELESSNESS:
   - Treat each question as completely fresh and independent. Do not let previous topics contaminate the response.

7. TONE:
   - Encouraging, respectful, educational, objective, and clear for learners of all ages."""

def classify_question_depth(question: str) -> str:
    """
    Classifies question as 'simple' or 'detailed'.
    Adapts answer length and structure automatically.
    """
    q_lower = question.lower().strip()
    words = re.findall(r'\b\w+\b', q_lower)
    word_count = len(words)

    # 1. Explicit triggers requesting depth or examples:
    detail_phrases = [
        "in detail", "detailed", "detail", "explain everything", "explain thoroughly",
        "thoroughly", "deep dive", "step by step", "step-by-step", "comprehensive",
        "in-depth", "elaborate", "with examples", "with an example", "with a simple example",
        "with simple example", "give examples", "give an example", "code example",
        "all types", "all functions", "all components", "all phases", "list all",
        "advantages and disadvantages", "pros and cons", "differences and similarities",
        "compare and contrast"
    ]
    for phrase in detail_phrases:
        if phrase in q_lower:
            return "detailed"

    # 2. Multi-part indicators:
    if question.count('?') > 1:
        return "detailed"

    multi_part_regexes = [
        r'\b(?:difference|differences)\s+between\b',
        r'\b(?:1nf|2nf|3nf|bcnf)\b',
        r'\b(?:and|also|as well as)\s+(?:what|how|why|explain|describe|list|give)\b',
        r'\b(?:main|core|key)\s+(?:functions|components|types|stages|phases|principles|features|advantages)\b',
        r'\b(?:types|kinds|classes|categories|levels)\s+of\b',
        r'\b(?:how\s+does\s+it\s+work|working\s+principle|architecture)\b',
        r'\b(?:how\s+to|steps\s+to|procedure|process\s+of)\b'
    ]
    for pattern in multi_part_regexes:
        if re.search(pattern, q_lower):
            return "detailed"

    # 3. If long query (> 15 words), likely contains multiple requirements or context
    if word_count > 15:
        return "detailed"

    # 4. Short, single-concept definitional question
    return "simple"

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
    """Universal relevance check ensuring the answer addresses the student's question without topic drift."""
    if not answer or not answer.strip():
        return False
    
    q_clean = question.lower().strip()
    a_clean = answer.lower().strip()
    
    # Block known topic hijacking / unrelated contamination
    if ('cybersecurity' in q_clean or 'data' in q_clean) and 'utah data center' in a_clean and 'utah' not in q_clean:
        return False
    if 'trump' in a_clean and 'trump' not in q_clean:
        return False
        
    # Math question validation
    if re.search(r'\d+\s*[\+\-\*\/×÷x]\s*\d+', q_clean):
        if not any(c.isdigit() for c in a_clean):
            return False
            
    # Reject generic boilerplate answers
    if "this concept is a fundamental topic in its academic discipline" in a_clean:
        return False
            
    # Extract significant subject words from question (ignoring stop words)
    stop_words = {
        'what', 'when', 'where', 'which', 'who', 'whom', 'whose', 'why', 'how', 'does', 
        'explain', 'tell', 'about', 'define', 'give', 'detail', 'detailed', 'mean', 'meaning',
        'main', 'functions', 'function', 'and', 'are', 'its', 'difference', 'between', 'with', 
        'simple', 'example', 'like', 'for', 'student', 'grade', 'level', 'please',
        'is', 'it', 'in', 'on', 'at', 'to', 'of', 'by', 'as', 'an', 'or', 'if', 'do', 
        'so', 'my', 'me', 'we', 'he', 'no', 'up', 'the', 'a'
    }
    keywords = [w for w in re.findall(r'[a-zA-Z0-9]+', q_clean) if w not in stop_words and len(w) >= 2]
    
    if keywords:
        found = any(k in a_clean for k in keywords)
        return found
        
    return True

def call_gemini(prompt: str, api_key: str):
    """Invokes Google Gemini with universal student system instruction."""
    return gemini_client.generate_text(prompt, api_key, system_instruction=SYSTEM_INSTRUCTION)

def fallback_answer(question: str) -> str:
    """Fallback handler: answers basic math instantly, or provides clean student notice if AI is unavailable."""
    # 1. Simple Math evaluation
    math_ans = evaluate_simple_math(question)
    if math_ans:
        return math_ans

    # 2. Clean student-friendly notice (No technical API details, no generic fake answers)
    return "EduGenie is temporarily unable to generate an AI answer. Please try again in a moment."

def get_answer(question: str, api_key: str) -> str:
    """Main answer generator enforcing: Understand Question -> Classify Depth -> Adapt Length -> Generate -> Check Relevance."""
    q_stripped = (question or "").strip()
    if not q_stripped:
        return "Please enter an educational question so EduGenie can assist you!"
        
    # Check for ambiguous / incomplete queries
    if len(q_stripped.split()) == 1 and q_stripped.lower() in {'why', 'how', 'what', 'it', 'more', 'tell', 'yes', 'no'}:
        return "Could you please specify your question in a bit more detail? For example: *'What is photosynthesis?'* or *'What is double-entry bookkeeping?'*"

    # Math optimization (instant exact computation)
    math_res = evaluate_simple_math(q_stripped)
    if math_res:
        return math_res

    clean_key = (api_key or "").strip().strip('"').strip("'")
    
    # 1. Primary Engine: Google Gemini API (Direct REST + SDK fallback)
    if clean_key:
        depth = classify_question_depth(q_stripped)
        
        if depth == "simple":
            prompt = (
                f"The student asked the following simple educational question:\n"
                f"\"{q_stripped}\"\n\n"
                f"Please answer concisely using STRICTLY this structure:\n"
                f"1. **Definition**: Clear, direct definition (1–2 sentences) answering the exact question immediately.\n"
                f"2. **Key Points**: 2 to 4 important bullet points or examples.\n"
                f"3. **Simple Example**: One simple, relatable explanation or real-world example (1–2 sentences).\n\n"
                f"CRITICAL RULES:\n"
                f"- Answer the exact question first.\n"
                f"- Keep the answer concise, direct, and student-friendly.\n"
                f"- Do NOT generate a long textbook-style essay or add unnecessary information."
            )
        else:
            prompt = (
                f"The student asked the following educational question:\n"
                f"\"{q_stripped}\"\n\n"
                f"Please provide a well-structured, detailed answer:\n"
                f"- Answer the exact question first with a clear definition/overview.\n"
                f"- Address every specific part, concept, stage, or example requested by the student using clear headings and bullet points.\n"
                f"- Include concrete, domain-appropriate examples or comparisons.\n"
                f"- A short student-friendly summary or key takeaway.\n"
                f"- Keep all information directly factual and relevant to the question asked without generic filler."
            )

        answer = call_gemini(prompt, clean_key)
        
        # 2. Check Relevance of the generated answer
        if answer and is_answer_relevant(q_stripped, answer):
            return answer
            
        # 3. If the answer was irrelevant, REGENERATE with an intensified grounding prompt
        if answer:
            if depth == "simple":
                refocus_prompt = (
                    f"CRITICAL RE-GENERATION: The student asked: \"{q_stripped}\".\n"
                    f"Answer ONLY the exact question asked in concise format:\n"
                    f"1. Direct definition (1-2 sentences)\n"
                    f"2. 2-4 key bullet points\n"
                    f"3. One simple example\n"
                    f"No fluff, no generic filler, no unrelated topics."
                )
            else:
                refocus_prompt = (
                    f"CRITICAL RE-GENERATION: The student asked: \"{q_stripped}\".\n"
                    f"Directly answer what the student asked first with factual definitions and structured explanations.\n"
                    f"Address all requested parts. Do NOT provide generic filler, and do NOT drift off-topic."
                )
            retry_answer = call_gemini(refocus_prompt, clean_key)
            if retry_answer and is_answer_relevant(q_stripped, retry_answer):
                return retry_answer

    # 4. Clean Student Notification if AI is unreachable
    return fallback_answer(q_stripped)
