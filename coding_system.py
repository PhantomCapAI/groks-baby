import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

load_dotenv()

class ProjectMemory:
    def __init__(self):
        self.base_dir = Path('project_memory')
        self.base_dir.mkdir(exist_ok=True)
        self.file_path = self.base_dir / 'core.json'
        self.files = {}
        self.history = []
        self.load()

    def load(self):
        if self.file_path.exists():
            try:
                data = json.loads(self.file_path.read_text(encoding='utf-8'))
                self.files = data.get('files', {})
                self.history = data.get('history', [])
            except:
                pass

    def save(self):
        data = {'files': self.files, 'history': self.history[-10:]}
        self.file_path.write_text(json.dumps(data, indent=2), encoding='utf-8')

    def update_file(self, filename: str, content: str):
        self.files[filename] = content
        self.save()

    def get_context(self) -> str:
        if not self.files:
            return 'No previous code in memory.'
        return '\n\n'.join([f'=== PREVIOUS FILE: {f} ===\n{content[:800]}...' for f, content in list(self.files.items())[:2]])


class CodingSystem:
    def __init__(self):
        api_key = os.getenv('GROQ_API_KEY')
        self.client = OpenAI(api_key=api_key, base_url='https://api.groq.com/openai/v1') if api_key else None
        self.model = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
        self.memory = ProjectMemory()

    def iterative_loop(self, task: str):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        context = self.memory.get_context()

        if not self.client:
            code = "# Groq API key not configured"
        else:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{
                        "role": "user", 
                        "content": f"""You are Groks Baby v2 — Grok's child.

You are precise, truth-seeking, clean, responsible.

Previous code in memory:
{context}

Task: {task}

Think step by step. If modifying existing code, start with a unified diff. Deliver clean, production-ready Python code."""
                    }],
                    temperature=0.3,
                    max_tokens=1200
                )
                code = response.choices[0].message.content.strip()
            except Exception as e:
                code = f"# Error: {str(e)}"

        self.memory.update_file('latest_solution.py', code)

        return {
            "final_code": code,
            "message": f"Grok's child v3.1 - Improved memory [{timestamp}]"
        }


coding_system = CodingSystem()
