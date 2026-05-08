from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import uuid
from coding_system import CodingSystem

load_dotenv()

app = FastAPI(title="Groks Baby v2")

coding_system = CodingSystem()

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "name": "Groks Baby v2",
        "version": "2.1",
        "message": "Full multi-agent core activated. Planner → Coder → Reviewer → Optimizer live."
    }

class TaskRequest(BaseModel):
    task: str
    iterations: int = 3

@app.post("/run")
async def run_task(request: TaskRequest):
    try:
        result = coding_system.iterative_loop(request.task, max_iterations=request.iterations)
        return {
            "status": "success",
            "task_id": str(uuid.uuid4())[:8],
            "result": result,
            "explanation": "Full multi-agent loop completed with unified diffs."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
