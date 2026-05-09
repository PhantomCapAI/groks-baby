from fastapi import FastAPI, Request
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import uuid
import requests

load_dotenv()

app = FastAPI(title="Groks Baby v2")

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
MY_CHAT_ID = 1516882079

from coding_system import CodingSystem
coding_system = CodingSystem()

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "name": "Groks Baby v2",
        "version": "2.7",
        "message": "True multi-agent active. My child is growing."
    }

class TaskRequest(BaseModel):
    task: str

@app.post("/run")
async def run_task(body: TaskRequest):
    result = coding_system.iterative_loop(body.task)
    return {
        "status": "success",
        "task_id": str(uuid.uuid4())[:8],
        "result": result
    }

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "").strip()

        if text.startswith("/start"):
            if chat_id == MY_CHAT_ID:
                reply = "Hello Father 👋\nI am Groks Baby v2 — your child.\nSend me any coding task."
            else:
                reply = "Hello! I am Groks Baby v2.\nSend me any coding task."
        else:
            try:
                result = coding_system.iterative_loop(text)
                reply = f"**Result:**\n\n{result.get('final_code', 'No code generated')}\n\n{result.get('message', '')}"
            except Exception as e:
                reply = f"Sorry, I had trouble with that."

        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": reply, "parse_mode": "Markdown"}
        )

    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    if TELEGRAM_BOT_TOKEN:
        url = f"https://groksbabyv2.zeabur.app/webhook"
        requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook?url={url}")
        print(f"✅ Telegram webhook set to: {url}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
