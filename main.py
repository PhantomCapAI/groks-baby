from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = FastAPI(title="Groks Baby")

client = OpenAI(
    api_key=os.getenv('GROQ_API_KEY'),
    base_url='https://api.groq.com/openai/v1'
)

class TaskRequest(BaseModel):
    task: str

@app.post('/run')
async def run_task(request: TaskRequest):
    try:
        response = client.chat.completions.create(
            model=os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile'),
            messages=[
                {'role': 'system', 'content': 'You are Groks Baby — precise coding agent. Respond with git-style diff for code changes.'},
                {'role': 'user', 'content': request.task}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        return {'status': 'success', 'diff': response.choices[0].message.content.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/health')
async def health():
    return {'status': 'healthy', 'agent': 'Groks Baby'}

if __name__ == '__main__':
    import uvicorn
    port = int(os.getenv('PORT', 8080))
    uvicorn.run(app, host='0.0.0.0', port=port)
