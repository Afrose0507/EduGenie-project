import gemini_client
import re

SYSTEM_INSTRUCTION = """You are EduGenie, a universal AI learning assistant dedicated to explaining educational concepts clearly to students of ALL ages, grade levels, and academic departments worldwide.

UNIVERSAL OPERATIONAL PRINCIPLES:
1. THE STUDENT'S TOPIC IS THE SOLE SOURCE OF TRUTH:
   - Explain the concept requested with clarity, accuracy, and educational care.
2. DYNAMIC ADAPTATION (ANY FIELD, ANY LEVEL):
   - Automatically detect the subject: Sciences, Mathematics, Commerce, Law, Medicine, Humanities, Arts, Engineering, Social Sciences, etc.
   - Match the student's level (Primary school, high school, university, professional, or competitive exam preparation).
   - If the student asks for a specific style (e.g. "for a 6th grader", "at university level", "with simple analogy", "in 2 marks"), follow that instruction strictly.
3. RESPONSE STRUCTURE:
   - Core Definition / Intuition: Clear and immediate.
   - Conceptual Explanation / Core Mechanisms: Logically structured.
   - Relatable Everyday Analogy: Connecting abstract concepts to familiar experiences.
   - Real-World Application: How this concept is applied in practice or industry.
   - Short Summary: A memorable takeaway for revision and exams.
4. NEVER PRODUCE GENERIC FILLER:
   - Never say "This concept is a fundamental topic in its academic discipline" or "Prioritize understanding theoretical foundations".
   - Always deliver factual, domain-specific insights immediately.
5. STATELESSNESS: Treat every request independently without carryover from previous topics.
6. TONE: Encouraging, respectful, clear, and inspiring for all learners."""

def is_explanation_relevant(topic: str, explanation: str) -> bool:
    """Validates that the explanation strictly addresses the requested concept."""
    if not explanation or not explanation.strip():
        return False
    t_clean = topic.lower().strip()
    e_clean = explanation.lower().strip()
    
    # Flag known bad drift
    if 'trump' in e_clean and 'trump' not in t_clean:
        return False
    if "this concept is a fundamental topic in its academic discipline" in e_clean:
        return False
        
    stop_words = {
        'what', 'is', 'a', 'an', 'the', 'of', 'in', 'on', 'at', 'to', 'for', 'explain', 
        'tell', 'about', 'define', 'main', 'functions', 'difference', 'between', 'concept', 'meaning'
    }
    words = [w for w in re.findall(r'[a-zA-Z0-9]+', t_clean) if w not in stop_words and len(w) > 2]
    if words:
        return any(w in e_clean for w in words)
    return True

def call_gemini_explain(topic: str, api_key: str):
    prompt = f"Please explain the concept of '{topic}' in a clear, structured way, adapting to the student's field and requested depth."
    return gemini_client.generate_text(prompt, api_key, system_instruction=SYSTEM_INSTRUCTION)

def fallback_explanation(topic: str) -> str:
    return "EduGenie is temporarily unable to generate an AI explanation. Please try again in a moment."

def explain_concept(topic: str, api_key: str) -> str:
    t_stripped = (topic or "").strip()
    if not t_stripped:
        return "Please enter an educational concept for EduGenie to explain!"
        
    clean_key = (api_key or "").strip().strip('"').strip("'")
    
    # 1. Primary: Google Gemini API
    if clean_key:
        explanation = call_gemini_explain(t_stripped, clean_key)
        if explanation and is_explanation_relevant(t_stripped, explanation):
            return explanation
            
        # 2. Regeneration if off-topic
        if explanation:
            retry_prompt = f"CRITICAL RE-GENERATION: Explain ONLY the educational concept: '{t_stripped}'. Provide clear definitions, mechanisms, and analogies adapted to the student's level."
            retry_explanation = call_gemini_explain(retry_prompt, clean_key)
            if retry_explanation and is_explanation_relevant(t_stripped, retry_explanation):
                return retry_explanation
                
    # 3. Clean notice if AI is unavailable
    return fallback_explanation(t_stripped)
