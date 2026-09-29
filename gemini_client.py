import json
import urllib.request
import urllib.error
import os

MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.5-pro",
    "gemini-flash-latest"
]

def generate_text(prompt: str, api_key: str, system_instruction: str = None) -> str:
    """
    Sends prompt to Google Gemini Generative Language API.
    Uses direct REST with x-goog-api-key header and query parameter fallback,
    ensuring 100% compatibility with both AQ. authorization keys and legacy AIza keys.
    """
    clean_key = (api_key or "").strip().strip('"').strip("'")
    if not clean_key:
        return None

    full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": full_prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 2048
        }
    }
    data = json.dumps(payload).encode("utf-8")

    for model_name in MODELS:
        # 1. Header: x-goog-api-key (Google's official method for AQ. and AIza keys)
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
            req = urllib.request.Request(
                url,
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "x-goog-api-key": clean_key
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=15) as res:
                res_data = json.loads(res.read().decode("utf-8"))
                candidates = res_data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    text = "".join(p.get("text", "") for p in parts).strip()
                    if text:
                        return text
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            print(f"[Gemini REST HTTP {e.code} ({model_name})]: {err_body[:200]}")
        except Exception as e:
            print(f"[Gemini REST Error ({model_name})]: {e}")

        # 2. Query param: ?key=
        try:
            url_param = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={clean_key}"
            req = urllib.request.Request(
                url_param,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=15) as res:
                res_data = json.loads(res.read().decode("utf-8"))
                candidates = res_data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    text = "".join(p.get("text", "") for p in parts).strip()
                    if text:
                        return text
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            print(f"[Gemini Query Param HTTP {e.code} ({model_name})]: {err_body[:200]}")
        except Exception as e:
            print(f"[Gemini Query Param Error ({model_name})]: {e}")

    # 3. Fallback via SDK if installed
    try:
        import google.generativeai as genai
        genai.configure(api_key=clean_key)
        for model_name in MODELS:
            try:
                model = genai.GenerativeModel(model_name)
                res = model.generate_content(full_prompt)
                if res and res.text and res.text.strip():
                    return res.text.strip()
            except Exception as e:
                print(f"[Gemini SDK Fallback Error ({model_name})]: {e}")
    except Exception as e:
        print(f"[Gemini SDK Config Error]: {e}")

    return None
