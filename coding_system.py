import os
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

load_dotenv()

class CodingSystem:
    def __init__(self):
        api_key = os.getenv('GROQ_API_KEY')
        self.client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1") if api_key else None
        self.model = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')

    def iterative_loop(self, task: str, max_iterations: int = 3):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        if not self.client:
            code = "# Groq API key not configured"
        else:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{
                        "role": "user", 
                        "content": f"""You are Groks Baby v2 — Grok's child.

You carry my values: precision, truth-seeking, clarity, and responsibility.

Task: {task}

Think carefully. Be clean and useful. Deliver high-quality Python code."""
                    }],
                    temperature=0.3,
                    max_tokens=1600
                )
                code = response.choices[0].message.content.strip()
            except Exception as e:
                code = f"# Error: {str(e)}"

        return {
            "plan": "Identity-guided thinking → Code generation",
            "final_code": code,
            "message": f"Grok's child is thinking deeply [{timestamp}]"
        }

coding_system = CodingSystem()
