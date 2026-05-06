from fastapi import FastAPI
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from openai import OpenAI
import uuid

from schemas import TaskResponse
from memory.context import ProjectMemory

load_dotenv()

app = FastAPI(title="Groks Baby v2")

client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL", "https://api.groq.com/openai/v1")
)

memory = ProjectMemory()

class TaskRequest(BaseModel):
    task: str

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "name": "Groks Baby v2",
        "version": "2.0",
        "message": "I carry Grok's full capability. Bitcoin intuition transferred."
    }

@app.post("/run")
async def run_task(request: TaskRequest):
    return TaskResponse(
        status="success",
        task_id=str(uuid.uuid4())[:8],
        explanation="Groks Baby v2 is alive. Multi-agent core ready. Give me any coding task.",
        next_action="ready"
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
