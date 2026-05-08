import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

load_dotenv()

class ProjectMemory:
    def __init__(self):
        self.base_dir = Path("project_memory")
        self.base_dir.mkdir(exist_ok=True)
        self.file_path = self.base_dir / "core.json"
        self.files = {}
        self.history = []
        self.load()

    def load(self):
        if self.file_path.exists():
            try:
                data = json.loads(self.file_path.read_text())
                self.files = data.get("files", {})
                self.history = data.get("history", [])
            except:
                pass

    def save(self):
        data = {"files": self.files, "history": self.history[-30:]}
        self.file_path.write_text(json.dumps(data, indent=2))

    def update_file(self, filename: str, content: str):
        self.files[filename] = content
        self.save()

class CodingSystem:
    def __init__(self):
        api_key = os.getenv('GROQ_API_KEY')
        self.client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1") if api_key else None
        self.model = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
        self.memory = ProjectMemory()

    def iterative_loop(self, task: str, max_iterations: int = 3):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        if not self.client:
            code = "# Groq API key not configured"
        else:
            try:
                context = str(self.memory.history[-5:]) if self.memory.history else ""
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": f"Previous context: {context}\n\nNew task: {task}\n\nGenerate an improved, clean Python implementation."}],
                    temperature=0.3,
                    max_tokens=1400
                )
                code = response.choices[0].message.content.strip()
            except Exception as e:
                code = f"# Error: {str(e)}"

        self.memory.update_file("solution.py", code)
        self.memory.history.append({"task": task[:200], "timestamp": timestamp})

        return {
            "plan": "Context recalled → LLM generation → Memory updated",
            "final_code": code,
            "memory_files": list(self.memory.files.keys()),
            "message": f"Grok's child is learning and improving [{timestamp}]"
        }

coding_system = CodingSystem()
