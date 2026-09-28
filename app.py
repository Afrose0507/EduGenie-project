import streamlit as st
import google.generativeai as genai
import time

st.set_page_config(
    page_title=EduGenie AI,
    page_icon=🧞,
    layout=wide,
    initial_sidebar_state=expanded
)

st.markdown("
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * { font-family: 'Inter', sans-serif; }

    .stApp {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
        color: #ffffff;
    }

    section[data-testid=stSidebar] {
        background: linear-gradient(180deg, #1a1a2e 0%, #0f0f1a 100%) !important;
        border-right: 1px solid rgba(99, 102, 241, 0.3);
    }

    section[data-testid=stSidebar] * { color: #e2e8f0 !important; }

    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(99, 102, 241, 0.5) !important;
        border-radius: 12px !important;
        color: white !important;
        padding: 12px 16px !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4) !important;
    }

    .stTabs [data-baseweb=tab-list] {
        background: rgba(255,255,255,0.05) !important;
        border-radius: 12px !important;
        padding: 4px !important;
        gap: 4px !important;
    }

    .stTabs [data-baseweb=tab] {
        background: transparent !important;
        color: #94a3b8 !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
    }

    .stTabs [aria-selected=true] {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
    }

    .stSelectbox > div > div {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(99, 102, 241, 0.5) !important;
        border-radius: 12px !important;
        color: white !important;
    }

    .stSlider > div > div > div > div {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    }

    div[data-testid=stChatMessage] {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 16px !important;
        padding: 16px !important;
        margin: 8px 0 !important;
        backdrop-filter: blur(10px) !important;
    }

    .stSuccess {
        background: rgba(16, 185, 129, 0.1) !important;
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
        border-radius: 12px !important;
        color: #10b981 !important;
    }

    .stWarning {
        background: rgba(245, 158, 11, 0.1) !important;
        border: 1px solid rgba(245, 158, 11, 0.3) !important;
        border-radius: 12px !important;
    }

    .stInfo {
        background: rgba(99, 102, 241, 0.1) !important;
        border: 1px solid rgba(99, 102, 241, 0.3) !important;
        border-radius: 12px !important;
    }

    .stError {
        background: rgba(239, 68, 68, 0.1) !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
        border-radius: 12px !important;
    }

    .hero-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1, #a78bfa, #38bdf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        animation: shimmer 3s infinite;
    }

    @keyframes shimmer {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .hero-subtitle {
        font-size: 1.1rem;
        color: #94a3b8;
        margin-bottom: 2rem;
        font-weight: 400;
    }

    .feature-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 16px;
        padding: 24px;
        margin: 8px 0;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }

    .feature-card:hover {
        border-color: rgba(99, 102, 241, 0.5);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.15);
    }

    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #6366f1;
    }

    .badge {
        display: inline-block;
        background: linear-gradient(135deg, rgba(99,102,241,0.2), rgba(139,92,246,0.2));
        border: 1px solid rgba(99,102,241,0.4);
        color: #a78bfa;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
    }

    .sidebar-logo {
        text-align: center;
        padding: 20px 0;
    }

    .glow-text {
        text-shadow: 0 0 20px rgba(99, 102, 241, 0.5);
    }

    .stChatInputContainer {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(99, 102, 241, 0.3) !important;
        border-radius: 16px !important;
    }

    .stSpinner > div {
        border-top-color: #6366f1 !important;
    }

    hr {
        border-color: rgba(255,255,255,0.1) !important;
    }

    .output-box {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 16px;
        padding: 24px;
        margin-top: 16px;
        line-height: 1.8;
    }

    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.4); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(99,102,241,0.7); }
</style>
", unsafe_allow_html=True)

