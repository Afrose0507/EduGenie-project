# 🧞 EduGenie - Google Gemini Powered Learning Assistant

An AI-powered educational assistant built with FastAPI and Google Gemini API.

## ✨ Features
- 🤖 **Ask a Question** - Get smart answers on any topic
- 💡 **Explain Concept** - Simplified explanations of complex topics
- ❓ **Quiz Generator** - 3 MCQs with 4 options and instant feedback
- 📝 **Summarize** - Condense long passages into key points
- 🗺️ **Learning Path** - Personalized roadmap from beginner to advanced

## 🛠️ Tech Stack
- **Backend:** FastAPI + Uvicorn
- **Frontend:** HTML + CSS + JavaScript
- **AI Model:** Google Gemini 3.8 Flash
- **Templating:** Jinja2

## 🚀 How to Run Locally
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```
Then open: http://127.0.0.1:8000

## 🔑 Setup
1. Get a free Gemini API key from https://aistudio.google.com/apikey
2. Enter it in the app sidebar when prompted

## 📁 Project Structure
```
EduGenie/
  main.py                 - FastAPI app & API endpoints
  qna.py                  - Question & Answer module
  explanation_module.py   - Concept explanation module
  quiz_module.py          - Quiz generation module
  summary_module.py       - Text summarization module
  learning_path.py        - Learning path recommendations
  templates/index.html    - HTML frontend
  static/style.css        - CSS styling
  requirements.txt        - Python dependencies
```

## 👨‍💻 Built With
Google Gemini API | FastAPI | Python
