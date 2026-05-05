from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from coding_system import CodingSystem

app = FastAPI(title="Zeabur Coding Agent")
coding_system = CodingSystem()

class TaskRequest(BaseModel):
    task: str

@app.post('/run')
async def run_task(request: TaskRequest):
    try:
        result = coding_system.iterative_loop(request.task)
        return {
            'status': 'success',
            'diff': result,
            'iterations': len(coding_system.memory_short)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/health')
async def health():
    return {'status': 'healthy'}

if __name__ == '__main__':
    import uvicorn
    port = int(os.getenv('PORT', 8080))
    uvicorn.run(app, host='0.0.0.0', port=port)
