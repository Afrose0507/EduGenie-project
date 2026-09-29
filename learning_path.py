import google.generativeai as genai

MODELS = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]

def get_learning_recommendations(topic: str, api_key: str) -> str:
    prompt = f"""You are EduGenie, an expert curriculum designer and academic advisor.
Design an extensive, high-impact, step-by-step learning roadmap for mastering "{topic}".

You MUST format the response with the following clear markdown headers:

### 📖 Curriculum Introduction & Scope
(A comprehensive overview of what mastering this subject entails, its industry relevance, career pathways, and expected learning outcomes.)

### ⚡ Quick Roadmap Overview (Short Answer)
(A crisp 2-3 sentence summary of the learning trajectory from novice to professional.)

### 🔑 Key Prerequisites & Foundational Skills
(Bullet points listing essential prior knowledge, software tools, development environments, or core concepts required.)

### 🔬 Deep Dive: Step-by-Step Structured Curriculum
#### 🟢 Phase 1: Beginner Fundamentals (Weeks 1 - 2)
(Topics, theoretical principles, hands-on tutorials, milestone test.)
#### 🟡 Phase 2: Intermediate Mastery & Problem Solving (Weeks 3 - 4)
(Core workflows, libraries, mini-projects, debugging practices, milestone challenge.)
#### 🔴 Phase 3: Advanced Specialization & Capstone Project (Weeks 5 - 6)
(Architecture, performance tuning, real-world deployment, portfolio capstone project.)

### 💡 Academic & Professional Next Steps
(Certification advice, interview questions, and recommended open-source contributions.)"""

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

    return f"""### 📖 Curriculum Introduction & Scope
Mastering **{topic}** requires a methodical approach that balances foundational theory with rigorous hands-on practice. In modern academia and industry, proficiency in this subject opens avenues across high-impact research, engineering, and innovative technological development.

### ⚡ Quick Roadmap Overview (Short Answer)
This 6-week curriculum transitions learners from foundational terminology and core mechanics (Weeks 1–2) through practical project implementation (Weeks 3–4) to enterprise-grade mastery and capstone deployment (Weeks 5–6).

### 🔑 Key Prerequisites & Foundational Skills
- **Analytical Problem-Solving:** Ability to decompose complex problems into modular steps.
- **Environment Setup:** Installing necessary development tools, compilers/interpreters, and documentation readers.
- **Core Mathematics / Logic:** Basic understanding of logical operators, algorithmic flow, and data organization.
- **Version Control:** Familiarity with Git and GitHub for tracking code milestones.

### 🔬 Deep Dive: Step-by-Step Structured Curriculum

#### 🟢 Phase 1: Beginner Fundamentals (Weeks 1 - 2)
- **Objective:** Grasp core syntax, fundamental rules, and basic operational models.
- **Week 1 Topics:** Setting up workspace, terminology, core variables, control flow, and basic functions.
- **Week 2 Topics:** Standard data structures, basic error handling, reading documentation, and writing first scripts.
- **Milestone 1:** Build 5 fundamental test programs and score 90%+ on foundational quiz tests.

#### 🟡 Phase 2: Intermediate Mastery & Problem Solving (Weeks 3 - 4)
- **Objective:** Apply concepts to solve real-world problems and construct functional modules.
- **Week 3 Topics:** Object-oriented design, modular programming, external libraries, and data serialization.
- **Week 4 Topics:** Database integration, API consumption, testing suites, and performance optimization.
- **Milestone 2:** Develop a working standalone project incorporating persistent storage and interactive UI.

#### 🔴 Phase 3: Advanced Specialization & Capstone Project (Weeks 5 - 6)
- **Objective:** Achieve production readiness, security compliance, and architectural excellence.
- **Week 5 Topics:** Asynchronous processing, architectural patterns, design patterns, and deployment pipelines.
- **Week 6 Topics:** Capstone project development, unit testing, documentation, and peer review.
- **Milestone 3:** Deploy your finished capstone project to a live public cloud server (e.g., Render or GitHub Pages).

### 💡 Academic & Professional Next Steps
Document your learning journey on GitHub, write technical breakdown articles, solve competitive practice challenges, and prepare for industry-recognized certifications."""
