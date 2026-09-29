import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from qna import get_answer
from explanation_module import explain_concept
from quiz_module import generate_quiz
from summary_module import summarize_text
from learning_path import get_learning_recommendations

API_KEY = (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or os.environ.get("API_KEY") or "").strip().strip('"').strip("'")

app = FastAPI(title="EduGenie API")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home():
    return FileResponse("templates/index.html")

@app.get("/api/status")
async def api_status():
    has_key = bool(API_KEY and len(API_KEY) > 10)
    return {
        "status": "online",
        "has_server_api_key": has_key,
        "key_preview": f"{API_KEY[:6]}...{API_KEY[-4:]}" if has_key else "Not Configured on Render"
    }

@app.get("/api/diagnose")
async def api_diagnose():
    import urllib.request, urllib.error, json
    import google.generativeai as genai
    
    diag = {
        "key_length": len(API_KEY),
        "key_prefix": API_KEY[:6] if API_KEY else "",
        "key_suffix": API_KEY[-4:] if API_KEY else "",
        "has_whitespace": bool(API_KEY and (" " in API_KEY or "\n" in API_KEY or "\r" in API_KEY or "\t" in API_KEY)),
    }
    
    # 1. Test gemini_client.generate_text directly
    try:
        from gemini_client import generate_text
        direct_ans = generate_text("What is Artificial Intelligence in one short sentence?", API_KEY)
        diag["direct_generate_text_result"] = f"SUCCESS: {direct_ans[:200]}" if direct_ans else "RETURNED_NONE"
    except Exception as e:
        diag["direct_generate_text_result"] = f"ERROR: {str(e)}"

    # 2. Test REST with x-goog-api-key header on gemini-3.8-flash
    try:
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent"
        payload = json.dumps({"contents": [{"parts": [{"text": "What is Artificial Intelligence in one sentence?"}]}]}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json", "x-goog-api-key": API_KEY})
        with urllib.request.urlopen(req, timeout=25) as r:
            body = r.read().decode("utf-8")
            res_json = json.loads(body)
            parts = res_json.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])
            text = "".join(p.get("text", "") for p in parts if not p.get("thought", False))
            if not text:
                text = "".join(p.get("text", "") for p in parts)
            diag["gemini_3_8_rest_header"] = f"SUCCESS ({r.status}): {text[:200]}"
    except urllib.error.HTTPError as e:
        diag["gemini_3_8_rest_header"] = f"HTTP {e.code}: {e.read().decode('utf-8')[:300]}"
    except Exception as e:
        diag["gemini_3_8_rest_header"] = f"ERROR: {str(e)}"

    # 3. Test Models List endpoint and list available generate models
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as r:
            body = r.read().decode("utf-8")
            data = json.loads(body)
            models = [m.get("name") for m in data.get("models", []) if "generateContent" in m.get("supportedGenerationMethods", [])]
            diag["models_list_available"] = models[:10]
    except urllib.error.HTTPError as e:
        diag["models_list_available"] = f"HTTP {e.code}: {e.read().decode('utf-8')[:300]}"
    except Exception as e:
        diag["models_list_available"] = f"ERROR: {str(e)}"

    return diag

@app.post("/qa")
async def qa(question: str = Form(...), api_key: str = Form("")):
    key = api_key.strip() or API_KEY
    result = get_answer(question, key)
    return JSONResponse({"result": result})

@app.post("/explain")
async def explain(topic: str = Form(...), api_key: str = Form("")):
    key = api_key.strip() or API_KEY
    result = explain_concept(topic, key)
    return JSONResponse({"result": result})

@app.post("/summarize")
async def summarize(passage: str = Form(...), api_key: str = Form("")):
    key = api_key.strip() or API_KEY
    result = summarize_text(passage, key)
    return JSONResponse({"result": result})

@app.post("/quiz")
async def quiz(passage: str = Form(...), api_key: str = Form("")):
    key = api_key.strip() or API_KEY
    result = generate_quiz(passage, key)
    return JSONResponse({"result": result})

@app.post("/learn/recommendations")
async def learn(topic: str = Form(...), api_key: str = Form("")):
    key = api_key.strip() or API_KEY
    result = get_learning_recommendations(topic, key)
    return JSONResponse({"result": result})
