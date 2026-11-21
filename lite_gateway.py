import copy, os, time
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

load_dotenv()
app = FastAPI(title="Zero-Downtime AI Gateway Lite", version="1.0.0")
cooldown_until = {"primary": 0.0, "fallback": 0.0}

def get_targets():
    return [
        ("primary", os.getenv("PRIMARY_BASE_URL", "").strip(), os.getenv("PRIMARY_API_KEY", "local").strip(), os.getenv("PRIMARY_MODEL", "").strip()),
        ("fallback", os.getenv("FALLBACK_BASE_URL", "").strip(), os.getenv("FALLBACK_API_KEY", "local").strip(), os.getenv("FALLBACK_MODEL", "").strip()),
    ]

def clean_payload(payload: dict, base_url: str, model: str) -> dict:
    body = copy.deepcopy(payload)
    body["model"] = model
    body["stream"] = False
    if "groq.com" in base_url.lower():
        for k in ("logprobs", "logit_bias", "top_logprobs"):
            body.pop(k, None)
        if body.get("n") not in (None, 1):
            body["n"] = 1
        for m in body.get("messages", []):
            if isinstance(m, dict):
                m.pop("name", None)
    return body

@app.get("/health")
async def health():
    now = time.time()
    return {"status": "ok", "cooldown_sec": {k: max(0, int(v - now)) for k, v in cooldown_until.items()}}

@app.post("/v1/chat/completions")
async def chat(request: Request):
    payload = await request.json()
    now = time.time()
    targets = [t for t in get_targets() if t[1] and t[3]]
    targets.sort(key=lambda t: 0 if cooldown_until[t[0]] <= now else 1)
    errors = []
    async with httpx.AsyncClient(timeout=60.0) as client:
        for idx, (slot, base_url, api_key, model) in enumerate(targets):
            url = base_url.rstrip("/") + "/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            try:
                r = await client.post(url, headers=headers, json=clean_payload(payload, base_url, model))
                if r.status_code == 200:
                    cooldown_until[slot] = 0.0
                    return JSONResponse(r.json(), headers={"X-Gateway-Slot": slot, "X-Gateway-Model": model, "X-Gateway-Failovers": str(idx)})
                cooldown_until[slot] = time.time() + (90 if r.status_code == 429 else 30)
                errors.append(f"{slot}: HTTP {r.status_code}")
            except Exception as exc:
                cooldown_until[slot] = time.time() + 30
                errors.append(f"{slot}: {exc}")
    raise HTTPException(status_code=503, detail={"message": "All providers failed", "errors": errors})