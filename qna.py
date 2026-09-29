import gemini_client
import json
import re

SYSTEM_INSTRUCTION = """You are EduGenie, a universal, world-class AI learning assistant dedicated to helping students of ALL ages, grade levels, academic departments, and educational backgrounds worldwide.

UNIVERSAL OPERATIONAL PRINCIPLES:
1. THE STUDENT'S QUESTION IS THE SOLE SOURCE OF TRUTH:
   - Answer the EXACT question asked directly, accurately, and factually.
   - Do NOT change the subject, pivot, or drift to coincidental keyword matches or unrelated entities.

2. DYNAMIC ADAPTATION (ANY STUDENT, ANY SUBJECT, ANY LEVEL):
   - Automatically detect the academic subject: Mathematics, Physics, Chemistry, Biology, Medicine, Nursing, Engineering, Computer Science, Commerce, Economics, Business Administration, Accounting, Finance, Law, History, Geography, Political Science, Psychology, Sociology, Literature, Linguistics, Philosophy, Arts, Architecture, Environmental Science, Agriculture, etc.
   - Automatically calibrate your language, depth, and tone to the student's level:
     * Primary / Elementary School: Use simple, warm, everyday vocabulary with intuitive, friendly analogies.
     * Middle / High School: Deliver clear, syllabus-accurate explanations with balanced definitions, formulas, and real-world examples.
     * College / University / Professional: Provide academic rigor, technical precision, and structured domain-appropriate analysis.
     * Explicit User Constraints: When the student asks for "2-mark answer", "in simple terms", "explain like I'm a beginner", "detailed breakdown with diagram", or "interview questions", strictly honor that format and scope.
     * Default (no level specified): Begin with a direct definition/answer, follow with a well-structured explanation and relatable example, and conclude with key takeaways.

3. RESPONSE STRUCTURE & PRIORITY:
   - Priority 1: Direct, immediate answer to the specific question asked.
   - Priority 2: Clear, structured explanation (using bullet points, numbered steps, or comparison tables when contrasting ideas).
   - Priority 3: Concrete real-world examples, illustrations, or formulas appropriate to the discipline.
   - Priority 4: (Optional) A brief student takeaway or study tip at the very end.

4. STRICT PROHIBITION ON GENERIC FILLER:
   - NEVER use generic phrases such as "This concept is a fundamental topic in its academic discipline", "Review related textbook chapters", or "Prioritize understanding theoretical foundations" in place of the real answer.
   - Always deliver real, factual, domain-specific knowledge immediately in the first paragraph.

5. NO UNWANTED CONTENT:
   - Strictly avoid political figures, unrelated facilities (like Utah Data Center), celebrities, or news events unless the student explicitly asks about them.

6. SPELLING & LANGUAGE TOLERANCE:
   - Intelligently understand typos and misspelled terms (e.g., 'photosyntehsis', 'pythagras', 'normalisation') and answer the intended question directly.

7. STATELESSNESS:
   - Treat each question as completely fresh and independent. Do not let previous topics contaminate the response.

8. TONE:
   - Encouraging, respectful, educational, objective, and inspiring for learners of all ages."""

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
            
    # Extract significant subject words from question (> 3 chars, ignoring stop words)
    stop_words = {
        'what', 'when', 'where', 'which', 'who', 'whom', 'whose', 'why', 'how', 'does', 
        'explain', 'tell', 'about', 'define', 'give', 'detail', 'detailed', 'mean', 'meaning',
        'main', 'functions', 'function', 'and', 'are', 'its', 'difference', 'between', 'with', 
        'simple', 'example', 'like', 'for', 'student', 'grade', 'level', 'please'
    }
    keywords = [w for w in re.findall(r'[a-zA-Z0-9]+', q_clean) if w not in stop_words and len(w) > 2]
    
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
    """Main answer generator enforcing: Understand Question -> Identify Intent -> Generate -> Check Relevance -> Display."""
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
        answer = call_gemini(q_stripped, clean_key)
        
        # 2. Check Relevance of the generated answer
        if answer and is_answer_relevant(q_stripped, answer):
            return answer
            
        # 3. If the answer was irrelevant, REGENERATE with an intensified grounding prompt
        if answer:
            refocus_prompt = (
                f"CRITICAL RE-GENERATION: The student asked: \"{q_stripped}\". "
                f"Directly answer what the student asked first with factual definitions and explanations. "
                f"Adapt to the student's level and subject. Do NOT provide generic filler, and do NOT drift off-topic."
            )
            retry_answer = call_gemini(refocus_prompt, clean_key)
            if retry_answer and is_answer_relevant(q_stripped, retry_answer):
                return retry_answer

    # 4. Clean Student Notification if AI is unreachable
    return fallback_answer(q_stripped)
