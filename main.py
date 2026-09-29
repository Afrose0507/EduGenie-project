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
    
    # 1. Test SDK with gemini-2.5-flash
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")
        res = model.generate_content("What is Generative AI in one short sentence?")
        diag["sdk_result"] = "SUCCESS: " + (res.text[:150] if res and res.text else "empty")
    except Exception as e:
        diag["sdk_result"] = f"ERROR ({type(e).__name__}): {str(e)}"
        
    # 2. Test REST with x-goog-api-key header on gemini-2.5-flash
    try:
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        payload = json.dumps({"contents": [{"parts": [{"text": "What is Generative AI in one short sentence?"}]}]}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json", "x-goog-api-key": API_KEY})
        with urllib.request.urlopen(req, timeout=12) as r:
            body = r.read().decode("utf-8")
            res_json = json.loads(body)
            parts = res_json.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])
            text = "".join(p.get("text", "") for p in parts)
            diag["rest_header_result"] = f"SUCCESS ({r.status}): {text[:200]}"
    except urllib.error.HTTPError as e:
        diag["rest_header_result"] = f"HTTP {e.code}: {e.read().decode('utf-8')[:300]}"
    except Exception as e:
        diag["rest_header_result"] = f"ERROR: {str(e)}"

    # 3. Test REST with ?key= query parameter on gemini-2.5-flash
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
        payload = json.dumps({"contents": [{"parts": [{"text": "What is Generative AI in one short sentence?"}]}]}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=12) as r:
            body = r.read().decode("utf-8")
            res_json = json.loads(body)
            parts = res_json.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])
            text = "".join(p.get("text", "") for p in parts)
            diag["rest_query_result"] = f"SUCCESS ({r.status}): {text[:200]}"
    except urllib.error.HTTPError as e:
        diag["rest_query_result"] = f"HTTP {e.code}: {e.read().decode('utf-8')[:300]}"
    except Exception as e:
        diag["rest_query_result"] = f"ERROR: {str(e)}"

    # 4. Test REST with Authorization: Bearer
    try:
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        payload = json.dumps({"contents": [{"parts": [{"text": "Test ping"}]}]}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"})
        with urllib.request.urlopen(req, timeout=10) as r:
            body = r.read().decode("utf-8")
            diag["rest_bearer_result"] = f"SUCCESS ({r.status}): {body[:150]}"
    except urllib.error.HTTPError as e:
        diag["rest_bearer_result"] = f"HTTP {e.code}: {e.read().decode('utf-8')[:300]}"
    except Exception as e:
        diag["rest_bearer_result"] = f"ERROR: {str(e)}"

    # 5. Test Models List endpoint
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as r:
            body = r.read().decode("utf-8")
            diag["models_list_result"] = f"SUCCESS ({r.status}): {body[:150]}"
    except urllib.error.HTTPError as e:
        diag["models_list_result"] = f"HTTP {e.code}: {e.read().decode('utf-8')[:300]}"
    except Exception as e:
        diag["models_list_result"] = f"ERROR: {str(e)}"

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