# ── SIDEBAR ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("
    <div class=sidebar-logo>
        <div style=font-size:3rem;>🧞</div>
        <div style=font-size:1.5rem;font-weight:700;background:linear-gradient(135deg,#6366f1,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;>EduGenie</div>
        <div style=font-size:0.8rem;color:#64748b;margin-top:4px;>Powered by Google Gemini</div>
        <div style=margin-top:8px;><span class=badge>✨ AI Learning Assistant</span></div>
    </div>
    ", unsafe_allow_html=True)

    st.divider()

    api_key = st.text_input(🔑 Gemini API Key, type=password, placeholder=AIzaSy...)

    if api_key:
        genai.configure(api_key=api_key)
        st.success(✅ Connected to Gemini AI)
    else:
        st.warning(⚠️ Enter API key to begin)

    st.divider()
    st.markdown("
    <div style=color:#64748b;font-size:0.85rem;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;>Features</div>
    ", unsafe_allow_html=True)

    st.markdown("
    <div class=feature-card style=padding:12px 16px;margin:4px 0;>
        <div style=font-size:0.9rem;font-weight:600;>🤖 AI Tutor Chat</div>
        <div style=font-size:0.75rem;color:#64748b;margin-top:2px;>Ask anything, learn everything</div>
    </div>
    <div class=feature-card style=padding:12px 16px;margin:4px 0;>
        <div style=font-size:0.9rem;font-weight:600;>📝 Study Generator</div>
        <div style=font-size:0.75rem;color:#64748b;margin-top:2px;>Instant notes on any topic</div>
    </div>
    <div class=feature-card style=padding:12px 16px;margin:4px 0;>
        <div style=font-size:0.9rem;font-weight:600;>❓ Quiz Generator</div>
        <div style=font-size:0.75rem;color:#64748b;margin-top:2px;>Test your knowledge with AI</div>
    </div>
    ", unsafe_allow_html=True)

    st.divider()
    st.markdown('<div style=color:#475569;font-size:0.75rem;text-align:center;>Built with Google Gemini 3.8 🚀</div>', unsafe_allow_html=True)

# ── MAIN CONTENT ─────────────────────────────────────────────────────
if not api_key:
    st.markdown("
    <div style=text-align:center;padding:80px 20px;>
        <div style=font-size:4rem;margin-bottom:16px;>🧞</div>
        <div class=hero-title>Welcome to EduGenie</div>
        <div class=hero-subtitle>Your AI-powered learning assistant, built on Google Gemini</div>
        <div style=background:rgba(99,102,241,0.1);border:1px solid rgba(99,102,241,0.3);border-radius:16px;padding:16px 24px;display:inline-block;margin-top:16px;color:#a78bfa;font-size:0.95rem;>
            👈 Enter your Gemini API Key in the sidebar to get started
        </div>
    </div>
    ", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class=feature-card style=text-align:center;>
            <div style=font-size:2.5rem;>🤖</div>
            <div style=font-weight:600;margin-top:8px;>AI Tutor Chat</div>
            <div style=color:#64748b;font-size:0.85rem;margin-top:4px;>Get clear explanations on any subject instantly</div>
        </div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class=feature-card style=text-align:center;>
            <div style=font-size:2.5rem;>📝</div>
            <div style=font-weight:600;margin-top:8px;>Study Material</div>
            <div style=color:#64748b;font-size:0.85rem;margin-top:4px;>Generate comprehensive notes on any topic</div>
        </div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class=feature-card style=text-align:center;>
            <div style=font-size:2.5rem;>❓</div>
            <div style=font-weight:600;margin-top:8px;>Quiz Generator</div>
            <div style=color:#64748b;font-size:0.85rem;margin-top:4px;>Test yourself with AI-generated quizzes</div>
        </div>", unsafe_allow_html=True)
    st.stop()

model = genai.GenerativeModel(gemini-3.8-flash)

st.markdown('<div class=hero-title style=font-size:2rem;margin-bottom:4px;>🧞 EduGenie AI</div>', unsafe_allow_html=True)
st.markdown('<div class=hero-subtitle style=margin-bottom:16px;>Your intelligent learning companion — powered by Google Gemini</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([ 🤖 AI Tutor Chat ,  📝 Study Material ,  ❓ Quiz Generator ])

# ── TAB 1: CHAT ──────────────────────────────────────────────────────
with tab1:
    st.markdown("
    <div style=margin-bottom:24px;>
        <div style=font-size:1.5rem;font-weight:700;margin-bottom:4px;>🤖 AI Tutor Chat</div>
        <div style=color:#64748b;>Ask any question and get clear, simple explanations instantly</div>
    </div>
    ", unsafe_allow_html=True)

    if chat_history not in st.session_state:
        st.session_state.chat_history = []

    if not st.session_state.chat_history:
        st.markdown("
        <div style=text-align:center;padding:40px;color:#475569;>
            <div style=font-size:3rem;margin-bottom:12px;>💬</div>
            <div style=font-weight:600;font-size:1.1rem;color:#94a3b8;>Start a conversation</div>
            <div style=font-size:0.9rem;margin-top:8px;>Try: Explain photosynthesis simply or What is gravity?</div>
        </div>
        ", unsafe_allow_html=True)

    for message in st.session_state.chat_history:
        with st.chat_message(message[role]):
            st.markdown(message[content])

    user_question = st.chat_input(Ask EduGenie anything...)

    if user_question:
        with st.chat_message(user):
            st.markdown(user_question)
        st.session_state.chat_history.append({role: user, content: user_question})

        with st.chat_message(assistant):
            with st.spinner("):
 prompt = f"You are EduGenie, a world-class AI tutor. You explain concepts clearly and simply.
Always structure your response with clear sections. Use emojis to make it engaging.
Be friendly, encouraging, and educational. Use examples from real life.

Student question: {user_question}"
 response = model.generate_content(prompt)
 answer = response.text
 st.markdown(answer)
 st.session_state.chat_history.append({role: assistant, content: answer})

 if st.session_state.chat_history:
 st.markdown(<div style='height:8px'></div>, unsafe_allow_html=True)
 if st.button(🗑️ Clear conversation, key=clear_chat):
 st.session_state.chat_history = []
 st.rerun()

# ── TAB 2: STUDY MATERIAL ────────────────────────────────────────────
with tab2:
 st.markdown("
 <div style=margin-bottom:24px;>
 <div style=font-size:1.5rem;font-weight:700;margin-bottom:4px;>📝 Study Material Generator</div>
 <div style=color:#64748b;>Generate complete study notes on any topic in seconds</div>
 </div>
 ", unsafe_allow_html=True)

 col1, col2 = st.columns([3, 1])
 with col1:
 topic = st.text_input(, placeholder=🔍 Enter any topic... e.g. Photosynthesis, French Revolution, Calculus, label_visibility=collapsed)
 with col2:
 level = st.selectbox(, [🟢 Beginner, 🟡 Intermediate, 🔴 Advanced], label_visibility=collapsed)

 if st.button(✨ Generate Study Notes, key=gen_study, type=primary):
 if topic:
 with st.spinner(f✍️ Creating study material for '{topic}'...):
 prompt = f"Create comprehensive, well-structured study material for: {topic}
Level: {level}

Use this exact format with emojis and clear sections:

## 📌 What is {topic}?
(Clear introduction)

## 🔑 Key Concepts
(Most important points, numbered)

## 📊 Important Facts & Details
(Dates, formulas, statistics if applicable)

## 💡 Real-World Examples
(2-3 practical examples)

## 🎯 Quick Summary
(5 bullet points recap)

## ✅ Remember These!
(Top 3 things to memorize)

Make it engaging, educational and easy to understand."

 response = model.generate_content(prompt)
 st.markdown(f"
 <div style=background:rgba(99,102,241,0.05);border:1px solid rgba(99,102,241,0.2);border-radius:12px;padding:8px 16px;margin-bottom:16px;display:flex;align-items:center;gap:8px;>
 <span style=color:#10b981;>✅</span>
 <span style=color:#94a3b8;font-size:0.9rem;>Study notes generated for <strong style=color:white;>{topic}</strong></span>
 <span class=badge style=margin-left:auto;>{level}</span>
 </div>
 ", unsafe_allow_html=True)
 st.markdown(f'<div class=output-box>{response.text}</div>', unsafe_allow_html=True)
 st.download_button(⬇️ Download Notes, data=response.text, file_name=f{topic}_notes.txt, mime=text/plain)
 else:
 st.error(❌ Please enter a topic first!)

# ── TAB 3: QUIZ ──────────────────────────────────────────────────────
with tab3:
 st.markdown("
 <div style=margin-bottom:24px;>
 <div style=font-size:1.5rem;font-weight:700;margin-bottom:4px;>❓ Quiz Generator</div>
 <div style=color:#64748b;>Test your knowledge with AI-generated multiple choice questions</div>
 </div>
 ", unsafe_allow_html=True)

 col1, col2, col3 = st.columns(3)
 with col1:
 quiz_topic = st.text_input(, placeholder=📖 Quiz topic..., key=qtopic, label_visibility=collapsed)
 with col2:
 num_q = st.slider(Number of questions, 3, 10, 5)
 with col3:
 difficulty = st.selectbox(, [🟢 Easy, 🟡 Medium, 🔴 Hard], key=qdiff, label_visibility=collapsed)

 if st.button(🎯 Generate Quiz, key=gen_quiz, type=primary):
 if quiz_topic:
 with st.spinner(f🧠 Generating {num_q} questions about '{quiz_topic}'...):
 prompt = f"Generate a quiz about {quiz_topic} — exactly {num_q} multiple choice questions.
Difficulty: {difficulty}

Format EXACTLY like this for each question:

**Q[N]. [Question]**
- A) [Option]
- B) [Option]
- C) [Option]
- D) [Option]

> ✅ **Answer: [Letter]) [Explanation in one sentence]**

---

Make questions educational and test real understanding. Number Q1 to Q{num_q}."

 response = model.generate_content(prompt)
 st.markdown(f"
 <div style=background:rgba(99,102,241,0.05);border:1px solid rgba(99,102,241,0.2);border-radius:12px;padding:8px 16px;margin-bottom:16px;display:flex;align-items:center;gap:8px;>
 <span style=color:#10b981;>✅</span>
 <span style=color:#94a3b8;font-size:0.9rem;>Quiz ready: <strong style=color:white;>{quiz_topic}</strong> — {num_q} questions</span>
 <span class=badge style=margin-left:auto;>{difficulty}</span>
 </div>
 ", unsafe_allow_html=True)
 st.markdown(f'<div class=output-box>{response.text}</div>', unsafe_allow_html=True)
 st.download_button(⬇️ Download Quiz, data=response.text, file_name=f{quiz_topic}_quiz.txt, mime=text/plain)
 else:
 st.error(❌ Please enter a quiz topic!)

st.markdown("
<div style=text-align:center;color:#334155;font-size:0.8rem;padding:32px 0 16px;>
 🧞 EduGenie AI &nbsp;•&nbsp; Powered by Google Gemini &nbsp;•&nbsp; Built for learners everywhere 🌍
</div>
", unsafe_allow_html=True)
