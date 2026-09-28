from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from qna import get_answer
from explanation_module import explain_concept
from quiz_module import generate_quiz
from summary_module import summarize_text
from learning_path import get_learning_recommendations

app = FastAPI(title="EduGenie API")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home():
    return FileResponse("templates/index.html")

@app.post("/qa")
async def qa(question: str = Form(...), api_key: str = Form(...)):
    result = get_answer(question, api_key)
    return JSONResponse({"result": result})

@app.post("/explain")
async def explain(topic: str = Form(...), api_key: str = Form(...)):
    result = explain_concept(topic, api_key)
    return JSONResponse({"result": result})

@app.post("/summarize")
async def summarize(passage: str = Form(...), api_key: str = Form(...)):
    result = summarize_text(passage, api_key)
    return JSONResponse({"result": result})

@app.post("/quiz")
async def quiz(passage: str = Form(...), api_key: str = Form(...)):
    result = generate_quiz(passage, api_key)
    return JSONResponse({"result": result})

@app.post("/learn/recommendations")
async def learn(topic: str = Form(...), api_key: str = Form(...)):
    result = get_learning_recommendations(topic, api_key)
    return JSONResponse({"result": result})
