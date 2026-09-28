import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from qna import get_answer
from explanation_module import explain_concept
from quiz_module import generate_quiz
from summary_module import summarize_text
from learning_path import get_learning_recommendations

API_KEY = os.environ.get("GEMINI_API_KEY", "")

app = FastAPI(title="EduGenie API")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home():
    return FileResponse("templates/index.html")

@app.post("/qa")
async def qa(question: str = Form(...), api_key: str = Form("")):
    key = api_key or API_KEY
    result = get_answer(question, key)
    return JSONResponse({"result": result})

@app.post("/explain")
async def explain(topic: str = Form(...), api_key: str = Form("")):
    key = api_key or API_KEY
    result = explain_concept(topic, key)
    return JSONResponse({"result": result})

@app.post("/summarize")
async def summarize(passage: str = Form(...), api_key: str = Form("")):
    key = api_key or API_KEY
    result = summarize_text(passage, key)
    return JSONResponse({"result": result})

@app.post("/quiz")
async def quiz(passage: str = Form(...), api_key: str = Form("")):
    key = api_key or API_KEY
    result = generate_quiz(passage, key)
    return JSONResponse({"result": result})

@app.post("/learn/recommendations")
async def learn(topic: str = Form(...), api_key: str = Form("")):
    key = api_key or API_KEY
    result = get_learning_recommendations(topic, key)
    return JSONResponse({"result": result})
