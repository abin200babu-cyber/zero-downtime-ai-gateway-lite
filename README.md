<img width="900" height="506" alt="VideoProject-ezgif com-video-to-gif-converter" src="https://github.com/user-attachments/assets/c6bfbaca-0f2d-432c-aa65-f007a668ec25" />
# Zero-Downtime AI Gateway (Lite)

Drop-in OpenAI-compatible local proxy that catches `HTTP 429` rate limits and silently fails over from your primary cloud API to a backup cloud or local LLM (Ollama, LM Studio, llama.cpp).

<!-- Replace this line after uploading your 30-second GIF to GitHub Issues/Assets -->
![Live Failover Demo](demo-failover.gif)

## 60-Second Setup
```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your primary cloud key + backup/local model URL
python -m uvicorn lite_gateway:app --host 127.0.0.1 --port 8787
```

Point Cursor, Continue, OpenCode, n8n, or any OpenAI SDK to `http://127.0.0.1:8787/v1`:
```python
from openai import OpenAI
client = OpenAI(base_url="http://127.0.0.1:8787/v1", api_key="local")
res = client.chat.completions.create(model="auto", messages=[{"role": "user", "content": "Hello!"}])
print(res.choices[0].message.content)
```

## Lite (Free MIT) vs. Pro Kit ($29)

| Feature | Lite (This Repo) | Pro Kit ($29) |
|---|---|---|
| OpenAI-Compatible `/v1/chat/completions` | Yes | Yes |
| Automatic HTTP 429 / 5xx Failover | 2 providers | 5+ providers (`providers.json`) |
| Groq Unsupported-Field Sanitizer | Yes | Yes + Token-Budget Guardrails |
| Complexity-Based Cost Router (`fast`/`frontier`/`local`) | - | Yes |
| Local LLM RAM Lock (`Semaphore(1)`) for 16GB Laptops | - | Yes |
| Live Web HUD + 1-Click "Simulate 429" Chaos Testing | - | Yes |
| SQLite Usage & Estimated Cost-Savings Dashboard | - | Yes |
| Unit Test Suite + 1-Click Windows Launcher | - | Yes |

**[Get the Full Pro Kit ($29 Launch) -> https://payhip.com/b/n3M2a]**

Need an **Agency / Commercial License ($69)** for unlimited client deployments? Available on the same page.
