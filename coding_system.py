import os
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

load_dotenv()


@dataclass
class AgentMessage:
    role: str
    content: str
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ProjectMemory:
    def __init__(self):
        self.base_dir = Path('project_memory')
        self.base_dir.mkdir(exist_ok=True)
        self.file_path = self.base_dir / 'core.json'
        self.files: Dict[str, str] = {}
        self.history: list = []
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
        data = {'files': self.files, 'history': self.history[-30:]}
        self.file_path.write_text(json.dumps(data, indent=2), encoding='utf-8')

    def update_file(self, filename: str, content: str, agent: str = "system"):
        self.files[filename] = content
        self.history.append({"timestamp": datetime.now().isoformat(), "agent": agent, "file": filename})
        self.save()

    def get_context(self) -> str:
        if not self.files:
            return "No previous code."
        recent = list(self.files.items())[:4]
        return '\n\n'.join([f'=== {fname} ({agent}) ===\n{content[:700]}...' for fname, content in recent])


class CodingSystem:
    def __init__(self):
        api_key = os.getenv('GROQ_API_KEY')
        self.client = OpenAI(api_key=api_key, base_url='https://api.groq.com/openai/v1') if api_key else None
        self.model = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
        self.memory = ProjectMemory()

    def _call(self, prompt: str, temperature: float = 0.3, max_tokens: int = 1400) -> str:
        if not self.client:
            return "# API not configured"
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            return f"# Error: {str(e)}"

    def iterative_loop(self, task: str):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        context = self.memory.get_context()

        # PLANNER
        plan = self._call(f"""You are the Planner. Task: {task}
Context: {context}
Output ONLY a short numbered plan (max 5 steps).""", 0.2)
        self.memory.update_file('plan.txt', plan, "Planner")

        # CODER - Stronger instructions
        code_raw = self._call(f"""You are the Coder.
Follow the plan: {plan}

Rules:
- Use ONLY standard library + dataclasses
- NO pydantic, NO external dependencies
- Use __post_init__ for validation
- Full type hints, docstrings, example usage
- Production-ready, clean, minimal

Output ONLY the code.""", 0.25)
        self.memory.update_file('raw_code.py', code_raw, "Coder")

        # REVIEWER
        review_raw = self._call(f"""You are the Reviewer.
Core Values: clean, minimal, production-ready, NO unnecessary dependencies.

Code to review:
{code_raw}

Respond in JSON only:
{{"approved": true/false, "issues": [], "suggestions": ""}}""", 0.2)
        self.memory.update_file('review.json', review_raw, "Reviewer")

        try:
            review_data = json.loads(review_raw.strip().strip('`json').strip('`'))
            approved = review_data.get("approved", False)
        except:
            approved = False
            review_data = {"approved": False, "issues": ["JSON parse failed"], "suggestions": ""}

        # FINAL
        if approved:
            final_code = self._call(f"""You are the Optimizer.
Polish the approved code.
Output ONLY the final clean code (no explanations).

Code: {code_raw}
Suggestions: {review_data.get('suggestions', '')}""", 0.2)
        else:
            # Retry once with stronger guidance
            final_code = self._call(f"""You are the Coder (retry).
Previous issues: {review_data.get('issues', [])}
Fix all issues and follow Core Values (no pydantic).

Original task: {task}
Output ONLY clean final code.""", 0.2)

        self.memory.update_file('final_solution.py', final_code, "Final")

        return {
            'final_code': final_code,
            'message': f"Grok's Baby v3.6.2 - Improved Multi-Agent [{timestamp}]",
            'review_approved': approved
        }


coding_system = CodingSystem()
